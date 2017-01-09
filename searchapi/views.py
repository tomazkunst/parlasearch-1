from django.shortcuts import render
from django.http import JsonResponse, Http404
import requests
from datetime import datetime, timedelta
from parlasearch.settings import SOLR_URL, API_URL, API_DATE_FORMAT, ANALIZE_URL
import calendar

from utils import enrichQuery, enrichHighlights, enrichDocs, enrichTFIDF, groupSpeakerTFIDF, groupPartyTFIDF, groupSpeakerTFIDFALL, groupPartyTFIDFALL, groupDFALL, tryHard, getTFIDFofSpeeches, enrichPersonData, enrichPartyData, getTFIDFofSpeeches2, getTFIDFofSpeeches3, add_months, addOrganizations

# Create your views here.

def regularQuery(request, words, start_page=None):

    rows = 50
    #solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'
    solr_url = SOLR_URL+'/select?wt=json'

    q = words.replace('+', ' ')

    solr_params = {
        'q': 'content_t:' + q.replace('IN', 'AND').replace('!', '+'),
        'facet': 'true',
        'facet.field': 'speaker_i&facet.field=party_i', # dirty hack
        'facet.range': 'datetime_dt',
        'facet.range.start': '2014-01-01T00:00:00.000Z',
        'facet.range.gap': '%2B1MONTHS',
        'facet.range.end': 'NOW',
        # 'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
        'hl.fragmenter': 'regex',
        'hl.regex.pattern': '\w[^\.!\?]{1,600}[\.!\?]',
        'hl.fragsize': '5000',
        'hl.mergeContiguous': 'false',
        'hl.snippets': '1',
        'fq': 'tip_t:govor',
        'rows': str(rows),
        'start': str(int(start_page) * rows) if start_page else '0',
    }

    # print q + 'asd'

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    #print url

    r = requests.get(url)

    return JsonResponse(enrichHighlights(enrichQuery(r.json())))


def filterQuery(request, words, start_page=None):

    rows = 50
    solr_url = SOLR_URL+'/select?wt=json'

    q = words.replace('+', ' ')
    people = request.GET.get('people')#
    parties = request.GET.get('parties')#
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    is_dz = request.GET.get('dz')#
    is_council = request.GET.get('council') #
    working_bodies = request.GET.get('wb') #
    time_filter = request.GET.get('time_filter')

    filters_speakers = []

    filters_orgs = []

    working_bodies = working_bodies.split(",") if working_bodies else []

    if parties:
        filters_speakers.append('party_i:(' + " OR ".join(parties.split(",")) + ')')
        print 'party_i:(' + " OR ".join(parties.split(",")) + ')'
    if people:
        filters_speakers.append('speaker_i:(' + " OR ".join(people.split(",")) + ')')
    if is_dz:
        working_bodies.append("95")
    if is_council:
        working_bodies.append("9")
    if working_bodies:
        filters_orgs.append('org_i:(' + " OR ".join(working_bodies) + ')')


    #print "org_filter", filters_orgs
    if time_filter:
        time_filter = [datetime.strptime(t_filter, API_DATE_FORMAT)
                       for t_filter in time_filter.split(",")]

    f_date = min(time_filter) if time_filter else None
    t_date = add_months(max(time_filter), 1) if time_filter else None

    time_query = "datetime_dt:(" + " OR ".join(["["+ t_time.strftime('%Y-%m-%d') + 'T00:00:00.000Z' + " TO " + add_months(t_time, 1).strftime('%Y-%m-%d') + 'T00:00:00.000Z'"]" for t_time in time_filter ])+")"  if time_filter else None

    #print time_query

    #print people, parties

    solr_params = {
        'q': 'content_t:' + q.replace('IN', 'AND').replace('!', '%2B') + " AND tip_t:govor",
        'fq': " OR ".join(filters_speakers)
              + (" AND " if filters_speakers and filters_orgs else "") + ((" OR ".join(filters_orgs)) if filters_orgs else "")
              + (" AND " if (filters_speakers or filters_orgs) and time_query else "") + (time_query if time_query else ""),
        'facet': 'true',
        'facet.field': 'speaker_i&facet.field=party_i&facet.field=org_i', # dirty hack
        'facet.range': 'datetime_dt',
        'facet.range.start': (f_date.strftime('%Y-%m-%d') if f_date else '2014-01-01')+'T00:00:00.000Z',
        'facet.range.gap': '%2B1MONTHS',
        'facet.range.end': ( t_date.strftime('%Y-%m-%d') + 'T00:00:00.000Z' ) if t_date else 'NOW',
        # 'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
        'hl.fragmenter': 'regex',
        'hl.regex.pattern': '\w[^\.!\?]{400,600}[\.!\?]',
        'hl.fragsize': '5000',
        'hl.mergeContiguous': 'false',
        'hl.snippets': '1',
        'rows': str(rows),
        'start': str(int(start_page) * rows) if start_page else '0',
    }
    #print solr_params
    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    #print url

    r = requests.get(url)
    out = addOrganizations(enrichHighlights(enrichQuery(r.json(), show_all=True)))
    return JsonResponse(out)


def motionQuery(request, words, start_page=None):

    rows = 50
    #solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'
    solr_url = SOLR_URL+'/select?wt=json'

    q = words.replace('+', ' ')

    solr_params = {
        'q': 'content_t:' + q.replace('IN', 'AND').replace('!', '%2B'),
        # 'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
        'fq': 'tip_t:v',
        'rows': str(rows),
        'start': str(int(start_page) * rows) if start_page else '0',
    }

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    r = requests.get(url).json()
    ids = []
    try:
        docs = r["response"]["docs"]
        for doc in docs:
            ids.append(str(doc["voteid_i"]))
    except:
        JsonResponse({"status": "no votes with this word"})

    if len(ids) > 0:
        url2 = ANALIZE_URL+ "/s/getMotionOfSessionVotes/"+",".join(ids)
        resp = tryHard(url2).json()

    else:
        resp = []

    return JsonResponse(resp, safe=False)


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

    data = getTFIDFofSpeeches2(speeches, True)[:15]

    return JsonResponse(enrichPersonData(data, speaker_i), safe=False)

def tfidfSpeakerQueryWithoutDigrams(request, speaker_i):
    speeches = tryHard(API_URL + '/getMPSpeechesIDs/' + speaker_i + "/" + datetime.today().strftime('%d.%m.%Y')).json()

    data = getTFIDFofSpeeches2(speeches, False)[:25]

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

    data = getTFIDFofSpeeches2(speeches, True)[:10]

    return JsonResponse(enrichPartyData(data, party_i), safe=False)

def tfidfPGQueryWithoutDigrams(request, party_i):
    speeches = tryHard(API_URL + '/getPGsSpeechesIDs/' + party_i + "/" + datetime.today().strftime(API_DATE_FORMAT)).json()

    data = getTFIDFofSpeeches2(speeches, False)[:15]

    return JsonResponse(enrichPartyData(data, party_i), safe=False)



#ALL TFIDF Speeker
def tfidfSpeakerQueryALL(request, speaker_i):
    date_str = datetime.now().strftime(API_DATE_FORMAT)

    return tfidfSpeakerDateQueryALL(request, speaker_i, date_str)

def tfidfSpeakerDateQueryALL(request, speaker_i, datetime_dt):
    speeches = tryHard(API_URL + '/getMPSpeechesIDs/' + speaker_i + "/" + datetime_dt).json()

    data = getTFIDFofSpeeches3(speeches, False)

    return JsonResponse(enrichPersonData(data, speaker_i), safe=False)


#ALL TFIDF PG
def tfidfPGQueryALL(request, party_i):
    date_str = datetime.now().strftime(API_DATE_FORMAT)

    return tfidfPGDateQueryALL(request, party_i, date_str)

def tfidfPGDateQueryALL(request, party_i, datetime_dt):
    date_str = datetime.now().strftime(API_DATE_FORMAT)
    speeches = tryHard(API_URL + '/getPGsSpeechesIDs/' + party_i + "/" + datetime_dt).json()

    data = getTFIDFofSpeeches3(speeches, False)

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
