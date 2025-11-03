# server.py
import os
import json
import time
import requests
import urllib.parse

from flask import Flask, jsonify, request, Response

from google.oauth2.credentials import Credentials

app = Flask(__name__)

if not os.path.isfile("./secrets/credentials.json"):
    print("Please add credentials.json in the directory './secrets/'. To add credentials.json, please go to Google Cloud and authorize the new application.")
    exit(1)

with open('./secrets/credentials.json') as f:
    creds = json.load(f)

CLIENT_ID = creds['installed']['client_id']
CLIENT_SECRET = creds['installed']['client_secret']
REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/tasks.readonly'

@app.route('/ping', methods=["GET"])
def ping():
    return Response("pong", status=200)

@app.route('/auth_url')
def auth_url():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return jsonify({'auth_url': url})

@app.route("/exchange", methods=["POST"])
def get_exchange():
    params = {
        'code': request.json.get("code"),
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    token_data = requests.post("https://oauth2.googleapis.com/token", data=params).json()

    token_data["obtained_at"] = time.time()  # удобно для кэширования

    return jsonify(token_data)

@app.route("/refresh", methods=["POST"])
def refresh_token():
    refresh_token = request.json.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Missing refresh_token"}), 400

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    r = requests.post("https://oauth2.googleapis.com/token", data=payload)
    if r.status_code != 200:
        return jsonify({"error": "Failed to refresh", "details": r.text}), 500

    token_info = r.json()
    token_info["obtained_at"] = time.time()  # удобно для кэширования

    return jsonify(token_info)

if __name__ == '__main__':
    app.run(port=5000)
