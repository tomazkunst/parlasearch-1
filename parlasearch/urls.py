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
from searchapi.views import motionQuery, regularQuery, filterQuery, mltQuery, tfidfSessionQuery, tfidfSpeakerQuery, tfidfSpeakerDateQuery, tfidfPGQuery, tfidfPGDateQuery, tfidfSpeakerQueryALL, tfidfPGQueryALL, dfALL, tfidfSpeakerDateQueryALL, tfidfPGDateQueryALL, dfDateALL, tfidfSpeakerQuery2, tfidfSpeakerQueryWithoutDigrams

from searchapi.utils import monitorMe

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(ur'^mlt/(?P<speech_i>[0-9]+)', mltQuery),

    url(ur'^filter/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)/(?P<start_page>\d+)', filterQuery),
    url(ur'^filter/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', filterQuery),

    url(ur'^q/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)/(?P<start_page>\d+)', regularQuery),
    url(ur'^q/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', regularQuery),

    url(ur'^v/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)/(?P<start_page>\d+)', motionQuery),
    url(ur'^v/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', motionQuery),

    url(ur'^tfidf/s/(?P<session_i>[0-9]+)', tfidfSessionQuery),

    url(ur'^tfidfALL/p/(?P<speaker_i>[0-9]+)/$', tfidfSpeakerQueryALL),
    url(ur'^tfidfALL/p/(?P<speaker_i>[0-9]+)/(?P<datetime_dt>[\w].+)/', tfidfSpeakerDateQueryALL),

    url(ur'^tfidfALL/ps/(?P<party_i>[0-9]+)/$', tfidfPGQueryALL),
    url(ur'^tfidfALL/ps/(?P<party_i>[0-9]+)/(?P<datetime_dt>[\w].+)/', tfidfPGDateQueryALL),

    url(ur'^dfall/$', dfALL),
    url(ur'^dfall/(?P<datetime_dt>[\w].+)/', dfDateALL),

    url(r'^monitoring/', monitorMe),
]
