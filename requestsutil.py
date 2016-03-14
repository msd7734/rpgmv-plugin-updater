from requests import RequestException

__STATMSG__ = "The request returned a failure status {0}"

class BadStatusException(RequestException):
    def __init__(self, status, *args, **kwargs):
        RequestException.__init__(self, args, kwargs)
        self.strerror = __STATMSG__.format(status)
