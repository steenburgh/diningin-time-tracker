from __future__ import print_function
import httplib

import sys

import requests

AUTH_TOKEN = 'xoxb-51798272368-vjpfYBtwRIpcSg28mzhbsXeS'
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


def get_channel_history(channelID, count=100):
    return call(
        'channels.history',
        args={
            'channel': channelID,
            'count': count,
        }
    )


def call(method, args={}, warn=True):
    args['token'] = AUTH_TOKEN
    r = requests.post(
        url=API_URL.format(method=method),
        params=args
    )

    if warn and r.json().__contains__('warning'):
        print(
            "Warning: {msg}".format(msg=r.json()['warning']),
            file=sys.stderr
        )

    if r.status_code != httplib.OK:
        raise requests.HTTPError(r.status_code)
    elif r.json().__contains__('error'):
        raise requests.RequestException(r.json()['error'])

    return r.json()
