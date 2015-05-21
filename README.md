# read-gooder-wikiparse
Parsing wikipedia content into plain text and creating small reading comprehension questions

## Dependencies
This utility makes heavy use of the (Wikimedia REST API)[http://rest.wikimedia.org/en.wikipedia.org/v1/?doc#!]. In particular, we use the (HTML endpoint)[http://rest.wikimedia.org/en.wikipedia.org/v1/?doc#!/Page_content/page_html__title__get] which allows you to retrieve the latest html for a wikipedia page title.

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
    "header": "Train", # Title of document
    "section": { # Sections are made up of paragraphs or subsections or both
        "paragraphs": [ # Paragraphs is a list of paragraph
            { # A paragraph
                "sentences": [ # Sentences is a list of sentence
                    { # sentence has num_words and a list of sentence_parts
                        "num_words": 26, 
                        "sentence_parts": [
                            { # sentence_parts have an indent amount and text
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
                "header": "Types", # Title of the section
                "paragraphs": [ # Paragraphs in that section
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



