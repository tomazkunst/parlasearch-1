import requests

def enrichQuery(data):

    data['facet_counts'].pop('facet_heatmaps', None)
    data['facet_counts'].pop('facet_ranges', None)
    data['facet_counts'].pop('facet_queries', None)
    data['facet_counts'].pop('facet_intervals', None)

    results = []

    for i, speaker in enumerate(data['facet_counts']['facet_fields']['speaker_i']):
        if i % 2 == 0 and i < 10:
            try:
                results.append({'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + str(speaker)).json(), 'score': str(data['facet_counts']['facet_fields']['speaker_i'][i + 1])})
                del data['facet_counts']['facet_fields']['speaker_i'][i]
            except ValueError:
                results.append({'person': {'party': {'acronym': 'unknown', 'id': 'unknown', 'name': 'unknown'}, 'name': 'unknown', 'gov_id': 'unknown', 'id': speaker}, 'score': str(data['facet_counts']['facet_fields']['speaker_i'][i + 1])})
                del data['facet_counts']['facet_fields']['speaker_i'][i]
        else:
            del data['facet_counts']['facet_fields']['speaker_i'][i]

    data['facet_counts']['facet_fields']['speaker_i'] = sorted(results, key=lambda k: k['score'], reverse=True)

    enrichedData = data

    return enrichedData

def enrichHighlights(data):

    results = []

    for i, highlight in enumerate(data['highlighting']):

        hkey = data['highlighting'].keys()[i]
        speechdata = requests.get('https://data.parlameter.si/v1/getSpeechData/' + hkey.split('g')[1]).json()

        try:
            results.append({'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + str(speechdata['speaker_id'])).json(), 'content_t': data['highlighting'][hkey]['content_t'], 'date': speechdata['date']})
        except ValueError:
            results.append({'person': {'party': {'acronym': 'unknown', 'id': 'unknown', 'name': 'unknown'}, 'name': 'unknown', 'gov_id': 'unknown', 'id': speechdata['speaker_id']}, 'content_t': data['highlighting'][hkey]['content_t'], 'date': speechdata['date']})

    data['highlighting'] = results

    enrichedData = data

    return enrichedData
