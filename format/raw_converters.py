"""
created by beth on 6/15/15
"""
import abc
from copy import deepcopy
from xml.etree import ElementTree
import re
from math import ceil

from bs4 import BeautifulSoup
from lxml import etree
from nltk import sent_tokenize, WhitespaceTokenizer, OrderedDict

from formatters import Formatter
from openmind_format import Document, Sentence, Paragraph, Section


class RawConverter:
    def __init__(self, sentence_formatter):
        if not isinstance(sentence_formatter, Formatter):
            raise Exception("RawConverter: this is not a Formatter")
        self.formatter = sentence_formatter

    def processRawSentences(self, raw_sentences, h1="", h2="", h3="", h4="", h5=""):
        sentences = []
        for raw_sentence in raw_sentences:
            sentence_fragments = self.formatter.format(raw_sentence)  # formatter can be of any recognized kind
            total_words_this_sentence = 0
            for fragment in sentence_fragments:
                total_words_this_sentence += fragment.len()
            sentence = Sentence(sentence_parts=sentence_fragments, numwords=total_words_this_sentence)
            sentences.append(sentence)
        return sentences

    @abc.abstractmethod
    def convertToDocument(self, rawTextOrHtml, doc_title):
        if not isinstance(rawTextOrHtml, str):
            raise Exception("This is not raw document text or html: " + str(rawTextOrHtml))
        return


class BasicTextFileRawConverter(RawConverter):
    def __init__(self, sentence_formatter):
        super().__init__(sentence_formatter)

    def convertToDocument(self, rawText, doc_title):
        raw_sentences = sent_tokenize(rawText, language='english')
        sentences = self.processRawSentences(raw_sentences)
        section = Section(paragraphs=[Paragraph(sentences=sentences)])
        return Document(header=doc_title, section=section)


class GibbonHtmlFileRawConverter(RawConverter):
    def __init__(self, sentence_formatter, htmlParser):
        super().__init__(sentence_formatter)
        self.htmlParser = htmlParser

    def convertToDocument(self, rawHtml, doc_title):
        tree = etree.fromstring(rawHtml, parser=self.htmlParser)
        root = tree.getroot()

        text = []
        for child in root.iter('p', 'i', 'h2'):
            if not child.text:
                continue
            text.append(child.text)

        full_text = " ".join(text)

        raw_sentences = sent_tokenize(full_text, language='english')

        sentences = self.processRawSentences(raw_sentences)
        section = Section(paragraphs=[Paragraph(sentences=sentences)])
        return Document(header=doc_title, section=section)


class WikiHtmlFileRawConverter(RawConverter):
    def __init__(self, sentence_formatter):
        super().__init__(sentence_formatter)

        self.HTML_SECTION_HEADERS = ["h2", "h3", "h4", "h5"]
        self.HTML_PARAGRAPH = 'p'
        self.HTML_TITLE = 'title'
        self.HTML_BODY = 'body'
        self.LEVEL = 'level'
        self.HEADER = 'header'
        self.SECTION = 'section'
        self.SECTIONS = 'sections'
        self.PARAGRAPHS = 'paragraphs'

        # Detect wikipedia style citations
        # for example: "[2] There are various"
        self.citation_regex = re.compile('\s*\[\d\]\s*')

    @staticmethod
    def element_level(element):
        level = None
        try:
            level = element.tag[re.search('\d', element.tag).start()]
        except:
            pass
        return level

    def is_subsection(self, element1, element2):
        return int(element1.get(self.LEVEL)) > int(element2.get(self.LEVEL))

    def is_sibsection(self, element1, element2):
        return int(element1.get(self.LEVEL)) == int(element2.get(self.LEVEL))

    def convert_to_xml(self, source):
        outline_stack = []
        root_element = None

        for action, elem in ElementTree.iterparse(source):

            if elem.tag == self.HTML_TITLE:
                root_element = ElementTree.Element(self.SECTION, {self.LEVEL: '0', self.HTML_TITLE: elem.text})
                outline_stack.append(root_element)

            if elem.tag in self.HTML_SECTION_HEADERS:
                # Entered a new section
                parent_section = None
                current_section = outline_stack.pop()
                new_section = ElementTree.Element(self.SECTION, {self.LEVEL: self.element_level(elem),
                                                                 self.HTML_TITLE: elem.text.strip()})

                if self.is_subsection(new_section, current_section):
                    parent_section = current_section
                else:
                    while outline_stack:
                        parent_section = outline_stack.pop()

                        if self.is_sibsection(parent_section, new_section) or \
                                self.is_subsection(parent_section, new_section):
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

                new_paragraph_section = ElementTree.Element(self.HTML_PARAGRAPH,
                                                            {self.LEVEL: '0', self.HTML_TITLE: 'p'})
                new_paragraph_section.text = paragraph_text
                current_section.append(new_paragraph_section)
        return root_element

    def line_length_tokenizer(self, sentence, length):
        sentence_parts = list()
        sentence_part = dict()
        words = WhitespaceTokenizer().tokenize(sentence)
        num_words = len(words)

        if num_words > 0:
            num_sentence_parts = ceil(num_words / length)

            for i in range(0, num_sentence_parts):
                start = i * length
                end = start + length if start + length < num_words else num_words
                sentence_part['indent'] = 0
                sentence_part['text'] = ' '.join(words[start:end])
                sentence_part['tokens'] = words[start:end]
                sentence_parts.append(deepcopy(sentence_part))

        return sentence_parts, num_words

    def tidy_text(self, text):
        tidy = text

        # Detect wikipedia style citations
        # for example: "[2] There are various"
        citation_regex = re.compile('\s*\[\d\]\s*')

        # Remove citations
        tidy = citation_regex.sub("", tidy)

        return tidy

    def parse_paragraph(self, paragraph):
        jparagraph = dict()
        jparagraph["sentences"] = list()
        jsentences = list()
        jsentence = dict()

        total_words = 0

        if paragraph.text is not None:
            sentences = sent_tokenize(paragraph.text)

            for sentence in sentences:
                # Clean the sentence
                sentence = self.tidy_text(sentence)
                jsentence_parts, num_words = self.line_length_tokenizer(sentence, 4)
                jsentence["sentence_parts"] = deepcopy(jsentence_parts)
                jsentence["num_words"] = num_words
                jparagraph["sentences"].append(deepcopy(jsentence))
                total_words += num_words

        return jparagraph, total_words

    def process_section(self, element, d):
        for child in element:
            if child.tag == self.HTML_PARAGRAPH:
                sentences, num_words = self.parse_paragraph(child)
                if self.PARAGRAPHS not in d:
                    d[self.PARAGRAPHS] = list()
                d[self.PARAGRAPHS].append(sentences)
            elif child.tag == self.SECTION:
                section_title = child.get(self.HTML_TITLE)
                new_section = OrderedDict()
                new_section[self.HEADER] = section_title
                new_section = self.process_section(child, new_section)

                if self.SECTION not in d:
                    d[self.SECTION] = list()

                d[self.SECTION].append(new_section)

        return d

    def elementtree_to_json(self, root):
        document = dict()
        document[self.HEADER] = root.get(self.HTML_TITLE)
        document[self.SECTION] = list()
        document[self.SECTION] = self.process_section(root, OrderedDict())

        return document

    def convertToDocument(self, rawHtml, doc_title):
        root_element = self.convert_to_xml(rawHtml)
        doc = Document.fromDict(self.elementtree_to_json(root_element))
        doc.header = root_element.get(self.HTML_TITLE)
        return doc
