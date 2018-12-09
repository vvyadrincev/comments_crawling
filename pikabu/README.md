# Crawler for pikabu posts with comments

##### Source: https://pikabu.ru

### Pikapu API
We are using XML API: https://pikabu.ru/generate_xml_comm.php?id=<POST_ID>, where POST_ID - id of the POST

**List if items (post ids) are generating from 'start_id' to 'max_id' with 'step'.**
 
**'max_id' was 5273009 at 15:50 18-08-2017**

## PikabuCommentsCommunicator supports two modes:
1. Adding each comment to Queue
2. Save post with comments to xml file

### PikabuCommentsCommunicator first mode:
* ``` ./PikabuCommentsCommunicator.py -c 1234 -p 2 --start_id=123464 --max_id=123466 --added_items=already_added.list ```
* ``` ./PikabuCommentsCommunicator.py -c 1234 -p 2 --crawl_from=to_process.list --added_items=already_added.list ```

Extracting metafields: 
* 200 : nick / author
* 203 : date    # 2017-08-18
* 81  : rating  # int 
* 202 : post id
* 80  : parent comment id ( zero when comment if for post itself)  >=0 int

### PikabuCommentsCommunicator second mode: 
* ``` ./PikabuCommentsCommunicator.py -c 1234 -p 2 --start_id=123464 --max_id=123466 --added_items=already_added.list -x ```
* ``` ./PikabuCommentsCommunicator.py -c 1234 -p 2 --crawl_from=to_process.list --added_items=already_added.list -x ```


## ! PikabuPostsCrawler -- is the second mode of PikabuCommentsCommunicator
* ``` ./PikabuPostsCrawler.py --start_id=123464 --max_id=123466 --added_items=already_added.list ```

