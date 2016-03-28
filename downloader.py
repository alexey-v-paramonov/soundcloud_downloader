#!/usr/bin/env python2
import os
import sys
import getopt
import urllib
import soundcloud
from dateutil import parser
from datetime import datetime, timedelta

# Default parameters
SC_USERNAME = "your username"
DAYS_N = 30
MIN_DURATION = 8  # Minutes
MAX_DURATION = 25  # Minutes

# Sound Cloud client ID
CLIENT_ID = "secret"

client = soundcloud.Client(client_id=CLIENT_ID)


def check_track(track):
    global DAYS_N, MIN_DURATION, MAX_DURATION
    created = parser.parse(track.created_at)
    date_N_days_ago = datetime.now(created.tzinfo) - timedelta(days=DAYS_N)
    return created >= date_N_days_ago and \
        track.duration >= MIN_DURATION*60000 and \
        track.duration <= MAX_DURATION*60000 and \
        hasattr(track, 'download_url')


def download_tracks(argv):
    global DAYS_N, MIN_DURATION, MAX_DURATION, SC_USERNAME
    try:
        opts, args = getopt.getopt(argv, "hd:i:a:l:", ["days=", "min_minutes=", "max_minutes=", "login="])
    except getopt.GetoptError:
        print 'downloader.py -d <number of days> -i <min track length in minutes> -a <max track length in minutes> -l <Sound Cloud login>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'downloader.py -d <number of days> -i <min track length in minutes> -a <max track length in minutes> -l <Sound Cloud login>'
            sys.exit()
        elif opt in ("-d", "--days"):
            DAYS_N = int(arg)
        elif opt in ("-i", "--min_minutes"):
            MIN_DURATION = int(arg)
        elif opt in ("-a", "--max_minutes"):
            MAX_DURATION = int(arg)
        elif opt in ("-l", "--login"):
            SC_USERNAME = arg

    download_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'download')
    if not os.path.exists(download_root):
        print "Creating download directory: {0}".format(download_root).encode('utf-8')
        try:
            os.mkdir(download_root)
        except Exception, e:
            print "Unable to create download directory: {0}".format(e.message)
            sys.exit(-1)

    try:
        sc_user = client.get('/resolve', url=u"http://soundcloud.com/{0}".format(SC_USERNAME))
    except Exception, e:
        print "Unable to resolve user {0}: {1}".format(SC_USERNAME, e.message)
        sys.exit(0)

    print sc_user.id

    print "Configuration: days: {0}, min_minutes: {1}, max_minutes: {2}, SC username: {3}".format(DAYS_N, MIN_DURATION, MAX_DURATION, SC_USERNAME)
    try:
        following = client.get("/users/{0}/followings".format(sc_user.id))
    except Exception, e:
        print "Unable to get a list of users who are followed by the user: {0}".format(e.message)
        sys.exit(-1)

    print "You are following {0} users".format(len(following.collection))
    for user in following.collection:
        uid = user.id
        print u"\n#########################\nFetching user: {0}".format(user.username).encode('utf-8')
        try:
            user_track = client.get("/users/{0}/tracks".format(uid))
        except Exception, e:
            print "Unable to get user tracks:".format(e.message)
            continue
        print u"User \"{0}\" has {1} tracks".format(user.username, len(user_track)).encode('utf-8')
        downloadable_tracks = filter(check_track, user_track)
        print "{0} of them will be downloaded".format(len(downloadable_tracks))
        n = 1
        for t in downloadable_tracks:
            print u"# Downloading file {0} of {1}: \"{2}\"".format(n, len(downloadable_tracks), t.title).encode('utf-8')
            url = "{0}?client_id={1}".format(t.download_url, CLIENT_ID)
            created = parser.parse(t.created_at).date().isoformat()
            user_dir = os.path.join(download_root, user.username)
            user_date_dir = os.path.join(user_dir, created)

            if not os.path.exists(user_dir):
                try:
                    os.mkdir(user_dir)
                except Exception, e:
                    print "Warning: Unable to create user download directory {0}: {1}".format(user_dir, e.message)
                    continue
            if not os.path.exists(user_date_dir):
                try:
                    os.mkdir(user_date_dir)
                except Exception, e:
                    print "Warning: Unable to create user download directory {0}: {1}".format(user_date_dir, e.message)
                    continue
            print t.user_id, t.user['id']
            continue
            target_fp = os.path.join(user_date_dir, u"{}.mp3".format(t.title).encode('utf-8'))
            if not os.path.exists(target_fp):
                urllib.urlretrieve (url, target_fp)
            else:
                print "Warning: file {} already exists".format(target_fp)
            n += 1

if __name__ == "__main__":
    download_tracks(sys.argv[1:])

