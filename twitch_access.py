import requests
import json
from config import load_secret_clientId

ACCESS_TOKEN_FILE = 'access_token.json'
REDIRECT_URI = 'http://localhost:5000/callback'

def retrieve_token(authorization_code):
    secret_clientId = load_secret_clientId()
    payload = {
    "client_id":  secret_clientId[1],
    "client_secret": secret_clientId[0],
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
    "code": authorization_code
    }
    r = requests.post("https://id.twitch.tv/oauth2/token", params=payload)
    data = r.json()
    print(data)
    return data

def save_access_payload(payload):
    with open(ACCESS_TOKEN_FILE, 'w') as f:
            f.write(json.dumps(payload))

def load_access_payload():
    with open(ACCESS_TOKEN_FILE) as f:
        stringified = f.readline()
        payload = json.loads(stringified)
        return payload
