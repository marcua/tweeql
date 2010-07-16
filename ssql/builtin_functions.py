# -*- coding: utf-8 -*-

from ssql.field_descriptor import ReturnType
from ssql.function_registry import FunctionInformation
from ssql.function_registry import FunctionRegistry
from geopy import geocoders
from ordereddict import OrderedDict
from urllib2 import URLError

import math
import re
import sys

class Temperature():
    fahr = re.compile(ur"(^| )(\-?\d+([.,]\d+)?)\s*\u00B0?(F$|F |Fahr)", re.UNICODE)
    celcius = re.compile(ur"(^| )(\-?\d+([.,]\d+)?)\s*\u00B0?(C$|C |Celsius)", re.UNICODE)
    return_type = ReturnType.FLOAT

    @staticmethod
    def temperature_f(tuple_data, status):
        """ 
            Returns the temperature found in 'status' in Fahrenheit.  Captures
            both systems of temperature and then converts to Fahrenheit.
        """
        fahr_search = Temperature.fahr.search(status)
        temperature = None
        try:
            if fahr_search != None:
                temperature = fahr_search.group(2).replace(",", ".")
                temperature = float(temperature)
            else:
                celcius_search = Temperature.celcius.search(status)
                if celcius_search != None:
                    temperature = celcius_search.group(2).replace(",", ".")
                    temperature = float(temperature)
                    temperature = ((9.0/5) * temperature) + 32
        except ValueError:
            print "Encoding error on '%s'" % (status)
        return temperature

class Rounding():
    return_type = ReturnType.FLOAT

    @staticmethod
    def floor(tuple_data, val, nearest = 1):
        """ 
            Returns the largest integer multiple of 'nearest' that is less than or equal to val.
            If nearest is less than 1, you may see funny results because of floating 
            point arithmetic.
        """
        retval = val - (val % nearest) if val != None else None
        return retval

class Location:
    class LruDict(OrderedDict):
        def __setitem__(self, key, value):
            self.pop(key, None)
            OrderedDict.__setitem__(self, key, value)
        def compact_to_size(self, size):
            while len(self) > size:
                self.popitem(last=False)

    gn = geocoders.GeoNames()
    return_type = ReturnType.FLOAT
    LATLNG = "__LATLNG"
    LAT = "lat"
    LNG = "lng"
    cache = LruDict()

    @staticmethod
    def get_latlng(tuple_data, lat_or_long):
        if not Location.LATLNG in tuple_data:
            tuple_data[Location.LATLNG] = Location.extract_latlng(tuple_data)
        val = None
        if tuple_data[Location.LATLNG] != None:
            if lat_or_long == Location.LAT:
                val = tuple_data[Location.LATLNG][0]
            elif lat_or_long == Location.LNG:
                val = tuple_data[Location.LATLNG][1]
        return val
    
    @staticmethod
    def extract_latlng(tuple_data):
        latlng = None
        if tuple_data["coordinates"] != None:
            coords = tuple_data["coordinates"]["coordinates"]
            latlng = (coords[1], coords[0])
        if latlng == None:
            loc = tuple_data["user"].location
            if (loc != None) and (loc != ""):
                loc = loc.lower()
                latlng = Location.cache.get(loc, None)
                if latlng == None:
                    latlng = Location.geonames_latlng(loc)
                Location.cache[loc] = latlng
                Location.cache.compact_to_size(5000)
        return latlng

    @staticmethod
    def geonames_latlng(loc):
        latlng = None
        try:
            g = Location.gn.geocode(loc.encode('utf-8'), exactly_one=False)
            for place, (lat, lng) in g:
                latlng = (lat, lng)
                break
        except URLError:
            e = sys.exc_info()[1]
            print "Unable to connect to GeoNames: %s" % (e)
        return latlng

class NormalOutliers():
    return_type = ReturnType.FLOAT
    groups = dict()

    class StdGroup():
        def __init__(self):
            self.n = 0
            self.mean = 0.0
            self.M2 = 0.0
            self.ewma = 0.0
            self.stdev = 0.0
        def update_and_calculate(self, value):
            """
                Returns the number of standard deviations from the EWMA if
                the number of values previously recorded is >= 5.  Otherwise,
                returns -1.
                If the value is less than 2 standard deviations away, it will
                also update the value as if it is not an outlier.
            """
            retval = -1
            if self.n >= 5: # only calculate stdevs if collected > 5 data pts.
                diff = self.ewma - value
                if self.stdev > 0:
                    stdevs = diff/self.stdev
                else:
                    stdevs = diff/.00001
                retval = abs(stdevs)
            if retval <= 2: # only update if less than 2 stdevs or still collecting data
                self.n += 1
                delta = value - self.mean
                self.mean += delta/self.n
                self.M2 += delta*(value - self.mean)
                if self.n > 1:
                    self.stdev = math.sqrt(self.M2/(self.n - 1))
                    self.ewma = (.15*value) + (.85*self.ewma)
                else:
                    self.ewma = value
            return retval 

    @staticmethod
    def numstdevs(tuple_data, value, *group):
        """ 
            Calculates how many standard deviations from the 
            exponentially weighted moving average value 
            is, given the other values that have been 
            given for the elements of this group.

            The return value will be greater than or equal to 0 
            if it represents the number of standard deviations.
            If it is less than 0, the group does not have enough data to
            calculate standard deviations.
        """
        std_group = NormalOutliers.groups.get(group, None)
        if std_group == None:
            std_group = NormalOutliers.StdGroup()
            NormalOutliers.groups[group] = std_group

        return std_group.update_and_calculate(value)

class MeanOutliers():
    return_type = ReturnType.FLOAT
    groups = dict()

    class MeanGroup():
        def __init__(self):
            self.n = 0
            self.ewma = 0.0 # exponentially weighted moving avgerage
            self.ewmmd = 0.0 # exponentially weighted moving mean deviation
        def update_and_calculate(self, value):
            """
                Returns the number of mean deviations from the EWMA if
                the number of values previously recorded is >= 5.  Otherwise,
                returns -1.

                Updates the EWMA and EWMMD after calculating how many median deviations
                away the result is.
            """
            retval = -1
            diff = abs(self.ewma - value)
            if self.n >= 5: # only calculate meandevs if collected > 5 data pts.
                if self.ewmmd > 0:
                    meandevs = diff/self.ewmmd
                else:
                    meandevs = diff/.00001
                retval = meandevs
            
            # update ewma/ewmmd
            self.n += 1
            if self.n > 1:
                if self.n > 2:
                    self.ewmmd = (.125*diff) + (.875*self.ewmmd)
                else:
                    self.ewmmd = diff
                self.ewma = (.125*value) + (.875*self.ewma)
            else:
                self.ewma = value
            return retval 

    @staticmethod
    def nummeandevs(tuple_data, value, *group):
        """ 
            Calculates how many mean deviations from the exponentially 
            weighted moving average value is, given the other values that have been 
            given for the elements of this group.

            Uses the method TCP utilizes to estimate the round trip time 
            and mean deviation time of a potentially congested packet:
            http://tools.ietf.org/html/rfc2988

            The return value will be greater than or equal to 0 
            if it represents the number of mean deviations the value was away
            from the exponentially weighted moving average.
            If it is less than 0, the group does not have enough data to
            calculate mean deviations.

            What is a good outlier value?  If your data is normally distributed, then
            I experimentally found that 1 mean deviation is .8 standard deviations.
            For normally distributed data, 68% of values are within 1 standard
            deviation, 95% of values are within 2, and nearly 100% are within 3.
            Thus, 68% of values are within 1.25 mean deviations, 95% are within
            2.5 mean deviations, and almost 100% are within 3.75 mean deviations.
            A good mean deviation cutoff for legitimate values is thus in the range
            2.5-3.75.
        """
        mean_group = MeanOutliers.groups.get(group, None)
        if mean_group == None:
            mean_group = MeanOutliers.MeanGroup()
            MeanOutliers.groups[group] = mean_group

        return mean_group.update_and_calculate(value)

def register_default_functions():
    fr = FunctionRegistry()
    fr.register("temperatureF", FunctionInformation(Temperature.temperature_f, Temperature.return_type))
    fr.register("tweetLatLng", FunctionInformation(Location.get_latlng, Location.return_type))
    fr.register("floor", FunctionInformation(Rounding.floor, Rounding.return_type))
    fr.register("normalStdevs", FunctionInformation(NormalOutliers.numstdevs, NormalOutliers.return_type))
    fr.register("meanDevs", FunctionInformation(MeanOutliers.nummeandevs, MeanOutliers.return_type))
