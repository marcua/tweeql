import os
import sys

settings_cache = None

def get_settings():
    global settings_cache
    if settings_cache == None:
        sys.path.insert(0, os.getcwd())
        try:
            import settings
        except ImportError, e:
            print "It looks like you don't have a settings.py with basic project settings."
            sys.exit(-1)
        settings_cache = settings
        sys.path.pop(0)
    return settings_cache
