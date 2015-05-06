# read-gooder-wikiparse
Parsing wikipedia content into plain text and creating small reading comprehension questions

### Dependencies
* [wikiextractor](https://github.com/zimmeee/wikiextractor) - Simple and fast tool for extracting plain text from Wikipedia dumps. Noah made minor modifications to improve section header output. 

Fetch some wikipedia data
```
Single article
wget http://en.wikipedia.org/wiki/Special:Export/Train -O Train.xml

Chunk of articles (46MB)
wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles1.xml-p000000010p000010000.bz2
```

Convert the article to text using wikiextractor
```
mkdir TextExtract
python WikiExtractor.py Train.xml -s -o TextExtract
```

Get a big chunk of wikipedia articles:
```
wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2
```
