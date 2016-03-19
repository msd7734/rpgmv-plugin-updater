import requests
import urllib
import re

import plugin_fetcher as PF
from PluginManifest import PluginManifest
from PluginConfigParser import PluginConfigParser

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
                print "Fetching from: {0}".format(update_url)
                
            if update_url:
                result[p] = update_url

    return result
                    
    

cfgparser = PluginConfigParser()
# initialize config parser
valid = cfgparser.read('config.ini')
if valid:
    plugin_map = get_plugin_mapping(cfgparser)
    print "Found update resources for the following plugins:"
    for p in plugin_map.keys():
        print "\t" + p

'''
pm = PluginManifest('js/plugins.js')
if pm.success == False:
    print "Could not find the plugins.js file. Aborting."
else:
    for p in pm.plugins:
        print p
'''
