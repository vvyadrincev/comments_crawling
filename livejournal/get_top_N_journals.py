#!/usr/bin/env python
# -*- coding:utf-8 -*-


import argparse
import logging

import requests
from lxml import html

base_url = "https://www.livejournal.com/ratings/users/authority/?country=cyr&page="


def fetch_url(page_num):
    return base_url + str(page_num)


def get_top_N(N):
    users = list()
    current_page = 1
    while len(users) < N:
        current_fetch_url = fetch_url(current_page)
        logging.info("Processing url %s", current_fetch_url)
        ht = html.fromstring(requests.get(current_fetch_url).content)
        user_hrefs = ht.xpath(
            "//*[@class='rating-journals-list']/*[@class='rating-journals-item']//a[@class='i-ljuser-username']/@href")
        logging.info("For '%s' '%s' hrefs extracted", current_fetch_url, len(user_hrefs))
        for user_href in user_hrefs:
            users.append(user_href)
        current_page = current_page + 1

    return users


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--users_count", "-N", required=True, type=int,
                        help="number of TOP users")
    parser.add_argument("--out_file", "-o", required=True,
                        help="out file")

    args = parser.parse_args()

    try:
        users = get_top_N(args.users_count)
        with open(args.out_file, 'w') as of:
            for u in users:
                of.write(u + '\n')
        logging.info("Saved '%s' users to %s", len(users), args.out_file)

    except Exception as e:
        logging.exception("failed to process: %s " % str(e))


if __name__ == '__main__':
    main()
