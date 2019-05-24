from __future__ import print_function
import sys
import json
from flask import Flask, request, redirect, g, render_template
import requests
import base64
import urllib
import pandas as pd
from pandas import DataFrame

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
app = Flask(__name__)

#  Client Keys
CLIENT_ID = "82a07fac675249ad829171208f9b0b01"
CLIENT_SECRET = "9ae759ef6d124393a0340d3c63ae9060"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-top-read"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


@app.route("/")
def home():
    return render_template("home.html")
    	
@app.route("/about")
def about():
	return render_template("about.html")

# Extract data from Spotify API
@app.route("/spotify")
def index():
    # Auth Step: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

def token():
    # Auth Step: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)
    # Auth Step: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    return access_token

def profile_data(access_token):
    # Auth Step: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)
    return profile_data

def get_top_tracks(access_token):
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    # Get user top tracks
    top_api_endpoint = "{}/me/top/tracks".format(SPOTIFY_API_URL)
    top_response = requests.get(top_api_endpoint, headers=authorization_header)
    top_data = json.loads(top_response.text)
#     print (top_data['items'][0].keys() )
    return top_data

def get_ids(top_data):

	id_tracks= [x['id'] for x in top_data['items']] 
	names= [x['name'] for x in top_data['items']] 
	return (id_tracks, names)


def get_audio_features(access_token, id_tracks):
	authorization_header = {"Authorization":"Bearer {}".format(access_token)}
	list_audio_features = []
	for id in id_tracks:
# 		print(id)
		audio_features_api_endpoint = "{}/audio-features/{}".format(SPOTIFY_API_URL,id)
		audio_features_response = requests.get(audio_features_api_endpoint, headers=authorization_header)
		audio_features_data = json.loads(audio_features_response.text)
# 		print( (id, audio_features_data, list_audio_features) )
		list_audio_features.append(audio_features_data)
# 	print (list_audio_features[1])
	print ( [x['valence'] for x in list_audio_features] )
	return list_audio_features
	
def get_some_features(list_audio_features):
	features = DataFrame(audio_features_data['items'])
# 	print (features)
	features_subset = features.danceability
	return features_subset

@app.route("/callback/q")
def top_artists():

    access_token = token()
    profile = profile_data(access_token)
    profile_info = profile.values()
    display_name = profile_info[0]
    top_tracks = get_top_tracks(access_token)
    ids, names = get_ids(top_tracks)
    # print (names)
#     print (ids)
    features = get_audio_features(access_token, ids)
    
    # get_genre = [most_common(artists)]
#     the_answer= []
#     for e in get_genre:
#         if e in london_places:
#             the_answer.append(london_places.get(e))
# 
#     get_genre = [most_common(artists)]
#     the_answer_info= []
#     for ei in get_genre:
#         if ei in london_places_info:
#             the_answer_info.append(london_places_info.get(ei))
    # Combine profile and tracks data to display

    return render_template("index.html", info_name = [display_name], danc=features)


if __name__ == "__main__":
    app.run(debug=True,port=PORT)