import time
import json
import httplib

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from header import consumer_key, consumer_secret
from header import access_token, access_token_secret
from streamScript.domain.send_data import execute_query


req_tok_url = 'https://api.twitter.com/oauth/request_token'
oauth_url = 'https://api.twitter.com/oauth/authorize'
acc_tok_url = 'https://api.twitter.com/oauth/access_token'


def get_data(json_data):
    language = json_data.get('lang', None)
    location = json_data.get('geo', None)
    place = json_data.get('place', None)
    country_code = None
    if place:
        country_code = place.get('country_code', None)
    if location and (language == 'en') and (country_code == 'US'):
        location = location.get('coordinates', None)
        screen_name = json_data.get('user', None).get('screen_name', None)
        text = json_data.get('text', None)
        location_lat = location[0]
        location_lng = location[1]
        created_at = json_data.get('created_at', None)
        try:
            hashtags = [i['text'] for i in json_data.get(
                'entities', None).get('hashtags', None)]
        except AttributeError:
            # print "I HAD THIS ERROR"
            return
        data_list = (
            screen_name, text, location_lat, location_lng, created_at, hashtags
        )
        return data_list
    else:
        return None


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    # This is a basic listener that just prints received tweets to stdout.

    """
    def __init__(self):
        self.start_time = time.clock()

    def on_data(self, data):
        json_data = json.loads(data)
        data_list = get_data(json_data)
        if data_list:
            sql = """INSERT INTO "Tweet" (screen_name, text,
                location_lat, location_lng, created_at, hashtags)
                VALUES (%s, %s, %s, %s, %s, %s); """
            execute_query(sql, data_list)
            print "Sending to database..."

    def on_error(self, status):
        if status == 420:
            time.sleep(15)
            print "Too many applications using these credentials."
            print '*' * 20

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    # print "Streaming..."
    while True:
        try:
            stream.filter(locations=[
                -124.848974, 24.396308, -66.885444, 49.384358,
                -150.011947, 61.040969, -149.6861, 61.234443,
                -157.966444, 21.255358, -157.663132, 21.373863])
        except httplib.IncompleteRead:
            pass
