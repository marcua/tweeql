from urllib import urlretrieve
from threading import Thread
from os import path,getcwd

# Please replace this with your own key in a production environment!
API_KEY = 'ABQIAAAAtGw1MDAVWMO6QjAEb2-w_hQCULP4XOMyhPd8d_NrQQEO8sT8XBR4nl1tfW8GUiQ2uIWU8ASwZR6mXA'

OBSURL = 'http://www.weather.gov/data/current_obs/all_xml.zip'
WURL = 'http://www.weather.gov/data/current_obs/%s.xml'
BASE = path.dirname(__file__)
ZFILE = path.join(BASE,'all_xml.zip')

class Fetch(Thread):
    """Thread fetching"""
    def run(self):
        fetch()

def fetch(thread=False):
    """
    Fetch observation base to a zipfile
    @param thread: Runs fetch in a separate thread if True
    """
    if thread:
        Fetch.start()
    else:
        urlretrieve(OBSURL,ZFILE)

