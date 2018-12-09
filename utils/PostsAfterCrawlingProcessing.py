#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import logging

import os
import numpy as np

from PostWithCommentsXml import PostWithCommentsXmlHandler
from utils.crawler_utils import FromFileFetcher, process_items_simulteaniously, setup_logging


class PostsAfterCrawlingProcessor():
    def __init__(self, opts):
        self._opts = opts

    def _process_xml(self, xml_path):
        post = PostWithCommentsXmlHandler(xml_path)

        content_len = post.content_len()
        comments_count = post.comments_count()

        if (self._opts.delete is True and
                (content_len < self._opts.min_len_content
                and comments_count < self._opts.min_comments_count) ):
            os.remove(xml_path)
            logging.info('Removed %s', xml_path)
            return

        title_len = post.title_len()
        comments_lens = post.comments_lens()

        if comments_lens is None or len(comments_lens) == 0:
            comment_mean = comment_median = comment_min = comment_max = 0
        else:
            comment_mean = np.mean(comments_lens)
            comment_median = np.median(comments_lens)
            comment_min = np.min(comments_lens)
            comment_max = np.max(comments_lens)

        logging.info('{}:{};{};{};{};{};{};{}'.format(
            xml_path,
            content_len,
            title_len,
            comments_count,
            comment_mean,
            comment_median,
            comment_min,
            comment_max))

    def __call__(self, item):
        if os.path.isfile(item):
            self._process_xml(item)
        else:
            logging.error("'{}'' not file!".format(item))


def process_docs(opts):
    procs = PostsAfterCrawlingProcessor(opts)
    fetcher = FromFileFetcher(opts)
    process_items_simulteaniously(opts, fetcher, procs)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--proc_cnt", "-p", default=2, type=int,
                        help="count of processes")

    parser.add_argument("--verbose", "-v", action="store_true")

    parser.add_argument("--delay", "-d", default=0, type=float,
                        help="delay between fetching items")

    parser.add_argument("--min_len_content", default=1, type=int,
                        help="min length of content")
    parser.add_argument("--min_comments_count", default=1, type=int,
                        help="min length of content")
    parser.add_argument("--delete", default=False, type=bool,
                        help="delete xml file, if len_content < min_len_content and comments_count < min_comments_count")

    parser.add_argument("--to_process_items", "-f", required=True, type=str,
                        help="path to file with items, item is path to xml")
    parser.add_argument("--added_items", default=None, type=str,
                        help="already processed items file.")

    parser.set_defaults(func=process_docs)

    args = parser.parse_args()

    setup_logging(args)

    try:
        args.func(args)
    except Exception as e:
        logging.exception("failed to communicate: %s " % str(e))


if __name__ == '__main__':
    main()
