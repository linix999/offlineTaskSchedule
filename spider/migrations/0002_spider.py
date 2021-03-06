# Generated by Django 2.2 on 2019-07-04 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Spider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='爬虫名称')),
                ('deployProject', models.CharField(max_length=100, verbose_name='爬虫部署项目名称')),
                ('catagery', models.IntegerField(choices=[(0, '普通'), (1, '重要')], verbose_name='爬虫分类')),
                ('keywordParameters', models.CharField(default='', max_length=1000, verbose_name='关键词参数')),
                ('dictParameters', models.CharField(default='', max_length=1000, verbose_name='字典参数')),
                ('status', models.IntegerField(choices=[(0, '禁用'), (1, '启用')], verbose_name='状态')),
                ('note', models.CharField(default='', max_length=1000, verbose_name='备注')),
            ],
            options={
                'verbose_name': '爬虫',
                'verbose_name_plural': '爬虫',
            },
        ),
    ]
