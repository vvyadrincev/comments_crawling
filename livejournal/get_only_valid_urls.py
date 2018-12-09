#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re

"""
Simple utility for extracting 'clear' article urls!
"""
in_dir = './article_lists_orig'
out_dir = './article_lists'
for author in os.listdir(in_dir):
    with open (os.path.join(out_dir, author), 'w') as fo:
        with open (os.path.join(in_dir, author)) as fi:
            for url in fi.readlines():
                if re.match("https://"+author+".livejournal.com/\d+.html\n", url):
                    fo.write(url)