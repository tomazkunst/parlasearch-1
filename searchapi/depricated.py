# views


def mltQuery(request, speech_i):

    solr_url = ('' + SOLR_URL + '/mlt?wt=json&mlt.count=5&q=id:g' + speech_i + ''
                '&fl=id,score,content_t,session_i,speaker_i,speech_i&fq=tip_t:govor')

    r = requests.get(solr_url)

    return JsonResponse(enrichDocs(r.json()))


# TFIDF PG
def tfidfPGQuery(request, party_i):
    date_str = datetime.now().strftime(API_DATE_FORMAT)

    return tfidfPGDateQuery(request, party_i, date_str)


def tfidfPGDateQuery(request, party_i, datetime_dt):
    url = API_URL + '/getPGsSpeechesIDs/' + party_i + '/' + datetime_dt
    speeches = tryHard(url).json()

    data = getTFIDFofSpeeches2(speeches, True)[:10]

    return JsonResponse(enrichPartyData(data, party_i), safe=False)


def tfidfPGQueryWithoutDigrams(request, party_i):
    now_str = datetime.today().strftime(API_DATE_FORMAT)
    url = API_URL + '/getPGsSpeechesIDs/' + party_i + '/' + now_str
    speeches = tryHard(url).json()

    data = getTFIDFofSpeeches2(speeches, False)[:15]

    return JsonResponse(enrichPartyData(data, party_i), safe=False)


# TFIDF Speeker
def tfidfSpeakerQuery(request, speaker_i):

    solr_url = ('' + SOLR_URL + '/tvrh/?q=id:p' + speaker_i + ''
                '&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t')

    print solr_url

    r = requests.get(solr_url)

    return JsonResponse(groupSpeakerTFIDF(r.json(),
                        int(speaker_i)),
                        safe=False)


def tfidfSpeakerQuery2(request, speaker_i):
    nowStr = datetime.today().strftime('%d.%m.%Y')
    url = API_URL + '/getMPSpeechesIDs/' + speaker_i + '/' + nowStr
    speeches = tryHard(url).json()

    data = getTFIDFofSpeeches2(speeches, True)[:15]

    return JsonResponse(enrichPersonData(data, speaker_i), safe=False)


def tfidfSpeakerDateQuery(request, speaker_i, datetime_dt):
    url = API_URL + '/getMPSpeechesIDs/' + speaker_i + '/' + datetime_dt
    speeches = tryHard(url).json()

    data = getTFIDFofSpeeches2(speeches, True)[:10]

    return JsonResponse(enrichPersonData(data, speaker_i), safe=False)

# utils


def getTFIDFofSpeeches(speeches, tfidf):
    data = {}
    speeches = ['g'+str(speech) for speech in speeches]

    hundret_speeches = [speeches[i:i+20] for i in range(0, len(speeches), 20)]
    for speech_ids in hundret_speeches:
        url = ('' + SOLR_URL + '/tvrh/?q=id:(' + ' '.join(speech_ids) + ''
               ')&tv.df=true&tv.tf=true&tv.tf_idf=true'
               '&wt=json&fl=id&tv.fl=content_t')
        temp_data = tryHard(url).json()
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

def groupSpeakerTFIDF(rawdata, person_i):

    allSpeeches = []

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:

                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    allSpeeches.append({'term': tkey,
                                        'scores': {tvalue[0]: tvalue[1],
                                                   tvalue[2]: tvalue[3],
                                                   tvalue[4]: tvalue[5]}})

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
                    new_tf = newdata[i]['scores']['tf'] + term['scores']['tf']
                    newdata[i]['scores']['tf'] = new_tf

    truncatedResults = truncateTFIDF(newdata)

    sortedResults = sorted(truncatedResults,
                           key=lambda k: k['scores']['tf-idf'],
                           reverse=True)[:10]

    url = 'https://analize.parlameter.si/v1/utils/getPersonData/' + str(person_i)
    person_data = requests.get(url).json()
    enrichedData = {'person': person_data, 'results': sortedResults}

    return enrichedData


def groupSpeakerTFIDFALL(rawdata, person_i):

    allSpeeches = []

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:

                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    allSpeeches.append({'term': tkey,
                                        'scores': {tvalue[0]: tvalue[1],
                                                   tvalue[2]: tvalue[3],
                                                   tvalue[4]: tvalue[5]}})

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
                    new_tf = newdata[i]['scores']['tf'] + term['scores']['tf']
                    newdata[i]['scores']['tf'] = new_tf

    truncatedResults = removeNumbers(removeSingles(removeDigrams(newdata)))

    sortedResults = sorted(truncatedResults,
                           key=lambda k: k['scores']['tf-idf'],
                           reverse=True)

    url = 'https://analize.parlameter.si/v1/utils/getPersonData/' + str(person_i)
    person_data = requests.get(url).json()
    enrichedData = {'person': person_data, 'results': sortedResults}

    return enrichedData


def groupPartyTFIDF(rawdata, party_i):

    allSpeeches = []

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:

                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    allSpeeches.append({'term': tkey,
                                        'scores': {tvalue[0]: tvalue[1],
                                                   tvalue[2]: tvalue[3],
                                                   tvalue[4]: tvalue[5]}})

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
                    new_tf = newdata[i]['scores']['tf'] + term['scores']['tf']
                    newdata[i]['scores']['tf'] = new_tf

    truncatedResults = removeNumbers(removeSingles(removeDigrams(newdata)))

    sortedResults = sorted(truncatedResults,
                           key=lambda k: k['scores']['tf-idf'],
                           reverse=True)[:10]

    url = 'https://analize.parlameter.si/v1/utils/getPgDataAPI/' + str(party_i)
    party_data = requests.get(url).json()
    enrichedData = {'party': party_data, 'results': sortedResults}

    return enrichedData


def groupPartyTFIDFALL(rawdata, party_i):

    allSpeeches = []

    for i, speech in enumerate(rawdata['termVectors']):
        if i % 2 == 1:

            for i, term in enumerate(speech[3]):
                if i % 2 == 0:

                    tkey = speech[3][i]
                    tvalue = speech[3][i + 1]

                    allSpeeches.append({'term': tkey,
                                        'scores': {tvalue[0]: tvalue[1],
                                                   tvalue[2]: tvalue[3],
                                                   tvalue[4]: tvalue[5]}})

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
                    new_tf = newdata[i]['scores']['tf'] + term['scores']['tf']
                    newdata[i]['scores']['tf'] = new_tf

    truncatedResults = removeNumbers(removeSingles(removeDigrams(newdata)))

    sortedResults = sorted(truncatedResults,
                           key=lambda k: k['scores']['tf-idf'],
                           reverse=True)

    url = 'https://analize.parlameter.si/v1/utils/getPgDataAPI/' + str(party_i)
    party_data = requests.get(url).json()
    enrichedData = {'party': party_data, 'results': sortedResults}

    return enrichedData


def makeTFIDFObject(data):

    results = []

    for i, term in enumerate(data):
        if i % 2 == 0:

            tkey = data[i]
            tvalue = data[i + 1]

            results.append({'term': tkey,
                            'scores': {tvalue[0]: tvalue[1],
                                       tvalue[2]: tvalue[3],
                                       tvalue[4]: tvalue[5]}})
            del data['termVectors'][1][3][i]
        else:
            del data['termVectors'][1][3][i]

    return results


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