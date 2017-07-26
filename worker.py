#!/usr/bin/env python3

import configparser
import peewee
import datetime
import sys
import os

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API, Cursor

from model import Tweet, User, BeerCode
from config import BotConfig

import time

config = BotConfig("config.ini")

# horrible
#while True:
for n in range(50):

    #get 1 twtit to process from database
    try:
        tweet = Tweet.select().where((Tweet.processed==False) & (Tweet.process_try <= config.max_beers())).get()
    except peewee.DoesNotExist:
        print("No more unprocessed tweets; sleeping...")
        time.sleep(5)
        continue

    print(tweet.user.user_id, "has ",tweet.user.beers," codes assigned")

    #check if user had more than 3 beers
    if (tweet.user.beers <= config.max_beers()):
        print ("Assign Beer to user")
        #Get Free Beer Code
        try:
            beer_code = BeerCode.get(BeerCode.used==False)
        except peewee.DoesNotExist:
            print("Out of beer!")
            break # this will quit the outer loop, so the tweet will not be saved and will remain with processed=False!

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
        print ("Quota exceeded")

    tweet.processed=True
    tweet.save()
