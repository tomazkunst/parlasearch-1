import requests

def enrichQuery(data):

    data['facet_counts'].pop('facet_heatmaps', None)
    data['facet_counts'].pop('facet_ranges', None)
    data['facet_counts'].pop('facet_queries', None)
    data['facet_counts'].pop('facet_intervals', None)

    results = []

    for i, speaker in enumerate(data['facet_counts']['facet_fields']['speaker_i']):
        if i % 2 == 0 and i < 10:
            results.append({'person': requests.get('https://analize.parlameter.si/v1/utils/getPersonData/' + speaker).json(), 'score': str(data['facet_counts']['facet_fields']['speaker_i'][i + 1])})
            del data['facet_counts']['facet_fields']['speaker_i'][i]
        else:
            del data['facet_counts']['facet_fields']['speaker_i'][i]

    data['facet_counts']['facet_fields']['speaker_i'] = sorted(results, key=lambda k: k['score'], reverse=True)

    enrichedData = data

    return enrichedData
