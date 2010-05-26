# -*- coding: utf-8 -*-

from ssql.function_registry import FunctionRegistry

import re

class Temperature():
    fahr = re.compile(ur"(\d+(\.\d+)?)\s*\u00B0F", re.UNICODE)
    celcius = re.compile(ur"(\d+(\.\d+)?)\s*\u00B0C", re.UNICODE)

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

class User:
    @staticmethod
    def get_location(tuple_data):
        return tuple_data["location"]

def register():
    fr = FunctionRegistry()
    fr.register("temperatureF", Temperature.temperature_f)
    fr.register("userLocation", User.get_location)
