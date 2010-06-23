# -*- coding: utf-8 -*-

from ssql.function_registry import FunctionRegistry
from geopy import geocoders

import re

class Temperature():
    fahr = re.compile(ur"(\-?\d+(\.\d+)?)\s*\u00B0?F", re.UNICODE)
    celcius = re.compile(ur"(\-?\d+(\.\d+)?)\s*\u00B0?C", re.UNICODE)

    @staticmethod
    def temperature_f(tuple_data, status):
        """ 
            Returns the temperature found in 'status' in Fahrenheit.  Captures
            both systems of temperature and then converts to Fahrenheit.
        """
        fahr_search = Temperature.fahr.search(status)
        temperature = None
        if fahr_search != None:
            temperature = float(fahr_search.group(1))
        else:
            celcius_search = Temperature.celcius.search(status)
            if celcius_search != None:
                temperature = float(celcius_search.group(1))
                temperature = ((9.0/5) * temperature) + 32
        return temperature

class Location:
    gn = geocoders.GeoNames()
    @staticmethod
    def get_latlng(tuple_data, *args):
        retval = None
        if tuple_data["coordinates"] != None:
            coords = tuple_data["coordinates"]["coordinates"]
            retval = (coords[1], coords[0])
        if retval == None:
            loc = tuple_data["user"].location
            if (loc != None) and (loc != ""):
                g = Location.gn.geocode(loc.encode('utf-8'), exactly_one=False)
                for place, (lat, lng) in g:
                    retval = (lat, lng)
                    break 
        return retval

def register():
    fr = FunctionRegistry()
    fr.register("temperatureF", Temperature.temperature_f)
    fr.register("tweetLatLng", Location.get_latlng)
