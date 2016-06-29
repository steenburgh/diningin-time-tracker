import json
import re
import datetime

import API
from Restaurant import Restaurant

LUNCH_DELIVERY = "C04FQP1G4"


def main():
    restaurants = {}
    resp_json = API.get_channel_history(channelID=LUNCH_DELIVERY, count=1000)

    # Using two separate regexes will help us identify restaurants with 'and' in their name more reliably
    # as we have to split multi-restaurant lists around the word 'and'
    single_rest_regex = re.compile('(?i)^<!group>\s(.*)\sis(?! not)(?:[a-z\s]+)?\shere.?$')
    multiple_rest_regex = re.compile('(?i)^<!group>\s(.*)\sare(?! not)(?:[a-z\s]+)?\shere.?$')
    single_rest_msgs = filter(
        lambda message: single_rest_regex.match(message['text']) is not None,
        resp_json['messages']
    )
    multiple_rest_msgs = filter(
        lambda message: multiple_rest_regex.match(message['text']) is not None,
        resp_json['messages']
    )

    for msg in single_rest_msgs:
        rest_name = single_rest_regex.match(msg['text']).group(1).strip()
        rest_name = clean_restaurant_name(rest_name)
        add_restaurant(restaurants, rest_name, msg)

    for msg in multiple_rest_msgs:
        rest_name_str = multiple_rest_regex.match(msg['text']).group(1)
        # Regex note: & signs come in through the API as &amp;
        rest_name_list = re.split("(?i),\s?(?:and|&amp;)?\s|\s(?:and|&amp;)\s", rest_name_str)
        rest_name_list = clean_rest_list(rest_name_list)
        for rest_name in rest_name_list:
            add_restaurant(restaurants, rest_name, msg)

    rests_list = restaurants.values()
    rests_list.sort(key=lambda rest: rest.get_average_time(), reverse=False)
    for rest in rests_list:
        print rest


def clean_rest_list(rest_name_list):
    # Special case
    if rest_name_list.__contains__("the burger"):
        rest_name_list.remove("the burger")

    rest_name_list = map(clean_restaurant_name, rest_name_list)
    return rest_name_list


def clean_restaurant_name(rest_name):
    # convert letters to lower case
    rest_name = rest_name.lower()
    # replace '&'' with 'and'
    rest_name = rest_name.replace("amp", "and")
    # remove special chars (only keep numbers, letters, and spaces)
    rest_name = re.sub('[^a-zA-Z0-9 \n\.]', '', rest_name)

    replacements = {
        "idof": "i dream of falafel",
        "mannys": "mannys deli",
        "sro": "standing room only",
        "tgab": "the great american bagel",
        "gab": "the great american bagel",
        "stax": "stax cafe",
        "uno": "unos",
        "ginos": "ginos east",
    }
    if rest_name in replacements.keys():
        rest_name = replacements[rest_name]

    return rest_name


def add_restaurant(rest_list, rest_name, msg):
    restaurant = Restaurant(name=rest_name)
    timestamp_str = msg['ts']

    if rest_list.__contains__(restaurant):
        rest_list[restaurant].add_time(timestamp_str)
    else:
        restaurant.add_time(timestamp_str)
        rest_list[restaurant] = restaurant


def pretty_print_dictionary(dict):
    print(json.dumps(dict, sort_keys=True, indent=4, separators={',', ':'}))

if __name__ == "__main__":
    main()

