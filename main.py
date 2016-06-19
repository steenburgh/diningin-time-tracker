import json
import re

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
        add_restaurant(restaurants, rest_name)

    for msg in multiple_rest_msgs:
        rest_name_str = multiple_rest_regex.match(msg['text']).group(1)
        # Regex note: & signs come in through the API as &amp;
        rest_name_list = re.split("(?i),\s?(?:and|&amp;)?\s|\s(?:and|&amp;)\s", rest_name_str)
        for rest_name in rest_name_list:
            add_restaurant(restaurants, rest_name)

    pretty_print_dictionary(restaurants)


def add_restaurant(rest_list, restaurant):
    if rest_list.__contains__(restaurant):
        rest_list[restaurant] += 1
    else:
        rest_list[restaurant] = 1


def pretty_print_dictionary(dict):
    print(json.dumps(dict, sort_keys=True, indent=4, separators={',', ':'}))

if __name__ == "__main__":
    main()
