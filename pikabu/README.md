# Crawler for pikabu posts with comments

##### Source: https://pikabu.ru

### Pikapu API
We are using XML API: https://pikabu.ru/generate_xml_comm.php?id=<POST_ID>, where POST_ID - id of the POST

**List if items (post ids) are generating from 'start_id' to 'max_id' with 'step'.**
 
**'max_id' was 5273009 at 15:50 18-08-2017**

## PikabuPostsCrawler (download and save to xml)
* ``` ./PikabuPostsCrawler.py --start_id=123464 --max_id=123466 --added_items=already_added.list ```

