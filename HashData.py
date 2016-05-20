'''
Simple data holder for getting a plugin's remote data
and storing its hash with it. This is to prevent multiple
remote requests.
'''
class HashData():
    def __init__(self, data, md5Hash):
        self.data = data
        self.md5Hash = md5Hash
