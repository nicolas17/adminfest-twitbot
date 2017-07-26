
import configparser
from tweepy import OAuthHandler

class BotConfig:
    def __init__(self, path):
        self.config = configparser.ConfigParser()
        self.config.read(path)

        for key in ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']:
            if key not in self.config['credentials']:
                raise RuntimeError("Required setting %s not found in [credentials]" % key)

        for key in ['max_beers']:
            if key not in self.config['sysarmy']:
                raise RuntimeError("Required setting %s not found in [sysarmy]" % key)

    def get_tweepy_auth(self):
        consumer_key = self.config['credentials']['consumer_key']
        consumer_secret = self.config['credentials']['consumer_secret']

        access_token = self.config['credentials']['access_token']
        access_token_secret = self.config['credentials']['access_token_secret']

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        return auth

    def max_beers(self):
        return int(self.config['sysarmy']['max_beers'])
