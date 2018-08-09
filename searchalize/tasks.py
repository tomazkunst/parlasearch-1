from __future__ import absolute_import, unicode_literals
from raven.contrib.django.raven_compat.models import client
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict

from . import views

from django_celery_monitor.models import TaskState
from celery import states, shared_task

import json
import requests

#[{"method": "setStyleScoresMPsALL", "attr": null, "type": "setter"}]

@csrf_exempt
def runAsyncSetter(request):
    args = ['method', 'attr']
    if request.method == 'POST':
        data = json.loads(request.body)
        auth_key = request.META['HTTP_AUTHORIZATION']
        if auth_key != settings.PARLALIZE_API_KEY:
            raise PermissionDenied

        for setter in data:
            list_args = [setter[element] for element in args if element in setter]
            run_search_analizes.apply_async(list_args, queue='parlasearch')
        return JsonResponse({'status':'runned'})
    else:
        return JsonResponse({'status': 'this isnt post'})


@shared_task
def run_search_analizes(method_name, attr=None):
    IDs = []
    method = getattr(views, method_name)
    try:
        if not attr:
            method()
        else:
            method(attr)
    except:
        client.captureException()


def get_celery_status(request):
    tasks = TaskState.objects.all().order_by('-tstamp')
    objs = [model_to_dict(task) for task in tasks]
    return JsonResponse(objs, safe=False)

