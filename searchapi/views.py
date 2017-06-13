from django.shortcuts import render
from django.http import JsonResponse, Http404
import requests
from datetime import datetime, timedelta
from parlasearch.settings import SOLR_URL, API_URL, API_DATE_FORMAT, ANALIZE_URL
import calendar

from utils import enrichQuery, enrichHighlights, enrichTFIDF, groupDFALL, tryHard, add_months, addOrganizations

# Create your views here.

ZERO_TIME = 'T00:00:00.000Z'


def regularQuery(request, words, start_page=None):
    """
    words: word/words for search
    start_page: pager in results

    search query in transcripts
    """

    rows = 50
    # solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'
    solr_url = SOLR_URL + '/select?wt=json'

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

    # print url

    r = requests.get(url)

    return JsonResponse(enrichHighlights(enrichQuery(r.json())))


def filterQuery(request, words, start_page=None):
    """
    words: word/words for search
    start_page: pager in results

    get parameters "filters":
        -people: array of people ids for filter
        -parties: array of party ids for filter
        -from: 
        -to:
        -dz: if true filter speeches spoken on sessions of Drzavni zbor
        -council: if true filter speeches spoken on sessions of president council
        -wb: array of working bodies for filter
        -time_fitler: Months of which can be words spoken

    filter search query in transcripts
    """
    rows = 50
    solr_url = SOLR_URL+'/select?wt=json'

    q = words.replace('+', ' ')
    people = request.GET.get('people')
    parties = request.GET.get('parties')
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    is_dz = request.GET.get('dz')
    is_council = request.GET.get('council')
    working_bodies = request.GET.get('wb', [])
    time_filter = request.GET.get('time_filter')

    filters = []

    working_bodies = working_bodies.split(',') if working_bodies else []
    # prepare speaker filter query
    if parties:
        filters_partys = 'party_i:(' + ' OR '.join(parties.split(',')) + ')'
        filters.append(filters_partys)
    if people:
        filters_speakers = 'speaker_i:(' + ' OR '.join(people.split(',')) + ')'
        filters.append(filters_speakers)

    # prepare organization of session filter query
    if is_dz:
        working_bodies.append('95')
    if is_council:
        working_bodies.append('9')
    if working_bodies:
        filters.append('org_i:(' + ' OR '.join(working_bodies) + ')')

    # prepare time filter query
    if time_filter:
        time_filter = [datetime.strptime(t_filter, API_DATE_FORMAT)
                       for t_filter in time_filter.split(',')]

        time_filter = [(t_time.strftime('%Y-%m-%d') + ZERO_TIME,
                        add_months(t_time,
                                   1).strftime('%Y-%m-%d') + ZERO_TIME + ']')
                       for t_time in time_filter]
        time_str = ['[' + t_time(0) + ' TO ' + t_time(1)
                    for t_time in time_filter]
        time_query = 'datetime_dt:(' + ' OR '.join(time_str) + ')'
        filters.append(time_query)

    f_date = min(time_filter) if time_filter else None
    t_date = add_months(max(time_filter), 1) if time_filter else None

    if f_date:
        facetStartRange = f_date.strftime('%Y-%m-%d') + ZERO_TIME
    else:
        facetStartRange = '2014-01-01' + ZERO_TIME

    if t_date:
        facetEndRange = t_date.strftime('%Y-%m-%d') + ZERO_TIME
    else:
        facetEndRange = 'NOW'

    query = 'content_t:' + q.replace('IN', 'AND').replace('!', '%2B')
    query += ' AND tip_t:govor'

    solr_params = {
        'q': query,
        'fq': ' AND '.join(filters),
        'facet': 'true',
        'facet.field': 'speaker_i&facet.field=party_i&facet.field=org_i', # dirty hack
        'facet.range': 'datetime_dt',
        'facet.range.start': facetStartRange,
        'facet.range.gap': '%2B1MONTHS',
        'facet.range.end': facetEndRange,
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
    # print solr_params
    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    # print url

    r = requests.get(url)
    out = addOrganizations(enrichHighlights(enrichQuery(r.json(),
                           show_all=True)))
    return JsonResponse(out)


def motionQuery(request, words, start_page=None):
    """
    search query by motion text
    """

    rows = 50
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
        docs = r['response']['docs']
        for doc in docs:
            ids.append(str(doc['voteid_i']))
    except:
        JsonResponse({'status': 'no votes with this word'})

    if len(ids) > 0:
        url2 = ANALIZE_URL + '/s/getMotionOfSessionVotes/'+','.join(ids)
        resp = tryHard(url2).json()

    else:
        resp = []

    return JsonResponse(resp, safe=False)


def tfidfSessionQuery(request, session_i):
    """
    method for TFIDF of session
    """

    solr_url = ('' + SOLR_URL + '/tvrh/?q=id:s' + session_i + ''
                '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t')

    r = requests.get(solr_url)

    try:
        output = enrichTFIDF(r.json())
        url = (ANALIZE_URL + '/utils/getSessionData/'
               '' + output['session'] + '')
        output['session'] = requests.get(url).json()
        return JsonResponse(output)
    except IndexError:
        raise Http404('No data for this session.')


def dfALL(request):
    """
    document frequerncy all
    """
    solr_url = SOLR_URL + '/tvrh/?q=tip_t:seja&tv.df=true&wt=json&fl=id&tv.fl=content_t'

    # solr_url = SOLR_URL + '/tvrh/?q=tip_t:govor&tv.df=true&wt=json&fl=id&tv.fl=content_t'

    print 'calling solr'
    r = requests.get(solr_url)
    print 'solr responded'

    return JsonResponse(groupDFALL(r.json()), safe=False)


# TODO
def dfDateALL(request, datetime_dt):
    """
    document frequerncy all to date
    """
    dateObj = datetime.strptime(datetime_dt, '%d.%m.%Y')
    dateStr = dateObj.strftime('%Y-%m-%dT%H:%M:%SZ')
    solr_url = ('' + SOLR_URL + '/tvrh/?q=tip_t:seja&tv.df=true&wt=json&'
                'fl=id&tv.fl=content_t&fq=datetime_dt:[*%20TO%20'
                '' + dateStr + ']')

    print 'calling solr'
    r = requests.get(solr_url)
    print 'solr responded'

    return JsonResponse(groupDFALL(r.json()), safe=False)
