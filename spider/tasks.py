# -*- coding: utf-8 -*-
# @Time    : 6/20/19 11:15 PM
# @Author  : linix

import json
import datetime
import requests
import re
import time
import redis
from celery.task import task,periodic_task
from celery.schedules import crontab
from scrapyd_api import ScrapydAPI
from .models import Spider
from hangzhou.models import MovieCrawlState,MusicCrawlState,MovieOfflineData,VideoDetailsData
from django.conf import settings
from django.db.models import Q

scrapydBatchSize=16
maxBatchCheckNums=256

@task()
def add(x,y):
    return x+y

def getRunServer(deployProject='offlineCheckSpiders'):
    """
    :return: 返回pending和running状态任务数最少的机器,暂时按每个任务进行一次安排。如果超过最大任务数就不添加任务
    """
    servers=settings.SCRAPYD_URLS
    minTaskServer=None
    minTasks=-1
    for server in servers:
        try:
            scrapyd = ScrapydAPI(server, timeout=8)
            jobs=scrapyd.list_jobs(project=deployProject)
            taskNums=len(jobs.get('pending',[]))+len(jobs.get('running',[]))
            print("server: %s Running tasks is %s" % (server, taskNums))
            if taskNums<scrapydBatchSize//2:
                return server
            if (taskNums<minTasks or minTasks<0) :
                minTaskServer=server
                minTasks=taskNums
        except BaseException as e:
            print(" %s this server is not deployed, %s" %(server,e))

    return minTaskServer

def setDeParams(dictPara):
    fields=dictPara.get('filterFields',{})
    spiderName=dictPara.get('spider_name',"")
    spiderObjs = Spider.objects.get(Q(name__exact=spiderName),Q(status__exact=0))
    proxyType=dictPara.get("proxyType","0")
    batchCheckNums=int(dictPara.get("batchCheckNums","1"))
    if batchCheckNums>maxBatchCheckNums:
        batchCheckNums=maxBatchCheckNums
    elif batchCheckNums<1:
        batchCheckNums=1
    extraParams={
        'proxytype':proxyType,
    }

    return spiderObjs,fields,batchCheckNums,extraParams

def commonSchedule(type,catagery,isChangeScheduleStatus):
    if type==2:
        if catagery == 1:
            results = MovieCrawlState.objects.filter(crawl__exact=10).filter(task__exact=catagery)
        else:
            results = MovieCrawlState.objects.filter(crawl__exact=10).filter(manage__exact=0).filter(task__exact=catagery)
    elif type==3:
        if catagery == 1:
            results = MusicCrawlState.objects.filter(crawl__exact=11).filter(task__exact=catagery)
        else:
            results = MusicCrawlState.objects.filter(crawl__exact=11).filter(manage__exact=0).filter(task__exact=catagery)

    if catagery!=1:
        results=results[:(len(settings.SCRAPYD_URLS)*scrapydBatchSize)]

    if len(results):
        addProxyWhiteList()

    for item in results:
        try:
            dictParam = json.loads(item.json) if item.json else {}
        except BaseException as e:
            print("json传入非法数据！")
            dictParam = {}
        spider, fields, batchCheckNums,extraParams = setDeParams(dictParam)
        extraParams = json.dumps(extraParams, ensure_ascii=False, separators=(',', ':'))
        if isChangeScheduleStatus:
            item.manage=1
        if spider and len(fields):
            try:
                if type==2:
                    args=(~Q(tag__exact='已下线'))
                    records=MovieOfflineData.objects.filter(args,**fields)
            except BaseException as e:
                print("过滤下线数据时出错,原因：%s" %e)
                records=[]

            deployProject = spider.deployProject
            i =0
            scheduleServer = None

            j=k=1
            paramList=[]

            for record in records:
                if i%scrapydBatchSize==0 and (j-1)%batchCheckNums==0:
                    scheduleServer = getRunServer(deployProject)

                if scheduleServer:
                    scrapyd = ScrapydAPI(scheduleServer, timeout=8)
                    #print(deployProject, spider.name, record.id, record.url, extraParams)

                    paramList.append({'id': record.id, 'targetUrl': record.url})
                    if j%batchCheckNums==0 or k==len(records):
                        params=json.dumps(paramList, ensure_ascii=False, separators=(',', ':'))
                        print(params)
                        status=scrapyd.schedule(project=deployProject, spider=spider.name, taskId=item.id,idTargetUrlList=params,extraParams=extraParams)
                        print(status)
                        paramList = []
                        i+=1
                    j+=1
                k+=1
            item.startNum = j-1 #开始数量设置为实际调度的数量，不用总的记录数，item.startNum = len(records)
        item.save()

def addProxyWhiteList():
    proxyPoolServer = redis.Redis(host=settings.IP_POOL_REDIS_HOST, port=settings.IP_POOL_REDIS_PORT,password=settings.IP_POOL_REDIS_PWD, decode_responses=True)
    proxyNotUsedZSetKey = 'PROXY:NotUsedSortedSet'
    url = "http://webapi.http.zhimacangku.com/getip?num={ipNum}&type=2&pro=&city=0&yys=0&port=11&time={timeType}&ts=1&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=".format(ipNum='1',timeType='1')
    res = requests.get(url, verify=True)
    try:
        info = json.loads(res.text)
        codeType = info.get('code')
    except BaseException as e:
        print("解析代理网站json出错，reason:%s" % e)
        return
    if codeType == 113:
        ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', info.get('msg'))[0]
        url = "http://web.http.cnapi.cc/index/index/save_white?neek=45702&appkey=503e887ce8fd148c055c22380f99d5d9&white=" + ip
        res = requests.get(url)
    elif codeType==0:
        proxyList=info.get('data',[])
        for proxy in proxyList:
            proxyIp=proxy.get('ip')+':'+str(proxy.get('port'))
            expireTime=proxy.get('expire_time')
            timeArray=datetime.datetime.strptime(expireTime, "%Y-%m-%d %H:%M:%S")
            timestamp=int(time.mktime(timeArray.timetuple()))
            proxyPoolServer.zadd(proxyNotUsedZSetKey, {proxyIp: timestamp})

def videoGetDetailsTaskSchedule():
    platformInfo={
        '哔哩哔哩视频':'bilibiliDetailInfo',
        '今日头条':'xiguaDetailInfo',
    }
    batchCheckNums=64
    extraParams={
        'proxytype':'1',
    }
    extraParams = json.dumps(extraParams, ensure_ascii=False, separators=(',', ':'))
    for k,v in platformInfo.items():
        if k=='哔哩哔哩视频':
            records=VideoDetailsData.objects.filter(platform__exact=k).filter(status__exact=2)
        elif k=='今日头条':
            records=MovieOfflineData.objects.filter(platform__exact=k).filter(ishz__exact=1).filter(detailStatus__exact=0).filter(tag__in=['待处理','未下线'])
        else:
            records=[]
        spider = Spider.objects.get(Q(name__exact=v), Q(status__exact=0))
        deployProject = spider.deployProject
        i = 0
        scheduleServer = None
        j = m = 1
        paramList = []
        for record in records:
            if i % scrapydBatchSize == 0 and (j - 1) % batchCheckNums == 0:
                scheduleServer = getRunServer(deployProject)

            if scheduleServer:
                scrapyd = ScrapydAPI(scheduleServer, timeout=8)

                paramList.append({'id': record.id, 'targetUrl': record.url})
                if j % batchCheckNums == 0 or m == len(records):
                    params = json.dumps(paramList, ensure_ascii=False, separators=(',', ':'))
                    print(params)
                    status = scrapyd.schedule(project=deployProject, spider=spider.name, idTargetUrlList=params, extraParams=extraParams)
                    print(status)
                    paramList = []
                    i += 1
                j += 1
            m += 1

@periodic_task(run_every=3)
def sheduleCustomerTask(**kwargs):
    commonSchedule(2,0,isChangeScheduleStatus=True) #影视机动下线任务
    #commonSchedule(3,0,isChangeScheduleStatus=True) #音乐机动下线任务
    return True

@periodic_task(run_every=crontab(minute=0,hour=18))
def sheduleUserTask(**kwargs):
    commonSchedule(2,1,isChangeScheduleStatus=False)   #影视定时下线任务
    #commonSchedule(3,1,isChangeScheduleStatus=False)   #音乐定时下线任务
    return True

@periodic_task(run_every=1800)
def sheduleVideoDetailInfoTask(**kwargs):
    videoGetDetailsTaskSchedule() #获取视频详细信息任务
    return True