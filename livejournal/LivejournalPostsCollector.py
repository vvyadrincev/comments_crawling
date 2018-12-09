#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import logging
import re
import os
from lxml import html
import sys
sys.path.append('../utils')
from crawler_utils import SomePipe, FromFileFetcher, process_items_simulteaniously, setup_logging

from LivejournalDownloader import LiveJournalStyle_Downloader
downloader = LiveJournalStyle_Downloader(delay=0.2)

def year_url(url, year):
    return url + "/" + str(year) + "/"


def dayly_urls(url, year):
    global downloader
    res_cont = downloader.download(year_url(url, year))
    ht = html.fromstring(res_cont)
    return ht.xpath("//article[@class='j-e j-e-years']//span/a/@href")


def dayly_articles(url):
    global downloader
    res_cont = downloader.download(url)
    ht = html.fromstring(res_cont)
    return ht.xpath("//article//h3/a/@href")


class LivejournalPostsProcessor(SomePipe):
    def __init__(self, opts):
        self._opts = opts

        global downloader
        downloader.delay = opts.download_delay

        if not os.path.isdir(self._opts.out_dir):
            os.mkdir(self._opts.out_dir)

        self.url_re_pat = re.compile("https?\://([^\.]+)\.(livejournal\.com)?/?")

    def __call__(self, item):  # item is user url (journal url). example:  https://nemihail.livejournal.com/
        self._process_url(item)

    def _process_url(self, url):
        name = re.match(self.url_re_pat, url).group(1)

        article_urls = list()
        for d_url in dayly_urls(url, self._opts.year):
            for a_url in dayly_articles(d_url):
                logging.info("{}: {}".format(name, a_url))
                article_urls.append(a_url)

        self._save_article_urls(name, article_urls)
        logging.info("Extracted and saved %s articles for %s.", len(article_urls), name)

    def _save_article_urls(self, name, article_urls):
        with open(os.path.join(self._opts.out_dir, name), 'w') as of:
            for u in article_urls:
                of.write(u + '\n')

def process_docs(opts):
    procs = LivejournalPostsProcessor(opts)
    fetcher = FromFileFetcher(opts)
    process_items_simulteaniously(opts, fetcher, procs)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--proc_cnt", "-p", default=1, type=int,
                        help="count of processes")

    parser.add_argument("--year", "-y", required=True, type=int,
                        help="year, for which collect article urls")

    parser.add_argument("--verbose", "-v", action="store_true")

    parser.add_argument("--delay", "-d", default=0, type=float,
                        help="delay between fetching items")
    parser.add_argument("--download_delay", default=0.2, type=float,
                        help="delay between download items by Downloader")
    parser.add_argument("--out_dir", default="./livejournal_posts", type=str,
                        help="dir path, where will be saved comments xmls!")
    parser.add_argument("--crawl_from", "-f", default="", type=str,
                        help="crawl from file, file contains ids")
    parser.add_argument("--added_items", default=None, type=str,
                        help="already added items file. This item will not be downloaded!")

    parser.set_defaults(func=process_docs)

    args = parser.parse_args()

    setup_logging(args)

    try:
        args.func(args)
    except Exception as e:
        logging.exception("failed to process: %s " % str(e))

if __name__ == '__main__':
    main()
