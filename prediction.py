from elasticsearch import Elasticsearch
from utils import emotion_list

"""
emotion profile for one particular line of lyric is the weighted average of emotion profile
of top X query results, with the score of each hits as the weight 

emotion profile of whole song is the average of emotion profiles of each lyric line 
"""

#
def predict_with_search_relevance(lyrics):
    # initialize empty emotion profile
    emotion_profile = {}

    # count how many lyric emotion profile are added
    counter = 0

    for emotion in emotion_list:
        emotion_profile[emotion] = 0

    client = Elasticsearch()
    for lyric in lyrics:
        # initialize emotion profile for this particular lyrical line
        lyric_line_emotion_profile = {}
        for emotion in emotion_list:
            lyric_line_emotion_profile[emotion] = 0

        response = client.search(index="songs", body={
            "size": 5,
            "query": {
                "match": {"lrc.line": lyric}
            }
        })

        emotion_scaler = 0  # for averaging out the result for this particular line of lyric
        response = response['hits']['hits']
        if len(response) == 0:
            continue
        # loop through all hits
        for hit in response:
            # add hit score to the scaler
            score = hit['_score']
            emotion_scaler += score

            # add emotion weighted emotion profile to the lyric line's emotion profile
            hit = hit['_source']['emotion_profile']
            for emotion in emotion_list:
                lyric_line_emotion_profile[emotion] += score * hit[emotion]
        for emotion in emotion_list:
            emotion_profile[emotion] += lyric_line_emotion_profile[emotion] / emotion_scaler
        counter += 1
    # average out of all lyrical lines
    for emotion in emotion_list:
        emotion_profile[emotion] /= counter
        emotion_profile[emotion] = round(emotion_profile[emotion])
    print(emotion_profile)





