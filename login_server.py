from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os
from config import load_secret_clientId
from twitch_access import retrieve_token, save_access_payload, REDIRECT_URI
import json

app = Flask(__name__)
app.secret_key = "woody-whos-streaming"



secret_clientId = load_secret_clientId() ## Not ideal to do this on module load TODO
client_id = secret_clientId[1]
client_secret = secret_clientId[0]
authorization_base_url = 'https://id.twitch.tv/oauth2/authorize?response_type=code&force_verify=true'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    twitch = OAuth2Session(client_id, redirect_uri=REDIRECT_URI)
    authorization_url, state = twitch.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    twitch = OAuth2Session(client_id, state=session['oauth_state'])
    access_code = request.args.get('code')

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    full_access_payload = retrieve_token(access_code)
    save_access_payload(full_access_payload)
    session['oauth_token'] = full_access_payload['access_token']
    return "Succesfully saved token to local file!"



if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)
