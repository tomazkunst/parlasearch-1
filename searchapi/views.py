from django.shortcuts import render
from django.http import JsonResponse, Http404
import requests

from utils import enrichQuery, enrichHighlights, enrichDocs, enrichTFIDF, groupSpeakerTFIDF, groupPartyTFIDF

# Create your views here.

def regularQuery(request, words):

    solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'

    q = words.replace('+', ' ')

    solr_params = {
        'q': 'content_t:' + q,
        'facet': 'true',
        'facet.field': 'speaker_i&facet.field=party_i', # dirty hack
        'facet.range': 'datetime_dt',
        'facet.range.start': '2014-01-01T00:00:00.000Z',
        'facet.range.gap': '%2B1MONTHS',
        'facet.range.end': 'NOW',
        'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
        'hl.fragmenter': 'regex',
        'hl.regex.pattern': '\w[^\.!\?]{400,600}[\.!\?]',
        'hl.fragsize': '1000',
        'hl.mergeContiguous': 'true',
        'fq': 'tip_t:govor',
        'rows': '50'
    }
    solr_params_no_date = {
        'q': 'content_t:' + q,
        'facet': 'true',
        'facet.field': 'speaker_i&facet.field=party_i', # dirty hack
        'facet.range': 'datetime_dt',
        'facet.range.start': '2014-01-01T00:00:00.000Z',
        'facet.range.gap': '%2B1MONTHS',
        'facet.range.end': 'NOW',
        'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
        'hl.fragmenter': 'regex',
        'hl.regex.pattern': '[A-Z]{1}\w[^\.!\?]{1,300}[\.!\?]',
#        'hl.fragsize': '300',
        'hl.mergeContiguous': 'true',
        'fq': 'tip_t:govor',
        'rows': '50'
    }

    # ROWS, START,
    # http://parlameter.si:8983/solr/knedl/select?wt=json&sort=datetime_dt%20desc&fq=tip_t:govor%20AND%20datetime_dt:[*%20TO%202016-10-12T00:00:00.000Z]&facet.field=speaker_i&facet.field=party_i&facet.range.gap=%2B1MONTHS&facet.range.end=NOW&hl=true&hl.fl=content_t&facet=true&hl.fragsize=1000&hl.regex.pattern=[%5Cw].*{30,100}[.!?]&q=content_t:zdravstvo&facet.range=datetime_dt&hl.fragmenter=regex&rows=20&start=15&facet.range.start=2014-01-01T00:00:00.000Z
    # http://parlameter.si:8983/solr/knedl/select?wt=json&sort=datetime_dt%20desc&fq=tip_t:govor&fq{!tag=ct}datetime_dt:[*%20TO%202016-01-12T00:00:00.000Z]&facet.field=speaker_i&facet.field=party_i&facet.range.gap=%2B1MONTHS&facet.range.end=NOW&hl=true&hl.fl=content_t&facet=true&hl.fragsize=1000&hl.regex.pattern=[%5Cw].*{30,100}[.!?]&q=content_t:zdravstvo&facet.range={!ex=ct}datetime_dt&hl.fragmenter=regex&rows=20&start=15&facet.range.start=2014-01-01T00:00:00.000Z

    if ' ' in q:
        solr_params = solr_params_no_date


    print q + 'asd'

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    print url

    r = requests.get(url)

    return JsonResponse(enrichHighlights(enrichQuery(r.json())))

def filterQuery(request, words):

    solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'

    q = words.replace('+', ' ')
    people = request.GET.get('people')
    parties = request.GET.get('parties')

    fq = ''

    if people == None:
        fq = 'party_i:(' + parties + ')'
    elif parties == None:
        fq = 'speaker_i:(' + people + ')'
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
        # 'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t'
    }

    print q + 'asd'

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    print url

    r = requests.get(url)

    return JsonResponse(r.json())

def mltQuery(request, speech_i):

    solr_url = 'http://127.0.0.1:8983/solr/knedl/mlt?wt=json&mlt.count=5&q=id:g' + speech_i + '&fl=id,score,content_t,session_i,speaker_i,speech_i&fq=tip_t:govor'

    print solr_url
    print 'bla'

    r = requests.get(solr_url)

    return JsonResponse(enrichDocs(r.json()))

def tfidfSessionQuery(request, session_i):

    solr_url = 'http://parlameter.si:8983/solr/knedl/tvrh/?q=id:s' + session_i + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'

    r = requests.get(solr_url)

    try:
        output = enrichTFIDF(r.json())
        output['session'] = requests.get('https://analize.parlameter.si/v1/utils/getSessionData/' + output['session']).json()
        return JsonResponse(output)
    except IndexError:
        raise Http404('No data for this session.')

def tfidfSpeakerQuery(request, speaker_i):

    solr_url = 'http://parlameter.si:8983/solr/knedl/tvrh/?q=speaker_i:' + speaker_i + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'

    r = requests.get(solr_url)

    return JsonResponse(groupSpeakerTFIDF(r.json(), int(speaker_i)), safe=False)

def tfidfSpeakerDateQuery(request, speaker_i, datetime_dt):

    solr_url = 'http://parlameter.si:8983/solr/knedl/tvrh/?q=speaker_i:' + speaker_i + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'

    r = requests.get(solr_url)

    return JsonResponse(groupSpeakerTFIDF(r.json(), int(speaker_i)), safe=False)

def tfidfPGQuery(request, party_i):

    solr_url = 'http://parlameter.si:8983/solr/knedl/tvrh/?q=party_i:' + party_i + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'

    r = requests.get(solr_url)

    return JsonResponse(groupPartyTFIDF(r.json(), int(party_i)), safe=False)

def tfidfPGDateQuery(request, party_i, datetime_dt):

    solr_url = 'http://parlameter.si:8983/solr/knedl/tvrh/?q=party_i:' + party_i + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'

    r = requests.get(solr_url)

    return JsonResponse(groupPartyTFIDF(r.json(), int(party_i)), safe=False)

def tfidfSpeakerQueryALL(request, speaker_i):

    solr_url = 'http://parlameter.si:8983/solr/knedl/tvrh/?q=speaker_i:' + speaker_i + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'

    r = requests.get(solr_url)

    return JsonResponse(groupSpeakerTFIDFALL(r.json(), int(speaker_i)), safe=False)
