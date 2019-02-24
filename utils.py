from elasticsearch import Elasticsearch
import json
import csv
import random

emotion_list = ["anger", "disgust", "sadness", "surprise", "fear", "trust", "joy", "anticipation"]

# scaler for emotions 45 degree from axis
scaler = 1 / (2**0.5)
emotion_scaler = {
    "anger": (-1, 0),
    "disgust": (-scaler, -scaler),
    "sadness": (0, -1),
    "surprise": (scaler, -scaler),
    "fear": (1, 0),
    "trust": (scaler, scaler),
    "joy": (0, 1),
    "anticipation": (-scaler, scaler)
}

# define index structure
index_structure = {
  "mappings": {
    "doc": {
      "properties": {
        "artist": {
          "type": "text",
          "analyzer": "standard"
        },
        "duration": {
          "type": "float"
        },
        "location": {
          "type": "geo_point"
        },
        "emotion_profile": {
          "properties": {
            "anger": {
              "type": "integer"
            },
            "anticipation": {
              "type": "integer"
            },
            "disgust": {
              "type": "integer"
            },
            "fear": {
              "type": "integer"
            },
            "joy": {
              "type": "integer"
            },
            "sadness": {
              "type": "integer"
            },
            "surprise": {
              "type": "integer"
            },
            "trust": {
              "type": "integer"
            }
          }
        },
        "lrc": {
          "properties": {
            "line": {
              "type": "text",
              "analyzer": "english",
              "search_analyzer": "english"
            },
            "lrc_timestamp": {
              "type": "text"
            },
            "milliseconds": {
              "type": "text"
            }
          }
        },
        "title": {
          "type": "text",
          "analyzer": "english"
        }
      }
    }
  },
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  }
}

# create a random emotion profile in JSON format
def generate_random_emotion_profile():
    profile = {emotion_list[i]: random.randint(0,100) for i in range(len(emotion_list))}
    return profile

# calculate the location tuple given emotion profile
def calc_location(emotion_profile):
    x_coord, y_coord = 0, 0
    for emotion in emotion_list:
        x_scaler, y_scaler = emotion_scaler[emotion]
        x_coord += emotion_profile[emotion] * x_scaler
        y_coord += emotion_profile[emotion] * y_scaler
    return round(x_coord/2, 2), round(y_coord/2, 2)

def load_data(data):
    csv_file = open(data, 'r')
    reader = csv.DictReader(csv_file)
    fields = reader.fieldnames
    # load all docs into a list
    jsons = []
    for row in reader:
        jsons.append({fields[i]: row[fields[i]] for i in range(len(fields))})

    # create index structure
    es = Elasticsearch()
    es.indices.create(index='songs', body=index_structure, ignore=400)


    ##  and index the doc
    id_counter = 1
    for doc in jsons:
        # make lrc field json
        doc['lrc'] = json.loads(doc['lrc'])
        if id_counter != 99:
            # assign emotion profile to each doc
            emotion_profile = generate_random_emotion_profile()
            doc['emotion_profile'] = emotion_profile

            # assign coordinate to each doc
            x_coord, y_coord = calc_location(emotion_profile)
            doc['location'] = str(x_coord) + "," + str(y_coord)
            # index the doc
            res = es.index(index="songs", doc_type="doc", id=id_counter, body=doc)
            id_counter += 1
        else:
            print("data loaded")
            # save the last song for testing prediction
            return doc


# list L2 similarity score query response
def test_response(input, response):
    # print(response.hits.hits)
    for hit in response['hits']['hits']:
        profile = hit['_source']['emotion_profile']
        sum_sq_err = 0
        for key in input:
            sum_sq_err += (input[key] - profile[key]) ** 2
        print(sum_sq_err)

# round emotion profile to whole numbers
def round_emotion_profile(profile):
    for emotion in emotion_list:
        profile[emotion] = round(profile[emotion])
    return profile
