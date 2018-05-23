# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import JsonResponse, Http404
import requests
from datetime import datetime, timedelta
from parlasearch.settings import SOLR_URL, API_URL, API_DATE_FORMAT, ANALIZE_URL
import calendar

from utils import enrichQuery, enrichHighlights, enrichTFIDF, groupDFALL, tryHard, add_months, addOrganizations, remove_law_or_act

# Create your views here.

ZERO_TIME = 'T00:00:00.000Z'


def regularQuery(request, words, start_page=None):
    """
    * @api {get} q/{word}/{?start_page} Search in transcripts
    * @apiName regularQuery
    * @apiGroup Search
    * @apiDescription
    words: word/words for search
    start_page: pager in results

    search query in transcripts
    * @apiParam {word} search word.
    * @apiParam {start_page} start page Optional.

    * @apiSuccess {Object} /
    * @apiSuccess {Object} /.facet_counts
    * @apiSuccess {Object} /.facet_counts.facet_ranges
    * @apiSuccess {Object} /.facet_counts.facet_ranges.datetime_dt
    * @apiSuccess {String} /.facet_counts.facet_ranges.datetime_dt.start
    * @apiSuccess {String} /.facet_counts.facet_ranges.datetime_dt.end
    * @apiSuccess {String} /.facet_counts.facet_ranges.datetime_dt.gap
    * @apiSuccess {String[]} /.facet_counts.facet_ranges.datetime_dt.counts
    * @apiSuccess {Object} /.facet_counts.facet_fields
    * @apiSuccess {Object[]} /.facet_counts.facet_fields.speaker_i

    * @apiSuccess {Object} /.facet_counts.facet_fields.speaker_i.person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} /.facet_counts.facet_fields.speaker_i.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} /.facet_counts.facet_fields.speaker_i.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.name MP's full name.
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} /.facet_counts.facet_fields.speaker_i.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} /.facet_counts.facet_fields.speaker_i.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} /.facet_counts.facet_fields.speaker_i.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.party.name The party's name.
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} /.facet_counts.facet_fields.speaker_i.person.id The person's Parladata id.
    * @apiSuccess {Boolean} /.facet_counts.facet_fields.speaker_i.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).
    
    * @apiSuccess {Object} /.facet_counts.facet_fields.speaker_i.score
    * @apiSuccess {String} /.facet_counts.facet_fields.party_i
    * @apiSuccess {Object[]} /.highlighting
    * @apiSuccess {Object[]} /.highlighting.start_time
    * @apiSuccess {String} /.highlighting.content_t
    * @apiSuccess {String} /.highlighting.date
    * @apiSuccess {Integer} /.highlighting.speech_id
    * @apiSuccess {Integer} /.highlighting.order

    * @apiSuccess {Object} /.highlighting.person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} /.highlighting.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} /.highlighting.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} /.highlighting.person.name MP's full name.
    * @apiSuccess {String} /.highlighting.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} /.highlighting.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} /.highlighting.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} /.highlighting.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} /.highlighting.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} /.highlighting.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} /.highlighting.person.party.name The party's name.
    * @apiSuccess {String} /.highlighting.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} /.highlighting.person.id The person's Parladata id.
    * @apiSuccess {Boolean} /.highlighting.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {Object} /.responseHeader
    * @apiSuccess {Integer} /.responseHeader.status
    * @apiSuccess {Integer} /.responseHeader.QTime
    * @apiSuccess {Object} /.responseHeader.params
    * @apiSuccess {String} /.responseHeader.params.fq
    * @apiSuccess {String} /.responseHeader.params.rows
    * @apiSuccess {Object[]} /.responseHeader.params.facet.field
    * @apiSuccess {String} /.responseHeader.params.facet.range.gap
    * @apiSuccess {String} /.responseHeader.params.wt
    * @apiSuccess {String} /.responseHeader.params.hl.snippets
    * @apiSuccess {String} /.responseHeader.params.facet.range.end
    * @apiSuccess {String} /.responseHeader.params.hl.regex.pattern
    * @apiSuccess {String} /.responseHeader.params.facet
    * @apiSuccess {String} /.responseHeader.params.q
    * @apiSuccess {String} /.responseHeader.params.start
    * @apiSuccess {String} /.responseHeader.params.facet.range
    * @apiSuccess {String} /.responseHeader.params.hl
    * @apiSuccess {String} /.responseHeader.params.hl.fragsize
    * @apiSuccess {String} /.responseHeader.params.hl.mergeContiguous
    * @apiSuccess {String} /.responseHeader.params.hl.fl
    * @apiSuccess {String} /.responseHeader.params.hl.fragmenter
    * @apiSuccess {String} /.responseHeader.params.facet.range.start

    * @apiSuccess {Object} /.response
    * @apiSuccess {Integer} /.response.start
    * @apiSuccess {Integer} /.response.numFound
    * @apiSuccess {Object[]} /.response.docs
    * @apiSuccess {Object[]} /.response.docs.tip_t
    * @apiSuccess {Integer} /.response.docs.session_i
    * @apiSuccess {Integer} /.response.docs.party_i
    * @apiSuccess {String} /.response.docs.datetime_dt
    * @apiSuccess {Integer} /.response.docs.speaker_i
    * @apiSuccess {Object[]} /.response.docs.content_t
    * @apiSuccess {Integer} /.response.docs._version_
    * @apiSuccess {String} /.response.docs.id
    * @apiSuccess {Integer} /.response.docs.org_i

    * @apiExample {curl} Example:
        curl -i https://isci.parlameter.si/q/parlameter

    * @apiSuccessExample {json} Example response:
    {
        "facet_counts": {
            "facet_ranges": {
                "datetime_dt": {
                    "start": "2014-01-01T00:00:00Z",
                    "counts": [
                        "2014-01-01T00:00:00Z",
                        0,
                        "2014-02-01T00:00:00Z",
                        0,
                        "2014-03-01T00:00:00Z",
                        0
                    ],
                    "end": "2014-03-01T00:00:00Z",
                    "gap": "+1MONTHS"
                }
            },
            "facet_fields": {
                "speaker_i": [
                    {
                        "person": {
                            "name": "Vinko Gorenak",
                            "district": [
                                42
                            ],
                            "gender": "m",
                            "is_active": false,
                            "party": {
                                "acronym": "SDS",
                                "id": 5,
                                "is_coalition": false,
                                "name": "PS Slovenska Demokratska Stranka"
                            },
                            "type": "mp",
                            "id": 25,
                            "gov_id": "P116",
                            "has_function": false
                        },
                        "score": 1
                    },
                    {
                        "person": {
                            "name": "Matjaž Han",
                            "district": [
                                13
                            ],
                            "gender": "m",
                            "is_active": false,
                            "party": {
                                "acronym": "SD",
                                "id": 7,
                                "is_coalition": true,
                                "name": "PS Socialni Demokrati"
                            },
                            "type": "mp",
                            "id": 30,
                            "gov_id": "P018",
                            "has_function": false
                        },
                        "score": 1
                    }
                ],
                "party_i": [
                    "5",
                    2,
                    "1",
                    1,
                    "7",
                    1
                ]
            }
        },
        "highlighting": [
            {
                "start_time": "2017-01-25T01:00:00",
                "session_id": 8940,
                "person": {
                    "name": "Marijan Pojbič",
                    "district": [
                        25
                    ],
                    "gender": "m",
                    "is_active": false,
                    "party": {
                        "acronym": "SDS",
                        "id": 5,
                        "is_coalition": false,
                        "name": "PS Slovenska Demokratska Stranka"
                    },
                    "type": "mp",
                    "id": 66,
                    "gov_id": "P098",
                    "has_function": false
                },
                "content_t": "<em>Parlameter</em>.</em>",
                "date": "2017-01-23",
                "speech_id": 893563,
                "order": 1340
            },
            {
                "start_time": "2017-01-25T01:00:00",
                "session_id": 8940,
                "person": {
                    "name": "Janja Sluga",
                    "district": [
                        31
                    ],
                    "gender": "f",
                    "is_active": false,
                    "party": {
                        "acronym": "SMC",
                        "id": 1,
                        "is_coalition": true,
                        "name": "PS Stranka modernega centra"
                    },
                    "type": "mp",
                    "id": 73,
                    "gov_id": "P284",
                    "has_function": false
                },
                "content_t": "ki se mu reče <em>parlameter</em> in ki se natančno vidi kaj kdo govori in kolikokrat se oglasi.</em>",
                "date": "2017-01-23",
                "speech_id": 893561,
                "order": 1320
            }
        ],
        "responseHeader": {
            "status": 0,
            "QTime": 18,
            "params": {
                "fq": "tip_t:govor",
                "rows": "50",
                "facet.field": [
                    "speaker_i",
                    "party_i"
                ],
                "facet.range.gap": "+1MONTHS",
                "wt": "json",
                "hl.snippets": "1",
                "facet.range.end": "NOW",
                "hl.regex.pattern": "\\w[^\\.!\\?]{1,600}[\\.!\\?]",
                "facet": "true",
                "q": "content_t:parlameter",
                "start": "0",
                "facet.range": "datetime_dt",
                "hl": "true",
                "hl.fragsize": "5000",
                "hl.mergeContiguous": "false",
                "hl.fl": "content_t",
                "hl.fragmenter": "regex",
                "facet.range.start": "2014-01-01T00:00:00.000Z"
            }
        },
        "response": {
            "start": 0,
            "numFound": 5,
            "docs": [
                {
                    "tip_t": [
                        "govor"
                    ],
                    "session_i": 7654,
                    "party_i": 7,
                    "datetime_dt": "2016-12-14T01:00:00Z",
                    "speaker_i": 30,
                    "content_t": [
                        "Hvala lepa predsednik, ministrica, predlagatelji, predvsem predlagateljica danes Suzana si boš v parlametru popravila statistiko, tak da besedni zaklad se ti bo povečal, imela boš veliko izgovorjenih besed, ampak koroški dečki bodo pa še kar ostali tam kjer so. To je problem. Parlameter pa bo jutri statistiko tvojih nastopov pač ocenil kot dobro. \nSedaj, jaz se ne bom ukvarjal z definicijo interpelacije. Dola leta sem poslanec, vem da je interpelacija orodja opozicije, da vem da ni pomembna vsebina, pomembne so besede, pomembni so nastopi, pomembni so televizijski kadri in pomembno je zbuditi v javnosti, da je v tej državi vse narobe. In, tako da, kar se tega tiče, je brezveze. Sedaj, problem pa je, kadar govorimo o interpelaciji, je pa vendarle malo problema ta vsebina. Sedaj bom tudi jaz kot neka papiga tukaj ponavljal, da pač izkoriščamo to tragedijo, ampak resnično tragedijo za to, da se politika sedaj med seboj obklada, se žali in še kaj več bi lahko našteval. To, gospe in gospodje, absolutno ni dobro. Mislim, da če ta dva fantka slučajno sta blizu televizije in slučajno prestavita televizijo, jaz upam, da gledata kaj lepšega, se bo take razprave, ki jih imamo danes, vtem fantkom sigurno usedle na dušo in jih bo ta duša spremljala celo življenje, ne samo tragedija, ki se je zgodila v njuni družini. In eno stvar vam pa povem. Ne družinski zakoni ne kakršnikoli zakoni, ne bo povrnil mamice tem dvema otrokoma in ne bo povrnil nekega dostojanstva in nekega srečnega otroštva tema dvema otrokoma. Saj je vse lepo in prav, zakoni da se pišejo, ampak še zmeraj zakone na nek način interpretiramo ljudje in ljudje v bistvu delajo ali pa delamo napake ali pa ne. \nSedaj, naši ministrice se danes očita, kakor vsaj jaz razumem, to interpelacijo. Glavni očitek je, da je bila tisti dan na novinarski konferenci in se je odzvala na, bom rekel, na novinarski problem oziroma novinarsko zgodbo, ki se je pač takrat dogajala. Jaz sem tisoč procentov prepričan, to pa zaradi izkušenj, ki jih imamo kot politik, da če ministrica se takrat ne bi odzvala in ne bi bila na tisti novinarski konferenci, bi bil pogrom na ministrico isti kot je sedaj, samo da bi bila vsebina drugačna. Govorili bi o tem, da je sramota, da se minister ne odzove pri taki tragediji kot se je naredila in kako je to mogoče, da sedi v nekih lepih prostorih in nič ne reče. Isto bi bilo, dragi gospodje in gospe. Saj sem tudi jaz politik, saj bi jaz verjetno isto delal, če bi bil na vašem mestu, samo vam pa povem, da ne bi delal takih zgodb, ko bi imele osnovo tako tragedijo. Vse ostalo, zakoni, sociala, drugo, pa to je, gospe in gospodje, toliko prostora za demagogijo, saj smo slišali prej Združeno levico, čeprav meni moji strankarski kolegi rečejo, ne se ukvarjati z Združeno levico, ne jih kregati, itn., ampak to kar je Kordiš govoril, pa to še v Venezueli ni. Ne, ker v življenju moraš biti malo realen. Če bi jaz lahko danes odločal in če bi imel čarobno palico, jaz bi dal vsem delo in za to delo bi morali biti ljudje pošteno plačani in ne bi rabil nobeden nobene socialne pomoči. Ja, razen tistih, ki ne morejo dela opravljati, to so pa invalidi, ljudje ki so bolni, ljudje ki ne morejo, ampak poglejte, ne živimo v Indiji Koromandija, živimo v enem grdem svetu, kjer vemo da ima kakorkoli en procent človeštva vso bogastvo, bom rekel, na nek način akumulirano pri sebi. \nSedaj pa še nekaj o eh koroških dečkih oziroma o tej zgodbi.    Nisem toliko razočaran, če politika zagrabi tako zgodbo, ker pač išče politične točke, pa išče ali se mu bo pokazalo tukaj na anketi v petek oziroma v ponedeljek. Bolj sem razočaran, ko odvetniki, ki nimajo kaj delati, najdejo tako zgodbo za svojo promocijo, zato da so lahko vsak dan na televiziji in zato, da lahko potem dobijo neke druge posle. Tega pa me je malo strah. In ta odvetnik, ki je bil nenazadnje tudi naš svetnik, slišal sem nekje na Koroškem ali celo podžupan, če si član neke socialdemokracije neke vrednote pač zagovarjaš, vloži in se potrudi v tej zgodbi vložiti 26 pritožb in 45 pravnih sredstev. Ampak gospe in gospodje, pa mi bomo imeli tu še 68 interpelacij na to temo, ker vsakič ko bo sodišče nekaj sprejelo, bo interpelacija. Saj tem otrokom in tej familiji se bo do konca zmešalo. Če je to otrokova korist, potem jaz ta trenutek sem res malo zmeden. \nSedaj pa samo še eno veliko vprašanje in velik vprašaj. Verjamem, pa moram reči, ker Jožeta, sva že kar nekaj časa, ne bom rekel, da prijatelja, ker bodo rekli da…, ampak zelo dobra znanca. Sigurno je eden tistih ljudi, ki želi ljudem dobro. Tudi jaz. Pa verjetno v tej dvorani vsi. Pa dajmo eno vprašanje. Če ministrica sedajle odstopi, vi boste srečni, mi bomo razočarani. Ali bodo dečki prišli k starim staršem? Ali bodo starši pred božičem najbolj srečni otroci na tem svetu? Bodo? Če se bo to naredilo in če bi se to naredilo, da Anja odstopi, jaz jo grem sedaj prositi, Anja odstopi. Ne bo jo treba prositi. Anja bi to naredila takoj, če bodo zaradi tega za božič ti otroci, ti fantki srečni odpirali darila pod smrekico, se veselili v družinskem okolju. Se bodo? Ne bodo, ali ne. Sedajle mi gre kurja polt, ker vem, jaz bom srečen in vesel, ker se mi bo hčerka vrnila iz Portugalske, ker bomo lepo za božič skupaj, srečni doma. Ti dragi otroci, ti bogi otroci, fantki pa ne bodo. Ali bodo pri starih starših? Ali bodo pri rejnikih? Ni pomembno. Ti otroci so etiketirani. Sedaj je samo vprašanje kakšno etiketo jim bomo dali. In največjo etiketo, se opravičujem, in dajva politika, ki se v tej tragediji vsak dan znova in znova pogovarja samo zato, da bi spravili iz mesta eno Anjo Kopač Mrak. Včasih sem žalosten in razočaran. Hvala lepa."
                    ],
                    "_version_": 1568412779027628000,
                    "id": "g1247808",
                    "org_i": 95
                },
                {
                    "tip_t": [
                        "govor"
                    ],
                    "session_i": 8940,
                    "party_i": 5,
                    "datetime_dt": "2017-01-25T01:00:00Z",
                    "speaker_i": 66,
                    "content_t": [
                        "Gospod podpredsednik, rad bi samo opozoril, da gospo Slugo opozorite, da zaradi tega, kar sem jaz govoril tukaj v parlamentu ne rabi biti tako bleda, ker ko poveš resnico o človeku potem pač ima težave človek in nastopi tako kot je ona zdaj nastopila, agresivno proti meni. Jaz nisem nič agresivno govoril. Jaz sem govoril zelo korektno, zelo pošteno in res je parlament. Kaj je že tista zgodba? Parlameter. Bodo ljudje videli kaj je kdo v tem državnem zboru govoril in še bolj pomembno ne kaj je govoril, pomembno je ali govori tisti, kar drži in kar je prav. In ne tisto, kar mu nekdo napiše, nek partijski sekretar. Meni nobeden ne piše govorov."
                    ],
                    "_version_": 1558596758970302500,
                    "id": "g893563",
                    "org_i": 95
                }
            ]
        }
    }
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

    return JsonResponse(enrichHighlights(enrichQuery(r.json(), True)))


def filterQuery(request, words='', start_page=None):
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
    """
    * @api {get} filter/{word}/{?start_page} Search votes
    * @apiName filterQuery
    * @apiGroup Search
    * @apiDescription

    search query in transcripts
    * @apiParam {word} search word.
    * @apiParam {start_page} start page Optional.

    * @apiSuccess {Object} /
    * @apiSuccess {Object} /.facet_counts
    * @apiSuccess {Object} /.facet_counts.facet_ranges
    * @apiSuccess {Object} /.facet_counts.facet_ranges.datetime_dt
    * @apiSuccess {String} /.facet_counts.facet_ranges.datetime_dt.start
    * @apiSuccess {String} /.facet_counts.facet_ranges.datetime_dt.end
    * @apiSuccess {String} /.facet_counts.facet_ranges.datetime_dt.gap
    * @apiSuccess {String[]} /.facet_counts.facet_ranges.datetime_dt.counts
    * @apiSuccess {Object} /.facet_counts.facet_fields
    * @apiSuccess {Object[]} /.facet_counts.facet_fields.speaker_i

    * @apiSuccess {Object} /.facet_counts.facet_fields.speaker_i.person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} /.facet_counts.facet_fields.speaker_i.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} /.facet_counts.facet_fields.speaker_i.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.name MP's full name.
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} /.facet_counts.facet_fields.speaker_i.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} /.facet_counts.facet_fields.speaker_i.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} /.facet_counts.facet_fields.speaker_i.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.party.name The party's name.
    * @apiSuccess {String} /.facet_counts.facet_fields.speaker_i.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} /.facet_counts.facet_fields.speaker_i.person.id The person's Parladata id.
    * @apiSuccess {Boolean} /.facet_counts.facet_fields.speaker_i.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {Object} /.facet_counts.facet_fields.speaker_i.score
    * @apiSuccess {String[]} /.facet_counts.facet_fields.org_i pairs of organization id and score
    * @apiSuccess {String[]} /.facet_counts.facet_fields.party_i pairs of party id and score
    * @apiSuccess {Object[]} /.facet_counts.facet_fields.party_e list of party objects
    * @apiSuccess {Object} /.facet_counts.facet_fields.party_e.party
    * @apiSuccess {String} /.facet_counts.facet_fields.party_e.party.acronym
    * @apiSuccess {Integer} /.facet_counts.facet_fields.party_e.party.id
    * @apiSuccess {Boolean} /.facet_counts.facet_fields.party_e.party.is_coalition
    * @apiSuccess {String} /.facet_counts.facet_fields.party_e.party.name
    * @apiSuccess {Integer} /.facet_counts.facet_fields.party_e.score

    * @apiSuccess {Object[]} /.highlighting
    * @apiSuccess {Object[]} /.highlighting.start_time
    * @apiSuccess {String} /.highlighting.content_t
    * @apiSuccess {String} /.highlighting.date
    * @apiSuccess {Integer} /.highlighting.speech_id
    * @apiSuccess {Integer} /.highlighting.order

    * @apiSuccess {Object} /.highlighting.person MP's person object (comes with most calls).
    * @apiSuccess {Boolean} /.highlighting.person.is_active Answer the question: Is this MP currently active?
    * @apiSuccess {Integer[]} /.highlighting.person.district List of Parladata ids for districts this person was elected in.
    * @apiSuccess {String} /.highlighting.person.name MP's full name.
    * @apiSuccess {String} /.highlighting.person.gov_id MP's id on www.dz-rs.si
    * @apiSuccess {String} /.highlighting.person.gender MP's gender (f/m) used for grammar
    * @apiSuccess {Object} /.highlighting.person.party This MP's standard party objects (comes with most calls).
    * @apiSuccess {String} /.highlighting.person.party.acronym The MP's party's acronym.
    * @apiSuccess {Boolean} /.highlighting.person.party.is_coalition Answers the question: Is this party in coalition with the government?
    * @apiSuccess {Integer} /.highlighting.person.party.id This party's Parladata (organization) id.
    * @apiSuccess {String} /.highlighting.person.party.name The party's name.
    * @apiSuccess {String} /.highlighting.person.type The person's parlalize type. Always "mp" for MPs.
    * @apiSuccess {Integer} /.highlighting.person.id The person's Parladata id.
    * @apiSuccess {Boolean} /.highlighting.person.has_function Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).

    * @apiSuccess {Object} /.responseHeader
    * @apiSuccess {Integer} /.responseHeader.status
    * @apiSuccess {Integer} /.responseHeader.QTime
    * @apiSuccess {Object} /.responseHeader.params
    * @apiSuccess {String} /.responseHeader.params.fq
    * @apiSuccess {String} /.responseHeader.params.rows
    * @apiSuccess {Object[]} /.responseHeader.params.facet.field
    * @apiSuccess {String} /.responseHeader.params.facet.range.gap
    * @apiSuccess {String} /.responseHeader.params.wt
    * @apiSuccess {String} /.responseHeader.params.hl.snippets
    * @apiSuccess {String} /.responseHeader.params.facet.range.end
    * @apiSuccess {String} /.responseHeader.params.hl.regex.pattern
    * @apiSuccess {String} /.responseHeader.params.facet
    * @apiSuccess {String} /.responseHeader.params.q
    * @apiSuccess {String} /.responseHeader.params.start
    * @apiSuccess {String} /.responseHeader.params.facet.range
    * @apiSuccess {String} /.responseHeader.params.hl
    * @apiSuccess {String} /.responseHeader.params.hl.fragsize
    * @apiSuccess {String} /.responseHeader.params.hl.mergeContiguous
    * @apiSuccess {String} /.responseHeader.params.hl.fl
    * @apiSuccess {String} /.responseHeader.params.hl.fragmenter
    * @apiSuccess {String} /.responseHeader.params.facet.range.start

    * @apiSuccess {Object} /.response
    * @apiSuccess {Integer} /.response.start
    * @apiSuccess {Integer} /.response.numFound
    * @apiSuccess {Object[]} /.response.docs
    * @apiSuccess {Object[]} /.response.docs.tip_t
    * @apiSuccess {Integer} /.response.docs.session_i
    * @apiSuccess {Integer} /.response.docs.party_i
    * @apiSuccess {String} /.response.docs.datetime_dt
    * @apiSuccess {Integer} /.response.docs.speaker_i
    * @apiSuccess {Object[]} /.response.docs.content_t
    * @apiSuccess {Integer} /.response.docs._version_
    * @apiSuccess {String} /.response.docs.id
    * @apiSuccess {Integer} /.response.docs.org_i
    * @apiSuccess {Object[]} /.organizations
    * @apiSuccess {Integer} /.organizations.score
    * @apiSuccess {Integer} /.organizations.id
    * @apiSuccess {String} /.organizations.name

    * @apiSuccess {Boolean} /.has_council_score
    * @apiSuccess {Boolean} /.has_dz_score

    * @apiExample {curl} Example:
        curl -i https://isci.parlameter.si/filter/parlameter

    * @apiSuccessExample {json} Example response:
    {
        "facet_counts": {
            "facet_ranges": {
                "datetime_dt": {
                    "start": "2014-09-01T00:00:00Z",
                    "counts": [
                        "2014-09-01T00:00:00Z",
                        47,
                        "2014-10-01T00:00:00Z",
                        11
                    ],
                    "end": "2017-07-01T00:00:00Z",
                    "gap": "+1MONTHS"
                }
            },
            "facet_fields": {
                "speaker_i": [
                    {
                        "person": {
                            "name": "Tomaž Gantar",
                            "district": [
                                80
                            ],
                            "gender": "m",
                            "is_active": false,
                            "party": {
                                "acronym": "DeSUS",
                                "id": 3,
                                "is_coalition": true,
                                "name": "PS Demokratska Stranka Upokojencev Slovenije"
                            },
                            "type": "mp",
                            "id": 22,
                            "gov_id": "P251",
                            "has_function": false
                        },
                        "score": 198
                    }
                ],
                "org_i": [
                    "95",
                    1415,
                    "27",
                    625
                ],
                "party_e": [
                    {
                        "party": {
                            "acronym": "SDS",
                            "id": 5,
                            "is_coalition": false,
                            "name": "PS Slovenska Demokratska Stranka"
                        },
                        "score": 522
                    }
                ],
                "party_i": [
                    "5",
                    522,
                    "1",
                    471
                ]
            }
        },
        "highlighting": [
            {
                "start_time": "2017-06-09T02:00:00",
                "session_id": 9587,
                "person": {
                    "name": "Jožica Mavčec Zakotnik",
                    "district": null,
                    "gender": null,
                    "is_active": null,
                    "party": {
                        "acronym": null,
                        "id": null,
                        "is_coalition": null,
                        "name": null
                    },
                    "type": "visitor",
                    "id": 3807,
                    "gov_id": null,
                    "has_function": false
                },
                "content_t": "da je Ministrstvo za <em>zdravje</em> od izbruha požara ves čas spremljalo delo zdravstvene službe pri zagotavljanju neposredne oskrbe prebivalcem. Službe za medicino dela, prometa in športa je ustrezno poskrbela za ugotavljanje izpostavljenosti gasilcev, članov civilne zaščite, drugega intervencijskega osebja ter delavcev na območju obrata podjetja Kemis. Vsem je bila takrat in je še vedno nudena posebna zdravstvena oskrba in zaščita. Za varovanje <em>zdravja</em> ljudi smo že med požarom in neprekinjeno do danes redno posredovali in objavljali priporočila kako naj preventivno ravnajo, da bi se izognili in v največji možni meri zmanjšali možnost izpostavljenosti snovem v okolju. Do prejetja prvih analiz teh nismo poznali. Smo pa ravnali tako, da smo upoštevali največjo možno zaščito ljudi. V primeru, da bi v dneh po nesreči obstajala večja akutna nevarnost za <em>zdravje</em>, bi na to opozorili.</em>",
                "date": "2017-05-30",
                "speech_id": 1263913,
                "order": 340
            }
        ],
        "responseHeader": {
            "status": 0,
            "QTime": 759,
            "params": {
                "fq": "",
                "rows": "50",
                "facet.field": [
                    "speaker_i",
                    "party_i",
                    "org_i"
                ],
                "facet.range.gap": "+1MONTHS",
                "wt": "json",
                "hl.snippets": "1",
                "facet.range.end": "NOW",
                "hl.regex.pattern": "\\w[^\\.!\\?]{400,600}[\\.!\\?]",
                "facet": "true",
                "q": "content_t:zdravje AND tip_t:govor",
                "start": "0",
                "facet.range": "datetime_dt",
                "hl": "true",
                "hl.fragsize": "5000",
                "hl.mergeContiguous": "false",
                "hl.fl": "content_t",
                "hl.fragmenter": "regex",
                "facet.range.start": "2014-01-01T00:00:00.000Z"
            }
        },
        "response": {
            "start": 0,
            "numFound": 2948,
            "docs": [
                {
                    "tip_t": [
                        "govor"
                    ],
                    "session_i": 6675,
                    "party_i": 8,
                    "datetime_dt": "2015-07-14T02:00:00Z",
                    "speaker_i": 31,
                    "content_t": [
                        "Hvala lepa, predsedujoči podpredsednik, pozdravljena ministrica!"
                    ],
                    "_version_": 1558596112263151600,
                    "id": "g583168",
                    "org_i": 95
                }
            ]
        },
        "organizations": [
            {
                "score": 4,
                "id": 105,
                "name": "Komisija za nadzor obveščevalnih in varnostnih služb"
            },
            {
                "score": 3,
                "id": 11,
                "name": "Komisija za narodni skupnosti"
            }
        ],
        "has_council_score": true,
        "has_dz_score": true
    }
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

    filters_out = {
        'people': people.split(',') if people else None,
        'parties': parties.split(',') if parties else None,
        'from': from_date,
        'to': to_date,
        'is_dz': is_dz,
        'council': is_council,
        'wb': working_bodies.split(',') if working_bodies else None,
        'time_filter': time_filter,
        }



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
    time_filter_dates = None
    if time_filter:
        time_filter_dates = [datetime.strptime(t_filter, API_DATE_FORMAT)
                             for t_filter in time_filter.split(',')]

        time_filter = [(t_time.strftime('%Y-%m-%d') + ZERO_TIME,
                        add_months(t_time,
                                   1).strftime('%Y-%m-%d') + ZERO_TIME + ']')
                       for t_time in time_filter_dates]
        time_str = ['[' + t_time[0] + ' TO ' + t_time[1]
                    for t_time in time_filter]
        time_query = 'datetime_dt:(' + ' OR '.join(time_str) + ')'
        filters.append(time_query)

    f_date = min(time_filter_dates) if time_filter_dates else None
    t_date = add_months(max(time_filter_dates), 1) if time_filter_dates else None

    if f_date:
        facetStartRange = f_date.strftime('%Y-%m-%d') + ZERO_TIME
    else:
        facetStartRange = '2014-01-01' + ZERO_TIME

    if t_date:
        facetEndRange = t_date.strftime('%Y-%m-%d') + ZERO_TIME
    else:
        facetEndRange = 'NOW'

    if not q:
        q = '*'
    
    query = 'content_t:' + q.replace('IN', 'AND').replace('!', '%2B')
    #query += ' AND tip_t:govor'
    filters.append('tip_t:govor')

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
    if q == '*':
        solr_params.update({'sort': 'datetime_dt desc'})
        solr_params.update({'hl': 'false'})
    # print solr_params
    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    # print url

    r = requests.get(url)
    out = addOrganizations(enrichHighlights(enrichQuery(r.json(),
                           show_all=True)))
    out.update({'filters': filters_out})
    return JsonResponse(out)


def motionQuery(request, words, start_page=None):
    """
    * @api {get} v/{words}/{?start_page}/
    * @apiName motionQuery
    * @apiGroup Search
    * @apiDescription
    search query by motion text

    search query in transcripts
    * @apiParam {words} words for filter.
    * @apiParam {start_page} start page is Optional pagination parameter.

    * @apiSuccess {Object[]} /
    * @apiSuccess {Object} /.created_for
    * @apiSuccess {String} /.session
    * @apiSuccess {String} /.session.name
    * @apiSuccess {String} /.session.date_ts
    * @apiSuccess {Object[]} /.session.orgs
    * @apiSuccess {String} /.session.orgs.acronym
    * @apiSuccess {Boolean} /.session.orgs.is_coalition
    * @apiSuccess {String} /.session.orgs.name
    * @apiSuccess {Integer} /.session.orgs.id
    * @apiSuccess {String} /.session.date
    * @apiSuccess {Integer} /.session.id
    * @apiSuccess {Boolean} /.session.in_review

    * @apiSuccess {Object} /.results
    * @apiSuccess {Integer} /.results.motion_id
    * @apiSuccess {String} /.results.text
    * @apiSuccess {Integer} /.results.abstain
    * @apiSuccess {Integer} /.results.votes_for
    * @apiSuccess {Integer} /.results.not_present
    * @apiSuccess {Integer} /.results.against
    * @apiSuccess {Boolean} /.results.result


    * @apiExample {curl} Example:
        curl -i https://isci.parlameter.si/v/zdravje

    * @apiSuccessExample {json} Example response:
    [
        {
            "created_for": "2016-12-12",
            "session": {
                "name": "25. redna seja",
                "date_ts": "2016-12-12T01:00:00",
                "org": {
                    "acronym": "DZ",
                    "is_coalition": false,
                    "name": "Državni zbor",
                    "id": 95
                },
                "date": "12. 12. 2016",
                "orgs": [
                    {
                        "acronym": "DZ",
                        "is_coalition": false,
                        "name": "Državni zbor",
                        "id": 95
                    }
                ],
                "id": 7654,
                "in_review": true
            },
            "results": {
                "abstain": 5,
                "text": "Predlog sklepa (razprava o odgovoru ministrice za zdravje Milojke Kolar Celarc na poslansko vprašanje Jelke Godec v zvezi s sklepom Ministrstva za zdravje.)",
                "votes_for": 7,
                "against": 47,
                "motion_id": 6654,
                "not_present": 31,
                "result": false
            }
        },
    ]
    """
    rows = 50
    solr_url = SOLR_URL+'/select?wt=json'

    q = words.replace('+', ' ')

    solr_params = {
        'q': 'content_t:' + q.replace('IN', 'AND').replace('!', '%2B'),
        #'sort': 'score',
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
    sort_ids = []
    try:
        docs = r['response']['docs']
        for doc in docs:
            ids.append(str(doc['voteid_i']))
            sort_ids.append(doc['voteid_i'])
    except:
        JsonResponse({'status': 'no votes with this word'})

    if len(ids) > 0:
        url2 = ANALIZE_URL + '/s/getVotesData/'+','.join(ids)
        resp = tryHard(url2).json()

    else:
        resp = []
    out_data = [None for i in range(rows)]
    for mot in resp:
        out_data[sort_ids.index(mot['results']['motion_id'])] = mot
    while None in out_data:
        out_data.remove(None)
    return JsonResponse(out_data, safe=False)


def dfALL(request):
    """
    * @api {get} dfall/
    * @apiGroup TFIDF
    * @apiDescription
    document frequerncy all

    search query in transcripts

    * @apiSuccess {Object[]} /
    * @apiSuccess {Integer} /.df
    * @apiSuccess {String} /.term

    * @apiExample {curl} Example:
        curl -i https://isci.parlameter.si/dfall/

    * @apiSuccessExample {json} Example response:
    [
        {
            "df": 79235,
            "term": "hvala"
        },
        {
            "df": 72746,
            "term": "in"
        },
        {
            "df": 72208,
            "term": "za"
        },
        {
            "df": 71292,
            "term": "je"
        },
        {
            "df": 70951,
            "term": "da"
        }
    ]
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


def index(request):
    return JsonResponse({'status': 'ok'})


def legislationQuery(request, words, start_page=None):
    rows = 50
    # solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'
    solr_url = SOLR_URL + '/select?wt=json'

    q = words.replace('+', ' ')

    q = remove_law_or_act(q)

    solr_params = {
        'q': '(content_t:' + q.replace('IN', 'AND').replace('!', '+')+') OR ('+'text_t:' + q.replace('IN', 'AND').replace('!', '+')+')',
        # 'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t text_t',
        'hl.fragmenter': 'regex',
        'hl.regex.pattern': '\w[^\.!\?]{1,600}[\.!\?]',
        'hl.fragsize': '5000',
        'hl.mergeContiguous': 'false',
        'hl.snippets': '1',
        'fq': 'tip_t:l',
        'rows': str(rows),
        'start': str(int(start_page) * rows) if start_page else '0',
    }

    # print q + 'asd'

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    # print url

    r = requests.get(url)
    return JsonResponse(r.json())
