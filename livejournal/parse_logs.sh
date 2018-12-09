#!/bin/bash

log_file=$1

echo "Loaded comments (messages count)" `grep -P "xml\. total: \d+\, uncorrect:" $log_file | wc -l`
echo "Loaded comments (0 comments)" `grep -Pi "xml. total: 0, uncorrect:" $log_file | wc -l`
echo "Loaded comments (1-9 comments)" `grep -Pi "xml. total: [1-9], uncorrect:" $log_file | wc -l`
echo "Loaded comments (10 - 99 comments)" `grep -P "xml. total: [1-9][0-9], uncorrect: " $log_file | wc -l`
echo "Loaded comments (100 - 999 comments)" `grep -P "xml. total: [1-9][0-9][0-9], uncorrect:" $log_file | wc -l`
echo "Loaded comments (1000+ comments)" `grep -P "xml. total: [1-9][0-9][0-9]\d+, uncorrect" $log_file | wc -l`

echo "WARNING: root: Can't extract publ date for " `grep "WARNING: root: Can't extract publ date for " $log_file | wc -l`
echo "ERROR: root: Did not extract 'content'" `grep "ERROR: root: Did not extract 'content'" $log_file | wc -l`

echo "INFO: root: Successfully saved " `grep "INFO: root: Successfully saved " $log_file | wc -l `

echo "ERROR: root: failed to process item" `grep "ERROR: root: failed to process item" $log_file | wc -l`

echo "HTTP Error 403: Forbidden" `grep "HTTP Error 403: Forbidden" $log_file | wc -l`
echo "HTTP Error 4**:" `grep -P "HTTP Error 4\d\d:" $log_file | wc -l`

echo "ERROR:" `grep "ERROR:"  $log_file | wc -l`
echo "WARNING" `grep "WARNING" $log_file | wc -l`

