# -*- coding: utf-8 -*-

from ssql.field_descriptor import ReturnType
from ssql.function_registry import FunctionInformation
from ssql.function_registry import FunctionRegistry
from geopy import geocoders
from ordereddict import OrderedDict
from urllib2 import URLError

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

def register_default_functions():
    fr = FunctionRegistry()
    fr.register("temperatureF", FunctionInformation(Temperature.temperature_f, Temperature.return_type))
    fr.register("tweetLatLng", FunctionInformation(Location.get_latlng, Location.return_type))
