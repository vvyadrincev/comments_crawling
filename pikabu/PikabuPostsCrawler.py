#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import logging
import xml.etree.ElementTree as ET
import datetime
import collections
import os
import lxml.html
import re
import sys

sys.path.append('../')
from PostWithCommentsXml import PostWithCommentsXml

sys.path.append('../utils')
from crawler_utils import Downloader, FromFileFetcher, IdsGenerateFetcher, process_items_simulteaniously, setup_logging


class PikabuCommentsProcessor(object):
    def __init__(self, opts):
        self._opts = opts
        self.downloader = Downloader(delay=opts.download_delay,
                                              mode="requests",
                                              timeout=300)

        if not os.path.isdir(self._opts.out_dir):
            os.mkdir(self._opts.out_dir)

        self.current_subdir = 1
        self.max_files_count_per_dir = 50100
        self.current_dir = os.path.join(self._opts.out_dir, str(self.current_subdir))
        self.enshure_that_dir_exists(self.current_dir)

    def __call__(self, item):
        self._process_post_id(item)

    def _process_post_id(self, post_id):
        comments = self._download_comments(post_id)

        logging.info("Loaded %s comments for %s post", len(comments), post_id)
        self._save_xml(post_id, comments)

    def _make_comments_download_url(self, post_id):
        url = "https://pikabu.ru/generate_xml_comm.php?id=" + str(post_id)
        return url

    def _make_comment_url(self, post_id, doc_id):
        return "https://pikabu.ru/story/" + str(post_id) + "?comment=" + doc_id

    def _make_post_url(self, post_id):
        return "https://pikabu.ru/story/_" + str(post_id)

    def _download_comments(self, post_id):
        url = self._make_comments_download_url(post_id)
        res_cont = self.downloader.download(url)
        comments = ET.fromstring(res_cont.encode('utf-8'))
        return comments

    def _extract_content_from_elem(self, elem, sep=' '):
        content = ""
        for t in elem.itertext():
            content += t + sep
        return content

    def _save_xml(self, post_id, comments):
        xml = PostWithCommentsXml(post_id, "post")

        res_cont = self.downloader.download(self._make_post_url(post_id))
        ht = lxml.html.fromstring(res_cont)

        title = descr = url = publ_date = ''
        author_name = author_href = tags = ''
        story_rating = comments_count = ''

        try:
            title = ht.xpath("/html/head/title/text()")[0]
        except Exception as e:
            logging.warning("Post %s. Title extracting err: %s", post_id, str(e))

        try:
            url = ht.xpath("/html/head/link[@rel='canonical']/@href")[0]
        except Exception as e:
            logging.warning("Post %s. Url extracting err: %s", post_id, str(e))

        try:
            publ_date = ht.xpath("//div[@class='user__info-item']/time/@datetime")[0]
        except Exception as e:
            logging.warning("Post %s. Publ_date extracting err: %s", post_id, str(e))

        try:
            for xp in ["/html/head/meta[@name='og:description']/@content",
                       "/html/head/meta[@name='twitter:description']/@content",
                       "/html/head/meta[@name='description']/@content"]:
                descr_ = ht.xpath(xp)
                if len(descr_) > 0:
                    descr = descr_[0]
                    break
        except Exception as e:
            logging.warning("Post %s. descr_ extracting err: %s", post_id, str(e))

        try:
            author = ht.xpath("//div[@class='story__user user']/a/@href")[0][2:]
        except Exception as e:
            logging.warning("Post %s. Author extracting err: %s", post_id, str(e))

        try:
            for tag in ht.xpath("//div[@class='story__tags tags']/a/text()"):
                tags += tag.lstrip().rstrip() + ";"
            if len(tags) > 0: tags = tags[:-1]

            story_rating = ht.xpath("//div[@class='story__rating-count']/text()")
            if len(story_rating) > 0: story_rating = story_rating[0].lstrip().rstrip()

            comments_count = ht.xpath("//a[@class='story__comments-count story__to-comments']//span[2]/text()")
            if len(comments_count) > 0:
                comments_count = comments_count[0]
                m = re.match("\d+", comments_count)
                if m is not None:
                    comments_count = m.group(0)
        except Exception as e:
            logging.warning("Post %s. Some meta extracting err: %s", post_id, str(e))

        if url == "":
            url = self._make_post_url(post_id)

        m = re.match("^(\d{4}\-\d{2}\-\d{2}T\d{2}\:\d{2}\:\d{2}).*", str(publ_date))
        if m:
            publ_date = datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")  # datetime.datetime
        elif publ_date.isdigit():
            publ_date = datetime.datetime.fromtimestamp(float(publ_date))

        xml.add_meta("title", title)
        xml.add_meta("url", url)
        xml.add_meta("description", descr)
        xml.add_meta("tags", tags)
        xml.add_meta("author", author)
        # xml.add_meta ("author_href", author_href)
        xml.add_meta("story_rating", story_rating)
        xml.add_meta("publ_date", str(publ_date))
        xml.add_meta("story_comments_count", comments_count)

        cont = ""
        for p_text in ht.xpath("//div[@class='story__main']//p/text()"):
            cont += p_text + '\n'

        logging.info("Content len of '%s' is %s", post_id, len(cont))

        xml.set_content(cont)

        comments_by_id = {}
        for comment in comments:
            comments_by_id[int(comment.attrib['id'])] = comment

        comments_by_id_ = collections.OrderedDict(sorted(comments_by_id.items()))

        for i in comments_by_id_:
            comment = comments_by_id[i]

            comment_id = int(comment.attrib['id'])
            parent = int(comment.attrib['answer'])
            comment_content = comment.text.strip()

            additional = {}
            additional['author'] = str(comment.attrib['nick'])
            additional['publication_date'] = str(comment.attrib['date'])
            additional['rating'] = str(comment.attrib['rating'])

            logging.debug("Adding comment %s, parent: %s, content len: %s" %
                          (comment_id, parent, len(comment_content)))

            xml.add_comment(id=comment_id,
                            parent=parent,
                            content=comment_content,
                            additional=additional)

        if len(os.listdir(self.current_dir)) > self.max_files_count_per_dir:
            self.current_subdir = self.current_subdir + 1
            self.current_dir = os.path.join(self._opts.out_dir, str(self.current_subdir))
            self.enshure_that_dir_exists(self.current_dir)

        xml.save(os.path.join(self.current_dir, str(post_id) + '.xml'))

    def enshure_that_dir_exists(self, dir):
        if os.path.exists(dir):
            if os.path.isdir(dir):
                return True
            else:
                logging.info('Dir path is alreasy exists (file: %s). Increasing dirname...', dir)
                self.current_subdir = self.current_subdir + 1
                self.current_dir = os.path.join(self._opts.out_dir, str(self.current_subdir))
                self.enshure_that_dir_exists(self.current_dir)
        else:
            os.mkdir(dir)

#################################################################################################
def process_docs(opts):
    procs = PikabuCommentsProcessor(opts)
    if not opts.crawl_from:
        fetcher = IdsGenerateFetcher(opts)
    else:
        fetcher = FromFileFetcher(opts)

    process_items_simulteaniously(opts, fetcher, procs)
#################################################################################################

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--proc_cnt", "-p", default=2, type=int,
                        help="count of processes")

    parser.add_argument("--verbose", "-v", action="store_true")

    parser.add_argument("--delay", "-d", default=0, type=float,
                        help="delay between fetching items")
    parser.add_argument("--download_delay", default=0.2, type=float,
                        help="delay between download items by Downloader")

    parser.add_argument("--min_len", default=1, type=int,
                        help="min length of content")

    parser.add_argument("--crawl_from", "-f", default="", type=str,
                        help="crawl from file, file contains ids")
    parser.add_argument("--added_items", default=None, type=str,
                        help="already added items file (where ids list). The doc with this ID will not be downloaded!")

    parser.add_argument("--start_id", default=4725356, type=int,
                        help="Story https://pikabu.ru/story/_4725356 is first in 2017")
    parser.add_argument("--max_id", default=5900100, type=int,
                        help="max id. was 5273009 at 15:50 18-08-2017")
    parser.add_argument("--step", default=1, type=int,
                        help="step for random generation")
    parser.add_argument("--shuffle", default=True, type=bool,
                        help="generated ids random shuffle")

    parser.add_argument("--out_dir", default="./pikabu_comments", type=str,
                        help="dir path, where will be saved comments xmls!")

    parser.set_defaults(func=process_docs)

    args = parser.parse_args()

    setup_logging(args)

    try:
        args.func(args)
    except Exception as e:
        logging.exception("failed to communicate: %s " % str(e))


if __name__ == '__main__':
    main()
