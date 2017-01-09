import json
import redis
import pickle

# open up the config file
try:
    with open("config.json") as config:
        config = json.loads(config.read())
except:
    print("you need to copy 'config.json.example' to a new 'config.json' file")
    quit()


def set_redis(user_id, api_key):
    r = redis.StrictRedis(host=config["redis_host"], port=config[
                          "redis_port"], db=config["redis_db"])

    pickled_object = pickle.dumps(api_key)
    r.set(user_id, pickled_object)


def get_redis(user_id):
    r = redis.StrictRedis(host=config["redis_host"], port=config[
                          "redis_port"], db=config["redis_db"])

    un_user = r.get(user_id)

    if un_user == None:
        return None

    unpickled = pickle.loads(un_user)
    return unpickled
