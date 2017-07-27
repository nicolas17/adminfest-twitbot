#!/usr/bin/env python3

import configparser
import peewee
import datetime
import sys
import os
import jsonpickle
import json
import slackweb

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API, Cursor, Friendship
from tweepy.error import TweepError

from model import Tweet, User, BeerCode

import time


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

slack = slackweb.Slack(url=config['slack']['web_hook_url'])

# horrible
#while True:
#for n in range(1):
while True:
    time.sleep(1)

    #get 1 twtit to process from database
    try:
        #tweet = Tweet.select().where(Tweet.processed==False).get()
        tweet = Tweet.select().where((Tweet.processed == False) &
                                     (Tweet.process_try <= int(config['sysarmy']['max_beers']))).get()
    except Tweet.DoesNotExist:
        print("No more unprocessed tweets; sleeping...")
        time.sleep(10)
        print("try to resend stupid blocked dms.")
        try:
            tweet = Tweet.select().where((Tweet.processed == True) & (Tweet.dm == False) & (Tweet.beer_code != "RT")
                                         & (Tweet.beer_code != "QUOTA") & (Tweet.beer_code != "FUCK") & (Tweet.process_try < 10)).get()

            # SELECT TWTIT processed=1 and dm=0 and beer_code not in ("QUOTA","RT","FUCK")
            try:
                # TODO Activate this.
                # dm = api.send_direct_message(tweet.user_id, text=dm_text)
                print("Sending DM", tweet.beer_code, tweet.dm)
                tweet.dm = True
                tweet.process_try += 1
                tweet.save()
                message = "Assigned %s to %s for tweet %s" % (tweet.beer_code, tweet.user.user_str, tweet.text)
                slack.notify(text=message)
                tweet.save()
            except TweepError as e:
                # "You cannot send messages to users who are not following you."
                if e.api_code == 150:
                    # TODO: tell user to follow us
                    print('User cant get our DMs', tweet.user.id)
        except Tweet.DoesNotExist:
            print("no pending dms, good.")

        continue

    # TODO if tweet is RT, skip those are not valid.
    if tweet.retweet:
        print("this is a RT, discarding //", tweet.id, tweet.text)
        tweet.beer_code = "RT"
        tweet.processed = True
        tweet.save()
        continue


    #check if user had more than 3 beers
    if (tweet.user.beers < int(config['sysarmy']['max_beers'])):
        print ("Assign Beer to user", tweet.user.user_id, "beers used / limit", tweet.user.beers, int(config['sysarmy']['max_beers']))
        #  Get Free Beer Code or get the code we already assigned if this is a reprocess because of DM error.
        try:
            if tweet.beer_code is "":
                beer_code = BeerCode.select().where(BeerCode.used == False).get()
            else:
                beer_code = BeerCode.select().where(BeerCode.beer_code == beer_code).get()

        except BeerCode.DoesNotExist:
            beer_code = None

        #Fix this shit while getting beer_codes when there are none available it breaks.
        if beer_code is not None:
            #Assign beer code to tweet
            print("Beer Code ",beer_code.beer_code)
            tweet.beer_code=beer_code.beer_code
            tweet.process_try=+1

            #Try to send the message to the user
            #api.send_direct_message(18344450, 'code: ABC1234')
            dm_text = 'Fulano te regala una cerveza = %s :) // para devolverlo responde RETURN' % beer_code.beer_code

            # TODO: if the user doesn't follow us, but has open DMs, we *can* DM,
            # if success bla		 +        # but the message will appear in a separate tab and they may not see it.
            # Maybe we should send a public reply telling them to check their DMs.
            try:
                #dm = api.send_direct_message(tweet.user_id, text=dm_text)
                print("Sending DM")
                #raise TweepError('test', api_code=150)
                tweet.dm = True
                message = "Assigned %s to %s for tweet %s" % (tweet.beer_code, tweet.user.user_str, tweet.text)
                slack.notify(text=message)

            except TweepError as e:
                # "You cannot send messages to users who are not following you."
                if e.api_code == 150:
                    # TODO: tell user to follow us
                    print('User cant get our DMs', tweet.user.id)
                else:
                    raise

            # Add 1 beer to user
            tweet.user.beers += 1
            tweet.user.save()

            # Set beer code in tweet
            tweet.beer_code = beer_code.beer_code

            # Set process tries +1
            tweet.process_try += 1
            tweet.processed = True
            tweet.save()

            beer_code.user=tweet.user
            beer_code.timestamp=datetime.datetime.now()
            beer_code.used=True
            beer_code.save()
        else:
            print("Out of Beer", tweet.user.id)
            tweet.beer_code = "FUCK"
            tweet.process_try += 1
            tweet.processed = True
            tweet.save()

    else:
        print ("User Quota exceeded, dumping tweet", tweet.user.id)
        tweet.beer_code = "QUOTA"
        tweet.processed=True
        tweet.save()
