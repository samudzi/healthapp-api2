'''
author: ankush.shah.nitk@gmail.com
date: 10th Nov 2015
desc: calculate the score using
      Behavior Risk Model Algorithm (brma)
'''

import json
import logging
import requests

from pprint import pprint

LOGGER = logging.getLogger(__name__)
PLACE_API = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
API_KEY = 'AIzaSyCAYAAI4o6mhETaz_YUrGvTVTQi9ePDKbU'

YIMBY_LOCS = ['grocery_or_supermarket', 'gym']
NIMBY_LOCS = ['bar', 'meal_takeaway', 'restaurant']
RADIUS = 20  # in meters


def get_nimby_score(loc_data):
    params = {'key': API_KEY,
              'radius': RADIUS,
              'types': "|".join(NIMBY_LOCS)}
    score = 0
    for (lati, longi) in loc_data:
        params['location'] = "%s,%s" % (lati, longi)
        res = requests.get(PLACE_API, params=params)
        res = json.loads(res.text)
        if len(res["results"]) > 0:
            score += 5

    score = min(score, 50)
    return score


def get_yimby_score(loc_data):
    params = {'key': API_KEY,
              'radius': RADIUS,
              'types': "|".join(YIMBY_LOCS)}
    score = 50
    for (lati, longi) in loc_data:
        params['location'] = "%s,%s" % (lati, longi)
        res = requests.get(PLACE_API, params=params)
        res = json.loads(res.text)
        if len(res["results"]) > 0:
            score -= 5

    score = max(score, 0)
    return score


def get_brma_score(loc_data):
    nimby_score = get_nimby_score(loc_data)
    print "nimby_score", nimby_score

    yimby_score = get_yimby_score(loc_data)
    print "yimby_score", yimby_score

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loc_data = {
                (50.73858, 7.07873): 120,
                (50.737204, 7.102983): 120
            }

    get_brma_score(loc_data)
    pass