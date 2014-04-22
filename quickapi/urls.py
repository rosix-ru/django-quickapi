# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import *

urlpatterns = patterns('quickapi.views',
    url(r'^$',      'index', name='quickapi'),
    url(r'^$',      'index', name='quickapi_index'),
    url(r'^test/$', 'test',  name='quickapi_test'),
)
