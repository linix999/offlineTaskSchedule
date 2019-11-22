# -*- coding: utf-8 -*-
# @Time    : 6/20/19 11:06 PM
# @Author  : linix

from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spider.settings')

from django.conf import settings  # noqa

app = Celery('spider')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)