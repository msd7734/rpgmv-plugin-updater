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

# dropbox_get("uzfxvvp17ypb1tb", "YEP_CoreEngine.js")

def yanfly_get():
    url = "http://yanfly.moe/plugins/en"
    root = PF.fetch_root(url)
    if root:
        plugin_urls = PF.parse_root(root)
    else:
        plugin_urls = []
    for u in plugin_urls:
        print u

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
        return None

    result = {}
    
    plugins = pm.plugins
    for p in plugins:
        # if key is in cfg.plugins, get val
        # else if matches any cfg.batch, get val from that
        if p in cfgParser.plugin:
            key = p
            pass
        else:
            # check match from wildcard strings
            key = match_wildcards(cfgParser.batch, p)

        if key and key in cfgParser.plugin:
            update_url = cfgParser.plugin[key]
            if update_url in cfgParser.root:
                update_url = cfgParser.root[update_url]

            result[p] = update_url

    return result
                    
    

cfgparser = PluginConfigParser()
# initialize config parser
valid = cfgparser.read('config.ini')
if valid:
    plugin_map = get_plugin_mapping(cfgparser)
    print plugin_map

'''
pm = PluginManifest('js/plugins.js')
if pm.success == False:
    print "Could not find the plugins.js file. Aborting."
else:
    for p in pm.plugins:
        print p
'''
