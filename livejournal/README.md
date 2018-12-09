# Crawler for livejounal posts with comments

##### Source: https://www.livejournal.com/

## Tested for python2.7

### Collecting top 1000 journals
```bash
nohup ./get_top_N_journals.py -N 1000 -o top1000 &
```

### Extracting posts for 2017 year for collected 1000 top journals
```bash
nohup ./LivejournalPostsCollector.py -p 3 -y 2017 --out_dir=article_lists/ --crawl_from=top1000 &
```

### Preparing article urls
```bash
cat article_lists/* | grep -Po "https\://.*\.livejournal.com/\d+.html" > to_process.articles.list
```

### Running articles downloading process!
```bash
nohup ./LivejournalPostsCrawler.py -p 3 -f to_process.articles.list --download_delay=0.3 &
```