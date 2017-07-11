#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tweepy import Cursor, OAuthHandler, API
from tweepy.error import TweepError
from random import choice
from localsettings import AUTH_DATA
import time

# Used to switch between tokens to avoid exceeding rates
class APIHandler(object):
    """docstring for APIHandler"""
    def __init__(self, auth_data, max_nreqs=10):
        self.auth_data = auth_data
        self.index = choice(range(len(auth_data)))
        self.max_nreqs = max_nreqs
        self.get_fresh_connection()

    def conn(self):
        if self.nreqs == self.max_nreqs:
            self.get_fresh_connection()
        else:
            # print("Continuing with API Credentials #%d" % self.index)
            self.nreqs += 1
        return self.conn_

    def get_fresh_connection(self):
        success = False
        while not success:
            try:
                self.index = (self.index + 1) % len(self.auth_data)
                d = self.auth_data[self.index]
                print "Switching to API Credentials #%d" % self.index
                auth = OAuthHandler(d['consumer_key'], d['consumer_secret'])
                auth.set_access_token(d['access_token'], d['access_token_secret'])
                self.conn_ = API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
                self.nreqs = 0
                return self.conn_
            except TweepError, e:
                print("Error trying to connect: %s" % e.message)
                time.sleep(10)

    def traer_seguidores(self, **kwargs):
        retries = 0
        fids = []
        c = Cursor(self.conn().followers_ids, count=5000, **kwargs).pages()
        while True:
            try:
                fids += c.next()
            except TweepError, e:
                if not 'rate limit' in e.reason.lower():
                    raise e
                if retries == 3:
                    raise TweepError(reason='retries exceeeded')
                else:
                    nmins = 15
                    print e
                    print "Rate limit reached. Waiting %d mins..." % nmins
                    print "fetched %d followers so far." % len(fids)
                    time.sleep(60 * nmins)
                    retries += 1
            except StopIteration:
                break
        return fids

API_HANDLER = APIHandler(AUTH_DATA)