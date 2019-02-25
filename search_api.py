from elasticsearch import Elasticsearch, TransportError
from elasticsearch_dsl import Search
from utils import calc_location

# this implementation does not work as it causes runtime error on elasticsearch
def search_with_L2_norm(emotion_profile):
    """
    :param emotion_profile: dict of emotion profile
    :return: elasticsearch response
    """

    # painless script for calculating sum of square error
    script_field = {
        "lang": "painless",
        "source": """
            def sum_sq_err = 0; 
            for (entry in params.input.entrySet()) {
                sum_sq_err += Math.pow(ctx._source['emotion_profile'][entry.getKey()] - entry.getValue(),2)
            }
            return sum_sq_err
        """,
        "params": {
            "input": emotion_profile
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

    client = Elasticsearch()
    s = Search(using=client, index="songs").sort(sort_field)
    # specify match_all query and set size to max 100
    s.query("match_all")
    s = s[:100]

    try:
        response = s.execute()
        return response
    except TransportError as e:
        print(e.info)
        exit()


# using geo_id as a way to search
def search_with_geodistance(emotion_profile):
    """
    :param emotion_profile: dict of emotion profile
    :return: elasticsearch response
    """
    # sort field of query
    query_x, query_y = calc_location(emotion_profile)
    sort_field = {
        "_geo_distance": {
            "location": {
                "lat": query_x,
                "lon": query_y
            },
            "order": "asc",
            "unit": "km",
            "distance_type": "plane"
        }
    }
    client = Elasticsearch()
    s = Search(using=client, index="songs").sort(sort_field)
    # specify match_all query and set size to max 100
    s.query("match_all")
    s = s[:100]
    try:
        response = s.execute()
        return response 
    except TransportError as e:
        print(e.info)
        exit()
