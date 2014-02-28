from datetime import datetime
from StringIO import StringIO


def return_file(url, *args, **kwargs):
    """
    Translate a url into a known local file. Reduces the time that tests take
    to complete if they do network access. Replaces `urllib.urlopen`

    Inputs:
    :url: URL to be retrieved
    :args: Ignored
    :kwargs: Ignored

    Outputs:
    :file: File-like object
    """
    feed = False
    if 'feed/rss' in url:
        file_ = 'rss.rss'
        feed = True
    elif 'feed/json' in url:
        file_ = 'json.json'
        feed = True
    elif 'mcdonalds/careers/' in url or \
       url.endswith('?location=chicago&q=nurse'):
        file_ = 'careers.html'
    elif 'www.my.jobs/jobs' in url or 'www.my.jobs/search' in url:
        file_ = 'jobs.html'
    else:
        file_ = 'other'

    target = 'mysearches/tests/local/'
    target += file_

    if feed:
        contents = open(target).read() % \
            {'date': datetime.strftime(datetime.now(), "%c -0300")}
        stream = StringIO(contents)
    else:
        stream = open(target)

    return stream
