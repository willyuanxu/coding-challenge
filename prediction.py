from elasticsearch import Elasticsearch
from utils import emotion_list, round_emotion_profile


# aux function to help generate an empty emotion profile
def generate_empty_emotion_profile():
    emotion_profile = {}
    for emotion in emotion_list:
        emotion_profile[emotion] = 0
    return emotion_profile

# aux function to generate emotion profile from a particular elasticsearch query response
def generate_emotion_profile_from_response(response):
    # initialize emotion profile for this particular lyrical line
    emotion_profile = generate_empty_emotion_profile()

    emotion_scaler = 0  # for averaging out the result for this particular line of lyric
    response = response['hits']['hits']
    if len(response) == 0:
        return None
    # loop through all hits
    for hit in response:
        # add hit score to the scaler
        score = hit['_score']
        emotion_scaler += score

        # add emotion weighted emotion profile to the lyric line's emotion profile
        hit = hit['_source']['emotion_profile']
        for emotion in emotion_list:
            emotion_profile[emotion] += score * hit[emotion]
    for emotion in emotion_list:
        emotion_profile[emotion] /= emotion_scaler
    return emotion_profile


"""
emotion profile for one particular line of lyric is the weighted average of emotion profile
of top X query results, with the score of each hits as the weight 

emotion profile of whole song is the average of emotion profiles of each lyric line 
"""
def predict_with_search_relevance(lyrics):
    # initialize empty emotion profile
    emotion_profile = generate_empty_emotion_profile()

    # count how many lyric emotion profile are added
    counter = 0

    client = Elasticsearch()
    for lyric in lyrics:

        response = client.search(index="songs", body={
            "size": 5,
            "query": {
                "match": {"lrc.line": lyric}
            }
        })

        # generate emotion profile from response
        lyric_line_emotion_profile = generate_emotion_profile_from_response(response)
        if not lyric_line_emotion_profile:
            continue
        else:
            for emotion in emotion_list:
                emotion_profile[emotion] += lyric_line_emotion_profile[emotion]
            counter += 1

    # average out of all lyrical lines
    for emotion in emotion_list:
        emotion_profile[emotion] /= counter

    return round_emotion_profile(emotion_profile)

"""
generate an emotion profile with similar approach as predict_with_search_relevance, but instead 
use the entire song's lyrics in one query, then average the result out with the emotion profile 
returned from predict_with_search_relevance
"""
def predict_with_search_relevance_avg(lyrics):
    client = Elasticsearch()
    # make lyrics into one single line
    lyrics = " ".join(lyrics)
    response = client.search(index="songs", body={
        "size": 5,
        "query": {
            "match": {"lrc.line": lyrics}
        }
    })
    emotion_profile = generate_emotion_profile_from_response(response)
    emotion_profile_lyric = predict_with_search_relevance(lyrics)

    # there's the possibility that nothing returns from elasticsearch query
    if not emotion_profile:
        return emotion_profile_lyric

    for emotion in emotion_list:
        emotion_profile[emotion] = (emotion_profile[emotion] + emotion_profile_lyric[emotion]) / 2
    return emotion_profile










