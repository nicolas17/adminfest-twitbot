#!/usr/bin/env python3

import configparser
import peewee
import datetime
import sys
import os

from tweepy import API
from tweepy.error import TweepError

from model import Tweet, User, BeerCode
from config import BotConfig

import time

config = BotConfig("config.ini")

auth = config.get_tweepy_auth()
api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

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
        # TODO: if the user doesn't follow us, but has open DMs, we *can* DM,
        # but the message will appear in a separate tab and they may not see it.
        # Maybe we should send a public reply telling them to check their DMs.
        try:
            dm = api.send_direct_message(tweet.user_id, text="Test message")
        except TweepError as e:
            # "You cannot send messages to users who are not following you."
            if e.api_code == 150:
                # TODO: tell user to follow us
                pass
            else:
                raise

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
