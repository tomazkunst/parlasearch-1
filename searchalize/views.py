from django.shortcuts import render
from kvalifikatorji.scripts import getCountListPG, getScores, problematicno, privzdignjeno, preprosto
from searchapi.utils import tryHard, enrichPartyData, getTFIDFofSpeeches2
from parlasearch.settings import SOLR_URL, API_URL, API_DATE_FORMAT, ANALIZE_URL
from datetime import datetime
from collections import Counter

import json
import requests


# Create your views here.
def setStyleScoresPGsALL(date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_=date_of.strftime(API_DATE_FORMAT)

    membersOfPGsRanges = tryHard(API_URL+'/getMembersOfPGsRanges' + ("/"+date_ if date_ else "/")).json()
    pgs = membersOfPGsRanges[-1]["members"].keys()

    print 'Starting PGs'
    scores = {}
    for pg in pgs:
        print 'PG id: ' + str(pg)
        # get word counts with solr
        counter = Counter(getCountListPG(int(pg), date_))
        total = sum(counter.values())
        scores_local = getScores([problematicno, privzdignjeno, preprosto], counter, total)

        print scores_local, #average
        scores[pg] = scores_local


    print scores
    average = {"problematicno": sum([score['problematicno'] for score in scores.values()])/len(scores),
               "privzdignjeno": sum([score['privzdignjeno'] for score in scores.values()])/len(scores), 
               "preprosto": sum([score['preprosto'] for score in scores.values()])/len(scores)}

    data = []

    for pg, score in scores.items():
        data.append({"party": pg,
                     "problematicno": score['problematicno'],
                     "privzdignjeno": score['privzdignjeno'],
                     "preprosto": score['preprosto'],
                     "problematicno_average": average['problematicno'],
                     "privzdignjeno_average": average['privzdignjeno'],
                     "preprosto_average": average['preprosto']})
    with open('tfidfs/style_score_PGs.json', 'w') as f:
        f.write(json.dumps(data))
    f.close()
    r = requests.post(ANALIZE_URL + "/pg/setAllPGsStyleScoresFromSearch/", json=data)
    return r.content


def setTFIDFforPGsALL(date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_=date_of.strftime(API_DATE_FORMAT)

    membersOfPGsRanges = tryHard('https://data.parlameter.si/v1/getMembersOfPGsRanges/'+date_).json()
    with open('tfidfs/tdidf_pg_ALL.json', 'w') as f:
        IDs = [key for key, value in membersOfPGsRanges[-1]["members"].items()]
        data_for_post = []
        for ID in IDs:
            try:
                print "tfidf ", ID
                speeches = tryHard(API_URL + '/getPGsSpeechesIDs/' + str(ID) + "/" + datetime.now().strftime(API_DATE_FORMAT)).json()
                data = getTFIDFofSpeeches2 (speeches, False)[:15]
                data_for_post.append(enrichPartyData(data, ID))
            except:
                print "neki je slo narobe"
        f.write(json.dumps(data_for_post))
    f.closed
    #r = requests.post(ANALIZE_URL + "/pg/setAllPGsTFIDFsFromSearch/", json=data_for_post)
    #return r.content
    return "Pa sem naredu vse"
