# -*- coding: utf-8 -*-
import tweeql.builtin_functions
import random
from tweeql.builtin_functions import MeanOutliers
from tweeql.builtin_functions import NormalOutliers

if __name__ == "__main__":
#    print(tweeql.builtin_functions.Temperature.temperature_f(None, u"Adelaide: Tue 25 May 3:30 AM - Rain Shower -  Temp. 13.0\u00B0C RH 100% Wind SW (230 degrees) at 6 km/h http://bit.ly/9Vkpg4"))
#    print(tweeql.builtin_functions.Temperature.temperature_f(None, "Temp. 13.0mC RH 100% Wind SW (230 degrees) at 6 km/h http://bit.ly/9Vkpg4"))
#    print(tweeql.builtin_functions.Temperature.temperature_f(None, "Temp. 13.0dC RH 100% Wind SW (230 degrees) at 6 km/h http://bit.ly/9Vkpg4"))
#    print repr(u"(\d+(\.\d+)?)\s+°C")
#    print repr(ur"(\d+(\.\d+)?)\s*°C")
    """
    print MeanOutliers.nummeandevs(None, 5, 1, 2)
    print MeanOutliers.nummeandevs(None, 6, 1, 2)
    print MeanOutliers.nummeandevs(None, 3, 1, 2)
    print MeanOutliers.nummeandevs(None, 2, 1, 2)
    print MeanOutliers.nummeandevs(None, 4, 1, 2)
    print MeanOutliers.nummeandevs(None, 4, 1, 2)
    print MeanOutliers.nummeandevs(None, 10, 1, 2)
    print MeanOutliers.nummeandevs(None, 40, 1, 2)
    print MeanOutliers.nummeandevs(None, 5, 1, 2)
    
    print MeanOutliers.nummeandevs(None, 60, 2, 2)
    print MeanOutliers.nummeandevs(None, 80, 2, 2)
    print MeanOutliers.nummeandevs(None, 75, 2, 2)
    print MeanOutliers.nummeandevs(None, 80, 2, 2)
    print MeanOutliers.nummeandevs(None, 90, 2, 2)
    print MeanOutliers.nummeandevs(None, 63, 2, 2)
    print MeanOutliers.nummeandevs(None, 72, 2, 2)
    print MeanOutliers.nummeandevs(None, 40, 2, 2)
    print MeanOutliers.nummeandevs(None, 120, 2, 2)
    
    print MeanOutliers.nummeandevs(None, 90, 2, 3)
    print MeanOutliers.nummeandevs(None, 20, 2, 3)
    print MeanOutliers.nummeandevs(None, 21, 2, 3)
    print MeanOutliers.nummeandevs(None, 23, 2, 3)
    print MeanOutliers.nummeandevs(None, 25, 2, 3)
    print MeanOutliers.nummeandevs(None, 15, 2, 3)
    print MeanOutliers.nummeandevs(None, 20, 2, 3)
    print MeanOutliers.nummeandevs(None, 25, 2, 3)
    print MeanOutliers.nummeandevs(None, 25, 2, 3)
    print MeanOutliers.nummeandevs(None, 25, 2, 3)
    print MeanOutliers.nummeandevs(None, 60, 2, 3)
    """
    meansum = 0.0
    meandevsum = 0.0
    count = 0
    std = 40
    incount = 0
    for i in range(1,10000):
        val = random.gauss(0,std)
        if abs(val) < 2*std:
            incount += 1
        meansum += 1.0*val
        count += 1
        meandevsum += abs(1.0*(val - meansum/count))
        MeanOutliers.nummeandevs(None, val, 2, 3)
    print meansum/count, meandevsum/count
    print "incount", incount
    print MeanOutliers.nummeandevs(None, 80, 2, 3)
    pass
