from django.shortcuts import render
from django.http import JsonResponse, Http404
import requests
from datetime import datetime
from parlasearch.settings import SOLR_URL, API_URL, API_DATE_FORMAT

from utils import enrichQuery, enrichHighlights, enrichDocs, enrichTFIDF, groupSpeakerTFIDF, groupPartyTFIDF, groupSpeakerTFIDFALL, groupPartyTFIDFALL, groupDFALL, tryHard, getTFIDFofSpeeches, enrichPersonData, enrichPartyData, getTFIDFofSpeeches2, getTFIDFofSpeeches3

# Create your views here.

def regularQuery(request, words):

    solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'

    q = words.replace('+', ' ')

    solr_params = {
        'q': 'content_t:' + q.replace('IN', 'AND').replace('!', '%2B'),
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
        'hl.fragsize': '5000',
        'hl.mergeContiguous': 'false',
        'fq': 'tip_t:govor',
        'rows': '50'
    }

    # print q + 'asd'

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    # print url

    r = requests.get(url)

    return JsonResponse(enrichHighlights(enrichQuery(r.json())))


def filterQuery(request, words):

    solr_url = SOLR_URL+'/select?wt=json'

    q = words.replace('+', ' ')
    people = request.GET.get('people')#
    parties = request.GET.get('parties')#
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    is_dz = request.GET.get('dz')#
    is_council = request.GET.get('council') #
    working_bodies = request.GET.get('wb') #

    f_date = datetime.strptime(from_date, API_DATE_FORMAT) if from_date else None
    t_date = datetime.strptime(to_date, API_DATE_FORMAT) if to_date else None

    filters_speakers = []

    filters_orgs = []

    if parties:
        filters_speakers.append('party_i:(' + " OR ".join(parties.split(",")) + ')')
        print 'party_i:(' + " OR ".join(parties.split(",")) + ')'
    if people:
        filters_speakers.append('speaker_i:(' + " OR ".join(people.split(",")) + ')')
    if is_dz:
        filters_orgs.append('org_i:( 95 )')
    if working_bodies:
        filters_orgs.append('org_i:(' + " OR ".join(working_bodies.split(",")) + ')')
    if is_council:
        filters_orgs.append('org_i:( 9 )')

    print "org_filter", filters_orgs

    print people, parties
    solr_params = {
        'q': 'content_t:' + q.replace('IN', 'AND').replace('!', '%2B'),
        'fq': "("+" OR ".join(filters_speakers) + ")" + (" AND ("+" OR ".join(filters_orgs) + ")") if filters_orgs else "",
        'facet': 'true',
        'facet.field': 'speaker_i&facet.field=party_i&facet.field=org_i', # dirty hack
        'facet.range': 'datetime_dt',
        'facet.range.start': (f_date.strftime('%Y-%m-%d') if f_date else '2014-01-01')+'T00:00:00.000Z',
        'facet.range.gap': '%2B1MONTHS',
        'facet.range.end': ( t_date.strftime('%Y-%m-%d') + 'T00:00:00.000Z' ) if t_date else 'NOW',
        'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
        'hl.fragmenter': 'regex',
        'hl.regex.pattern': '\w[^\.!\?]{400,600}[\.!\?]',
        'hl.fragsize': '5000',
        'hl.mergeContiguous': 'false',
        'rows': '50'
    }
    print solr_params
    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    print url

    r = requests.get(url)

    return JsonResponse(r.json())


def mltQuery(request, speech_i):

    solr_url = SOLR_URL + '/mlt?wt=json&mlt.count=5&q=id:g' + speech_i + '&fl=id,score,content_t,session_i,speaker_i,speech_i&fq=tip_t:govor'

    print solr_url
    print 'bla'

    r = requests.get(solr_url)

    return JsonResponse(enrichDocs(r.json()))


def tfidfSessionQuery(request, session_i):

    solr_url = SOLR_URL + '/tvrh/?q=id:s' + session_i + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'

    r = requests.get(solr_url)

    try:
        output = enrichTFIDF(r.json())
        output['session'] = requests.get('https://analize.parlameter.si/v1/utils/getSessionData/' + output['session']).json()
        return JsonResponse(output)
    except IndexError:
        raise Http404('No data for this session.')


#TFIDF Speeker
def tfidfSpeakerQuery(request, speaker_i):

    solr_url = SOLR_URL + '/tvrh/?q=id:p' + speaker_i + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'

    print solr_url

    r = requests.get(solr_url)

    return JsonResponse(groupSpeakerTFIDF(r.json(), int(speaker_i)), safe=False)

def tfidfSpeakerQuery2(request, speaker_i):
    speeches = tryHard(API_URL + '/getMPSpeechesIDs/' + speaker_i + "/" + datetime.today().strftime('%d.%m.%Y')).json()

    data = getTFIDFofSpeeches(speeches, True)[:10]

    return JsonResponse(enrichPersonData(data, speaker_i), safe=False)

def tfidfSpeakerDateQuery(request, speaker_i, datetime_dt):
    speeches = tryHard(API_URL + '/getMPSpeechesIDs/' + speaker_i + "/" + datetime_dt).json()

    data = getTFIDFofSpeeches2(speeches, True)[:10]

    return JsonResponse(enrichPersonData(data, speaker_i), safe=False)


#TFIDF PG
def tfidfPGQuery(request, party_i):
    date_str = datetime.now().strftime(API_DATE_FORMAT)

    return tfidfPGDateQuery(request, party_i, date_str)

def tfidfPGDateQuery(request, party_i, datetime_dt):
    speeches = tryHard(API_URL + '/getPGsSpeechesIDs/' + party_i + "/" + datetime_dt).json()

    data = getTFIDFofSpeeches(speeches, True)[:10]

    return JsonResponse(enrichPartyData(data, party_i), safe=False)


#ALL TFIDF Speeker
def tfidfSpeakerQueryALL(request, speaker_i):
    date_str = datetime.now().strftime(API_DATE_FORMAT)

    return tfidfSpeakerDateQueryALL(request, speaker_i, date_str)

def tfidfSpeakerDateQueryALL(request, speaker_i, datetime_dt):
    speeches = tryHard(API_URL + '/getMPSpeechesIDs/' + speaker_i + "/" + datetime_dt).json()

    data = getTFIDFofSpeeches3(speeches, True)

    return JsonResponse(enrichPersonData(data, speaker_i), safe=False)


#ALL TFIDF PG
def tfidfPGQueryALL(request, party_i):
    date_str = datetime.now().strftime(API_DATE_FORMAT)

    return tfidfPGDateQueryALL(request, party_i, date_str)

def tfidfPGDateQueryALL(request, party_i, datetime_dt):
    date_str = datetime.now().strftime(API_DATE_FORMAT)
    speeches = tryHard(API_URL + '/getPGsSpeechesIDs/' + party_i + "/" + datetime_dt).json()

    data = getTFIDFofSpeeches3(speeches, True)

    return JsonResponse(enrichPartyData(data, party_i), safe=False)


def dfALL(request):

    solr_url = SOLR_URL + '/tvrh/?q=tip_t:seja&tv.df=true&wt=json&fl=id&tv.fl=content_t'

    # solr_url = SOLR_URL + '/tvrh/?q=tip_t:govor&tv.df=true&wt=json&fl=id&tv.fl=content_t'

    print 'calling solr'
    r = requests.get(solr_url)
    print 'solr responded'

    return JsonResponse(groupDFALL(r.json()), safe=False)


def dfDateALL(request, datetime_dt): #TODO

    solr_url = SOLR_URL + '/tvrh/?q=tip_t:seja&tv.df=true&wt=json&fl=id&tv.fl=content_t&fq=datetime_dt:[*%20TO%20' + datetime.strptime(datetime_dt, '%d.%m.%Y').strftime('%Y-%m-%dT%H:%M:%SZ') + ']'

    print 'calling solr'
    r = requests.get(solr_url)
    print 'solr responded'

    return JsonResponse(groupDFALL(r.json()), safe=False)
