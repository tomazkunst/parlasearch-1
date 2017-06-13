from django.shortcuts import render
from kvalifikatorji.scripts import getCountListPG, getScores, problematicno, privzdignjeno, preprosto, getCountList
from searchapi.utils import tryHard, enrichPartyData, getTFIDFofSpeeches2, enrichPersonData
from parlasearch.settings import SOLR_URL, API_URL, API_DATE_FORMAT, ANALIZE_URL
from datetime import datetime
from collections import Counter

import json
import requests


# Create your views here.
def setStyleScoresPGsALL(date_=None):
    """
    Method for analyze Style scores of all parliamentray groups and POST data
    to parlalize.
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    url = API_URL+'/getMembersOfPGsRanges' + ('/'+date_ if date_ else '/')
    membersOfPGsRanges = tryHard(url).json()
    pgs = membersOfPGsRanges[-1]['members'].keys()

    print 'Starting PGs'
    scores = {}
    for pg in pgs:
        print 'PG id: ' + str(pg)
        # get word counts with solr
        counter = Counter(getCountListPG(int(pg), date_))
        total = sum(counter.values())
        scores_local = getScores([problematicno,
                                 privzdignjeno,
                                 preprosto],
                                 counter,
                                 total)

        print scores_local
        scores[pg] = scores_local

    average = {'problematicno': sum([score['problematicno']
                                     for score
                                     in scores.values()])/len(scores),
               'privzdignjeno': sum([score['privzdignjeno']
                                     for score
                                     in scores.values()])/len(scores),
               'preprosto': sum([score['preprosto']
                                 for score
                                 in scores.values()])/len(scores)}

    data = []

    for pg, score in scores.items():
        data.append({'party': pg,
                     'problematicno': score['problematicno'],
                     'privzdignjeno': score['privzdignjeno'],
                     'preprosto': score['preprosto'],
                     'problematicno_average': average['problematicno'],
                     'privzdignjeno_average': average['privzdignjeno'],
                     'preprosto_average': average['preprosto']})
    with open('tfidfs/style_score_PGs.json', 'w') as f:
        f.write(json.dumps(data))
    f.close()
    r = requests.post(ANALIZE_URL + '/pg/setAllPGsStyleScoresFromSearch/',
                      json=data)
    return r.content


def setStyleScoresMPsALL(date_=None):
    """
    Method for analyze Style scores of all parliamentray groups and POST data
    to parlalize.
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    mps = tryHard(API_URL+'/getMPs/'+date_).json()

    print 'Starting MPs'
    scores = {}
    for mp in mps:

        person_id = mp['id']

        print 'MP id: ' + str(person_id)

        # get word counts with solr
        counter = Counter(getCountList(int(person_id), date_))
        total = sum(counter.values())

        scores_local = getScores([problematicno,
                                  privzdignjeno,
                                  preprosto
                                  ],
                                 counter,
                                 total)

        print scores_local
        scores[person_id] = scores_local

    print scores
    average = {"problematicno": sum([score['problematicno']
                                     for score
                                     in scores.values()])/len(scores),
               "privzdignjeno": sum([score['privzdignjeno']
                                     for score
                                     in scores.values()])/len(scores),
               "preprosto": sum([score['preprosto']
                                 for score
                                 in scores.values()])/len(scores)}
    data = []
    for person, score in scores.items():
        data.append({'member': person,
                     'problematicno': score['problematicno'],
                     'privzdignjeno': score['privzdignjeno'],
                     'preprosto': score['preprosto'],
                     'problematicno_average': average['problematicno'],
                     'privzdignjeno_average': average['privzdignjeno'],
                     'preprosto_average': average['preprosto']})
    with open('tfidfs/style_score_MPs.json', 'w') as f:
        f.write(json.dumps(data))
    f.close()
    r = requests.post(ANALIZE_URL + '/p/setAllMPsStyleScoresFromSearch/',
                      json=data)
    return r.content


def setTFIDFforPGsALL(date_=None):
    """
    Method for analyze TFIDF of all parliamentray groups and POST data
    to parlalize.
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    url = API_URL + '/getMembersOfPGsRanges/' + date_
    membersOfPGsRanges = tryHard(url).json()
    with open('tfidfs/tdidf_pg_ALL.json', 'w') as f:
        IDs = [key for key, value in membersOfPGsRanges[-1]['members'].items()]
        data_for_post = []
        for ID in IDs:
            try:
                print 'tfidf ', ID
                url = ('' + API_URL + '/getPGsSpeechesIDs/' + str(ID) + '/'
                       '' + datetime.now().strftime(API_DATE_FORMAT) + '')
                speeches = tryHard(url).json()
                data = getTFIDFofSpeeches2(speeches, False)[:25]
                data_for_post.append(enrichPartyData(data, ID))
            except:
                print 'neki je slo narobe'
        f.write(json.dumps(data_for_post))
    f.closed
    r = requests.post(ANALIZE_URL + '/pg/setAllPGsTFIDFsFromSearch/',
                      json=data_for_post)
    return r.content
    return 'Pa sem naredu vse'


def setTFIDFforMPsALL(date_=None):
    """
    Method for analyze TFIDF of all parliamentray groups and POST data
    to parlalize.
    """
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

    api_url = ANALIZE_URL + '/p/setAllMPsTFIDFsFromSearch/'

    members = tryHard(API_URL + '/getMPs').json()
    with open('tfidfs/tdidf_MPs_ALL.json', 'w') as f:
        data_for_post = []
        for member in members:
            try:
                print 'tfidf member ', member['id']
                now_str = datetime.now().strftime(API_DATE_FORMAT)
                url = ('' + API_URL + '/getMPSpeechesIDs/'
                       '' + str(member['id']) + '/' + now_str + '')
                speeches = tryHard(url).json()
                data = getTFIDFofSpeeches2(speeches, False)[:25]
                e_data = enrichPersonData(data, str(member['id']))
                data_for_post.append(e_data)
            except:
                print 'neki je slo narobe'
        f.write(json.dumps(data_for_post))
    f.closed
    r = requests.post(ANALIZE_URL + '/pg/setAllMPsTFIDFsFromSearch/',
                      json=data_for_post)

    return 'Pa sem naredu vse', r.content
