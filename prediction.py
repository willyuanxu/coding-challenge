from elasticsearch import Elasticsearch
from utils import emotion_list, round_emotion_profile
from queue import Queue
from threading import Thread


# aux function to help generate an empty emotion profile
def generate_empty_emotion_profile():
    """
    :return: dict of emotion profile
    """
    emotion_profile = {}
    for emotion in emotion_list:
        emotion_profile[emotion] = 0
    return emotion_profile


# aux function to generate emotion profile from a particular elasticsearch query response
def generate_emotion_profile_from_response(response):
    """
    :param response: elasticsearch response
    :return:  dict of emotion profile
    """
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


def predict_with_search_relevance(lyrics):
    """
    emotion profile for one particular line of lyric is the weighted average of emotion profile
    of top X query results, with the score of each hits as the weight
        In this implementation X==5. if X is sufficiently large potentially need generate profile
        for each lyric line on a separate thread
    emotion profile of whole song is the average of emotion profiles of each lyric line
    :param lyrics: list[str] of lyrics
    :return: dict of emotion profile
    """

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



def predict_with_search_relevance_avg(lyrics):
    """
    generate an emotion profile with similar approach as predict_with_search_relevance, but instead
    use the entire song's lyrics in one query, then average the result out with the emotion profile
    returned from predict_with_search_relevance
    :param lyrics: list[str] of lyrics
    :return: dict of emotion profile
    """
    emotion_profile_lrc_que = Queue()  # use a queue to save response from thread
    # get emotion profile with first approach on a thread
    search_thread = Thread(target=lambda q, lrc: q.put(predict_with_search_relevance(lrc)),
                           args=(emotion_profile_lrc_que, lyrics))
    search_thread.start()

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

    search_thread.join()
    emotion_profile_lyric = emotion_profile_lrc_que.get()
    # there's the possibility that nothing returns from elasticsearch query
    if not emotion_profile:
        return emotion_profile_lyric

    for emotion in emotion_list:
        emotion_profile[emotion] = (emotion_profile[emotion] + emotion_profile_lyric[emotion]) / 2
    return emotion_profile










