from utils import load_data, test_response
import search_api

load_data()
profile = {"anger": 40, "disgust": 20, "sadness": 10, "surprise": 90, "fear": 10, "trust": 40, "joy": 30, "anticipation": 10}
# search_api.search_with_L2_norm(profile)
response = search_api.search_with_geodistance(profile)
test_response(profile, response)