'''
Load media of users who you have liked their photos.
The data is stored in a Postgres database.

Python: 3.x
'''

import sys, time, os
import getpass
import psycopg2
import psycopg2.extras
from instagram.client import InstagramAPI

# ---------------------------------------------------------
#  Instagram Connection
# ---------------------------------------------------------

access_token = os.environ.get('ACCESS_TOKEN')
client_secret = os.environ.get('CLIENT_SECRET')
api = InstagramAPI(access_token=access_token, client_secret=client_secret)

# ---------------------------------------------------------
#  Postgres connection
# ---------------------------------------------------------
conn = psycopg2.connect("dbname=instagram_lda user=%s" % (getpass.getuser(), ))
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# ---------------------------------------------------------
#  1) get media I've liked
# ---------------------------------------------------------

def get_liked_media():
    media = []
    liked_media, next_ = api.user_liked_media()
    media.extend(liked_media)
    while next_:
        liked_media, next_ = api.user_liked_media(with_next_url=next_)
        media.extend(liked_media)
        print("Remaining API Calls: %s/%s" % (api.x_ratelimit_remaining, api.x_ratelimit))
    return media

liked_media = get_liked_media()

cur.execute("""DELETE FROM liked_media""")

for media in liked_media:
    cur.execute("""INSERT INTO liked_media(media_id, user_id) VALUES (%s, %s)""", (media.id, int(media.user.id)))

conn.commit()

# ---------------------------------------------------------
#  2) get user's latest posts for each photo I've liked
# ---------------------------------------------------------

def get_recent_media(user_id):
    media = []
    recent_media, next_ = api.user_recent_media(user_id=user_id)
    media.extend(recent_media)
    while next_ and len(media) < 200:
        recent_media, next_ = api.user_recent_media(with_next_url=next_)
        media.extend(recent_media)
        print("Remaining API Calls: %s/%s" % (api.x_ratelimit_remaining, api.x_ratelimit))
    return media


for media in liked_media:

    # only retrieve media for user if we don't have them in store already
    cur.execute("SELECT * FROM media WHERE user_id = %s", (media.user.id, ))
    twt = cur.fetchall()

    if len(twt) == 0:
        print("Remaining API Calls: %s/%s" % (api.x_ratelimit_remaining, api.x_ratelimit))
        recent_media = get_recent_media(media.user.id)

        text = ' '.join([(m.caption.text if m.caption else '') for m in recent_media])
        item = {
            'raw_text': text,
            'user_id': media.user.id,
            'n_media': len(recent_media),
            'username': recent_media[0].user.username,
        }


        print("Saving... %s" % (media.user.id, ))
        cur.execute("""INSERT INTO media(raw_text, user_id, n_media, username) VALUES (%(raw_text)s, %(user_id)s, %(n_media)s, %(username)s)""", item)

        conn.commit()
    else:
        print("Skipping... %s" % (media.user.id, ))

# ---------------------------------------------------------
#  check how many documents we now have in the Database
# ---------------------------------------------------------

cur.execute("SELECT * FROM media")
follower_docs = cur.fetchall()

records = [m['raw_text'] for m in follower_docs]
print("We have " + str(len(records)) + " records ")

n_media = sum([m['n_media']  for m in follower_docs if 'n_media' in m.keys()])
print("Total number of records: ", n_media)
print("On average #tweets per document: ", n_media / len(records))
