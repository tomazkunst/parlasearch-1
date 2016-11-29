# -*- coding: utf-8 -*-

import requests
import re
from parlasearch.settings import SOLR_URL, ANALIZE_URL
from django.core.cache import cache
import time

def tryHard(url):
    data = None
    counter = 0
    while data is None:
        try:
            if counter > 10:
                print "Ne gre vec"
                return None
                #client.captureMessage(url+" je zahinavu več ko 10x.")
            data = requests.get(url)
        except:
            counter += 1
            time.sleep(30)
            pass
    return data

def enrichQuery(data):

    data['facet_counts'].pop('facet_heatmaps', None)
    # data['facet_counts'].pop('facet_ranges', None)
    data['facet_counts'].pop('facet_queries', None)
    data['facet_counts'].pop('facet_intervals', None)

    results = []

    for i, speaker in enumerate(data['facet_counts']['facet_fields']['speaker_i']):
        if i % 2 == 0 and i < 10:
            try:
                results.append({'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + str(speaker)).json(), 'score': str(data['facet_counts']['facet_fields']['speaker_i'][i + 1])})
                del data['facet_counts']['facet_fields']['speaker_i'][i]
            except ValueError:
                results.append({'person': {'party': {'acronym': 'unknown', 'id': 'unknown', 'name': 'unknown'}, 'name': 'unknown' + speaker, 'gov_id': 'unknown', 'id': speaker}, 'score': str(data['facet_counts']['facet_fields']['speaker_i'][i + 1])})
                del data['facet_counts']['facet_fields']['speaker_i'][i]
        else:
            del data['facet_counts']['facet_fields']['speaker_i'][i]

    data['facet_counts']['facet_fields']['speaker_i'] = sorted(results, key=lambda k: k['score'], reverse=True)

    enrichedData = data

    return enrichedData

def trimHighlight(highlight):
    m = re.search('[A-ZĆČŽŠ][^\.\?\!]*<em.*\/em>.*\.?', highlight, re.UNICODE)
    if m:
        return m.group() + '</em>'
    else:
        return ''

def enrichHighlights(data):

    results = []

    for i, hkey in enumerate(data['highlighting'].keys()):

        speechdata = requests.get('https://data.parlameter.si/v1/getSpeechData/' + hkey.split('g')[1]).json()

        content_t = trimHighlight(data['highlighting'][hkey]['content_t'][0]) if 'content_t' in data['highlighting'][hkey].keys() else None

        if content_t != '' and content_t != None:

            if speechdata['date'] not in [result['date'] for result in results]:

                try:
                    results.append({
                        'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + str(speechdata['speaker_id'])).json(),
                        'content_t': trimHighlight(content_t),
                        'date': speechdata['date'],
                        'speech_id': int(hkey.split('g')[1]),
                        'session_id': speechdata['session_id']
                    })
                except ValueError:
                    results.append({'person': {'party': {'acronym': 'unknown', 'id': 'unknown', 'name': 'unknown'}, 'name': 'unknown', 'gov_id': 'unknown', 'id': speechdata['speaker_id']}, 'content_t': trimHighlight(content_t), 'date': speechdata['date'], 'speech_id': int(hkey.split('g')[1])})

    data['highlighting'] = sortedResults = sorted(results, key=lambda k: k['date'], reverse=True)

    enrichedData = data

    return enrichedData

def enrichDocs(data):

    results = []

    for i, doc in enumerate(data['response']['docs']):

        hkey = doc['id']
        speechdata = requests.get('https://data.parlameter.si/v1/getSpeechData/' + hkey.split('g')[1]).json()

        try:
            results.append({'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + str(speechdata['speaker_id'])).json(), 'content_t': doc['content_t'], 'date': speechdata['date'], 'speech_id': int(hkey.split('g')[1]), 'session_id': doc['session_i'], 'session_name': speechdata['session_name'], 'score': doc['score']})
        except ValueError:
            results.append({'person': {'party': {'acronym': 'unknown', 'id': 'unknown', 'name': 'unknown'}, 'name': speechdata['speaker_id'], 'gov_id': 'unknown', 'id': speechdata['speaker_id']}, 'content_t': doc['content_t'], 'date': speechdata['date'], 'speech_id': int(hkey.split('g')[1]), 'session_id': doc['session_i'], 'session_name': speechdata['session_name']})

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

            results.append({'term': tkey, 'scores': {tvalue[0]: tvalue[1], tvalue[2]: tvalue[3], tvalue[4]: tvalue[5]}})
            del data['termVectors'][1][3][i]
        else:
            del data['termVectors'][1][3][i]

    truncatedResults = truncateTFIDF(results)

    sortedResults = sorted(truncatedResults, key=lambda k: k['scores']['tf-idf'], reverse=True)[:10]

    enrichedData = {'session': data['termVectors'][0].split('s')[1], 'results': sortedResults}

    return enrichedData

def makeTFIDFObject(data):

    results = []

    for i, term in enumerate(data):
        if i % 2 == 0:

            tkey = data[i]
            tvalue = data[i + 1]

            results.append({'term': tkey, 'scores': {tvalue[0]: tvalue[1], tvalue[2]: tvalue[3], tvalue[4]: tvalue[5]}})
            del data['termVectors'][1][3][i]
        else:
            del data['termVectors'][1][3][i]

    return results

def groupSpeakerTFIDF(rawdata, person_i):

    allSpeeches = []

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:

                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    allSpeeches.append({'term': tkey, 'scores': {tvalue[0]: tvalue[1], tvalue[2]: tvalue[3], tvalue[4]: tvalue[5]}})

    dkeys = []
    newdata = []

    for term in allSpeeches:

        tkey = term['term']

        if tkey not in dkeys:
            dkeys.append(tkey)
            newdata.append(term)
        else:
            for i, ndterm in enumerate(newdata):
                if ndterm['term'] == term['term']:
                    newdata[i]['scores']['tf'] = newdata[i]['scores']['tf'] + term['scores']['tf']

    truncatedResults = truncateTFIDF(newdata)

    sortedResults = sorted(truncatedResults, key=lambda k: k['scores']['tf-idf'], reverse=True)[:10]

    enrichedData = {'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + str(person_i)).json(), 'results': sortedResults}

    return enrichedData

def groupSpeakerTFIDFALL(rawdata, person_i):

    allSpeeches = []

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:

                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    allSpeeches.append({'term': tkey, 'scores': {tvalue[0]: tvalue[1], tvalue[2]: tvalue[3], tvalue[4]: tvalue[5]}})

    dkeys = []
    newdata = []

    for term in allSpeeches:

        tkey = term['term']

        if tkey not in dkeys:
            dkeys.append(tkey)
            newdata.append(term)
        else:
            for i, ndterm in enumerate(newdata):
                if ndterm['term'] == term['term']:
                    newdata[i]['scores']['tf'] = newdata[i]['scores']['tf'] + term['scores']['tf']

    truncatedResults = removeNumbers(removeSingles(removeDigrams(newdata)))

    sortedResults = sorted(truncatedResults, key=lambda k: k['scores']['tf-idf'], reverse=True)

    enrichedData = {'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + str(person_i)).json(), 'results': sortedResults}

    return enrichedData

def groupPartyTFIDF(rawdata, party_i):

    allSpeeches = []

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:

                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    allSpeeches.append({'term': tkey, 'scores': {tvalue[0]: tvalue[1], tvalue[2]: tvalue[3], tvalue[4]: tvalue[5]}})

    dkeys = []
    newdata = []

    for term in allSpeeches:

        tkey = term['term']

        if tkey not in dkeys:
            dkeys.append(tkey)
            newdata.append(term)
        else:
            for i, ndterm in enumerate(newdata):
                if ndterm['term'] == term['term']:
                    newdata[i]['scores']['tf'] = newdata[i]['scores']['tf'] + term['scores']['tf']

    truncatedResults = removeNumbers(removeSingles(removeDigrams(newdata)))

    sortedResults = sorted(truncatedResults, key=lambda k: k['scores']['tf-idf'], reverse=True)[:10]

    enrichedData = {'party': requests.get('https://analize.parlameter.si/v1/utils/getPgDataAPI/' + str(party_i)).json(), 'results': sortedResults}

    return enrichedData

def groupPartyTFIDFALL(rawdata, party_i):

    allSpeeches = []

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:

                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    allSpeeches.append({'term': tkey, 'scores': {tvalue[0]: tvalue[1], tvalue[2]: tvalue[3], tvalue[4]: tvalue[5]}})

    dkeys = []
    newdata = []

    for term in allSpeeches:

        tkey = term['term']

        if tkey not in dkeys:
            dkeys.append(tkey)
            newdata.append(term)
        else:
            for i, ndterm in enumerate(newdata):
                if ndterm['term'] == term['term']:
                    newdata[i]['scores']['tf'] = newdata[i]['scores']['tf'] + term['scores']['tf']

    truncatedResults = removeNumbers(removeSingles(removeDigrams(newdata)))

    sortedResults = sorted(truncatedResults, key=lambda k: k['scores']['tf-idf'], reverse=True)

    enrichedData = {'party': requests.get('https://analize.parlameter.si/v1/utils/getPgDataAPI/' + str(party_i)).json(), 'results': sortedResults}

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

    newdata = {v['term']:v for v in allSessions}.values()

    truncatedResults = removeNumbers(removeDigrams(newdata))

    sortedResults = sorted(truncatedResults, key=lambda k: k['df'], reverse=True)

    # enrichedData = {'party': requests.get('https://analize.parlameter.si/v1/utils/getPgDataAPI/' + str(party_i)).json(), 'results': sortedResults}

    return sortedResults

def appendTFIDFALL(rawdata, data, with_digrams):
    ex_words = data.keys()

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:
                    if len(speech)<4:
                        continue
                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    if isNumber(tkey) or ( not with_digrams and isDigram(tkey)):
                        continue

                    if tkey in ex_words:
                        data[tkey]["scores"]["tf"] += tvalue[1]

                    else:
                        data[tkey] = {"term": tkey, "scores":{tvalue[0]: tvalue[1], tvalue[2]: tvalue[3]}}
                        ex_words.append(tkey)


def getTFIDFofSpeeches(speeches, tfidf):
    data = {}
    speeches = ["g"+str(speech) for speech in speeches]

    hundret_speeches = [speeches[i:i+20] for i in range(0, len(speeches), 20)]
    for speech_ids in hundret_speeches:
        print SOLR_URL + '/tvrh/?q=id:(' + " ".join(speech_ids) + ')&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t'
        temp_data = tryHard(SOLR_URL + '/tvrh/?q=id:('+ " ".join(speech_ids) + ')&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t').json()
        appendTFIDFALL(temp_data, data, tfidf)

    for word in data:
        if data[word]['scores']['tf'] > 10:
            data[word]["scores"]["tf-idf"] = float(data[word]["scores"]["tf"]) / data[word]["scores"]["df"]
        else:
            data[word]["scores"]["tf-idf"] = float(0)
    data = sorted(data.values(), key=lambda k,: k["scores"]['tf-idf'], reverse=True)

    return data

def getTFIDFofSpeeches2(speeches, tfidf):
    data = {}
    for speech_id in speeches:
        temp_data = cache.get("govor_"+str(speech_id))
        if not temp_data:
            temp_data = tryHard(SOLR_URL + '/tvrh/?q=id:g' + str(speech_id) + '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t').json()
            cache.set("govor_"+str(speech_id), temp_data, None)
        appendTFIDFALL(temp_data, data, tfidf)

    for word in data:
        if data[word]['scores']['tf'] > 10:
            data[word]["scores"]["tf-idf"] = float(data[word]["scores"]["tf"]) / data[word]["scores"]["df"]
        else:
            data[word]["scores"]["tf-idf"] = float(0)

    data = sorted(data.values(), key=lambda k,: k["scores"]['tf-idf'], reverse=True)

    return data

def getTFIDFofSpeeches3(speeches, tfidf):
    data = {}
    speeches = ["g"+str(speech) for speech in speeches]

    hundret_speeches = [speeches[i:i+20] for i in range(0, len(speeches), 20)]
    for speech_ids in hundret_speeches:
        temp_data = tryHard(SOLR_URL + '/tvrh/?q=id:(' + " OR ".join(speech_ids) + ')&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t').json()
        appendTFIDFALL(temp_data, data, tfidf)

    data = sorted(data.values(), key=lambda k,: k["scores"]['df'], reverse=True)

    return data

def enrichPersonData(data, person_id):
    enrichedData = {'person': tryHard(ANALIZE_URL + '/utils/getPersonData/' + str(person_id)).json(), 'results': data}
    return enrichedData


def enrichPartyData(data, party_id):
    enrichedData = {'party': tryHard(ANALIZE_URL + '/utils/getPgDataAPI/' + str(party_id)).json(), 'results': data}
    return enrichedData
