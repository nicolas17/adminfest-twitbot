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

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_status(self, status):
        # aca levantar el status y encolarlo para el worker.
        print(status.id,' ', status.text)

        new_user, _ = User.get_or_create(user_id=status.user.id, user_str=status.user.screen_name, location=status.user.location, timezone=status.user.time_zone)
        try:
            tweet = Tweet.select().where(Tweet.status_id == status.id).get()
        except Tweet.DoesNotExist:
            tweet = None

        if tweet is not None:
            print("stream: already saved", status.user.id, status.id_str)
        else:
            new_twit = Tweet.create(user=new_user, status_id=status.id, retweet=hasattr(status, 'retweeted_status'), text=status.text,json=jsonpickle.encode(status._json, unpicklable=False))
            new_twit.save()
            print("stream: new ", status.user.id)

        return True

    def on_direct_messag(self, status):
        # def on_data(self, status):
        # TODO hay que monitorear inbox para aceptar RETURN de gente que no venga. O sino darle tickets a todos
        # TODO y hacer que la ticketera corte a las 200 consumisiones.
        # tambien podemos monitorear el inbox de DMs y otros estados.
        print(status)
        if 'CRITICAL' in status.text:
            # buscar al usuario y invalidarlo aumentando la cantidad de birra a 999
            new_user, _ = User.get_or_create(user_id=status.user.id, user_str=status.user.screen_name)
            new_user.beers = 999
            new_user.save()
            print("invalidated ", status.user.id)

    def on_error(self, status):
        print(status)

if __name__ == '__main__':

    # Faltaria hacer la parte de buscar para atras, y encolar en algo tipo previous_queue para que el worker decida si tiene que aceptarlos o no. en sucesivos runs el worker ya tiene en su db guardados los twits que proceso o skipeo para no reprocesarlos.
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    searchQuery = '%23downtime99999'

    # Maximum number of tweets we want to collect
    maxTweets = 1000000

    tweetCount = 0

    # Tell the Cursor method that we want to use the Search API (api.search)
    # Also tell Cursor our query, and the maximum number of tweets to return
    for status in Cursor(api.search, q=searchQuery).items(maxTweets):
        new_user, _ = User.get_or_create(user_id=status.user.id, user_str=status.user.screen_name, location=status.user.location, timezone=status.user.time_zone)
        try:
            tweet = Tweet.select().where(Tweet.status_id == status.id).get()
        except Tweet.DoesNotExist:
            tweet = None

        if tweet is not None:
            print("search: already saved", status.user.id, status.id_str)
        else:
            new_twit = Tweet.create(user=new_user, status_id=status.id, retweet=hasattr(status, 'retweeted_status'), text=status.text,json=jsonpickle.encode(status._json, unpicklable=False))
            new_twit.save()
            print("search: new ", status.user.id)

        # Write the JSON format to the text file, and add one to the number of tweets we've collected
        tweetCount += 1

    # Display how many tweets we have collected
    print("Downloaded {0} tweets".format(tweetCount))
    ##exit(0)
    # http://www.dealingdata.net/2016/07/23/PoGo-Series-Tweepy/
    print("Starting stream to db")
    stream = Stream(auth, l)
    try:

        stream.filter(track=['downtime99999'])
        #stream.filter(track=['bitch'])
    except(KeyboardInterrupt, SystemExit):
        stream.disconnect()
        print("Goodbye :)")