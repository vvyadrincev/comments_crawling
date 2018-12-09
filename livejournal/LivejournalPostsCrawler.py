#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import logging
import datetime
import re
import os
import lxml.html
import json
import sys

sys.path.append('../')
from PostWithCommentsXml import PostWithCommentsXml

sys.path.append('../utils')
from crawler_utils import FromFileFetcher, process_items_simulteaniously, setup_logging

from LivejournalDownloader import LiveJournalStyle_Downloader


class LivejournalCommentsProcessor():
    def __init__(self, opts):
        self._opts = opts

        self.downloader = LiveJournalStyle_Downloader(delay=opts.download_delay)

        self.url_re_pat = re.compile("https?\://([^\.]+)\.livejournal\.com\/([^\.]+)\.html")

        self.js_parse_pattern = re.compile(
            '\"thread_url\":\"https?\://[^\.]+\.livejournal\.com/\d+\.html\?thread=\d+\#t\d+\"\,\"above\"\:null\,')
        self.comment_from_js_pattern = re.compile(".*thread\=(\d+)\#.*")

        self._ensure_that_folder_exists_2(self._opts.out_dir)

        self.current_subdir = 1
        self.max_files_count_per_dir = 50100
        self.current_dir = os.path.join(self._opts.out_dir, str(self.current_subdir))
        self.enshure_that_dir_exists(self.current_dir)
        self.redownloaded = set()

    def __call__(self, item):
        self.empty_comment_count = 0
        self.uncorrect_comments_count = 0
        self._process_url(item)
        self.redownloaded = set()

    def _process_url(self, url):

        self.already_processed_comments = set()

        res_cont = self.downloader.download(url)
        ht = lxml.html.fromstring(res_cont)

        title = ""
        description = ""
        tags = ""

        try:
            title_ = ht.xpath("//h1[@class=' b-singlepost-title entry-title p-name ']")
            if len(title_) > 0:
                title = title_[0].text  # str
                title = self._normalise_string(title)

            description_ = ht.xpath("//meta[@name='description']/@content")
            if len(description_) > 0:
                description = description_[0]  # str
                description = self._normalise_string(description)

            for tag in ht.xpath("//meta[@property='article:tag']/@content"):  # list
                tags += tag.lstrip().rstrip() + ";"
            if len(tags) > 0: tags = tags[:-1]

        except Exception as e:
            logging.error("Can't extract some meta for '%s'. Error: ", url, str(e))
            return

        publ_date = ""
        if len(ht.xpath("//dd[@class='b-singlepost-author-userinfo']/div[1]/time/a")) == 3:
            year_month_day = ht.xpath("//dd[@class='b-singlepost-author-userinfo']/div[1]/time/a")
            for i in year_month_day:
                if isinstance(i.text, (str,)):
                    publ_date += i.text + "-"
            publ_date = publ_date[:-1]
        else:
            publ_date = datetime.datetime.now()
            publ_date = publ_date.strftime('%Y-%m-%d')
            logging.warning("Can't extract publ date for '%s'", url)

        publ_date = datetime.datetime.strptime(publ_date, "%Y-%m-%d")  # datetime.datetime

        try:
            url_xpath_res = ht.xpath("//meta[@property='og:url']/@content")
            if len(url_xpath_res) > 0:
                m = re.match(self.url_re_pat, url_xpath_res[0])
            else:
                m = re.match(self.url_re_pat, url)
            author = m.group(1)
            post_id = m.group(2)
        except Exception as e:
            logging.error("Can't extract author and post_id for %s", url)
            return

        content = ''
        # cont_xpath_result = ht.xpath("//article[@class=' b-singlepost-body entry-content e-content ']")
        cont_xpath_result = ht.xpath("//div[@class='b-singlepost-bodywrapper']/article")

        if len(cont_xpath_result) > 0:
            content = self._extract_content_from_elem(cont_xpath_result[0], '\n')
        else:
            logging.error("Did not extract 'content' for %s", url)

        self.__xml = PostWithCommentsXml(post_id, "post")
        self.__xml.set_content(content)
        self.__xml.add_meta("title", title)
        self.__xml.add_meta("url", url)
        self.__xml.add_meta("description", description)
        self.__xml.add_meta("tags", tags)
        self.__xml.add_meta("author", author)
        self.__xml.add_meta("publ_date", str(publ_date))

        for root_comment_ in re.findall(self.js_parse_pattern, res_cont):
            comment_id = re.match(self.comment_from_js_pattern, root_comment_).group(1)
            self._process_comment_id(author, post_id, comment_id)

        next_page_url = self._extract_next_page(ht)
        while next_page_url is not None:
            logging.info("Processing page %s", next_page_url)
            res_cont = self.downloader.download(next_page_url)
            ht = lxml.html.fromstring(res_cont)
            for root_comment_ in re.findall(self.js_parse_pattern, res_cont):
                comment_id = re.match(self.comment_from_js_pattern, root_comment_).group(1)
                self._process_comment_id(author, post_id, comment_id)

            next_page_url = self._extract_next_page(ht)

        if len(os.listdir(self.current_dir)) > self.max_files_count_per_dir:
            self.current_subdir = self.current_subdir + 1
            self.current_dir = os.path.join(self._opts.out_dir, str(self.current_subdir))
            self.enshure_that_dir_exists(self.current_dir)

        self._ensure_that_folder_exists_2(os.path.join(self.current_dir, author))

        logging.info("%s: %s. total: %s, uncorrect: %s, empty: %s", url,
                     (os.path.join(self.current_dir, author, str(post_id) + '.xml')), self.__xml.comments_count(),
                     self.uncorrect_comments_count, self.empty_comment_count)
        self.__xml.save(os.path.join(self.current_dir, author, str(post_id) + '.xml'))

    def _extract_next_page(self, ht):
        n = ht.xpath("//link[@rel='next']/@href")
        if len(n) > 0:
            logging.debug("Extracted next page: %s", n[0])
            return n[0]
        else:
            return None

    def _process_comment_id(self, author, post_id, comment_id, parent_id=0):
        if comment_id not in self.already_processed_comments:
            logging.debug("Processing comment_id %s; author: %s; post_id: %s; parent_id: %s", comment_id, author,
                          post_id, parent_id)

            thread_url = self._make_thread_json_rpc_download_url(author, post_id, comment_id)
            comment_thread_js = self._download_thread_json(thread_url)

            logging.debug("replycount: %s for %s", comment_thread_js["replycount"], thread_url)

            if 'comments' not in comment_thread_js:
                logging.warning(
                    "'comments' not in comment_thread_js. comment_id %s; author: %s; post_id: %s; parent_id: %s. thread_url: %s",
                    comment_id, author, post_id, parent_id, thread_url)

            for comment in comment_thread_js["comments"]:
                comment_id_ = self._get_by_key(comment, 'dtalkid')
                parent = self._get_by_key(comment, 'parent', 0)
                # loaded = self._get_by_key(comment, 'loaded', 0)
                deleted = self._get_by_key(comment, 'deleted', 0)
                collapsed = self._get_by_key(comment, 'collapsed', 0)
                above = self._get_by_key(comment, 'above', 0)

                comment_content = self._get_by_key(comment, 'article')
                talkid = self._get_by_key(comment, 'talkid')
                username = self._get_by_key(comment, 'uname')

                comment_ts = ""
                if 'ctime_ts' in comment:
                    comment_ts = datetime.datetime.fromtimestamp(int(comment["ctime_ts"])).strftime('%Y-%m-%d %H:%M:%S')

                thread_url = self._get_by_key(comment, 'thread_url')

                self._add_comment_to_xml(comment_id_, comment_content,
                                         talkid, username, comment_ts,
                                         parent, above, deleted, thread_url)
                if collapsed:
                    self._process_comment_id(author, post_id, comment_id_, parent)

        else:
            logging.debug("Comment %s is already added to xml!", comment_id)

    def _get_by_key(self, dic, key, def_value=""):
        if isinstance(dic, (dict,)):
            if key in dic:
                return dic[key]
            else:
                logging.debug("%s not in dic!. keys: %s", key, dic.keys())
        else:
            logging.debug(' not dict! type: %s, len: %s', type(dic), len(dic))

        return def_value

    def _ensure_that_folder_exists_2(self, folderpath):
        if not os.path.isdir(folderpath):
            if os.path.isfile(folderpath):
                logging.debug("!! out_dir '%s' is file, not dir", folderpath)
            else:
                os.mkdir(folderpath)
                logging.debug("Mkdir: '%s'", folderpath)

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

    def _normalise_string(self, s):
        if isinstance(s, (str, )):
            s = s.strip()
        else:
            s = u""
        return s

    def _make_thread_json_rpc_download_url(self, author, post_id, comment_id):
        return "https://" + str(author) + ".livejournal.com/" + str(author) + "/__rpc_get_thread?journal=" + str(
            author) + "&itemid=" + str(post_id) + "&thread=" + str(comment_id) + "&expand_all=1"

    def _download_thread_json(self, thread_url):
        return json.loads(self.downloader.download(thread_url))

    def _extract_content_from_elem(self, elem, sep=' '):
        content = ""
        for t in elem.itertext():
            content += t + sep
        return content

    def _add_comment_to_xml(self, comment_id, comment_content,
                            talkid, username, comment_ts,
                            parent, above, deleted, thread_url):
        if str(comment_id).isdigit() and str(talkid).isdigit():
            self.__xml.add_comment(id=comment_id,
                                   parent=parent,
                                   content=comment_content,
                                   additional={
                                       "publication_date": comment_ts,
                                       "author": username,
                                       "talkid": talkid,
                                       "above": above,
                                       "thread_url": thread_url
                                   })
        else:
            self.uncorrect_comments_count += 1

        if len(comment_content) == 0:
            self.empty_comment_count += 1

        self.already_processed_comments.add(comment_id)
        logging.debug("Comment %s added to xml. content len: %s", comment_id, len(comment_content))


######################################################################################################
def process_docs(opts):
    procs = LivejournalCommentsProcessor(opts)
    fetcher = FromFileFetcher(opts)
    process_items_simulteaniously(opts, fetcher, procs)
######################################################################################################

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proc_cnt", "-p", default=1, type=int,
                        help="count of processes")

    parser.add_argument("--verbose", "-v", action="store_true")

    parser.add_argument("--delay", "-d", default=0, type=float,
                        help="delay between fetching items")

    parser.add_argument("--download_delay", default=1.0, type=float,
                        help="delay between download items by Downloader")

    parser.add_argument("--out_dir", default="./livejournal_comments", type=str,
                        help="dir path, where will be saved comments xmls!")

    parser.add_argument("--min_len", default=1, type=int,
                        help="min length of content")

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
        logging.exception("failed to communicate: %s " % str(e))


if __name__ == '__main__':
    main()
