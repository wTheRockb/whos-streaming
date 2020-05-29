# whos-streaming
A simple tool to view what streamers you follow on twitch.tv are currently live.

## Usage

Install the requirements:
`pip install requirements.txt`

**Note**
As of March 2020 Twitch has overhauled security on their endpoints. This tool has been updated majorly per the [announcement here](https://discuss.dev.twitch.tv/t/requiring-oauth-for-helix-twitch-api-endpoints/23916). Updated instructions below.

1. Create an application on the twitch developer website, noting your client id and secret. Set your redirect uri to `http://localhost:5000/callback`.
2. Create a `secret.txt` and add you client secret, then a newline, and then your client id. (Don't worry about version control this file is git ignored.)
3. Then, run `FLASK_APP=login_server.py python -m flask run` and navigate to `http://localhost:5000/`, and authorize twitch. This saves an access token locally to access the necessary APIs from twitch. (This is also git ignored.) You should be greeted with the message `Succesfully saved token to local file!` on your browser if successful.
4. Finally, to use the tool run `python whos_streaming.py <username>` to get a list of live streams, titles, game and viewer count.

With any bugs feel free to open issues, pull requests or directly email me at forrestwbutler@gmail.com.

## Screenshots

![images/out.png]
![images/auth.png]