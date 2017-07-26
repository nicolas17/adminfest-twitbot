#!/usr/bin/env python3

import configparser
import peewee
import datetime
import sys
import os
import jsonpickle
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API, Cursor, Friendship

from model import Tweet, User, BeerCode

import time


config = configparser.ConfigParser()
config.read('config.ini')

config = configparser.ConfigParser()
config.read('config.ini')

# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key = config['credentials']['consumer_key']
consumer_secret = config['credentials']['consumer_secret']

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token = config['credentials']['access_token']
access_token_secret = config['credentials']['access_token_secret']

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# horrible
#while True:
for n in range(1):
    #time.sleep(1)

    #get 1 twtit to process from database
    try:
        tweet = Tweet.select().where(Tweet.processed==False).get()
    except Tweet.DoesNotExist:
        tweet = None
        continue

    #if tweet is None:
    #    continue

    #check if user had more than 3 beers
    if (tweet.user.beers < int(config['sysarmy']['max_beers'])):
        print ("Assign Beer to user", tweet.user.user_id)
        #  Get Free Beer Code
        try:
            beer_code = BeerCode.select().where(BeerCode.used == False).get()
        except BeerCode.DoesNotExist:
            beer_code = None

        #Fix this shit while getting beer_codes when there are none available it breaks.
        if beer_code is not None:
            #Assign beer code to tweet
            tweet.beer_code=beer_code.beer_code
            tweet.process_try=+1

            #Try to send the message to the user
            #api.send_direct_message(18344450, 'code: ABC1234')
            dm_text = 'Beer Code = %s' % beer_code.beer_code
            friends = api.show_friendship(source_screen_name='sysarmy', target_id=tweet.user.user_id)


            print('Can DM?', friends)
            #re = api.send_direct_message('jedux',text=dm_text)

            #if success bla

            #if it fails bla bla bla
            tweet.user.beers += 1
            tweet.user.save()

            tweet.beer_code = beer_code.beer_code
            tweet.process_try += 1
            tweet.processed = True
            tweet.save()

            beer_code.user=tweet.user
            beer_code.timestamp=datetime.datetime.now()
            beer_code.used=True
            beer_code.save()
        else:
            print("Out of Beer")
            tweet.beer_code = "FUCK"
            tweet.process_try += 1
            tweet.processed = True
            tweet.save()


    else:
        print ("User Quota exceeded, dumping tweet")
        tweet.beer_code = "OVER QUOTA"
        tweet.processed=True
        tweet.save()
