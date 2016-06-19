import json
import re
import datetime

import API

LUNCH_DELIVERY = "C04FQP1G4"


def main():
    restaurants = {}
    # resp_json = API.post_message('test_dininginbot', 'test')
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
        timestamp = msg['ts']
        add_restaurant(restaurants, rest_name, timestamp)

    for msg in multiple_rest_msgs:
        rest_name_str = multiple_rest_regex.match(msg['text']).group(1)
        # Regex note: & signs come in through the API as &amp;
        rest_name_list = re.split("(?i),\s?(?:and|&amp;)?\s|\s(?:and|&amp;)\s", rest_name_str)
        for rest_name in rest_name_list:
            add_restaurant(restaurants, rest_name, timestamp)

    map_to_averages(restaurants)

    # map_dict(lambda L: len(L), restaurants)

    pretty_print_dictionary(restaurants)


def map_dict(map_fn, dict):
    for (key, val) in dict.iteritems():
        dict[key] = map_fn(val)


# converts dict of unix timestamp list to average seconds
def map_to_averages(dict):
    for (key, val) in dict.iteritems():
        dict[key] = reduce(lambda x, y: x+y, map(convert_from_timestamp, val)) / len(val)


# converts unix timestamp to seconds (in 24 hour period)
# Ex. "1456768776.000113" => 43176
def convert_from_timestamp(timestamp_str):
    dt_obj = datetime.datetime.fromtimestamp(int(float(timestamp_str)))
    hour = dt_obj.hour
    minutes = dt_obj.minute
    seconds = dt_obj.second
    return hour*3600 + minutes*60 + seconds


def clean_restaurant_name(restaurant):
    # only lower case letters
    restaurant = restaurant.lower()
    # replace '&'' with 'and'
    restaurant = restaurant.replace("amp", "and")
    # remove special chars (only keep numbers, letters, and spaces)
    restaurant = re.sub('[^a-zA-Z0-9 \n\.]', '', restaurant)
    return restaurant


def add_restaurant(rest_list, restaurant, timestamp):
    restaurant = clean_restaurant_name(restaurant)
    # print rest_list.get(restaurant, [])
    # print restaurant
    rest_list[restaurant] = rest_list.get(restaurant, []) + [timestamp]
    if restaurant in rest_list:
        rest_list[restaurant].append(timestamp)
    else:
        rest_list[restaurant] = [timestamp]


def pretty_print_dictionary(dict):
    print(json.dumps(dict, sort_keys=True, indent=4, separators={',', ':'}))

if __name__ == "__main__":
    main()
