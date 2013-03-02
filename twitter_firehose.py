# First get tweetsream
# Second, you'll need to manually merge this guy's pull request to enable
# Oauth identification.

import ConfigParser

import tweetstream
import h5py
import pymongo
connection = pymongo.Connection()
db = connection.tweets

def get_connection_secrets(cfg_name):
    config = ConfigParser.ConfigParser()
    config.readfp(open(cfg_name))
    consumer_key = config.get("Oauth", "consumer_key")
    consumer_secret = config.get("Oauth", "consumer_secret")
    access_token = config.get("Oauth", "access_token")
    access_token_secret = config.get("Oauth", "access_token_secret")
    return (consumer_key, consumer_secret, access_token, access_token_secret)


if __name__ == "__main__":
    (consumer_key, consumer_secret,
     access_token, access_token_secret) = get_connection_secrets("oauth.cfg")
    words = ["sequester", "boehner", "sequestration", "obama",
             "fiscal cliff", "democrat", "republican", "compromise",
             "taxes", "deficit"]

    # sw corner first
    #dc_bbox = ["-77.401428", "38.751941", "-76.728516", "39.123668"]

    #with tweetstream.FilterStream(consumer_key, consumer_secret, access_token,
    #                              access_token_secret, track=words,
    #                              locations=dc_bbox) as stream:
    with tweetstream.FilterStream(consumer_key, consumer_secret, access_token,
                                  access_token_secret, track=words) as stream:
        for tweet in stream:
            db.tweets.save(tweet)
