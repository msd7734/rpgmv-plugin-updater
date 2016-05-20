import requests
import urllib
import re
import os
import md5
import sets

import plugin_fetcher as PF
from PluginManifest import PluginManifest
from PluginConfigParser import PluginConfigParser
from HashData import HashData

dropbox_url = "https://www.dropbox.com/s/{0}/{1}"

def dropbox_get(obj_id, obj_name):
    obj_id, obj_name = \
            map(urllib.quote_plus, [obj_id, obj_name])
    
    url = dropbox_url.format(obj_id, obj_name)
    dl = True   # if we don't set this, we'll get the browser view
    
    param = {"dl": int(dl)}
    r = requests.get(url, param, stream=True)
    with open(obj_name, 'wb') as fd:
        for chunk in r.iter_content():
            fd.write(chunk)

def pname_from_url(url):
    '''
    Get a plugin name extracted from a url.

    Args:
        url (str): A string containing a plugin name in the format
                    PluginName.js
    Returns:
        plugin name (str) or None if none found
    '''

    m = re.search('.*/(.+)\.js', url)
    if m:
        return m.group(1)
    else:
        return None

def match_wildcards(pdict, matchstr):
    '''
    From a dict of keys : wildcard patterns, return the key of
    the first pattern that matches the matchstr or None if no match.
    '''
    for p in pdict.keys():
        regex = pdict[p].replace('*', '*.')
        if re.match(regex, matchstr):
            return p
    return None

def get_plugin_mapping(cfgParser):
    '''
    Match canonical urls to active plugins from the manifest.

    Args:
        cfgParser (PluginConfigParser): An initialized config parser.
    Returns:
        dict{plugin_name(str) : update_url(str)}
    '''

    pm = PluginManifest(cfgParser.manifest)
    if pm.success == False:
        print "Could not find a valid plugins file at {0}.".format(pm.fname)
        return {}

    hrefParsers = {}

    result = {}
    
    plugins = pm.plugins
    
    for p in plugins:
        # if key is in cfg.plugins, get val
        # else if matches any cfg.batch, get val from that
        inCfg = p in cfgParser.plugin
        if inCfg == True:
            key = p
        else:
            # check match from wildcard strings
            key = match_wildcards(cfgParser.batch, p)
            if key:
                inCfg = True
            else:
                inCfg = False

        # if plugin from manifest found in cfg
        if inCfg:
            # update_url is direct match to plugin name
            update_url = cfgParser.plugin[key]
            # but if update_url is a root...
            if update_url in cfgParser.root:
                update_url = cfgParser.root[update_url]
                # ...parse it
                # but don't fetch same root multiple times
                if update_url in hrefParsers:
                    hrefParser = hrefParsers[update_url]
                else:
                    hrefParser = PF.fetch_root(update_url)
                    hrefParsers[update_url] = hrefParser
                    
                root_purls = PF.parse_root(hrefParser)
                
                # if we get back some valid resource urls...
                if root_purls:
                    # ...find first match to plugin name
                    try:
                        update_url = next(url for url in root_purls \
                                          if pname_from_url(url)==p)
                    except StopIteration as si:
                        update_url = None

            else:
                pass
                # print "Fetching from: {0}".format(update_url)
                
            if update_url:
                result[p] = update_url

    return result
                    

def get_local_hashes(plugins, path):
    '''
    Get the local md5 hashes of all given plugins.

    Args:
        plugins(List[str]): Plugin names w/o file extension.
        path: Path to plugin folder.
    Returns:
        Dictionary { PluginName(str) : MD5 digest(str) }
    '''
    
    result = {}
    for pname in plugins:
        fpath = os.path.join(path, pname+".js")
        try:
            with open(fpath, 'r') as f:
                data = f.read()
                data = unicode(data, 'utf-8').encode('utf-8')
                m = md5.new()
                m.update(data)
                result[pname] = m.digest()
        except IOError as ioe:
            # TODO: Make this MD5 = 0 so it always gets updated?
            # Well, technically written as a new file, not updated.
            print "Missing local plugin: {0}".format(\
                os.path.abspath(fpath))

    return result

    
def get_remote_data(plugin_map):
    '''
    Get the remote data and md5 hashes of all given plugins at mapped URLS.

    Args:
        plugin_map(Dict{ PluginName(str) : URL(str) })
    Returns:
        Dictionary { PluginName(str) : Data(HashData) }
    '''
    result = {}
    for pname in plugin_map.keys():
        data = PF.fetch_url(plugin_map[pname])
        # Everything is unicode!
        data = data.encode('utf-8')
        if data:
            m = md5.new(data)
            result[pname] = HashData(data, m.digest())
            pass
        else:
            print "Could not get {0} update: {1}".format(\
                pname, plugin_map[pname])
            
    return result

def write_data(data_map, dest):
    '''
    Write downloaded plugin data to plugin files.

    Args:
        data_map(Dict{ PluginName(str) : Data(HashData) })
        dest(String): Directory to write
    Returns:
        List of plugin names that could not be written.
    '''
    failed = []
    try:
        if os.path.exists(dest) == False:
            os.makedirs(dest)
    except:
        return data_map.keys()
    
    for plugin in data_map:
        with open(os.path.join(dest, plugin+".js"), 'w') as f:
            try:
                f.write(data_map[plugin].data)
            except IOError as ioe:
                failed.append(plugin)
    return failed

def set_difference(L1, L2):
    '''
    Return the set difference of two lists as a list.
    '''
    S1 = sets.Set(L1)
    S2 = sets.Set(L2)
    return list(S1.difference(S2))

def set_intersection(L1, L2):
    '''
    Return the set intersection of two lists as a list.
    '''
    S1 = sets.Set(L1)
    S2 = sets.Set(L2)
    return list(S1.intersection(S2))

cfgparser = PluginConfigParser()
# initialize config parser
print "Reading config file..."
valid = cfgparser.read('config.ini')
if valid:
    print "Reading plugin manifest ({0})...".format(cfgparser.manifest)
    plugin_map = get_plugin_mapping(cfgparser)
    if plugin_map:
        
        # get hashes for comparison
        print "Checking local plugins..."
        loc_hashes = get_local_hashes(plugin_map.keys(), \
                                      cfgparser.pluginsfolder)

        print "Checking remote plugins..."
        rem_hashdata = get_remote_data(plugin_map)
        print ""

        updatable = set_intersection(loc_hashes, rem_hashdata)
        hasNew = []

        for p in updatable:
            if loc_hashes[p] == rem_hashdata[p].md5Hash:
                print p + " is up to date."
            else:
                hasNew.append(p)
                print p + " has a new version."

        print ""

        if len(hasNew) == 0:
            print "No updates to be done."
        else:
            print "Update type: {0}\n".format(cfgparser.update)

            newData = {plugin:data for plugin,data \
                       in rem_hashdata.iteritems() \
                       if plugin in hasNew}
                
            if cfgparser.update == 'none':
                print "No updates to be done."
            else:
                writePath = ''
                if cfgparser.update == 'auto':
                    writePath = cfgparser.pluginsfolder
                elif cfgparser.update == 'save':
                    writePath = 'updates'
                else:
                    print "Unknown update type: {0}"\
                          .format(cfgparser.update)
                    print "Program will now exit."
                    sys.exit(0)

                failed = write_data(newData, writePath)
                for success in set_difference(newData, failed):
                    print "{0} was saved.".format(success)
                for f in failed:
                    print "The plugin {0} could not be written.".format(f)                 .format(f)
                
        
    else:
        print "No updatable plugins."
