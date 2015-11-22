from django.shortcuts import render
from django.http import JsonResponse
import requests

# Create your views here.

def regularQuery(request, words):

    solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'

    q = words.replace('+', ' ')

    solr_params = {
        'q': 'content_t:' + q,
        'facet': 'true',
        'facet.field': 'speaker_i&facet.field=party_i', # dirty hack
        'facet.date': 'datetime_dt',
        'facet.date.start': '2014-01-01T00:00:00.000Z',
        'facet.date.gap': '%2B1MONTHS',
        'facet.date.end': 'NOW',
        'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
    }


    print q + 'asd'

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    print url

    r = requests.get(url)

    return JsonResponse(r.json())

def filterQuery(request, words):

    solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'

    q = words.replace('+', ' ')
    people = request.GET.get('people')
    parties = request.GET.get('parties')

    fq = ''

    if people == None:
        fq = 'party_i:(' + parties + ')'
    elif parties == None:
        fq = 'person_i:(' + people + ')'
    else:
        fq = 'speaker_i:(' + people + ') OR party_i:(' + parties + ')'

    print people, parties

    solr_params = {
        'q': 'content_t:' + q,
        'fq': fq,
        'facet': 'true',
        'facet.field': 'speaker_i&facet.field=party_i', # dirty hack
        'facet.date': 'datetime_dt',
        'facet.date.start': '2014-01-01T00:00:00.000Z',
        'facet.date.gap': '%2B1MONTHS',
        'facet.date.end': 'NOW',
        'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
    }

    print q + 'asd'

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    print url

    r = requests.get(url)

    return JsonResponse(r.json())

def mltQuery(request, speech_i):

    solr_url = 'http://127.0.0.1:8983/solr/knedl/mlt?wt=json&mlt.count=5&q=id:g' + speech_i + '&fl=id,score,content_t,session_i,speaker_i,speech_i'

    print solr_url
    print 'bla'

    r = requests.get(solr_url)

    return JsonResponse(r.json())
