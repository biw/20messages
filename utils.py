import json
import requests
import pymysql.cursors
import redis
import pickle

# open up the config file
with open("config.json") as config:
    config = json.loads(config.read())


def send_message(recipient_id, message_data):
    params = {
        "access_token": config["page_access_token"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": message_data
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)
    if r.status_code != 200:
        print("Status Code: '{0}'".format(r.status_code))
        print("Details: '{0}'".format(r.text))


def createDBConnection():
    return pymysql.connect(host=config["host"],
                           user=config["user"],
                           password=config["password"],
                           db=config["dbname"],
                           charset=config["charset"],
                           cursorclass=pymysql.cursors.DictCursor)


def set_redis(user_id, api_key):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    pickled_object = pickle.dumps(api_key)
    r.set(user_id, pickled_object)


def get_redis(user_id):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    un_user = r.get(user_id)
    print(type(un_user))

    if un_user == None:
        print("hit none")
        return None
    print("hit unpickeled")
    unpickled = pickle.loads(un_user)
    print("finished")
    return unpickled
