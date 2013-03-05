# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# This notebook is available on github at [http://github.com/jseabold/web-scraping/](http://github.com/jseabold/web-scraping/)

# <headingcell level=4>

# Connecting to the Twitter Streaming API

# <markdowncell>

# * Twitter now provides access to its [Streaming API](https://dev.twitter.com/docs/streaming-apis)
# * The streaming API means you don't have to do any REST polling of an endpoing
# * Think of the streaming API like downloading a file of infinite length
# * You send one request, then open your mouth and drink from the firehose
# * Technically, the firehose is *all* of the tweets (or a good portion)
# * Twitter provides access to this on an as-needed basis (for cost, though academics likely get some leeway)
# * We will connect to the free "garden hose" or "spritzer" public API

# <headingcell level=4>

# A word on context managers

# <markdowncell>

# * Python (>= 2.5) provides a language construct called a "context manager"
# * Context managers allow you to write code that "does stuff" on entry and exit of a block of code
# * They make use of the `with` statement
# * Use of a context manager may look something like this

# <markdowncell>

#     with EXPRESSION [as VARIABLE]
#         BLOCK OF CODE

# <markdowncell>

# * A context manager can be implemented as a class
# * This class needs to define __enter__ and __exit__ methods
# * There are other ways to create context managers using the [contextlib](http://docs.python.org/2/library/contextlib.html) module and decorators
# * Let's look at an example

# <codecell>

from timeit import default_timer as timer

class Timer(object):
    def __enter__(self):
        self.tic = timer()
    
    def __exit__(self, exc_type, exc_value, traceback):
        # these arguments allow the exit to gracefully handle exceptions
        toc = timer()
        elapsed = (toc - self.tic)
        print "Code took %2.2f seconds to execute" % elapsed

# <codecell>

import numpy as np

with Timer():
    for i in range(10000):
        a = np.random.random(1000)
        b = a.sum()

# <markdowncell>

# * As you can imagine, context managers can be very powerful and useful
# * For example, I wrote a context manager manager to [text message](https://gist.github.com/jseabold/1291003) me when some code is done running

# <headingcell level=4>

# Twitter Streaming API using tweetstream

# <markdowncell>

# * [tweetstream](https://pypi.python.org/pypi/tweetstream) is a framework for working with the Twitter Streaming API
# * Since it is a framework it's not terribly flexible, but it will meet our needs
# * If you are interested in how it works, look at the source on their [bitbutcket repository](https://bitbucket.org/runeh/tweetstream/src)
# * **Note:** Twitter has recently moved exclusively to OAuth identification
# * As of the writing of this notebook (3/4/13) tweetstream did not support OAuth, but there is a pull request to do so
# * I merged that pull request locally before installing tweetstream to run this code
# * Let's see how to use tweetstream using their `FilterStream` class

# <codecell>

import tweetstream

# <markdowncell>

# * Say we were interested in what people are saying in DC right now
# * Define a bounding box as longitude, latitude pairs starting with the Southwest corner

# <codecell>

dc_bounding_box = ["-77.401428", "38.751941", "-76.728516", "39.123668"]

# <markdowncell>

# * Load OAuth configuration (go get your own!)

# <codecell>

import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open("oauth.cfg"))
consumer_key = config.get("Oauth", "consumer_key")
consumer_secret = config.get("Oauth", "consumer_secret")
access_token = config.get("Oauth", "access_token")
access_token_secret = config.get("Oauth", "access_token_secret")

# <codecell>

with tweetstream.FilterStream(consumer_key, consumer_secret, 
                              access_token, access_token_secret,
                              locations=dc_bounding_box) as stream:
    tweets = []
    for tweet in stream:
        tweets.append(tweet)
        print tweet["text"]
        if stream.count > 25:
            break

# <markdowncell>

# * In the repository for this talk, there is a file twitter_firestream.py
# * It uses filtered by keyword to see what the world thinks about the sequester
# * I ran it over the weekend of 3/1/13 when the sequest took place
# * It uses [MongoDB](http://www.mongodb.org/) and [pymongo](http://api.mongodb.org/python/current/) to store the tweets

