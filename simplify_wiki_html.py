"""

created by noah on 4/30/15
"""
import sys
import argparse

from bs4 import BeautifulSoup
from collections import OrderedDict
from xml.etree import ElementTree
from urllib2 import urlopen

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



HTML_SECTION_HEADERS = ["h2", "h3", "h4", "h5"]
HTML_PARAGRAPH = 'p'
HTML_TITLE = 'title'
HTML_BODY = 'body'
LEVEL = 'level'
HEADER = 'header'
SECTION = 'section'
SECTIONS = 'sections'
PARAGRAPHS = 'paragraphs'

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



def tidy_text(text):
    tidy = text

    # Remove citations
    tidy = citation_regex.sub("", tidy)

    return tidy


def parse_paragraph(paragraph):
    jparagraph = dict()
    jparagraph["sentences"] = list()
    jsentences = list()
    jsentence = dict()

    total_words = 0

    if paragraph.text is not None:
        sentences = sent_tokenize(paragraph.text)

        for sentence in sentences:
            # Clean the sentence
            sentence = tidy_text(sentence)
            jsentence_parts, num_words = line_length_tokenizer(sentence, 4)
            jsentence["sentence_parts"] = deepcopy(jsentence_parts)
            jsentence["num_words"] = num_words
            jparagraph["sentences"].append(deepcopy(jsentence))
            total_words += num_words

    return jparagraph, total_words


def process_section(element, d):
    for child in element:
        if child.tag == HTML_PARAGRAPH:
            sentences, num_words = parse_paragraph(child)
            if PARAGRAPHS not in d:
                d[PARAGRAPHS] = list()
            d[PARAGRAPHS].append(sentences)
        elif child.tag == SECTION:
            section_title = child.get(HTML_TITLE)
            new_section = OrderedDict()
            new_section[HEADER] = section_title
            new_section = process_section(child, new_section)

            if SECTION not in d:
                d[SECTION] = list()

            d[SECTION].append(new_section)

    return d


def process_outline(element, depth):

    for child in element:
        if child.tag == HTML_PARAGRAPH:
            continue
        elif child.tag == SECTION:
            print '  '*depth + child.get(HTML_TITLE)
            process_outline(child, depth+1)

    return depth



def elementtree_to_json(root):

    document = dict()
    document[HEADER] = root.get(HTML_TITLE)
    document[SECTION] = list()
    document[SECTION] = process_section(root, OrderedDict())

    # Print an outline from the ElementTree object
    # process_outline(root, 0)

    return document



def convert_to_xml(source):
    outline_stack = []
    root_element = None

    for action, elem in ElementTree.iterparse(source):

        if elem.tag == HTML_TITLE:
            root_element = ElementTree.Element(SECTION, {LEVEL: '0', HTML_TITLE: elem.text})
            outline_stack.append(root_element)

        if elem.tag in HTML_SECTION_HEADERS:
            # Entered a new section
            parent_section = None
            current_section = outline_stack.pop()
            new_section = ElementTree.Element(SECTION, {LEVEL: element_level(elem), HTML_TITLE: elem.text.strip()})

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

            # This adds the sub-element in the tree
            parent_section.append(new_section)

            # This keeps track of the stack
            outline_stack.append(parent_section)
            outline_stack.append(new_section)

        elif elem.tag == 'p' or elem.tag == 'dd':
            soup = BeautifulSoup(ElementTree.tostring(elem))
            paragraph_text = re.sub("\s\s+", " ", soup.get_text())
            current_section = outline_stack[-1]

            new_paragraph_section = ElementTree.Element(HTML_PARAGRAPH, {LEVEL: '0', HTML_TITLE: 'p'})
            new_paragraph_section.text = paragraph_text
            current_section.append(new_paragraph_section)

    return root_element


def test_function():
    return "SimplifyWikiHTML return"


def goodify_wiki(source):
    # source = urlopen(url)
    root_element = convert_to_xml(source)
    json_result = elementtree_to_json(root_element)
    return json_result


def main():
    endpoint = "http://rest.wikimedia.org:80/en.wikipedia.org/v1/page/html/"

    parser = argparse.ArgumentParser(description="Convert a wikipedia page into OpenMind JSON format")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--title", help="title of the wikipedia article to process")
    group.add_argument("-f", "--file", help="path to local HTML file")
    args = parser.parse_args()

    source = None

    if not (args.title or args.file):
        parser.print_help()
        return

    if args.title:
        source = urlopen(endpoint + args.title)
    elif args.file:
        source = open(args.file)
    else:
        parser.error("hello world")

    if source:
        json_result = goodify_wiki(source)
        print(json.dumps(json_result, indent=4, sort_keys=True, ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())