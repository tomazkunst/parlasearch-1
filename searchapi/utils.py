import requests

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

def enrichHighlights(data):

    results = []

    for i, hkey in enumerate(data['highlighting'].keys()):

        speechdata = requests.get('https://data.parlameter.si/v1/getSpeechData/' + hkey.split('g')[1]).json()

        try:
            results.append({
                'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + str(speechdata['speaker_id'])).json(),
                'content_t': data['highlighting'][hkey]['content_t'] if 'content_t' in data['highlighting'][hkey].keys() else None,
                'date': speechdata['date'],
                'speech_id': int(hkey.split('g')[1])
            })
        except ValueError:
            results.append({'person': {'party': {'acronym': 'unknown', 'id': 'unknown', 'name': 'unknown'}, 'name': 'unknown', 'gov_id': 'unknown', 'id': speechdata['speaker_id']}, 'content_t': data['highlighting'][hkey]['content_t'], 'date': speechdata['date'], 'speech_id': int(hkey.split('g')[1])})

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

def removeDigrams(data):
    newdata = []
    for i, term in enumerate(data):
        if ' ' not in term['term']:
            newdata.append(term)

    return newdata

def removeSingles(data):
    newdata = []
    for i, term in enumerate(data):
        if term['scores']['tf'] != 1:
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

    truncatedResults = removeNumbers(removeSingles(removeDigrams(results)))

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

    truncatedResults = removeNumbers(removeSingles(removeDigrams(newdata)))

    sortedResults = sorted(truncatedResults, key=lambda k: k['scores']['tf-idf'], reverse=True)[:10]

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
