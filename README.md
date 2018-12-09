## XML structure
```xml
<?xml version="1.0" ?>
<post id="POST_ID">
  <meta>
     <author>AUTHOR</author>
     <publ_date>2017-06-06 00:00:00</publ_date>
     <url>URL</url>
     <title>TITLE</title>
     <description></description>
     <len_content_utf_8>UTF-8_LEN</len_content_utf_8>
     <comments_count>COMMENTS_COUNT</comments_count>
  </meta>
  <content>POST CONTENT!</content>
  <comments>
     <comment author="AUTHOR" id="COMMENT_ID" parent="PARENT_COMMENT_ID" publication_date="2017-06-06 17:08:01">
        <content>COMMENT CONTENT!</content>
        <comment author="AUTHOR" id="COMMENT_ID" parent="PARENT_COMMENT_ID" publication_date="2017-06-06 17:11:00">
           <content>COMMENT CONTENT!</content>
        </comment>
     </comment>
  </comments>
</post>
```


### Converting xml to plain text 
##### Default (only post content)
```bash
./post2txt.py -i <path_to_post_with_xml>.xml -o <path_to_post_plain_text>.txt 
```
##### content + comments 
```bash
./post2txt.py -w -i <path_to_post_with_xml>.xml -o <path_to_post_plain_text>.txt 
```
##### only comments 
```bash
./post2txt.py -c -i <path_to_post_with_xml>.xml -o <path_to_post_plain_text>.txt 
```

### Collecting statistics of crawler posts with comments
```bash
nohup ./PostsAfterCrawlingProcessing.py -f <list_with_paths_to_xmls> &
```

