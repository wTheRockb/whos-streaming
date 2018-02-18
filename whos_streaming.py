import sys
import requests
from collections import namedtuple


def load_secret_clientId():
    with open('secret.txt', 'r') as fp:
        secret = fp.readline().split('\n')[0]
        client_id = fp.readline()
        return (secret, client_id)

Stream = namedtuple('Stream', [
                    'name', 'game_id', 'game_title', 'user_id', 'title', 'thumbnail_url', 'type', 'viewer_count'])

def retrieve_token():
    secret_clientId = load_secret_clientId()
    payload = {
    "client_id":  secret_clientId[1],
    "client_secret": secret_clientId[0],
    "grant_type": "client_credentials",
    }
    r = requests.post("https://api.twitch.tv/kraken/oauth2/token", params=payload)
    return r.json()["access_token"]

HEADERS = {"Authorization": "Bearer " + retrieve_token()}

def group_by_100s(input):
    return [input[i:i+100] for i in range(0, len(input), 100)]


def parse_username():
    try:
        username = sys.argv[1]
        return username
    except:
        exit("Could not parse username. Usage: 'python check.py [USERNAME]")


def get_games(game_ids):
    payload = {"id": game_ids}
    r = requests.get("https://api.twitch.tv/helix/games", params=payload, headers=HEADERS)
    return r.json()


def get_user(username):
    payload = {"login": username}
    r = requests.get("https://api.twitch.tv/helix/users",
                     params=payload, headers=HEADERS)
    return r.json()

def get_follows(user_id):
    still_paginated = True
    payload = {"from_id": user_id, "first": 100}
    while still_paginated:
        r = requests.get("https://api.twitch.tv/helix/users/follows",
                         params=payload, headers=HEADERS)
        data = r.json()

        if data["data"] != []:
            for i in data["data"]:
                yield i["to_id"]
        else:
            break
        if "cursor" in data["pagination"]:
            payload["after"] = data["pagination"]["cursor"]
        else:
            still_paginated = False

def request_streams_info(ids):
    payload = {"first": 100}
    first = True
    for grouping in group_by_100s(ids):
        payload["user_id"] = grouping

        r = requests.get("https://api.twitch.tv/helix/streams",
                         params=payload, headers=HEADERS)

        if r.status_code != 200:
            exit("Error: Could not request data from twitch API.")
        resp = r.json()
        if resp["data"] == [] and first:
            exit("No streamers online.")
        else:
            first = False

        for i in resp["data"]:
            s = Stream(None, i["game_id"], None, i["user_id"], i["title"], i[
                       "thumbnail_url"], i["type"], i["viewer_count"])
            yield s

def convert_logins_to_ids(streams):
    ids_displays = {}
    streams = list(streams)
    user_ids = list(map(lambda x: x.user_id, streams))
    
    for grouping in group_by_100s(user_ids):
        payload = {"id": grouping}
        r = requests.get("https://api.twitch.tv/helix/users",
                         params=payload, headers=HEADERS)
        assert r.status_code == 200
        for i in r.json()["data"]:
            ids_displays[i["id"]] = i["display_name"]
    for s in streams:
        s2 = s._replace(name=ids_displays[s.user_id])
        yield s2

def convert_gameids_to_names(streams):
    ids_names = {}
    streams = list(streams)
    game_ids = list(map(lambda x: x.game_id, streams))
    for grouping in group_by_100s(game_ids):
        payload = {"id": grouping}
        r = requests.get("https://api.twitch.tv/helix/games",
                        params=payload, headers=HEADERS)
        assert r.status_code == 200
        for i in r.json()["data"]:
            ids_names[i["id"]] = i["name"]
    for s in streams:
        s2 = s._replace(game_title=ids_names[s.game_id])
        yield s2

def print_streams(streams):
    for s in streams:
        line = "{0:22} | {1:30}  | {2:8} | {3:125}".format(s.name, s.game_title, s.viewer_count, s.title)
        print(line)

def main():
    username = parse_username()
    user = get_user(username)
    user_id = user["data"][0]["id"]
    follows = list(get_follows(user_id))
    streams_info = request_streams_info(follows)
    streams_with_names = convert_logins_to_ids(streams_info)
    streams_with_games = convert_gameids_to_names(streams_with_names)
    stream_list = list(streams_with_games)
    stream_list.sort(key=lambda x: x.viewer_count, reverse=True)
    print_streams(stream_list)

if __name__ == "__main__":
    main()
