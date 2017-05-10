#!/usr/bin/env python
# -*- coding: utf-8 -*-

from string import maketrans, punctuation
from collections import Counter
from math import log
from itertools import repeat
import requests
import json

from searchapi.utils import tryHard, tfidfPGDateQueryALL, tfidfSpeakerDateQueryALL


def getWords(filename):
    """
    filename: name of file

    method open file and return list of all words which is in file
    """
    f = open(filename, 'r')
    return f.read().splitlines()


def getWordsDict(filename):
    """
    filename: name of file

    method return dictionary with keys of all words in file
    """
    wordslist = getWords(filename)
    wordsdict = {word: 1 for word in wordslist}

    return wordsdict

problematicno = getWordsDict('kvalifikatorji/problematicno_nase.txt')
privzdignjeno = getWordsDict('kvalifikatorji/privzdignjeno_nase.txt')
preprosto = getWordsDict('kvalifikatorji/preprosto_nase.txt')

text = ('Tudi v Poslanski skupini Socialnih demokratov ne bomo podprli'
        ' proračunov za leti 2013 in 2014. Že v uvodnem nagovoru v imenu'
        ' poslanske skupine smo opozorili, da ta dva proračuna nista odgovor '
        'na dogajanje v Sloveniji. Ljudje pričakujejo, da bosta ta dva '
        'proračuna omogočala gospodarski razvoj, da bosta omogočala '
        'zagotavljanje novih delovnih mest, da bosta omogočala nadaljnji '
        'obstoj in razvoj javnega šolstva, tako osnovnega kot tudi do nivoja '
        'univerz, in predvsem da bomo imeli vsi tudi temu primerno socialno '
        'varnost. Vseh teh problemov ta dva proračuna ne odpravljata, '
        'nasprotno. Kaže se, da vladajoča koalicija razume in sledi samo cilju'
        ' čimprejšnje razprodaje državnega premoženja in želi pri tem '
        'omogočiti vsem tistim, ki imajo te informacije, da se vključijo v ta '
        'proces na način, da dajo prioriteto osebnim interesom, ne pa '
        'interesom države, ne interesom ljudi, ki pričakujejo, da bomo ravnali'
        ' po našem mnenju, tudi v Državnem zboru, povsem drugače kot je '
        'zapisano v teh dveh proračunih.')


def getCountList(speaker_id, date_):
    """
    speaker_id: id of speaker
    date_: date of analysis

    method return term frequency for each word spoken by speaker
    """
    data = None
    while data is None:
        try:
            data = tfidfSpeakerDateQueryALL(str(party_id), date_)
        except:
            pass

    wordlist = data['results']

    wordlist_new = {word["term"]: word["scores"]["tf"] for word in wordlist}

    return wordlist_new


def getCountListPG(party_id, date_):
    """
    party_id: id of parliamentary group
    date_: date of analysis

    method return term frequency for each word spoken by speaker of
    parliamentary group
    """
    data = tfidfPGDateQueryALL(str(party_id), date_)
    wordlist = data['results']

    wordlist_new = {word["term"]: word["scores"]["tf"] for word in wordlist}

    return wordlist_new


def getScores(words_list, counter, total):
    """
    word_list: list of words for each classificator (problematicno,
    privzdignjeno, preprosto)
    counter: counter of words for classfication
    total: counter of unique words

    method returns dictionary with score for each classificator
    """

    print 'Getting style scores'

    scores = {'problematicno': 0, 'privzdignjeno': 0, 'preprosto': 0}

    for word in counter:
        scores['problematicno'] = scores['problematicno'] + words_list[0].setdefault(word, 0)
        scores['privzdignjeno'] = scores['privzdignjeno'] + words_list[1].setdefault(word, 0)
        scores['preprosto'] = scores['preprosto'] + words_list[2].setdefault(word, 0)

    if float(total) == 0.0:
        total = 1

    scores['problematicno'] = scores['problematicno']*1000000000/float(total)
    scores['privzdignjeno'] = scores['privzdignjeno']*1000000000/float(total)
    scores['preprosto'] = scores['preprosto']*1000000000/float(total)

    return scores
