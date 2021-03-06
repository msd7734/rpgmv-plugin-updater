import os.path
from ConfigParser import SafeConfigParser
from ConfigParser import NoSectionError

# to recreate behavior from ConfigParser
from collections import OrderedDict as _default_dict

req_sections = ['manifest', 'pluginsfolder', 'batch', 'plugin',\
                'update']

update_types = ['auto', 'save', 'none']

fail_read_msg = "Failed to read config file (expected \'{0}\')."
poor_frmt_msg = "Config file was poorly formatted (missing section \'{0}\')."

class PluginConfigParser(SafeConfigParser):
    def __init__(self, defaults=None, dict_type=_default_dict, \
                 allow_no_value=False):
        self.manifest = ''
        self.pluginsfolder = ''
        self.root = {}
        self.batch = {}
        self.plugin = {}
        self.update = ''
        
        SafeConfigParser.__init__(self, defaults, dict_type, allow_no_value)
        
        # the bizarre way to preserve key case-sensitvity...
        self.optionxform = str

    def read(self, filenames):
        '''
        Override standard read() to do validation and error reporting.
        '''
        success_list = SafeConfigParser.read(self, filenames)
        if not success_list:
            # Docs say filenames is a list, but it also accepts
            # a single string. So handle it like this to be safe... 
            if hasattr(filenames, '__iter__'):
                # we only want to read 1 config anyway
                print fail_read_msg.format(filenames[0])
            else:
                print fail_read_msg.format(filenames)
        else:
            s = ""
            try:
                # test config for expected sections
                for s in req_sections:
                    i = self.items(s)
                self._init_members()
            except NoSectionError as nse:
                print poor_frmt_msg.format(s)
                # make sure to return empty list to indicate failure
                return []
        
        return success_list

    def readfp(fp, filename=''):
        nie = NotImplementedError()
        nie.strerror = "readfp() is not supported in PluginConfigParser." \
        + "Use read() instead."
        raise nie

    def _init_members(self):
        self.manifest = self.get('manifest', 'Location')
        if self.manifest.lower() == 'default':
            self.manifest = 'js'
        self.manifest = os.path.join(self.manifest, 'plugins.js')

        self.pluginsfolder = self.get('pluginsfolder', 'Location')
        if self.pluginsfolder.lower() == 'default':
            self.pluginsfolder = 'js/plugins'

        # root is technically optional to the program functioning
        try:
            for r in self.items('root'):
                self.root[ r[0] ] = r[1]
        except NoSectionError as nse:
            pass

        for b in self.items('batch'):
            self.batch[ b[0] ] = b[1]

        for p in self.items('plugin'):
            self.plugin[ p[0] ] = p[1]

        self.update = self.get('update', 'Type')
        if not(self.update in update_types):
            self.update = "auto"
    
    def printall(self):
        print self.manifest
        print self.root
        print self.batch
        print self.plugin
