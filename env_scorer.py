'''
* Copyright ProjectVisionHealth (c) 2015
* Author Name: Ankush Shah
* Date : 22 Dec 2015
* Description: Module for calculating environment metrics
'''

import json
import logging
import requests
import urllib
import crime_rate_api
import yaml

WEIGHT_CRIME_SCORE = 12.5
WEIGHT_AQI = 12.5
NORM_ENV_SCORE = 2

CONFIG = yaml.load(open("config.yaml"))


def get_crime_score(loc_data):
    total_crime_score = 0.0
    total_time_spent = 0.0
    for key in loc_data:
        (lati, longi) = key
        time_spent = loc_data[key]
        crime_rate = crime_rate_api.get_crime_rate(lati, longi)
        if crime_rate is not None:
            total_crime_score += crime_rate * time_spent
            total_time_spent += time_spent

    if total_time_spent > 0:
        avg_crime_score = total_crime_score / total_time_spent
        crime_score = (avg_crime_score) * WEIGHT_CRIME_SCORE / 100
        crime_score = min(max(0, crime_score), WEIGHT_CRIME_SCORE)
        return crime_score
    else:
        # if we don't know about the place,
        # we assume the best case and return 0
        return 0


def get_aqi_score(loc_data):
    # base url of the air quality index api
    # from breezometer
    api_url = CONFIG['APIS']['breezometer_aqi_api']
    api_key = CONFIG['APIS']['breezometer_aqi_api_key']
    params = {}
    params['key'] = api_key
    total_aqis = 0.0
    total_time_spent = 0.0
    for key in loc_data:
        (lati, longi) = key
        time_spent = loc_data[key]
        params['lat'] = lati
        params['lon'] = longi
        data = urllib.urlencode(params)
        response = requests.get(api_url + data)
        response = json.loads(response.text)
        if 'breezometer_aqi' in response:
            total_aqis += response['breezometer_aqi'] * time_spent
            total_time_spent += time_spent

    if total_time_spent > 0:
        avg_aqi = total_aqis / total_time_spent
        aqi_score = (100 - avg_aqi) * WEIGHT_AQI / 100
        aqi_score = min(max(0, aqi_score), WEIGHT_AQI)
        return aqi_score
    else:
        # if we don't know about the place,
        # we assume the best case and return 0
        return 0


def get_env_score(loc_data):
    env_score = {}
    aqi_score = get_aqi_score(loc_data)
    env_score['air_quality_index'] = aqi_score
    env_score['crime_rate'] = get_crime_score(loc_data)
    env_score['normalized_environment_score'] = NORM_ENV_SCORE * (env_score['air_quality_index'] + env_score['crime_rate'])
    return env_score


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loc_data = {
                (50.73858, 7.07873): 120,  # McFit in bonn
                (50.737204, 7.102983): 120,  # Subway
                (37.757815, -122.5076408): 120,  # San Francisco
                (40.7058316, -74.2582003): 120  # New York
            }

    env_score = get_env_score(loc_data)
    print env_score
