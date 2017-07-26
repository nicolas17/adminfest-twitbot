#!/usr/bin/env python3

# vim: nospell
import logging
import multiprocessing as mp
from configparser import ConfigParser
import tweepy as tw

logger = logging.getLogger(__name__)


def get_config(filename):
    """
    Get configuration info
    """
    try:
        config = ConfigParser()
        config.read(filename)
    except Exception as e:
        logger.error('Fail to load config from %s', filename)
        logger.error('Exception: %s', type(e))
        logger.error('Exception msg: %s', e.message)
    return config


class TwitterApi(object):
    """
    Twitter auth info
    """

    def __init__(self, config):
        self._config = config
        # Auth and set the internal API object:
        self._auth = tw.OAuthHandler(
            self._config['credentials']['consumer_key'],
            self._config['credentials']['consumer_secret'])
        self._auth.set_access_token(
            self._config['credentials']['access_token'],
            self._config['credentials']['access_token_secret'])
        self._api = tw.API(self._auth)

    @property
    def auth(self):
        return self._auth

    @property
    def api(self):
        return self._api

    def reauth(self, config=None):
        if config is not None:
            self._config = config
        self._auth = tw.OAuthHandler(
            self._config['credentials']['consumer_key'],
            self._config['credentials']['consumer_secret'])
        self._auth.set_access_token(
            self._config['credentials']['access_token'],
            self._config['credentials']['access_token_secret'])
        return self._api


class TwStreamListener(tw.StreamListener):

    def on_connect(self):
        logger.error('TwStreamListener object requires that define this func!')

    def on_status(self, status):
        logger.error('TwStreamListener object requires that define this func!')

    def on_error(self, status_code):
        logger.error('TwStreamListener object requires that define this func!')

    def on_disconnect(self, notice):
        logger.error('TwStreamListener object requires that define this func!')


class TwitterStreamer(object):
    """
    Stream from the Twitter.
    """

    def __init__(self, twauth):
        self._twauth = twauth
        self._stream_listener = TwStreamListener()
        self._stream_listener.on_connect = self._on_status
        self._stream_listener.on_status = self._on_status
        self._stream_listener.on_error = self._on_error
        self._stream_listener.on_disconnect = self._on_disconnect
        self._stream = tw.Stream(auth=twauth.auth,
                                 listener=self._stream_listener)

    def _on_connect(self):
        logger.info('Connected!')

    def _on_status(self, status):
        logger.debug('Status Received: %s', status)

    def _on_error(self, status_code):
        logger.error('Receive an error - %i', status_code)

    def _on_disconnect(self, notice):
        logger.info('Disconnected! - %s', notice)

    def stream(self, **kwargs):
        """
        Start to stream!, receive the same params that you can use
        with Stream.filter()
        """
        self._stream.filter(kwargs)


class TwitterDeEmer(object):
    """
    Send DMs, try to fix if can't do it
    """
    def __init__(self, twauth):
        self._twauth = twauth
        self._can_DM = OrderedDict()

    def _check_DM(self, user):
        return self._twauth.api.exist_friendship('@sysarmy', user)

    def _fix_DM_issue(self, user):
        """
        Try to fix the DM issue alerting the other part to follow us back
        """
        status = self.api.update_status("""Hey! {} seguime para pasarte x DM """
                                        """codigo!""".format(user))
        # NOTE: If we go multiprocess we can wait and _check_DM again.

    def send_DM(self, user, code):
        able2DM = False
        if user not in self._can_DM:
            able2DM = self._check_DM(user)
            self._can_DM [user]=(able2DM, 1)
        if not self._can_DM[user][0]:
            if self._can_DM[user][1]>3:
                return None
            able2DM = self._fix_DM_issue(qlixed)
            self._can_DM[user] = (able2DM, self._can_DM[user][1]+1)
            if not able2DM:  # TODO: Think how to free the beer code to reuse
                return None
        return self._twauth.api.send_direct_message(user,
                                             'Borrachin code: {code}'.format(code))
