# Project:  strava-epaper-display.py
# Author:   officialdavidtaylor

# Special thanks to:
# - franchyze923: Code_From_Tutorials/Strava_Api/strava_api.py

# --Libraries--

from operator import mod
from PIL import Image, ImageDraw, ImageFont
import credentials as auth
import requests
import urllib3
import urllib.parse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --Globals--

epaper_params = {
    'width': 300,
    'height': 400
}

# --Functions--


def GetRecentStravaData():
    # Use Strava API to extract most recent ride data

    # Strava API URLs
    auth_url = "https://www.strava.com/oauth/token"
    activites_url = "https://www.strava.com/api/v3/athlete/activities"

    # structure of payload to retrieve current access token using refresh token
    payload = {
        'client_id': auth.StravaCredentials['client_id'],
        'client_secret': auth.StravaCredentials['client_secret'],
        'refresh_token': auth.StravaCredentials['refresh_token'],
        'grant_type': 'refresh_token',
        'f': 'json'
    }

    # retrieve current access token
    print('Requesting Token...\n')
    res = requests.post(auth_url, data=payload, verify=False)
    try:
        access_token = res.json()['access_token']
        auth.StravaCredentials['acess_token'] = access_token
    except:
        print('POST request failed, new access token not generated')

    print('Access token retrieved and updated')

    # poll server for new activities
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


def GetMapImage(route_polyline, map_name):
    map_resolution = '280x280'
    # map_name = 'map.png' # commented out, now an arg

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
        image = open(('static_maps/' + map_name + '.png'), 'wb')
        image.write(res.content)
        image.close()
        return './static_maps/{}.png'.format(map_name)
    except:
        print('error retrieving image from the server')


def GenerateEpaperOutput(strava_activity, map_file_path):
    # TODO: use pillow to create an image using mapbox static image and strava data
    # Reference Figma design: https://www.figma.com/file/fpX1GIlazQLY8EfvvzSyrE/Ride-Viewer-%7C-e-Paper-4.2%22?node-id=0%3A1

    activity_name = strava_activity['name']
    activity_date = strava_activity['start_date_local'][:10]

    # create new image with Pillow
    canvas = Image.new(mode='1', size=(
        epaper_params['width'], epaper_params['height']), color=255)

    # import static map image
    map_image = Image.open(map_file_path)
    # convert map to 1-bit image
    map_image = map_image.convert(mode='1')

    # overlay static map on Pillow canvas
    canvas.paste(map_image, (10, 10))

    # create drawing context
    d = ImageDraw.Draw(canvas)

    # draw rounded rectangles
    d.rounded_rectangle([(10, 10), (290, 390)], radius=10,
                        fill=None, outline='black', width=1)
    d.rounded_rectangle([(10, 10), (290, 290)], radius=10,
                        fill=None, outline='black', width=1)

    # define fonts
    ImageFont.load_default()
    # define title font
    fnt_title = ImageFont.truetype('./__pycache__/Lato-Bold.ttf', 20)
    # define body font
    fnt_body = ImageFont.truetype('./__pycache__/Lato-Regular.ttf', 12)

    # draw Name text
    d.text((20, 298), activity_name, font=fnt_title, fill='#000000')

    # draw Distance text (divide by 1609 to convert meters into miles)
    d.text((20, 328), 'Distance: {:.2f} mi'.format(
        (strava_activity['distance'] / 1609)), font=fnt_body, fill='#000000')

    # draw Avg. speed text (multiply by 2.237 to convert m/s to mph)
    d.text((20, 348), 'Avg. Speed: {:.1f} mph'.format(
        (strava_activity['average_speed'] * 2.237)), font=fnt_body, fill='#000000')

    # draw Average Watts text
    d.text((20, 368), 'Avg. Watts: {} W'.format(
        strava_activity['average_watts']), font=fnt_body, fill='#000000')

    # draw Elevation text
    d.text((150, 328), 'Elevation Gain: {:.1f} ft'.format(
        (strava_activity['total_elevation_gain'] * 3.281)), font=fnt_body, fill='#000000')

    # draw Moving Time text
    d.text((150, 348), 'Moving Time: {} s'.format(
        strava_activity['moving_time']), font=fnt_body, fill='#000000')

    # draw Date text, grab yyyy-mm-dd only (first 10 digits) from Strava date string
    d.text((150, 368), 'Date: {}'.format(
        activity_date), font=fnt_body, fill='#000000')

    canvas.save(fp='./display_outputs/{}'.format((activity_name +
                '_' + activity_date)), format='png')
    canvas.show()

# def DisplayError():
#     # TODO: Generate template error image in Gimp, save to GitHub so it can be displayed
#     # TODO: Generate live QR code to redirect to docs for specific error

# --Script Logic--


strava_activity = GetRecentStravaData()

# check to see if Strava data was returned
if not strava_activity:
    print('error accessing Strava data')

else:
    # extract compressed polyline from activity object
    strava_polyline = strava_activity["map"]["summary_polyline"]
    strava_map_id = strava_activity["map"]["id"]
    # use Mapbox to create image and save to local folder
    map_file_path = GetMapImage(strava_polyline, strava_map_id)

    display_output = GenerateEpaperOutput(strava_activity, map_file_path)


# TODO: MISC Operations to be deleted later
# print(strava_data[0]["name"])
# print(strava_data[0]["map"]["summary_polyline"])
