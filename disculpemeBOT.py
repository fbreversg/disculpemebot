import configparser
import json
import random
import tweepy
import safygiphy

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

        print("DATA " + data)
        tweet = json.loads(data.strip())

        retweeted = tweet.get('retweeted', False)

        if 'screen_name' not in data or tweet.get('user', {}).get('screen_name', '') == account_user_id:
            from_self = True
        else:
            from_self = False

        if retweeted is not None and not retweeted and not from_self:

            tweet_id = tweet.get('id_str')
            screen_name = tweet.get('user', {}).get('screen_name', '')

            giphy = safygiphy.Giphy()
            gif = giphy.random(tag=random.choice(tags))
            chat_response = gif['data']['image_url']

            reply_text = '@' + screen_name + ' ' + chat_response

            if len(reply_text) > 140:
                reply_text = reply_text[0:137] + '...'

            api.update_status(reply_text, tweet_id)

    def on_error(self, status):
        print('STATUS: ' + status)

if __name__ == '__main__':
    streamListener = ReplyToTweet()
    twitterStream = tweepy.Stream(auth, streamListener)
    twitterStream.userstream(_with='user')
