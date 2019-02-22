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

# define index structure with a geopoint
index_structure = {
  "mapping": {
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
              "analyzer": "standard"
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
          "analyzer": "standard"
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
    return x_coord, y_coord

def load_data():
    csv_file = open('data.csv', 'r')
    reader = csv.DictReader(csv_file)
    fields = reader.fieldnames
    # load all docs into a list
    jsons = []
    for row in reader:
        jsons.append({fields[i]: row[fields[i]] for i in range(len(fields))})

    # create index structure
    es = Elasticsearch()
    es.indices.create(index="songs", body=index_structure, ignore=400)

    # make lrc field json, assign emotion profile to each doc, and index the doc
    id_counter = 1
    for doc in jsons:
        doc['lrc'] = json.loads(doc['lrc'])
        emotion_profile =  generate_random_emotion_profile()
        doc['emotion_profile'] = emotion_profile
        x_coord, y_coord = calc_location(emotion_profile)
        doc['location'] = {
            "lat": x_coord,
            "lon": y_coord
        }
        res = es.index(index="songs", doc_type="doc", id=id_counter, body=doc)
        id_counter += 1




