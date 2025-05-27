# server.py
from flask import Flask, jsonify, request
import json
import requests
import urllib.parse

from google.oauth2.credentials import Credentials

app = Flask(__name__)

with open('./secrets/credentials.json') as f:
    creds = json.load(f)

CLIENT_ID = creds['installed']['client_id']
CLIENT_SECRET = creds['installed']['client_secret']
REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'

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

    token_data["client_id"] = CLIENT_ID
    token_data["client_secret"] = CLIENT_SECRET
    token_data["scopes"] = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/tasks.readonly"]
    token_data["universe_domain"] = "googleapis.com"
    token_data["token_uri"] = "https://oauth2.googleapis.com/token"
    

    creds = Credentials.from_authorized_user_info(token_data)

    return jsonify(json.loads(creds.to_json()))

if __name__ == '__main__':
    app.run(port=5000)
