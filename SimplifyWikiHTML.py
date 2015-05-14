"""

created by noah on 4/30/15
"""
import sys

from bs4 import BeautifulSoup

from xml.etree import ElementTree

import re
import json
import string
from pprint import pprint

from copy import deepcopy

import nltk
import nltk.data
from nltk import word_tokenize
from nltk import sent_tokenize
from nltk.tokenize import WhitespaceTokenizer

from urllib2 import urlopen

SECTION_HEADERS = ["h2", "h3", "h4", "h5"]
SECTION = 'section'
LEVEL = 'level'
TITLE = 'title'
BODY = 'body'

# Detect wikipedia style citations
# for example: "[2] There are various"
citation_regex = re.compile('\s*\[\d\]\s*')

def element_level(element):
    level = None

    try:
        level = element.tag[re.search('\d', element.tag).start()]
    except:
        pass

    return level


def is_subsection(element1, element2):
    return int(element1.get(LEVEL)) > int(element2.get(LEVEL))


def is_sibsection(element1, element2):
    return int(element1.get(LEVEL)) == int(element2.get(LEVEL))


def make_outline(simplified_html):
    for section in simplified_html.iter():
        section_title = section.get(TITLE)
        section_level = int(section.get(LEVEL))

        print '  ' * section_level + section_title


def line_length_tokenizer(sentence, length):
    sentence_parts = list()
    sentence_part  = dict()
    words = WhitespaceTokenizer().tokenize(sentence)
    num_words = len(words)

    if num_words > 0:
        num_sentence_parts = (num_words / length) if (num_words % length) == 0 else (num_words / length) + 1

        for i in range(0, num_sentence_parts):
            start = i * length
            end = start + length if start + length < num_words else num_words
            sentence_part['indent'] = 0
            sentence_part['text'] = ' '.join(words[start:end])
            sentence_parts.append(deepcopy(sentence_part))

    return sentence_parts, num_words


def outline_dict(outline_stack):
    o_dict = {}
    max_depth = len(outline_stack)

    for i in range(0, 5):
        text = outline_stack[i] if i < max_depth else None
        o_dict["H"+str(i+1)] = text

    return o_dict


def tidy_text(text):
    tidy = text

    # Remove citations
    tidy = citation_regex.sub("", tidy)

    return tidy


def convert_to_json(simplified_html):
    # make_outline(simplified_html)

    document = dict()
    jsentences = list()
    jsentence = dict()
    jsentence_parts = list()
    jsentence_part = dict()
    total_words = 0
    total_sentences = 0

    document["a_title"] = simplified_html.get(TITLE)

    outline_stack = []
    current_level = -1

    for section in simplified_html.iter():
        section_title = section.get(TITLE)
        section_level = int(section.get(LEVEL))

        while section_level <= current_level:
            outline_stack.pop()
            current_level -= 1

        current_level = section_level
        outline_stack.append(section_title)
        headers = outline_dict(outline_stack)

        if section.text is not None:
            sentences = sent_tokenize(section.text)
            jsentence = deepcopy(headers)

            for sentence in sentences:
                # Clean the sentence
                jsentence_parts, num_words = line_length_tokenizer(tidy_text(sentence), 4)
                jsentence["sentence_parts"] = deepcopy(jsentence_parts)
                jsentence["num_words"] = num_words
                jsentences.append(deepcopy(jsentence))
                total_words += num_words

            total_sentences += len(sentences)

    document["sentences"] = jsentences
    document["num_words"] = total_words
    document["num_sentences"] = total_sentences

    print "Finished encoding article %s (%s sentences, %s words)" % (document["a_title"], total_sentences, total_words)

    # print(json.dumps(document, indent=4, sort_keys=True))

    return document


def add_outline_sections(source):
    outline_stack = []
    root_element = None

    for action, elem in ElementTree.iterparse(source):

        if elem.tag == TITLE:
            root_element = ElementTree.Element(SECTION, {LEVEL: '0', TITLE: elem.text})
            outline_stack.append(root_element)

        if elem.tag in SECTION_HEADERS:
            # Entered a new section
            parent_section = None
            current_section = outline_stack.pop()
            new_section = ElementTree.Element(SECTION, {LEVEL: element_level(elem), TITLE: elem.text.strip()})

            if is_subsection(new_section, current_section):
                parent_section = current_section
            else:
                while outline_stack:
                    parent_section = outline_stack.pop()

                    if is_sibsection(parent_section, new_section) or is_subsection(parent_section, new_section):
                        continue
                    else:
                        break

                if parent_section is None:
                    parent_section = root_element

            # This adds the subelement in the tree
            parent_section.append(new_section)

            # This keeps track of the stack
            outline_stack.append(parent_section)
            outline_stack.append(new_section)

        elif elem.tag == 'p' or elem.tag == 'dd':
            soup = BeautifulSoup(ElementTree.tostring(elem))
            paragraph_text = re.sub("\s\s+", " ", soup.get_text())
            current_section = outline_stack[-1]
            current_section.text = paragraph_text if current_section.text is None else current_section.text + paragraph_text

    return root_element


def test_function():
    return "SimplifyWikiHTML return"


def goodify_wiki(url):
    source = urlopen(url)
    root_element = add_outline_sections(source)
    # make_outline(root_element)
    json_result = convert_to_json(root_element)
    return json_result


def main():
    # Open from file
    # source = open("css/GabrielTrain.html")
    json_result = goodify_wiki("http://rest.wikimedia.org:80/en.wikipedia.org/v1/page/html/Train")
    print(json.dumps(json_result, indent=4, sort_keys=True, ensure_ascii=False))




if __name__ == '__main__':
    sys.exit(main())