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
from searchapi.views import regularQuery, filterQuery, mltQuery, tfidfSessionQuery, tfidfSpeakerQuery, tfidfSpeakerDateQuery, tfidfPGQuery, tfidfPGDateQuery, tfidfSpeakerQueryALL, tfidfPGQueryALL, dfALL, tfidfSpeakerDateQueryALL, tfidfPGDateQueryALL, dfDateALL

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^mlt/(?P<speech_i>[0-9]+)', mltQuery),

    url(r'^filter/(?P<words>[a-zA-Z0-9 \-\+!"]+)', filterQuery),

    url(r'^q/(?P<words>[a-zA-Z0-9 \-\+!"']+)', regularQuery),

    url(r'^tfidf/s/(?P<session_i>[0-9]+)', tfidfSessionQuery),

    url(r'^tfidf/p/(?P<speaker_i>[0-9]+)/$', tfidfSpeakerQuery),
    url(r'^tfidf/p/(?P<speaker_i>[0-9]+)/(?P<datetime_dt>[\w].+)/', tfidfSpeakerDateQuery),

    url(r'^tfidf/ps/(?P<party_i>[0-9]+)/$', tfidfPGQuery),
    url(r'^tfidf/ps/(?P<party_i>[0-9]+)/(?P<datetime_dt>[\w].+)/', tfidfPGDateQuery),

    url(r'^tfidfALL/p/(?P<speaker_i>[0-9]+)/$', tfidfSpeakerQueryALL),
    url(r'^tfidfALL/p/(?P<speaker_i>[0-9]+)/(?P<datetime_dt>[\w].+)/', tfidfSpeakerDateQueryALL),

    url(r'^tfidfALL/ps/(?P<party_i>[0-9]+)/$', tfidfPGQueryALL),
    url(r'^tfidfALL/ps/(?P<party_i>[0-9]+)/(?P<datetime_dt>[\w].+)/', tfidfPGDateQueryALL),

    url(r'^dfall/$', dfALL),
    url(r'^dfall/(?P<datetime_dt>[\w].+)/', dfDateALL),
]
