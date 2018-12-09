#!/bin/bash

log_file=$1

echo "Loaded comments (POST_ID count): " `grep -P "Loaded \d+ comments for \d+ post" $log_file | wc -l`
echo "Loaded 0 comments (POST_ID count): " `grep -P "Loaded 0 comments for \d+ post" $log_file | wc -l`
echo "Loaded comments (1-9 comments)" `grep -P "INFO: root: Loaded [1-9] comments for" $log_file | wc -l`
echo "Loaded comments (10 - 99 comments)" `grep -P "INFO: root: Loaded [1-9][0-9] comments for" $log_file | wc -l `
echo "Loaded comments (100 - 999 comments)" `grep -P "INFO: root: Loaded [1-9][0-9][0-9] comments for" $log_file | wc -l`
echo "Loaded comments (1000+ comments)" `grep -P "INFO: root: Loaded [1-9][0-9][0-9]\d+ comments for" $log_file | wc -l`


echo "Can't extract content for: "`grep "Can't extract content for" $log_file | wc -l`
echo "Processing doc: "`grep -P "Processing doc https\:\/\/pikabu.ru\/story\/\d+\?comment\=\d+" $log_file | wc -l`
echo "Document added to Queue: "`grep -P "Document \d+ added to Queue" $log_file | wc -l`
echo "Content is small:" `grep -P "Content of '\d+' is empty or smaller than \d+"  $log_file | wc -l`

echo "ERROR:" `grep "ERROR:"  $log_file | wc -l`
echo "WARNING:" `grep "WARNING:"  $log_file | wc -l`