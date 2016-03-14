import json
import re
import os.path

class PluginManifest():
    def __init__(self, fname):
        self.fname = fname
        self.plugins = []
        self.success = False

        # read file containing javascript
        try:
            with open(self.fname, 'r') as manifest:
                data = manifest.read()
                j = json.loads(self.__parse_js(data)[0])
                for plugin in j:
                    self.plugins.append(plugin['name'])

            self.success = True
        except IOError as ioe:
            print "Could not open plugin manifest {0}: {1}".format(\
                os.path.abspath(fname), \
                ioe.strerror)
            

    def __parse_js(self, s):
        return re.findall('var.*?=\s*(.*?);', s, re.DOTALL | re.MULTILINE)
        
        
