from __future__ import print_function
import httplib
from Credentials import AUTH_TOKEN

import sys

import requests


API_URL = "https://sproutsocial.slack.com/api/{method}"


def post_message(channel_name, message, username='Diningin Bot', icon_emoji=":knife_fork_plate:"):
    return call(
        'chat.postMessage',
        args={
            'channel': channel_name,
            'text': message,
            'username': username,
            'icon_emoji': icon_emoji,
        }
    )


def get_channel_history(channel_id, count=100):
    return call(
        'channels.history',
        args={
            'channel': channel_id,
            'count': count,
        }
    )


def call(method, args={}, warn=True):
    args['token'] = AUTH_TOKEN
    r = requests.post(
        url=API_URL.format(method=method),
        params=args
    )

    if warn and r.json().__contains__('warnings'):
        print(
            "Warnings: {msg}".format(msg=",".join(r.json()['warnings'])),
            file=sys.stderr
        )

    if r.status_code != httplib.OK:
        raise requests.HTTPError(r.status_code)
    elif r.json().__contains__('error'):
        raise requests.RequestException(r.json()['error'])

    return r.json()
