import requests
import urllib
from HrefParser import HrefParser
from requestsutil import BadStatusException

def fetch_root(url, *args, **kwargs):
    '''
    Put the contents of a root page of plugins into a parser.

    Args:
        url (string): The URL of the page. May be a formattable string.
        *args: Values with which for format the URL string.
        **kwargs: Web request parameters
            ex. {'ref', True} -> http://example.com?ref=true

    Returns:
        HrefParser: Parser loaded with contents of the page.
    '''
    url = url.format(*args)
    try:
        r = requests.get(url, params=kwargs)
        if r.status_code != 200:
            bse = BadStatusException(r.status_code)
            raise bse
        parser = HrefParser(r.url)
        parser.feed(r.text)
    except requests.exceptions.RequestException as re:
        print "Request error {0}: {1}".format(re.errno, re.strerror)
        parser = None
        
    return parser

def parse_root(hrefParser):
    '''
    Get plugin URLs from a filled HrefParser

    Args:
        hrefParser (HrefParser): Parser to read from.

    Returns:
        List of all valid plugin resource URLs from parsed page links.
    '''
    if hrefParser.hrefs:
        return filter(lambda x: x[-3:]=='.js', hrefParser.hrefs)
    else:
        return []

def fetch_url(url, *args, **kwargs):
    url = url.format(*args)
    try:
        r = requests.get(url, params=kwargs)
        if r.status_code != 200:
            bse = BadStatusException(r.status_code)
            raise bse
        return r.text
    except requests.exceptions.RequestException as re:
        print "Request error {0}: {1}".format(re.errno, re.strerror)
        return ''
    
