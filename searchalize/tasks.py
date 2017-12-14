from __future__ import absolute_import, unicode_literals
from celery import shared_task
from raven.contrib.django.raven_compat.models import client
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied

from .views import setStyleScoresPGsALL, setStyleScoresMPsALL, setTFIDFforPGsALL, setTFIDFforMPsALL, setTfidfOfSession

import json
import requests

status_api = settings.DASHBOARD_URL + '/api/status/'

exports = {'setStyleScoresPGsALL': setStyleScoresPGsALL,
           'setStyleScoresMPsALL': setStyleScoresMPsALL,
           'setTFIDFforPGsALL': setTFIDFforPGsALL,
           'setTFIDFforMPsALL':setTFIDFforMPsALL,
           'setTfidfOfSession': setTfidfOfSession}


@csrf_exempt
def runAsyncSetter(request):
    print('ivan')
    if request.method == 'POST':
        data = json.loads(request.body)
        print data
        status_id = data.pop('status_id')
        auth_key = request.META['HTTP_AUTHORIZATION']
        if auth_key != settings.PARLALIZE_API_KEY:
            print("auth fail")
            sendStatus(status_id, "Fail", "Authorization fails", ['buuu'])
            raise PermissionDenied
        if data['attr']:
            attr = data['attr']
        else:
            attr = None
        run_search_analizes.apply_async((data['setters'], status_id, attr), queue='parlasearch')
        return JsonResponse({'status':'runned'})
    else:
        return JsonResponse({'status': 'this isnt post'})


@shared_task
def run_search_analizes(expoert_tasks, status_id, attr=None):
    methods = [exports[task] for task in expoert_tasks]
    sendStatus(status_id, 'Running', '[]')
    if attr:
        data = {'session_i': attr}
    else:
        data = {}
    try:
        resp = ''
        for method in methods:
            print(method, data)
            resp = method(**data)
        print "naj se bi exportal"
        sendStatus(status_id, 'Done', resp)
    except:
        sendStatus(status_id, 'Fails', '[]')
        client.captureException()

def sendStatus(status_id, type_, data):
    requests.put(status_api + str(status_id) + '/',
                 data= {
                            "status_type": type_,
                            "status_note": datetime.now().strftime(settings.API_DATE_FORMAT),
                            "status_done": data
                        })
