import json
import re
import datetime
import time

import API
from Restaurant import Restaurant
from Restaurant import format_seconds

LUNCH_DELIVERY = "C04FQP1G4"


def main():
    # dictionary mapping Restaurant to Restaurant
    restaurants = {}
    lunch_channel_json = API.get_channel_history(channelID=LUNCH_DELIVERY, count=1000)

    id_to_rest_name_dict = json_file_to_dic('rest_ids.json')
    rest_name_to_id_dict = reverse_dic(id_to_rest_name_dict)
    # gather official list of restuarants
    official_rest_name_list = id_to_rest_name_dict.values()

    # Using two separate regexes will help us identify restaurants with 'and' in their name more reliably
    # as we have to split multi-restaurant lists around the word 'and'
    single_rest_regex = re.compile('(?i)^<!group>\s(.*)\sis(?! not)(?:[a-z\s]+)?\shere.?$')
    multiple_rest_regex = re.compile('(?i)^<!group>\s(.*)\sare(?! not)(?:[a-z\s]+)?\shere.?$')
    single_rest_msgs = filter(
        lambda message: single_rest_regex.match(message['text']) is not None,
        lunch_channel_json['messages']
    )
    multiple_rest_msgs = filter(
        lambda message: multiple_rest_regex.match(message['text']) is not None,
        lunch_channel_json['messages']
    )

    for msg in single_rest_msgs:
        rest_name = single_rest_regex.match(msg['text']).group(1).strip()
        rest_name = clean_restaurant_name(rest_name)
        if rest_name in rest_name_to_id_dict:
            rest_id = rest_name_to_id_dict[rest_name]
            add_restaurant(restaurants, rest_name, rest_id, msg)

    for msg in multiple_rest_msgs:
        rest_name_str = multiple_rest_regex.match(msg['text']).group(1)
        # Regex note: & signs come in through the API as &amp;
        rest_name_list = re.split("(?i),\s?(?:and|&amp;)?\s|\s(?:and|&amp;)\s", rest_name_str)
        rest_name_list = clean_rest_list(rest_name_list)
        for rest_name in rest_name_list:
            if rest_name in rest_name_to_id_dict:
                rest_id = rest_name_to_id_dict[rest_name]
                add_restaurant(restaurants, rest_name, rest_id, msg)

    rests_list = restaurants.values()
    rests_list.sort(key=lambda rest: rest.get_average_time(), reverse=False)

    for rest in rests_list:
        print rest

    write_averages_json_file(rests_list)

    


def clean_rest_list(rest_name_list):
    # Special case
    rest_name_list = map(clean_restaurant_name, rest_name_list)

    if "the burger" in rest_name_list:
        rest_name_list.remove("the burger")

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
        "cpk": "california pizza kitchen",
        "butcher": "butcher and the burger",
        "blue frogs 22": "blue frogs local 22",
        "blue frog 22": "blue frogs local 22",
        "tgab": "the great american bagel",
        "gab": "the great american bagel",
        "stax": "stax cafe",
        "uno": "unos",
        "ginos": "ginos east",
    }
    if rest_name in replacements.keys():
        rest_name = replacements[rest_name]

    return rest_name


def add_restaurant(rest_dict, rest_name, rest_id, msg):
    restaurant = Restaurant(name=rest_name, id=rest_id)
    timestamp_str = msg['ts']

    if rest_dict.__contains__(restaurant):
        rest_dict[restaurant].add_time(timestamp_str)
    else:
        restaurant.add_time(timestamp_str)
        rest_dict[restaurant] = restaurant


def pretty_print_dictionary(dict):
    print(json.dumps(dict, sort_keys=True, indent=4, separators={',', ':'}))


def json_file_to_dic(json_filename):
    with open('rest_ids.json', 'r') as data_file: 
        D = json.load(data_file)
    return D


# accepts list of restaurant objects (all with times already added to them)
# writes json file mapping restaurant id to average time
def write_averages_json_file(rests_list):
    final_dict = {}
    for rest in rests_list:
        final_dict[rest.id] = format_seconds(rest.get_average_time())

    time_now = datetime.datetime.now()
    # time in millseconds
    javascript_time_now = int(time.mktime(time_now.timetuple())) * 1000
    final_dict['last_updated'] = javascript_time_now

    with open("averages.json", "w") as write_file:
        write_file.write(json.dumps(final_dict, write_file, indent=4))


# reverses the keys and values in a dictionary
def reverse_dic(D):
    inv_map = {v: k for k, v in D.iteritems()}
    return inv_map


if __name__ == "__main__":
    main()

