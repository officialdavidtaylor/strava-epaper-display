# Project:  strava-epaper-display.py
# Author:   officialdavidtaylor

# Special thanks to:
# - franchyze923: Code_From_Tutorials/Strava_Api/strava_api.py

# --Libraries--

from asyncio.windows_events import NULL
import credentials as auth
import requests
import urllib3
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
    response = requests.post(auth_url, data=payload, verify=False)
    try:
        access_token = response.json()['access_token']
        auth.StravaCredentials['acess_token'] = access_token
    except:
        print('POST request failed, new access token not generated')

    print('Access token retrieved and updated')

    try:
        header = {'Authorization': 'Bearer ' + access_token}
        strava_data = requests.get(activites_url, headers=header).json()
        # if operation is successful, return data
        return strava_data
    except:
        print('GET request failed, please try again later')
        return False

# def GetMapImage(route_polyline):
#   # TODO: use Maps Static API to generate map image from Strava route polyline
#     # code here


# def GenerateEpaperOutput():
#   # TODO: use pillow to create an image from Google API call and Strava Data
#     # more code here

# --Script Logic--

strava_data = GetRecentStravaData()

# map_image = GetMapImage(strava_data[0]["map"]["summary_polyline"])

# display_output = GenerateEpaperOutput(map_image, strava_data[0])


# TODO: MISC Operations to be deleted later
# print(strava_data[0]["name"])
# print(strava_data[0]["map"]["summary_polyline"])
