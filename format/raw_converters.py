"""
RawConverters convert raw input documents into the OpenMind Document format
created by beth on 6/15/15
edited on 7/16/15
"""
import abc
from xml.etree import ElementTree
import re

from bs4 import BeautifulSoup
from nltk import sent_tokenize

from document import Document, Paragraph, Section, Sentence


class RawConverter:
    @abc.abstractmethod
    def convertToDocument(self, source, doc_title):
        return


class BasicTextFileRawConverter(RawConverter):
    def convertToDocument(self, rawText, doc_title):
        sentence_strings = sent_tokenize(rawText, language='english')
        sentences = []
        for i in range(len(sentence_strings)):
            sentences.append(Sentence(text=sentence_strings[i], position=i))
        section = Section(paragraphs=[Paragraph(sentences=sentences, position=0)])
        return Document(header=doc_title, section=section)


# many free ebooks have newlines in unfortunate places, breaking up sentences
# this raw converter eliminates newlines
class BookNewlineFileRawConverter(RawConverter):
    def convertToDocument(self, source, doc_title):
        rawText = source.replace("\n", " ")
        sentence_strings = sent_tokenize(rawText, language='english')
        sentences = []
        for i in range(len(sentence_strings)):
            sentences.append(Sentence(text=sentence_strings[i], position=i))
        section = Section(paragraphs=[Paragraph(sentences=sentences, position=0)])
        return Document(header=doc_title, section=section)


class WikiHtmlFileRawConverter(RawConverter):
    def __init__(self):
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
    def elementLevel(element):
        level = None
        try:
            level = element.tag[re.search('\d', element.tag).start()]
        except:
            pass
        return level

    def isSubSection(self, element1, element2):
        return int(element1.get(self.LEVEL)) > int(element2.get(self.LEVEL))

    def isSibSection(self, element1, element2):
        return int(element1.get(self.LEVEL)) == int(element2.get(self.LEVEL))

    def convertToXml(self, source):
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
                new_section = ElementTree.Element(self.SECTION, {self.LEVEL: self.elementLevel(elem),
                                                                 self.HTML_TITLE: elem.text.strip()})

                if self.isSubSection(new_section, current_section):
                    parent_section = current_section
                else:
                    while outline_stack:
                        parent_section = outline_stack.pop()

                        if self.isSibSection(parent_section, new_section) or \
                                self.isSubSection(parent_section, new_section):
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

    def tidyText(self, text):
        tidy = text

        # Detect wikipedia style citations
        # for example: "[2] There are various"
        citation_regex = re.compile('\s*\[\d*\]\s*')

        # Remove citations
        tidy = citation_regex.sub("", tidy)

        return tidy

    def parseParagraph(self, paragraph_element, count):
        sentences = list()

        sentence_count = 0
        if paragraph_element.text:
            for sentence in sent_tokenize(paragraph_element.text):
                sentences.append(Sentence(text=self.tidyText(sentence), position=sentence_count))
                sentence_count += 1

        return Paragraph(sentences, count)

    def processSection(self, element, section):
        paragraph_count = 0
        for child in element:
            if child.tag == self.HTML_PARAGRAPH:
                paragraph = self.parseParagraph(child, paragraph_count)
                paragraph_count += 1
                if not section.paragraphs:
                    section.paragraphs = list()
                section.paragraphs.append(paragraph)
            elif child.tag == self.SECTION:
                section_title = child.get(self.HTML_TITLE)
                new_section = Section()
                new_section = self.processSection(child, new_section)
                new_section.header = section_title

                if not section.subsections:
                    section.subsections = list()

                section.subsections.append(new_section)

        return section

    def convertToDocument(self, rawHtml=None, doc_title=None):
        root_element = self.convertToXml(rawHtml)
        return Document(header=root_element.get(self.HTML_TITLE), section=self.processSection(root_element, Section()))
