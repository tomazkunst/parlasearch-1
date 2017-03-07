# -*- coding: utf-8 -*-

import requests
import re
from parlasearch.settings import SOLR_URL, ANALIZE_URL, API_URL, API_DATE_FORMAT
from django.core.cache import cache
import time
import datetime
import calendar
import json

from django.http import HttpResponse


def tryHard(url):
    data = None
    counter = 0
    while data is None:
        try:
            if counter > 10:
                print 'Ne gre vec'
                return None
                # client.captureMessage(url+' je zahinavu več ko 10x.')
            data = requests.get(url)
        except:
            print url
            print 'try Harder'
            counter += 1
            time.sleep(30)
            pass
    return data


def enrichQuery(data, show_all=False):

    data['facet_counts'].pop('facet_heatmaps', None)
    # data['facet_counts'].pop('facet_ranges', None)
    data['facet_counts'].pop('facet_queries', None)
    data['facet_counts'].pop('facet_intervals', None)

    results = []
    url = 'https://analize.parlameter.si/v1/utils/getAllStaticData/'
    static_data = requests.get(url).json()

    for i, speaker in enumerate(data['facet_counts']['facet_fields']['speaker_i']):
        if i < 5 or show_all:
            try:
                score = data['facet_counts']['facet_fields']['speaker_i']
                results.append({'person': static_data['persons'][str(speaker)],
                                'score': str(score[i + 1])})
                del data['facet_counts']['facet_fields']['speaker_i'][i]
            except (ValueError, KeyError) as e:
                score = data['facet_counts']['facet_fields']['speaker_i']
                results.append({'person': {'party': {'acronym': 'unknown',
                                                     'id': 'unknown',
                                                     'name': 'unknown'},
                                           'name': 'unknown' + speaker,
                                           'gov_id': 'unknown',
                                           'id': speaker},
                                'score': str(score[i + 1])})
                del data['facet_counts']['facet_fields']['speaker_i'][i]
        else:
            del data['facet_counts']['facet_fields']['speaker_i'][i]

    for result in results:
        result.update({'score': int(result['score'])})

    out = sorted(results,
                 key=lambda k: k['score'],
                 reverse=True)
    data['facet_counts']['facet_fields']['speaker_i'] = out

    # enrich party
    results = []

    for i, speaker in enumerate(data['facet_counts']['facet_fields']['party_i']):
        if i % 2 == 0:
            try:
                score = data['facet_counts']['facet_fields']['party_i']
                results.append({'party': static_data['partys'][str(speaker)],
                                'score': str(score[i + 1])})
            except ValueError:
                score = data['facet_counts']['facet_fields']['party_i']
                results.append({'party': {'acronym': 'unknown',
                                          'is_coalition': unknown,
                                          'name': 'unknown',
                                          'id': speaker},
                                'score': str(score[i + 1])
                                })

    for result in results:
        result.update({'score': int(result['score'])})

    out = sorted(results, key=lambda k: k['score'], reverse=True)
    data['facet_counts']['facet_fields']['party_e'] = out

    enrichedData = data

    return enrichedData


def trimHighlight(highlight):
    m = re.search('[A-ZĆČŽŠĐ^\.\?\!]*<em.*\/em>.*\.?', highlight, re.UNICODE)
    if m:
        return m.group() + '</em>'
    else:
        return highlight


def enrichHighlights(data):

    results = []

    url = 'https://analize.parlameter.si/v1/utils/getAllStaticData/'
    static_data = requests.get(url).json()

    for hkey in data['highlighting'].keys():

        speechdata = getSpeechData(hkey.split('g')[1])
        if 'content_t' in data['highlighting'][hkey].keys():
            content_t = (data['highlighting'][hkey]['content_t'][0])
        else:
            content_t = None

        if content_t != '' and content_t is not None:

            try:
                results.append({
                    'person': static_data['persons'][str(speechdata['speaker_id'])],
                    'content_t': trimHighlight(content_t),
                    'date': speechdata['date'],
                    'speech_id': int(hkey.split('g')[1]),
                    'session_id': speechdata['session_id']
                })
            except (ValueError, KeyError) as e:
                results.append({'person': {'party': {'acronym': 'unknown',
                                                     'id': 'unknown',
                                                     'name': 'unknown'},
                                           'name': 'unknown',
                                           'gov_id': 'unknown',
                                           'id': speechdata['speaker_id']},
                                'content_t': trimHighlight(content_t),
                                'date': speechdata['date'],
                                'speech_id': int(hkey.split('g')[1])})

    data['highlighting'] = sortedResults = sorted(results,
                                                  key=lambda k: k['date'],
                                                  reverse=True)

    enrichedData = data

    return enrichedData


def addOrganizations(data):
    WBs = requests.get(ANALIZE_URL + '/s/getWorkingBodies/').json()
    orgs = {}
    for i, speaker in enumerate(data['facet_counts']['facet_fields']['org_i']):
        if i % 2 == 0:
            if int(data['facet_counts']['facet_fields']['org_i'][i+1]) != 0:
                orgs[str(speaker)] = data['facet_counts']['facet_fields']['org_i'][i+1]
    data['organizations'] = []
    for wb in WBs:
        if str(wb['id']) in orgs.keys():
            wb.update({'score': orgs[str(wb['id'])]})
            data['organizations'].append(wb)
    data['has_dz_score'] = True if '95' in orgs.keys() else False
    data['has_council_score'] = True if '9' in orgs.keys() else False
    return data


def enrichDocs(data):

    results = []

    for i, doc in enumerate(data['response']['docs']):

        hkey = doc['id']
        speechdata = getSpeechData(hkey.split('g')[1])

        try:
            sID = str(speechdata['speaker_id'])
            url = 'https://analize.parlameter.si/v1/utils/getPersonData/' + sID
            person_data = requests.get(url).json()
            results.append({'person': person_data,
                            'content_t': doc['content_t'],
                            'date': speechdata['date'],
                            'speech_id': int(hkey.split('g')[1]),
                            'session_id': doc['session_i'],
                            'session_name': speechdata['session_name'],
                            'score': doc['score']})
        except ValueError:
            results.append({'person': {'party': {'acronym': 'unknown',
                                                 'id': 'unknown',
                                                 'name': 'unknown'},
                                       'name': speechdata['speaker_id'],
                                       'gov_id': 'unknown',
                                       'id': speechdata['speaker_id']},
                            'content_t': doc['content_t'],
                            'date': speechdata['date'],
                            'speech_id': int(hkey.split('g')[1]),
                            'session_id': doc['session_i'],
                            'session_name': speechdata['session_name']})

    data['response']['docs'] = results

    enrichedData = data

    return enrichedData


def truncateTFIDF(data):
    newdata = []
    for term in data:
        if ' ' not in term['term']:
            if term['scores']['tf'] > 10:
                try:
                    float(term['term'])
                    pass
                except ValueError:
                    newdata.append(term)

    return newdata


def removeDigrams(data):
    newdata = []
    for i, term in enumerate(data):
        if ' ' not in term['term']:
            newdata.append(term)

    return newdata


def removeSingles(data):
    newdata = []
    for i, term in enumerate(data):
        if term['scores']['tf'] > 10:
            newdata.append(term)

    return newdata


def removeNumbers(data):
    newdata = []
    for i, term in enumerate(data):
        try:
            float(term['term'])
            pass
        except ValueError:
            newdata.append(term)

    return newdata


def isDigram(word):
    if ' ' in word:
        return True
    else:
        return False


def isNumber(word):
    try:
        float(word)
        return True
    except ValueError:
        return False


def enrichTFIDF(data):

    results = []

    for i, term in enumerate(data['termVectors'][1][3]):
        if i % 2 == 0:

            tkey = data['termVectors'][1][3][i]
            tvalue = data['termVectors'][1][3][i + 1]

            results.append({'term': tkey,
                            'scores': {tvalue[0]: tvalue[1],
                                       tvalue[2]: tvalue[3],
                                       tvalue[4]: tvalue[5]}})
            del data['termVectors'][1][3][i]
        else:
            del data['termVectors'][1][3][i]

    truncatedResults = truncateTFIDF(results)

    sortedResults = sorted(truncatedResults,
                           key=lambda k: k['scores']['tf-idf'],
                           reverse=True)[:25]

    enrichedData = {'session': data['termVectors'][0].split('s')[1],
                    'results': sortedResults}

    return enrichedData


def groupDFALL(rawdata):

    print 'beginning groupDFALL'

    allSessions = []

    print 'beginning iteration through sessions'

    for i, session in enumerate(rawdata['termVectors']):

        print i

        if i % 2 == 1:

            if len(session) == 4:

                for i, term in enumerate(session[3]):
                    if i % 2 == 0:

                        tkey = session[3][i]
                        tvalue = session[3][i + 1][1]

                        allSessions.append({'term': tkey, 'df': tvalue})

    print 'iterated through sessions'

    dkeys = []
    newdata = []

    print 'iterating through terms'

    # for term in allSessions:
    #
    #     tkey = term['term']
    #
    #     if tkey not in dkeys:
    #         dkeys.append(tkey)
    #         newdata.append(term)
    #     # else:
    #     #     for i, ndterm in enumerate(newdata):
    #     #         if ndterm['term'] == term['term']:
    #     #             newdata[i]['df'] = newdata[i]['df'] + term['df']

    newdata = {v['term']: v for v in allSessions}.values()

    truncatedResults = removeNumbers(removeDigrams(newdata))

    sortedResults = sorted(truncatedResults,
                           key=lambda k: k['df'],
                           reverse=True)

    return sortedResults


def appendTFIDFALL(rawdata, data, with_digrams):
    ex_words = data.keys()

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:
            if len(speech) < 4:
                continue
            for i, term in enumerate(speech[3]):
                if i % 2 == 0:
                    if len(speech) < 4:
                        continue
                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    if isNumber(tkey) or (not with_digrams and isDigram(tkey)):
                        continue

                    if tkey in ex_words:
                        data[tkey]['scores']['tf'] += tvalue[1]

                    else:
                        data[tkey] = {'term': tkey,
                                      'scores': {tvalue[0]: tvalue[1], # tf
                                                 tvalue[2]: tvalue[3]}} # df
                        ex_words.append(tkey)


def getTFIDFofSpeeches2(speeches, tfidf):
    data = {}
    for speech_id in speeches:
        temp_data = cache.get('govor_'+str(speech_id))
        if not temp_data:
            url = ('' + SOLR_URL + '/tvrh/?q=id:g' + str(speech_id) + ''
                   '&tv.df=true&tv.tf=true&tv.tf_idf=true'
                   '&wt=json&fl=id&tv.fl=content_t')
            temp_data = tryHard(url).json()
            cache.set('govor_'+str(speech_id), temp_data, None)
        appendTFIDFALL(temp_data, data, tfidf)

    for word in data:
        if data[word]['scores']['tf'] > 10:
            tfidf = float(data[word]['scores']['tf']) / data[word]['scores']['df']
            data[word]['scores']['tf-idf'] = tfidf
        else:
            data[word]['scores']['tf-idf'] = float(0)

    data = sorted(data.values(),
                  key=lambda k,: k['scores']['tf-idf'],
                  reverse=True)

    return data


def getTFIDFofSpeeches3(speeches, tfidf):
    data = {}
    for speech_id in speeches:
        temp_data = cache.get('govor_'+str(speech_id))
        if not temp_data:
            url = ('' + SOLR_URL + '/tvrh/?q=id:g' + str(speech_id) + ''
                   '&tv.df=true&tv.tf=true&tv.tf_idf=true'
                   '&wt=json&fl=id&tv.fl=content_t')
            temp_data = tryHard(url).json()
            cache.set('govor_'+str(speech_id), temp_data, None)
        appendTFIDFALL(temp_data, data, tfidf)

    data = sorted(data.values(),
                  key=lambda k,: k['scores']['df'],
                  reverse=True)

    return data


def enrichPersonData(data, person_id):
    url = ANALIZE_URL + '/utils/getPersonData/' + str(person_id)
    enrichedData = {'person': tryHard(url).json(), 'results': data}
    return enrichedData


def enrichPartyData(data, party_id):
    url = ANALIZE_URL + '/utils/getPgDataAPI/' + str(party_id)
    enrichedData = {'party': tryHard(url).json(), 'results': data}
    return enrichedData


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def tfidf_to_file():
    url = 'https://data.parlameter.si/v1/getMembersOfPGsRanges/14.11.2016'
    membersOfPGsRanges = tryHard(url).json()
    IDs = [key for key, value in membersOfPGsRanges[-1]['members'].items()]
    for ID in IDs:
        with open('tfidfs/tfidf_pg_' + str(ID) + '.json', 'w') as f:
            print 'delam zdej ', ID
            now_str = datetime.datetime.now().strftime(API_DATE_FORMAT)
            url = API_URL + '/getPGsSpeechesIDs/' + str(ID) + '/' + now_str
            speeches = tryHard(url).json()

            data = getTFIDFofSpeeches2(speeches, False)[:10]

            read_data = f.write(json.dumps(enrichPartyData(data, ID)))
        f.closed


def getSpeechData(speech_id):
    data = cache.get('s_data_' + str(speech_id))
    if not data:
        url = 'https://data.parlameter.si/v1/getSpeechData/' + str(speech_id)
        data = requests.get(url).json()
        cache.set('s_data_' + str(speech_id), data, 60 * 60 * 24 * 7)
    return data


def monitorMe(request):

    r = requests.get('https://isci.parlameter.si/q/krompir')
    if r.status_code == 200:
        return HttpResponse('All iz well.')
    else:
        return HttpResponse('PANIC!')
