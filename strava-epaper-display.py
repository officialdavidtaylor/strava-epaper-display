# Project:  strava-epaper-display.py
# Author:   officialdavidtaylor

# Special thanks to:
# - franchyze923: Code_From_Tutorials/Strava_Api/strava_api.py

# --Libraries--

import credentials as auth
import requests
import urllib3
import urllib.parse
import polyline
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --Functions--


def GetRecentStravaData():
    # Use Strava API to look for new data
    auth_url = "https://www.strava.com/oauth/token"
    activites_url = "https://www.strava.com/api/v3/athlete/activities"

    payload = {
        'client_id': auth.StravaCredentials['client_id'],
        'client_secret': auth.StravaCredentials['client_secret'],
        'refresh_token': auth.StravaCredentials['refresh_token'],
        'grant_type': 'refresh_token',
        'f': 'json'
    }

    print('Requesting Token...\n')
    res = requests.post(auth_url, data=payload, verify=False)
    try:
        access_token = res.json()['access_token']
        auth.StravaCredentials['acess_token'] = access_token
    except:
        print('POST request failed, new access token not generated')

    print('Access token retrieved and updated')

    try:
        # poll server for new activities
        header = {'Authorization': 'Bearer ' + access_token}
        strava_data = requests.get(activites_url, headers=header).json()

        # identify most recent ride and return it
        for activity in strava_data:
            if activity['type'] == 'Ride':
                return activity

    except:
        print('GET request failed, please try again later')
        return False


def GetMapImage(route_polyline):
    map_resolution = '300x300'
    file_name = 'map.png'

    # URI encode the polyline data
    route_polyline = urllib.parse.quote(route_polyline.encode('utf8'))

    # use Static Map API to generate map image from Strava route polyline
    mapbox_url = 'https://api.mapbox.com/styles/v1/mapbox/light-v10/static/path+000000({0})/auto/{1}?access_token={2}'
    # insert path and access token
    mapbox_url = mapbox_url.format(route_polyline, map_resolution,
                                   auth.MapboxCredentials['access_token'])

    print(mapbox_url)

    try:
        h = requests.head(mapbox_url, allow_redirects=True)
        header = h.headers
        content_type = header.get('content-type')

        print(content_type)

        res = requests.get(mapbox_url, allow_redirects=True)
        image = open(file_name, 'wb')
        image.write(res.content)
        image.close()
        return file_name
    except:
        print('error retrieving image from the server')

# def GenerateEpaperOutput():
#   # TODO: use pillow to create an image from Google API call and Strava Data
#     # more code here

# def DisplayError():
#   # TODO: Generate template error image in Gimp, save to GitHub so it can be displayed
#   # TODO: Generate live QR code to redirect to docs for specific error


# --Script Logic--
strava_activity = GetRecentStravaData()

strava_polyline = strava_activity["map"]["summary_polyline"]

map_image = GetMapImage(strava_polyline)

# display_output = GenerateEpaperOutput(map_image, strava_data[0])


# TODO: MISC Operations to be deleted later
# print(strava_data[0]["name"])
# print(strava_data[0]["map"]["summary_polyline"])
