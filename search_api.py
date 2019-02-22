from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

def search(emotion_profile):
    client = Elasticsearch()
    s = Search(using=client, index="songs")
    # specify match_all query and set size to max 100
    s.query("match_all")
    s = s[:100]

    params = {
                "anger": emotion_profile['anger'],
                "disgust": emotion_profile['disgust'],
                "sadness": emotion_profile['sadness'],
                "surprise": emotion_profile['surprise'],
                "fear": emotion_profile['fear'],
                "trust": emotion_profile['trust'],
                "joy": emotion_profile['joy'],
                "anticipation": emotion_profile['anticipation'],
            }

    # painless script for calculating sum of square error
    script_field = {
        "language": "painless",
        "source": """
            def sum_sq_err = 0; 
            for (entry in params.input.entrySet()) {
                sum_sq_err += Math.pow(doc['emotion_profile'][entry.getKey()] - entry.getValue()),2)
            }
            return sum_sq_err
        """,
        "params": {
            "input": params
        }
    }

    # sort field of query
    sort_field = {
        "_script": {
            "type": "number",
            "script": script_field,
            "order": "asc"
        }
    }

    s.sort(sort_field)
    response = s.execute()
    # print(response.hits.hits)
    for hit in response.hits.hits:
        profile = hit['_source']['emotion_profile']
        sum_sq_err = 0
        for key in params:
            sum_sq_err += (params[key] - profile[key])**2
        print(sum_sq_err)


search({"anger":40, "disgust": 20,"sadness": 10, "surprise": 90, "fear": 10, "trust": 40, "joy": 30, "anticipation": 10})
