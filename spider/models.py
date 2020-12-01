from django.db import models

STATUS_CHOICES = (
    (0, '禁用'),
    (1, '启用'),
)
CATAGERY_CHOICES = (
    (0, '普通'),
    (1, '重要'),
)
SPIDER_TYPE = (
    (0, '影视爬虫'),
    (1, '音乐爬虫'),
    (2, '影视下线验证爬虫'),
    (3, '其他爬虫'),
)

class Spider(models.Model):
    name=models.CharField(max_length=100,verbose_name='爬虫名称')
    deployProject = models.CharField(max_length=100, verbose_name='爬虫部署项目名称')
    spiderType = models.IntegerField(choices=SPIDER_TYPE,default=0, verbose_name='爬虫类型')
    catagery=models.IntegerField(choices=CATAGERY_CHOICES,verbose_name='爬虫分类')
    keywordParameters=models.CharField(max_length=1000,default="",blank=True,null=True,verbose_name='关键词参数')
    dictParameters=models.CharField(max_length=1000,default="",blank=True,null=True,verbose_name='字典参数')
    status=models.IntegerField(choices=STATUS_CHOICES,default=0,verbose_name='状态')
    note=models.CharField(max_length=1000,default="",blank=True,null=True,verbose_name='备注')

    class Meta:
        verbose_name='爬虫'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name
