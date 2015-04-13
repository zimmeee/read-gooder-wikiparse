# read-gooder-wikiparse
Parsing wikipedia content into plain text and creating small reading comprehension questions

### Dependencies
* [wikiextractor](https://github.com/attardi/wikiextractor) - Simple and fast tool for extracting plain text from Wikipedia dumps.

Fetch some wikipedia data
```
wget http://en.wikipedia.org/wiki/Special:Export/Train -O Train.xml
```

Convert the article to text using wikiextractor
```
mkdir TextExtract
python WikiExtractor.py Train.xml -o TextExtract
```




Get a big chunk of wikipedia articles:
```
wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
```
