'''
This script retrieves the tweets of all followers of a given twitter account.
The data is stored in a MongoDB store.

The twitter and MongoDB credentials are stored in a cfg file

Python: 3.4
'''

import sys, time
import psycopg2
import psycopg2.extras
from twython import Twython, TwythonRateLimitError, TwythonAuthError

# This function allows us to check the remaining statuses and applications
# limits imposed by twitter.
# When the app_status or the timeline_status is exhausted, forces a wait
# for the period indicated by twitter
def handle_rate_limiting():
    # prepopulating this to make the first 'if' check fail
    app_status = {'remaining':1}
    while True:
        if app_status['remaining'] > 0:
            status = twitter.get_application_rate_limit_status(resources =
                                                    ['statuses', 'application'])
            status = status['resources']
            app_status = status['application']['/application/rate_limit_status']
            timeline_status = status['statuses']['/statuses/user_timeline']
            if timeline_status['remaining'] == 0:
                wait = max(timeline_status['reset'] - time.time(), 0) + 1
                time.sleep(wait)
            else:
                return
        else:
            wait = max(app_status['reset'] - time.time(), 0) + 10
            time.sleep(wait)

# ---------------------------------------------------------
#  Twitter Connection
# ---------------------------------------------------------

APP_KEY      = 't9q9gpzY7fUmpQZYZR7TMYj9t'
APP_SECRET   = 'Rjd5ul0FGhXvFvyVbRIiSpodkpDjmNWy6uedjmyjLDfBQvt0h4'

twitter     = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter     = Twython(APP_KEY, access_token=ACCESS_TOKEN)

# ---------------------------------------------------------
#  MongoDB connection
# ---------------------------------------------------------
conn = psycopg2.connect("dbname=twitter")
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

screen_name  = 'RESPEKT_CZ'     # The main twitter account
n_max_folwrs = 700          # The number of followers to consider

# ---------------------------------------------------------
#  1) get follower ids
#  see https://dev.twitter.com/rest/reference/get/followers/ids
# ---------------------------------------------------------
flwrs   = twitter.get_followers_ids(screen_name = screen_name,
                                    count = n_max_folwrs)
flw_ids = flwrs['ids']
flw_ids.sort()

# ---------------------------------------------------------
#  Get 200 tweets per follower
#  (200 is the maximum number of tweets imposed by twitter)
# ---------------------------------------------------------

cur.execute("""DELETE FROM followers""")

for id in flw_ids:
    cur.execute("""INSERT INTO followers(id) VALUES (%s)""", (id, ))
    try:
        print("[Log] loading:", id)

        handle_rate_limiting()
        params = {'user_id': id, 'count': 200, 'contributor_details': 'true' }
        try:
            tl = twitter.get_user_timeline(**params)
        except TwythonAuthError as e:
            pass
        # aggregate tweets
        text = ' '.join( [tw['text'] for tw in tl])

        if len(tl) == 0:
            continue

        try:
            item = {
                'raw_text': text,
                'user_id': id,
                'n_tweets': len(tl),
                'screen_name': tl[0]['user']['screen_name'],
                'lang': tl[0]['lang'],
            }
        except Exception as e:
            print("[Exception Raised] Eror constructing entity, skipping. %s", e)
            continue


        cur.execute("SELECT n_tweets FROM tweets WHERE user_id = %s", (id, ))
        twt = cur.fetchall()

        if len(twt) == 0:
            # store document
            cur.execute("""INSERT INTO tweets(raw_text,user_id,n_tweets,screen_name,lang) VALUES (%(raw_text)s, %(user_id)s, %(n_tweets)s, %(screen_name)s, %(lang)s)""", item)
        else:
            # update the record
            cur.execute("""UPDATE tweets SET raw_text=%(raw_text)s, n_tweets=%(n_tweets)s, screen_name=%(screen_name)s, lang=%(lang)s WHERE user_id=%(user_id)s""", item)
            print("replaced id ", tl[0]['user']['screen_name'], id, len(tl), tl[0]['lang'])


    except TwythonRateLimitError as e:
        # Wait if we hit the Rate limit
        reset = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
        wait = max(reset - time.time(), 0) + 10 # addding 10 second pad
        print("[Exception Raised] Rate limit exceeded waiting: %s", wait)
        time.sleep(wait)

conn.commit()

# ---------------------------------------------------------
#  check how many documents we now have in the Database
# ---------------------------------------------------------

cur.execute("SELECT * FROM tweets")
follower_docs = cur.fetchall()

documents = [tw['raw_text'] for tw in follower_docs]
print("We have " + str(len(documents)) + " documents ")

n_tweets = sum([tw['n_tweets']  for tw in follower_docs if 'n_tweets' in tw.keys()])
print("Total number of tweets: ", n_tweets)
print("On average #tweets per document: ", n_tweets / len(documents))
