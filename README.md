# soundcloud_downloader
A script for downloading Sound Cloud tracks for users that your follow

Setup:
Install all required python modules with

   pip install -r requirements.txt

(may require sudo)

Usage:
 * Open downloader.py and set your SoundCloud client ID and the username (SC_USERNAME, CLIENT_ID)

* Start the script with

    ./downloader.py --days=30 --minutes=8 --login=idontlikewords

    --days (-d): the number of days the track was published
    --minutes (-m): the minimal track length in minutes
    --login: SoundCloud username

By default the number of days is 30 and the minimal track length is 8 minutes.
