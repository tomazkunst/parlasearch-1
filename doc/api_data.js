define({ "api": [
  {
    "type": "get",
    "url": "q/{word}/{?start_page}",
    "title": "Search in transcripts and votes",
    "name": "regularQuery",
    "group": "Search",
    "description": "<p>words: word/words for search start_page: pager in results</p> <pre><code>search query in transcripts</code></pre>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "date",
            "optional": false,
            "field": "date",
            "description": "<p>Optional date.</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person",
            "description": "<p>MP's person object (comes with most calls).</p>"
          },
          {
            "group": "Success 200",
            "type": "Boolean",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.is_active",
            "description": "<p>Answer the question: Is this MP currently active?</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer[]",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.district",
            "description": "<p>List of Parladata ids for districts this person was elected in.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.name",
            "description": "<p>MP's full name.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.gov_id",
            "description": "<p>MP's id on www.dz-rs.si</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.gender",
            "description": "<p>MP's gender (f/m) used for grammar</p>"
          },
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.party",
            "description": "<p>This MP's standard party objects (comes with most calls).</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.party.acronym",
            "description": "<p>The MP's party's acronym.</p>"
          },
          {
            "group": "Success 200",
            "type": "Boolean",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.party.is_coalition",
            "description": "<p>Answers the question: Is this party in coalition with the government?</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.party.id",
            "description": "<p>This party's Parladata (organization) id.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.party.name",
            "description": "<p>The party's name.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.type",
            "description": "<p>The person's parlalize type. Always &quot;mp&quot; for MPs.</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.id",
            "description": "<p>The person's Parladata id.</p>"
          },
          {
            "group": "Success 200",
            "type": "Boolean",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.person.has_function",
            "description": "<p>Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).</p>"
          },
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "/.facet_counts.facet_fields.speaker_i.score",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "/.highlighting.person",
            "description": "<p>MP's person object (comes with most calls).</p>"
          },
          {
            "group": "Success 200",
            "type": "Boolean",
            "optional": false,
            "field": "/.highlighting.person.is_active",
            "description": "<p>Answer the question: Is this MP currently active?</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer[]",
            "optional": false,
            "field": "/.highlighting.person.district",
            "description": "<p>List of Parladata ids for districts this person was elected in.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.highlighting.person.name",
            "description": "<p>MP's full name.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.highlighting.person.gov_id",
            "description": "<p>MP's id on www.dz-rs.si</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.highlighting.person.gender",
            "description": "<p>MP's gender (f/m) used for grammar</p>"
          },
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "/.highlighting.person.party",
            "description": "<p>This MP's standard party objects (comes with most calls).</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.highlighting.person.party.acronym",
            "description": "<p>The MP's party's acronym.</p>"
          },
          {
            "group": "Success 200",
            "type": "Boolean",
            "optional": false,
            "field": "/.highlighting.person.party.is_coalition",
            "description": "<p>Answers the question: Is this party in coalition with the government?</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.highlighting.person.party.id",
            "description": "<p>This party's Parladata (organization) id.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.highlighting.person.party.name",
            "description": "<p>The party's name.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.highlighting.person.type",
            "description": "<p>The person's parlalize type. Always &quot;mp&quot; for MPs.</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.highlighting.person.id",
            "description": "<p>The person's Parladata id.</p>"
          },
          {
            "group": "Success 200",
            "type": "Boolean",
            "optional": false,
            "field": "/.highlighting.person.has_function",
            "description": "<p>Answers the question: Is this person the president or vice president of the national assembly (speaker of the house kind of thing).</p>"
          },
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "/.responseHeader",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.responseHeader.status",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.responseHeader.QTime",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "/.responseHeader.params",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.fq",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.rows",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Object[]",
            "optional": false,
            "field": "/.responseHeader.params.facet.field",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.facet.range.gap",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.wt",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.hl.snippets",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.facet.range.end",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.hl.regex.pattern",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.facet",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.q",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.start",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.facet.range",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.hl",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.hl.fragsize",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.hl.mergeContiguous",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.hl.fl",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.hl.fragmenter",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.responseHeader.params.facet.range.start",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "/.response",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.response.start",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.response.numFound",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Object[]",
            "optional": false,
            "field": "/.response.docs",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Object[]",
            "optional": false,
            "field": "/.response.docs.tip_t",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.response.docs.session_i",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.response.docs.party_i",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.response.docs.datetime_dt",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.response.docs.speaker_i",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Object[]",
            "optional": false,
            "field": "/.response.docs.content_t",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.response.docs._version_",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "/.response.docs.id",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "/.response.docs.org_i",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "Example response:",
          "content": "{\n    \"facet_counts\": {\n        \"facet_ranges\": {\n            \"datetime_dt\": {\n                \"start\": \"2014-01-01T00:00:00Z\",\n                \"counts\": [\n                    \"2014-01-01T00:00:00Z\",\n                    0,\n                    \"2014-02-01T00:00:00Z\",\n                    0,\n                    \"2014-03-01T00:00:00Z\",\n                    0\n                ],\n                \"end\": \"2014-03-01T00:00:00Z\",\n                \"gap\": \"+1MONTHS\"\n            }\n        },\n        \"facet_fields\": {\n            \"speaker_i\": [\n                {\n                    \"person\": {\n                        \"name\": \"Vinko Gorenak\",\n                        \"district\": [\n                            42\n                        ],\n                        \"gender\": \"m\",\n                        \"is_active\": false,\n                        \"party\": {\n                            \"acronym\": \"SDS\",\n                            \"id\": 5,\n                            \"is_coalition\": false,\n                            \"name\": \"PS Slovenska Demokratska Stranka\"\n                        },\n                        \"type\": \"mp\",\n                        \"id\": 25,\n                        \"gov_id\": \"P116\",\n                        \"has_function\": false\n                    },\n                    \"score\": 1\n                },\n                {\n                    \"person\": {\n                        \"name\": \"Matjaž Han\",\n                        \"district\": [\n                            13\n                        ],\n                        \"gender\": \"m\",\n                        \"is_active\": false,\n                        \"party\": {\n                            \"acronym\": \"SD\",\n                            \"id\": 7,\n                            \"is_coalition\": true,\n                            \"name\": \"PS Socialni Demokrati\"\n                        },\n                        \"type\": \"mp\",\n                        \"id\": 30,\n                        \"gov_id\": \"P018\",\n                        \"has_function\": false\n                    },\n                    \"score\": 1\n                }\n            ],\n            \"party_i\": [\n                \"5\",\n                2,\n                \"1\",\n                1,\n                \"7\",\n                1\n            ]\n        }\n    },\n    \"highlighting\": [\n        {\n            \"start_time\": \"2017-01-25T01:00:00\",\n            \"session_id\": 8940,\n            \"person\": {\n                \"name\": \"Marijan Pojbič\",\n                \"district\": [\n                    25\n                ],\n                \"gender\": \"m\",\n                \"is_active\": false,\n                \"party\": {\n                    \"acronym\": \"SDS\",\n                    \"id\": 5,\n                    \"is_coalition\": false,\n                    \"name\": \"PS Slovenska Demokratska Stranka\"\n                },\n                \"type\": \"mp\",\n                \"id\": 66,\n                \"gov_id\": \"P098\",\n                \"has_function\": false\n            },\n            \"content_t\": \"<em>Parlameter</em>.</em>\",\n            \"date\": \"2017-01-23\",\n            \"speech_id\": 893563,\n            \"order\": 1340\n        },\n        {\n            \"start_time\": \"2017-01-25T01:00:00\",\n            \"session_id\": 8940,\n            \"person\": {\n                \"name\": \"Janja Sluga\",\n                \"district\": [\n                    31\n                ],\n                \"gender\": \"f\",\n                \"is_active\": false,\n                \"party\": {\n                    \"acronym\": \"SMC\",\n                    \"id\": 1,\n                    \"is_coalition\": true,\n                    \"name\": \"PS Stranka modernega centra\"\n                },\n                \"type\": \"mp\",\n                \"id\": 73,\n                \"gov_id\": \"P284\",\n                \"has_function\": false\n            },\n            \"content_t\": \"ki se mu reče <em>parlameter</em> in ki se natančno vidi kaj kdo govori in kolikokrat se oglasi.</em>\",\n            \"date\": \"2017-01-23\",\n            \"speech_id\": 893561,\n            \"order\": 1320\n        }\n    ],\n    \"responseHeader\": {\n        \"status\": 0,\n        \"QTime\": 18,\n        \"params\": {\n            \"fq\": \"tip_t:govor\",\n            \"rows\": \"50\",\n            \"facet.field\": [\n                \"speaker_i\",\n                \"party_i\"\n            ],\n            \"facet.range.gap\": \"+1MONTHS\",\n            \"wt\": \"json\",\n            \"hl.snippets\": \"1\",\n            \"facet.range.end\": \"NOW\",\n            \"hl.regex.pattern\": \"\\\\w[^\\\\.!\\\\?]{1,600}[\\\\.!\\\\?]\",\n            \"facet\": \"true\",\n            \"q\": \"content_t:parlameter\",\n            \"start\": \"0\",\n            \"facet.range\": \"datetime_dt\",\n            \"hl\": \"true\",\n            \"hl.fragsize\": \"5000\",\n            \"hl.mergeContiguous\": \"false\",\n            \"hl.fl\": \"content_t\",\n            \"hl.fragmenter\": \"regex\",\n            \"facet.range.start\": \"2014-01-01T00:00:00.000Z\"\n        }\n    },\n    \"response\": {\n        \"start\": 0,\n        \"numFound\": 5,\n        \"docs\": [\n            {\n                \"tip_t\": [\n                    \"govor\"\n                ],\n                \"session_i\": 7654,\n                \"party_i\": 7,\n                \"datetime_dt\": \"2016-12-14T01:00:00Z\",\n                \"speaker_i\": 30,\n                \"content_t\": [\n                    \"Hvala lepa predsednik, ministrica, predlagatelji, predvsem predlagateljica danes Suzana si boš v parlametru popravila statistiko, tak da besedni zaklad se ti bo povečal, imela boš veliko izgovorjenih besed, ampak koroški dečki bodo pa še kar ostali tam kjer so. To je problem. Parlameter pa bo jutri statistiko tvojih nastopov pač ocenil kot dobro. \\nSedaj, jaz se ne bom ukvarjal z definicijo interpelacije. Dola leta sem poslanec, vem da je interpelacija orodja opozicije, da vem da ni pomembna vsebina, pomembne so besede, pomembni so nastopi, pomembni so televizijski kadri in pomembno je zbuditi v javnosti, da je v tej državi vse narobe. In, tako da, kar se tega tiče, je brezveze. Sedaj, problem pa je, kadar govorimo o interpelaciji, je pa vendarle malo problema ta vsebina. Sedaj bom tudi jaz kot neka papiga tukaj ponavljal, da pač izkoriščamo to tragedijo, ampak resnično tragedijo za to, da se politika sedaj med seboj obklada, se žali in še kaj več bi lahko našteval. To, gospe in gospodje, absolutno ni dobro. Mislim, da če ta dva fantka slučajno sta blizu televizije in slučajno prestavita televizijo, jaz upam, da gledata kaj lepšega, se bo take razprave, ki jih imamo danes, vtem fantkom sigurno usedle na dušo in jih bo ta duša spremljala celo življenje, ne samo tragedija, ki se je zgodila v njuni družini. In eno stvar vam pa povem. Ne družinski zakoni ne kakršnikoli zakoni, ne bo povrnil mamice tem dvema otrokoma in ne bo povrnil nekega dostojanstva in nekega srečnega otroštva tema dvema otrokoma. Saj je vse lepo in prav, zakoni da se pišejo, ampak še zmeraj zakone na nek način interpretiramo ljudje in ljudje v bistvu delajo ali pa delamo napake ali pa ne. \\nSedaj, naši ministrice se danes očita, kakor vsaj jaz razumem, to interpelacijo. Glavni očitek je, da je bila tisti dan na novinarski konferenci in se je odzvala na, bom rekel, na novinarski problem oziroma novinarsko zgodbo, ki se je pač takrat dogajala. Jaz sem tisoč procentov prepričan, to pa zaradi izkušenj, ki jih imamo kot politik, da če ministrica se takrat ne bi odzvala in ne bi bila na tisti novinarski konferenci, bi bil pogrom na ministrico isti kot je sedaj, samo da bi bila vsebina drugačna. Govorili bi o tem, da je sramota, da se minister ne odzove pri taki tragediji kot se je naredila in kako je to mogoče, da sedi v nekih lepih prostorih in nič ne reče. Isto bi bilo, dragi gospodje in gospe. Saj sem tudi jaz politik, saj bi jaz verjetno isto delal, če bi bil na vašem mestu, samo vam pa povem, da ne bi delal takih zgodb, ko bi imele osnovo tako tragedijo. Vse ostalo, zakoni, sociala, drugo, pa to je, gospe in gospodje, toliko prostora za demagogijo, saj smo slišali prej Združeno levico, čeprav meni moji strankarski kolegi rečejo, ne se ukvarjati z Združeno levico, ne jih kregati, itn., ampak to kar je Kordiš govoril, pa to še v Venezueli ni. Ne, ker v življenju moraš biti malo realen. Če bi jaz lahko danes odločal in če bi imel čarobno palico, jaz bi dal vsem delo in za to delo bi morali biti ljudje pošteno plačani in ne bi rabil nobeden nobene socialne pomoči. Ja, razen tistih, ki ne morejo dela opravljati, to so pa invalidi, ljudje ki so bolni, ljudje ki ne morejo, ampak poglejte, ne živimo v Indiji Koromandija, živimo v enem grdem svetu, kjer vemo da ima kakorkoli en procent človeštva vso bogastvo, bom rekel, na nek način akumulirano pri sebi. \\nSedaj pa še nekaj o eh koroških dečkih oziroma o tej zgodbi.    Nisem toliko razočaran, če politika zagrabi tako zgodbo, ker pač išče politične točke, pa išče ali se mu bo pokazalo tukaj na anketi v petek oziroma v ponedeljek. Bolj sem razočaran, ko odvetniki, ki nimajo kaj delati, najdejo tako zgodbo za svojo promocijo, zato da so lahko vsak dan na televiziji in zato, da lahko potem dobijo neke druge posle. Tega pa me je malo strah. In ta odvetnik, ki je bil nenazadnje tudi naš svetnik, slišal sem nekje na Koroškem ali celo podžupan, če si član neke socialdemokracije neke vrednote pač zagovarjaš, vloži in se potrudi v tej zgodbi vložiti 26 pritožb in 45 pravnih sredstev. Ampak gospe in gospodje, pa mi bomo imeli tu še 68 interpelacij na to temo, ker vsakič ko bo sodišče nekaj sprejelo, bo interpelacija. Saj tem otrokom in tej familiji se bo do konca zmešalo. Če je to otrokova korist, potem jaz ta trenutek sem res malo zmeden. \\nSedaj pa samo še eno veliko vprašanje in velik vprašaj. Verjamem, pa moram reči, ker Jožeta, sva že kar nekaj časa, ne bom rekel, da prijatelja, ker bodo rekli da…, ampak zelo dobra znanca. Sigurno je eden tistih ljudi, ki želi ljudem dobro. Tudi jaz. Pa verjetno v tej dvorani vsi. Pa dajmo eno vprašanje. Če ministrica sedajle odstopi, vi boste srečni, mi bomo razočarani. Ali bodo dečki prišli k starim staršem? Ali bodo starši pred božičem najbolj srečni otroci na tem svetu? Bodo? Če se bo to naredilo in če bi se to naredilo, da Anja odstopi, jaz jo grem sedaj prositi, Anja odstopi. Ne bo jo treba prositi. Anja bi to naredila takoj, če bodo zaradi tega za božič ti otroci, ti fantki srečni odpirali darila pod smrekico, se veselili v družinskem okolju. Se bodo? Ne bodo, ali ne. Sedajle mi gre kurja polt, ker vem, jaz bom srečen in vesel, ker se mi bo hčerka vrnila iz Portugalske, ker bomo lepo za božič skupaj, srečni doma. Ti dragi otroci, ti bogi otroci, fantki pa ne bodo. Ali bodo pri starih starših? Ali bodo pri rejnikih? Ni pomembno. Ti otroci so etiketirani. Sedaj je samo vprašanje kakšno etiketo jim bomo dali. In največjo etiketo, se opravičujem, in dajva politika, ki se v tej tragediji vsak dan znova in znova pogovarja samo zato, da bi spravili iz mesta eno Anjo Kopač Mrak. Včasih sem žalosten in razočaran. Hvala lepa.\"\n                ],\n                \"_version_\": 1568412779027628000,\n                \"id\": \"g1247808\",\n                \"org_i\": 95\n            },\n            {\n                \"tip_t\": [\n                    \"govor\"\n                ],\n                \"session_i\": 8940,\n                \"party_i\": 5,\n                \"datetime_dt\": \"2017-01-25T01:00:00Z\",\n                \"speaker_i\": 66,\n                \"content_t\": [\n                    \"Gospod podpredsednik, rad bi samo opozoril, da gospo Slugo opozorite, da zaradi tega, kar sem jaz govoril tukaj v parlamentu ne rabi biti tako bleda, ker ko poveš resnico o človeku potem pač ima težave človek in nastopi tako kot je ona zdaj nastopila, agresivno proti meni. Jaz nisem nič agresivno govoril. Jaz sem govoril zelo korektno, zelo pošteno in res je parlament. Kaj je že tista zgodba? Parlameter. Bodo ljudje videli kaj je kdo v tem državnem zboru govoril in še bolj pomembno ne kaj je govoril, pomembno je ali govori tisti, kar drži in kar je prav. In ne tisto, kar mu nekdo napiše, nek partijski sekretar. Meni nobeden ne piše govorov.\"\n                ],\n                \"_version_\": 1558596758970302500,\n                \"id\": \"g893563\",\n                \"org_i\": 95\n            }\n        ]\n    }\n}",
          "type": "json"
        }
      ]
    },
    "examples": [
      {
        "title": "Example:",
        "content": "curl -i https://isci.parlameter.si/q/parlameter",
        "type": "curl"
      }
    ],
    "version": "0.0.0",
    "filename": "./searchapi/views.py",
    "groupTitle": "Search"
  }
] });
