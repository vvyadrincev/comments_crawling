#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os
import sys

from PostWithCommentsXml import PostWithCommentsXmlHandler


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--xml_file", "-i", required=True,
                        help="input xml file")

    parser.add_argument("--out_file", "-o", default=None, type=str,
                        help="output txt file")

    parser.add_argument("--out_dir", default=None, type=str,
                        help="output dir")

    parser.add_argument("--with_comments", "-w", action="store_true",
                        help="with comments")
    parser.add_argument("--only_comments", "-c", action="store_true",
                        help="only comments")

    args = parser.parse_args()

    post = PostWithCommentsXmlHandler(args.xml_file, True)

    t = post.get_content(args.with_comments, args.only_comments)

    if args.out_file is not None and args.out_dir is not None:
        out = os.path.join(args.out_dir, args.out_file)
    elif args.out_file is not None:
        out = args.out_file
    elif args.out_dir is not None:
        out = os.path.join(args.out_dir, os.path.basename(args.xml_file) + ".txt")
    else:
        out = None

    if out is not None:
        with open(out, 'w') as f:
            if ((3,) > sys.version_info):
                f.write(t.encode('utf-8'))
            else:
                f.write(t)
    else:
        print (t)


if __name__ == '__main__':
    main()
