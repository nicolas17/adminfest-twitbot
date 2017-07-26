#!/usr/bin/env python3

import configparser
import peewee
import datetime
import sys
import os
import jsonpickle

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API, Cursor

from model import Tweet, User, BeerCode

import time


config = configparser.ConfigParser()
config.read('config.ini')


# horrible
#while True:
for n in range(50):
    #time.sleep(1)

    #get 1 twtit to process from database
    tweet = Tweet.select().where(Tweet.processed==False & Tweet.process_try<=int(config['sysarmy']['max_beers'])).get()
    if tweet is None:
        break

    print(tweet.user.user_id, "has ",tweet.user.beers," codes assigned")

    #check if user had more than 3 beers
    if (tweet.user.beers <= int(config['sysarmy']['max_beers'])):
        print ("Assign Beer to user")
        #Get Free Beer Code
        beer_codes = BeerCode.select().where(BeerCode.used==False)
        #Fix this shit while getting beer_codes when there are none available it breaks.
        for beer_code in beer_codes:
            if beer_code is not None:
                #Assign beer code to tweet
                tweet.beer_code=beer_code.beer_code
                tweet.process_try=+1

                #Try to send the message to the user

                #if success bla

                #if it fails bla bla bla
                tweet.user.beers=+1
                tweet.user.save()

                beer_code.user=tweet.user
                beer_code.timestamp=datetime.datetime.now()
                beer_code.used=True
                beer_code.save()
            else:
                print("Out of Beer")
                tweet.beer_code = "FUCK"
                tweet.process_try = +1


    else:
        print ("Quota exceeded")

    tweet.processed=True
    tweet.save()
