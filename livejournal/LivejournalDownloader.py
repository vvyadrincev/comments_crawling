#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import time
import requests

import sys
sys.path.append('../utils')

class LiveJournalStyle_Downloader(object):
    def __init__(self, delay=0.):
        self.delay = delay

        FORMAT="%(asctime)s %(levelname)s: %(name)s: %(message)s"
        logging.basicConfig(level=logging.DEBUG,
                            format = FORMAT)
        self.LOGGER = logging.getLogger()

        self.last_download = time.time() - delay

        headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'),
                   ('Cookie', 'prop_opt_readability=1')] # CHECKBOX "В стиле ЖЖ" - приводит в стандартный вид!
        self.headers = headers

        self.session = requests.Session()
        self.session.headers.update(headers)

    def download(self, url, headers = None):
        # if headers is None:
        #     headers = self.headers

        self._sleep_is_need()
        self.last_download = time.time()
        return self.session.get(url).text


    def _time_diff(self):
        diff = self.delay - (time.time() - self.last_download)
        if diff < 0.:
            return 0.
        else:
            return diff

    def _sleep_is_need(self):
        if (self._time_diff() < self.delay):
            time.sleep(self._time_diff())