"""
 ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <etiorum@gmail.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return. Paco Brevers
 * ----------------------------------------------------------------------------
"""

import configparser
import json
import os
import random
import safygiphy
import ssl
import time
import tweepy
from urllib.request import urlretrieve
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.exceptions import ReadTimeoutError

DOWNLOADED_IMAGE_PATH = "images/"

config = configparser.ConfigParser()
config.read('disculpemeBOT.config')

consumer_key = config.get('apikey', 'key')
consumer_secret = config.get('apikey', 'secret')
access_token = config.get('token', 'token')
access_token_secret = config.get('token', 'secret')
account_user_id = config.get('user', 'account_user_id')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

tags = ["perdon", "sorry", "pardon", "excuse me"]


class ReplyToTweet(tweepy.StreamListener):
    """ Twitter stream """

    def on_data(self, data):

        # print("DATA " + data)
        tweet = json.loads(data.strip())

        retweeted = tweet.get('retweeted', False)
        event = tweet.get('event', False)

        if 'screen_name' not in data or tweet.get('user', {}).get('screen_name', '') == account_user_id:
            from_self = True
        else:
            from_self = False

        if retweeted is not None and not retweeted and event is not None and not event and not from_self:
            tweet_id = tweet.get('id_str')
            screen_name = tweet.get('user', {}).get('screen_name', '')

            giphy = safygiphy.Giphy()
            gif = giphy.random(tag=random.choice(tags))
            img_url = gif['data']['fixed_height_downsampled_url']

            filename = img_url.split('/')[-1]

            urlretrieve(img_url, filename)

            reply_text = '@' + screen_name + " Ego te absolvo."

            if len(reply_text) > 140:
                reply_text = reply_text[0:137] + '...'

            api.update_with_media(filename, status=reply_text, in_reply_to_status_id=tweet_id)

            os.remove(filename)

    def on_error(self, status):
        print('STATUS: ' + status)


if __name__ == '__main__':

    while True:
        try:
            streamListener = ReplyToTweet()
            twitterStream = tweepy.Stream(auth, streamListener)

            twitterStream.userstream(_with='user')

        except (Timeout, ssl.SSLError, ReadTimeoutError, ConnectionError) as exc:
            print("Some kind of crash")
            time.sleep(180)
            continue
