#!/usr/bin/env python
#
# app.py - Example Wiredrive RSS reader Developer Test submission.
#
# Reference: https://github.com/byrondover/wiredrive_devtest

################################################################################
# User defined constants.

cdn = 'http://www.wdcdn.net/'
uri = 'rss/presentation/library/client/iowa/id/128b053b916ea1f7f20233e8a26bc45d'

################################################################################
# Establish runtime propriety.

from cStringIO import StringIO
from flask import Flask, render_template
from humanize import naturalsize
from multiprocessing import Pool
from werkzeug.contrib.cache import SimpleCache
import av
import feedparser
import requests
import time

app = Flask(__name__)
cache = SimpleCache()

################################################################################
# Function definitions.

def parse_metadata(entry):
  """
  Parses and formats metadata from video file headers. Returns a video metadata
  dictionary.
  """

  # Stream in first 164 KB of each file to parse metadata.
  data = requests.get(entry['media_content'][0]['url'], stream=True)
  asset = StringIO(data.raw.read(167936))

  # Parse video metadata with PyAV (ffmpeg wrapper).
  container = av.open(asset)
  stream = next(s for s in container.streams if s.type == 'video')

  # Add duration, video codec and bitrate values to video metadata dictionaries.
  # @NOTE: Requirement 2.
  minutes, seconds = divmod(stream.duration / 600, 60)

  entry['codec'] = stream.metadata['encoder']
  entry['duration'] = '%sm %ss' % (minutes, seconds)
  entry['bitrate'] = '{0:,} kb/s'.format(int(stream.bit_rate / 1024))

  # Determine smallest available thumbnail.
  # @NOTE: Requirement 3.
  entry['thumbnail'] = \
    sorted(entry['media_thumbnail'], key=lambda k: k['height'])[0]['url']

  # Beautify and populate.
  date = time.strftime('%l:%M%p on %A, %B %d, %Y', entry['published_parsed'])

  entry['client'] = \
    next(s['content'] for s in entry['media_credit'] if s['role'] == 'client')
  entry['credits'] = sorted(entry['media_credit'], key=lambda k: k['role'])
  entry['date'] = date.replace('AM', 'am').replace('PM', 'pm')
  entry['size'] = naturalsize(entry['media_content'][0]['filesize'])

  if len(entry['summary']) > 60:
    entry['summary'] = '<None>'

  return entry

def parse_rss_feed(url):
  """
  Parse RSS feed from URL argument, then distribute decoding operations to
  subprocesses. Returns a list of video metadata dictionaries.
  """

  # Parse RSS feed items into dictionaries.
  # @NOTE: Requirement 1.
  feed = feedparser.parse(url)

  # Parallelize fetches.
  parallelize = Pool(15)
  entries = parallelize.map(parse_metadata, feed['entries'])

  return entries

################################################################################
# Routes, views and main method.

@app.route('/')
def display_feed():
  """
  Fetch and render list of video metadata dictionaries in a web application, and
  attempt to cache the results.
  """

  data = cache.get('data')

  if data is None:
    data = sorted(parse_rss_feed(cdn + uri), key=lambda k: k['title'])
    cache.set('data', data, timeout=24 * 60 * 60)

  return render_template('index.html', data=data)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
