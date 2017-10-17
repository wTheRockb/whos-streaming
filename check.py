import sys
import requests
import configparser
from collections import namedtuple
from math import ceil
import pprint

config = configparser.ConfigParser()

TWITCH_CLIENT_ID = "xrl2910nixis8ogn2q23ev7gjwb4kj"

Stream = namedtuple('Stream', [
                    'name', 'game_id', 'user_id', 'title', 'thumbnail_url', 'type', 'viewer_count'])

headers = {"Client-ID": "xrl2910nixis8ogn2q23ev7gjwb4kj"}


def group_by_100s(input):
    return [input[i:i+100] for i in range(0, len(input), 100)]


def parse_username():
    try:
        username = sys.argv[1]
        return username
    except:
        exit("Could not parse username. Usage: 'python check.py [USERNAME]")


def get_user(username):
    payload = {"login": username}
    r = requests.get("https://api.twitch.tv/helix/users",
                     params=payload, headers=headers)
    return r.json()


def get_logins_from_ids(streams):
    ids_displays = {}
    streams = list(streams)
    user_ids = list(map(lambda x: x.user_id, streams))
    for grouping in group_by_100s(user_ids):
        payload = {"id": grouping}
        r = requests.get("https://api.twitch.tv/helix/users",
                         params=payload, headers=headers)
        assert r.status_code == 200
        for i in r.json()["data"]:
            ids_displays[i["id"]] = i["display_name"]
    for s in streams:
        s2 = s._replace(name=ids_displays[s.user_id])
        yield s2


def get_follows(user_id):
    still_paginated = True
    payload = {"from_id": user_id, "first": 100}
    while still_paginated:
        r = requests.get("https://api.twitch.tv/helix/users/follows",
                         params=payload, headers=headers)

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
                         params=payload, headers=headers)

        if r.status_code != 200:
            exit("Error: Could not request data from twitch API.")
        resp = r.json()
        if resp["data"] == [] and first:
            exit("No streamers online.")
        else:
            first = False

        for i in resp["data"]:
            s = Stream(None, i["game_id"], i["user_id"], i["title"], i[
                       "thumbnail_url"], i["type"], i["viewer_count"])
            yield s


def print_streams(streams):
    pp = pprint.PrettyPrinter(indent=4)
    for s in streams:
        # line = "{0:22} | {1:125} | {2:10} | {3:8}".format(s.name, s.title,
        # s.game_id, s.viewer_count)  # TODO: waiting on twitch API V5 to
        # include a game api
        line = "{0:22} | {1:125} | {2:8}".format(
            s.name, s.title, s.viewer_count)
        print(line)


username = parse_username()
user = get_user(username)
user_id = user["data"][0]["id"]
follows = list(get_follows(user_id))


streams_info = request_streams_info(follows)


streams_with_names = get_logins_from_ids(streams_info)


print_streams(streams_with_names)
