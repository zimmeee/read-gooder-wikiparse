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

## JSON Format

I'll try to document this a couple ways to see which one makes more sense.

### Grammar-like documentation
```
<document> ::=
	"header": STRING,
	"sections": <sections> | <paragraphs>

<section> ::=
	?"header": STRING,
	<paragraphs> | <section> | <paragraphs>,<section>

<paragraphs> ::=
	"sentences": [<sentences>]

<sentences> ::=
	[<sentence>]

<sentence> ::=
	"num_words": INT,
	"sentence_parts": [<sentence_parts>]

<sentence_parts> ::=
	"indent": INT,
	"text": STRING
```

### English-like documentation
```
{
    "header": "Train", 
    "section": {
        "paragraphs": [
            {
                "sentences": [
                    {
                        "num_words": 26, 
                        "sentence_parts": [
                            {
                                "indent": 0, 
                                "text": "A train is a"
                            }, 
                            {
                                "indent": 0, 
                                "text": "form of rail transport"
                            }, 
                            {
                                "indent": 0, 
                                "text": "consisting of a series"
                            },
                            .
                            .
                            .
                        ] # End sentence_part
                    } # End sentence
                ] # End sentences
            }, # End paragraph
            .
            .
            .
        ], # End paragraphs
        "section": [
            {
                "header": "Types", 
                "paragraphs": [
                    {
                        "sentences": [
                            {
                                "num_words": 12, 
                                "sentence_parts": [
                                    {
                                        "indent": 0, 
                                        "text": "There are various types"
                                    }, 
                                    {
                                        "indent": 0, 
                                        "text": "of trains that are"
                                    }, 
                                    {
                                        "indent": 0, 
                                        "text": "designed for particular purposes."
                                    }
                                ]
                            }, 
                        ]
                    }
                ]
            }
        ]
    }
}
```



