import csv
import zipfile
import os
from math import *
from Weather.globals import *

rows = lambda: csv.reader(open(path.join(BASE,'data','station-locations.csv')).readlines())

def calcDist(lat_A, long_A, lat_B, long_B):
    """from http://zips.sourceforge.net/#dist_calc"""
    distance = (sin(radians(lat_A)) *
        sin(radians(lat_B)) +
        cos(radians(lat_A)) *
        cos(radians(lat_B)) *
        cos(radians(long_A - long_B)))
    return (degrees(acos(distance))) * 69.09

class Miner:
    """
    Class to mine weather data from NOAA against zipcode database
    creates the CSVs for the *2station methods
    Still runs in O(N^2 +some) and NEVER SHOUD YOU TRY TO RUN
    Unless you have a really fast computer and have lots of time
    This class generates the station-locations.csv which should be in distro
    """
    def __init__(self):
        if os.path.isfile(ZFILE):
            fname = path.join(BASE,'data','station-locations.csv')
            self.writer = csv.writer(open(fname,'w'))
            file = zipfile.ZipFile(ZFILE,'r')
            for name in file.namelist():
                if name.endswith('index.xml'):
                    self.write(file.read(name))
                    break
        else:
            fetch()
            self.__init__()

    def write(self, data):
        """
        Simple, scrappy XML parsing
        """
        strip = lambda t: t.split('>')[1].split('<')[0]
        for l in data.splitlines():
            if l.find('station_id')>-1:
                sid = strip(l)
            elif l.find('latitude')>-1:
                la = float(strip(l))
            elif l.find('longitude')>-1:
                self.ugly(sid, sa, la, float(strip(l)), na)
            elif l.find('state')>-1:
                sa = strip(l)
            elif l.find('station_name')>-1:
                na = strip(l)

    def ugly(self, *args):
        # the best could not get any worse
        best = 99999999

        sid,ss,lat,lon,d = args[:5]

        # zips.csv from http://sourceforge.net/projects/zips/
        for row2 in csv.reader(open(path.join(BASE,'data','zips.csv')).readlines()[1:]):
            z,s,la,lo,c,sl = map(lambda x: x.replace('"','').strip(), row2)
            la,lo = float(la),float(lo)
            # distance from station to zip lat&long
            dist = calcDist(lat,lon,la,lo)
            if dist < best:
                best = dist
                t = (sid,d,lat,lon,c,s,z,dist)
        self.writer.writerow(t)

if __name__ == '__main__':
    if not path.isfile(path.join(BASE,'data','station-locations.csv')):
        Miner()
    from Weather.stats import DistStats
    print DistStats()