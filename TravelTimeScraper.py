'''
Created on Apr 21, 2017

@author: andrewbloomberg
'''
from bs4 import BeautifulSoup
import urllib2
import re
from urllib2 import URLError
import json

if __name__ == '__main__':
    file = open('buildings_and_addresses.txt', 'r')
    lines = file.readlines()
    buildings = []
    for line in lines:
        split = line.split(":")
        buildings.append((split[0], split[1]))
    walking_travels = []
    for building1 in buildings:
        for building2 in buildings:
            if(building1 == building2):
                pass
            else:
                place1 = building1[1].replace(" ", "_").rstrip()
                place2 = building2[1].replace(" ", "_").rstrip()
                travel = "https://maps.googleapis.com/maps/api/directions/json?mode=bicycling&origin=" + place1 + "&destination=" + place2
                header = {'User-Agent': 'Mozilla/5.0'}
                req = urllib2.Request(travel, headers=header)
                page = urllib2.urlopen(req)
                data = json.loads(page.read())
                try:
                    time = data["routes"][0]["legs"][0]["duration"]["text"]
                    walking_travels.append((building1[0], building2[0], time))
                    print(time)
                except IndexError:
                    print("failure")
                    pass
    with open('data_bicycling.json', 'w') as outfile:
        json.dump(walking_travels, outfile, indent = 4, sort_keys= True)