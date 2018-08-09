# -*- coding: utf-8 -*-
"""parlasearch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from searchapi.views import motionQuery, regularQuery, filterQuery, dfALL, dfDateALL, index, legislationQuery, motionQuery2

from searchapi.utils import monitorMe
from searchalize.tasks import runAsyncSetter, get_celery_status

urlpatterns = [
    url(r'^$', index),
    url(r'^admin/', include(admin.site.urls)),

    url(ur'^filter/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,\*]+)/(?P<start_page>\d+)', filterQuery),
    url(ur'^filter/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,\*]+)', filterQuery),

    url(ur'^q/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)/(?P<start_page>\d+)', regularQuery),
    url(ur'^q/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', regularQuery),

    url(ur'^v/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)/(?P<start_page>\d+)', motionQuery),
    url(ur'^v/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', motionQuery),

    url(ur'^v2/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)/(?P<start_page>\d+)', motionQuery2),
    url(ur'^v2/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', motionQuery2),

    url(ur'^l/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)/(?P<start_page>\d+)', legislationQuery),
    url(ur'^l/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', legislationQuery),

    url(ur'^dfall/$', dfALL),
    url(ur'^dfall/(?P<datetime_dt>[\w].+)/', dfDateALL),

    url(r'^monitoring/', monitorMe),

    url(r'^tasks/', runAsyncSetter),
    url(r'^tasks/status/', get_celery_status),
    
]
