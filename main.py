from utils import load_data, test_response, round_emotion_profile
import search_api
from elasticsearch import Elasticsearch
import prediction

# load data into elasticsearch, return the last song for testing prediction
predict_doc = load_data('data.csv')

# make sure the data is fully loaded
client = Elasticsearch()
while not client.indices.exists(index="songs"): pass
while not client.count(index="songs")['count'] == 98: pass

# searching
profile = {"anger": 40, "disgust": 20, "sadness": 10, "surprise": 90, "fear": 10, "trust": 40, "joy": 30, "anticipation": 10}
# search_api.search_with_L2_norm(profile)
response = search_api.search_with_geodistance(profile)
# test_response(profile, response)  # uncomment this test to see the L2 norm scores for response

# predicting
lyrics = [line['line'] for line in predict_doc['lrc']]
pred_profile = prediction.predict_with_search_relevance(lyrics)
print(round_emotion_profile(pred_profile))

pred_profile_avg = prediction.predict_with_search_relevance_avg(lyrics)
print(round_emotion_profile(pred_profile_avg))