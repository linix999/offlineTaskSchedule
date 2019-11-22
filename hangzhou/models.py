from django.db import models

# Create your models here.
class MovieCrawlState(models.Model):
    id=models.IntegerField(primary_key=True)
    keyword = models.CharField(max_length=50)
    status = models.IntegerField()  #爬虫状态0：未开始，1：已开始，当爬虫开始爬时修改，不是调度了就修改
    json = models.CharField(max_length=2000, blank=True, null=True)
    task = models.IntegerField()    #任务类型 0：用户建项目，1：每天定时任务
    manage = models.IntegerField()  #任务是否已调度，0：未调度，1：已调度
    startNum = models.IntegerField()
    finishNum = models.IntegerField()
    crawl = models.IntegerField()   #视频下线为10
    createTime = models.DateTimeField(db_column='createTime', blank=True, null=True)

    class Meta:
        managed = True
        app_label="hangzhou"
        db_table = 'movie_crawl_state'

class MusicCrawlState(models.Model):
    id=models.IntegerField(primary_key=True)
    keyword = models.CharField(max_length=50)
    status = models.IntegerField()  #爬虫状态0：未开始，1：已开始，当爬虫开始爬时修改，不是调度了就修改
    json = models.CharField(max_length=2000, blank=True, null=True)
    task = models.IntegerField()    #任务类型 0：用户建项目，1：每天定时任务
    manage = models.IntegerField()  #任务是否已调度，0：未调度，1：已调度
    startNum = models.IntegerField()
    finishNum = models.IntegerField()
    crawl = models.IntegerField()   #音乐下线为11
    createTime = models.DateTimeField(db_column='createTime', blank=True, null=True)

    class Meta:
        managed = True
        app_label="hangzhou"
        db_table = 'music_crawl_state'

class MovieOfflineData(models.Model):
    id=models.IntegerField(primary_key=True)
    platform = models.CharField(max_length=255)
    url = models.CharField(max_length=2000)
    checkdate = models.CharField(max_length=20)
    tag = models.CharField(max_length=20)
    createTime = models.DateTimeField(db_column='createTime', blank=True, null=True)

    class Meta:
        managed = True
        app_label="hangzhou"
        db_table = 'movie_online_check'