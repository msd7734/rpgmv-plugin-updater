from urlparse import urljoin
from HTMLParser import HTMLParser


class HrefParser(HTMLParser):
    '''
    HrefParser > HTMLParser
    Get absolute/canonical urls of all anchors in HTML text fed
    through the parser.

    Attributes:
        url (string): url to resolve anchors against, generally
            the url of the page the HTML is sourced from.

            hrefs (list): Absolute urls from <a> tag hrefs attributes.
    '''

    def __init__(self, url):
        self.url = url
        self.hrefs = []
        HTMLParser.__init__(self)
    
    def __extract_href(self, attrs):
        f = filter(lambda x: x[0] == 'href', attrs)
        m = map(lambda x: x[1], f)
        if not m:
            return None
        else:
            return m[0]
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            h = self.__extract_href(attrs)
            if h:
                resolve = urljoin(self.url, h)
                self.hrefs.append(resolve)
