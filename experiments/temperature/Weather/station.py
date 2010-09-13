import os
import zipfile
from sgmllib import SGMLParser
from UserDict import UserDict
from urllib import urlopen,quote
from datetime import datetime
from Weather.data import rows
from Weather.globals import *

class Station(SGMLParser,UserDict):
    """
    SGMLParser and dictionary for NOAA XML weather data by station name

    @param station: The NOAA station identifier to search, eg KMTN
    @param force: Boolean for whether an update should be forced
    """
    def __init__(self, station):
        SGMLParser.__init__(self)
        UserDict.__init__(self)
        self.tag = None
        self.station = station.upper()
        self.update()

    def update(self, live=False):
        self.data = {}
        # csv update
        keys = ('latitude','longitude','city','state','zipcode')
        for row in rows():
            if self.station == row[0]:
                UserDict.update(self, dict(zip(keys,row[2:-1])))
                break
        if not self.data:
            raise AttributeError,'Station %s not found'%self.station
        # sgmllib update
        self.reset()
        if os.path.isfile(ZFILE) and not live:
            zfile = zipfile.ZipFile(ZFILE,'r')
            for name in zfile.namelist():
                if name.endswith('%s.xml'%self.station):
                    SGMLParser.feed(self, zfile.read(name))
                    del zfile
                    break
        else:
            #Fetch().start()
            SGMLParser.feed(self, urlopen(WURL%self.station).read())
        self.close()


    def unknown_starttag(self, tag, attrs):
        self.tag = tag
        self.data[tag] = None

    def handle_data(self, text):
        text = text.rstrip()
        if self.tag and text:
            if text in ('None','NA') or not text:
                value = None
            else:
                try: value = float(text)
                except ValueError:
                    try: value = int(text)
                    except ValueError:
                        value = str(text)
            self.data[self.tag] = value

    def datetime(self):
        """
        Parses and returns the observation datetime object (if possible)
        """
        if 'observation_time_rfc822' in self.data \
           and self.data['observation_time_rfc822']:
            tstr = self.data['observation_time_rfc822']
            tstr = ' '.join(tstr.split(' ')[:-2])
            return datetime.strptime(tstr, '%a, %d %b %Y %H:%M:%S')
        elif 'observation_time' in self.data:
            return datetime.strptime(self.data['observation_time'] \
                +' %s'%datetime.now().year,
                'Last Updated on %b %d, %H:%M %p %Z %Y')
        return ''


    def icon(self):
        """
        Returns URL of weather icon if it exists
        """
        try:
            return self.data['icon_url_base']+self.data['icon_url_name']
        except KeyError:
            return ''

    def location(self):
        """
        Returns location string usually in `StationName,State` format
        """
        try:
            return self.data['location']
        except KeyError:
            return self.data['station_name']

    def pprint(self):
        """
        Pretty print the weather items (for debugging)
        """
        for i in self.items():
            print '%s => %r'%i

    def __repr__(self):
        return '<Weather.Station %s>'%self

    def __str__(self):
        return '%s: %s'%(self.station,self.location())

def stations():
    """
    Returns iterator of station tuples
    """
    for row in rows():
        yield tuple(row)

def state2stations(state):
    """
    Translate a state identifier (ie DC) into a list of
    Station tuples from that state
    """
    state = state[:2].upper()
    for row in rows():
        if row[5]==state:
            yield tuple(row)

def location2station(location):
    """
    Translate full location into Station tuple by closest match
    Locations can be in any Google friendly form like
    "State St, Troy, NY", "2nd st & State St, Troy, NY" and "7 State St, Troy, NY"
    """
    # just forget it, use google
    location = quote(str(location))
    geo_url = 'http://maps.google.com/maps/geo?key=%s&q=%s&sensor=false&output=csv'%(API_KEY,location)
    point = map(float,urlopen(geo_url).readline().split(',')[-2:])
    best,result = 99999999,[]
    for row in rows():
        test_point = map(float, (row[2],row[3]))
        distance = ((test_point[0]-point[0])**2 + (test_point[1]-point[1])**2)**.5
        if distance < best:
            best,result = distance,row
    return tuple(result)

if __name__ == '__main__':
    print Station('KMTN')
    print location2station('Baltimore, MD')
    print location2station(21204)
    print location2station('Dulaney Valley rd, towson MD')
    print len([x for x in stations()])