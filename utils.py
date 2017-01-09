import json
import redis
import pickle

# open up the config file
with open("config.json") as config:
    config = json.loads(config.read())


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
