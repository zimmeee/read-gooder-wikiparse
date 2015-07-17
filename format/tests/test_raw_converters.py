import json
import unittest
from urllib.request import urlopen

from openmind_format import DocumentJSONEncoder, Document
from raw_converters import BasicTextFileRawConverter, WikiHtmlFileRawConverter


class BasicTextFileRawConverterTests(unittest.TestCase):
    def setUp(self):
        self.doc_title = "Supernovas!"
        self.text = "Supernovas are among the most energetic events in the universe and result in the " \
                    "complete disruption of stars at the end of their lives. Originally, the distinction " \
                    "between Type I and Type II supernovas was based solely on the presence or absence of " \
                    "hydrogen atoms (hydrogen lines). Supernovas without hydrogen lines were called Type I, " \
                    "while those with hydrogen lines were Type II. Subsequent analysis of many of these events " \
                    "revealed that this empirical classification schema instead reflected two different mechanisms " \
                    "for the supernova explosion. Type I supernovas happen in binary stars — two stars that orbit " \
                    "closely each other — when one of the two binary stars is a small, dense, white dwarf star. " \
                    "If the companion star ranges too close to the white dwarf that it is orbiting, the white dwarf’s " \
                    "gravitational pull will draw matter from the other star. When the white dwarf acquires enough " \
                    "matter to become at least 1.4 times as big as the Sun, it collapses and explodes in a supernova. " \
                    "Type II supernovas occur when a star, much more massive than the Sun, ends its life. " \
                    "When such a star begins burning out, the core of the star quickly collapses releasing amazing " \
                    "energy in the form of neutrinos, a kind of particle smaller than even an atom. Electromagnetic " \
                    "radiation — energy that is electric and magnetic — causes the star to explode in a supernova. " \
                    "Whereas Type I supernovas typically destroy their parent stars, Type II explosions usually leave " \
                    "behind the stellar core. The classification schema regarding the mechanism for supernova " \
                    "explosions helps to more succinctly answer the question: Is the Sun in danger of becoming a " \
                    "supernova? Neither does our Sun have a companion star orbiting it nor does our Sun have the mass " \
                    "necessary to become a supernova. Furthermore, it will be another billion years until the Sun runs " \
                    "out of fuel and swells into a red giant star before going into a white dwarf form."

    def testDeserialize(self):
        raw_converter = BasicTextFileRawConverter()
        document = raw_converter.convertToDocument(self.text, self.doc_title)
        self.assertEquals(document.header, "Supernovas!")
        section = document.section
        self.assertEquals(section.header, None)
        self.assertEquals(len(section.paragraphs), 1)
        paragraph = section.paragraphs[0]
        self.assertEquals(paragraph.position, 0)
        self.assertEquals(len(paragraph.sentences), 14)
        self.assertEquals(paragraph.sentences[0].text,
                          "Supernovas are among the most energetic events in the universe and result "
                          "in the complete disruption of stars at the end of their lives.")
        self.assertEquals(paragraph.sentences[13].text,
                          "Furthermore, it will be another billion years until the Sun runs " +
                          "out of fuel and swells into a red giant star before going into a white dwarf form.")
        self.assertEquals(paragraph.sentences[0].position, 0)
        self.assertEquals(paragraph.sentences[13].position, 13)

    def testSerialize(self):
        raw_converter = BasicTextFileRawConverter()
        document = raw_converter.convertToDocument(self.text, self.doc_title)
        formatted_document = json.dumps(document, cls=DocumentJSONEncoder, indent=None, sort_keys=True)
        new_document = Document.fromDict(json.loads(formatted_document))
        self.assertEquals(document.header, new_document.header)
        for i in range(len(document.section.paragraphs)):
            self.assertEquals(document.section.paragraphs[i], new_document.section.paragraphs[i])
        self.assertEquals(document.section.header, new_document.section.header)
        self.assertEquals(document.section.subsections, new_document.section.subsections)
        self.assertEquals(document, new_document)


class WikiHtmlRawConverterTests(unittest.TestCase):
    def setUp(self):
        source_url = "http://rest.wikimedia.org:80/en.wikipedia.org/v1/page/html/Supernova"
        self.doc_source = urlopen(source_url)
        self.doc_title = "Supernova"

    def testDeserialize(self):
        raw_converter = WikiHtmlFileRawConverter()
        document = raw_converter.convertToDocument(self.doc_source, self.doc_title)
        self.assertEquals(document.header, "Supernova")
        section = document.section
        self.assertEquals(section.header, None)
        self.assertEquals(len(section.paragraphs), 4)
        for i in range(len(section.paragraphs)):
            paragraph = section.paragraphs[i]
            self.assertEquals(paragraph.position, i)
        self.assertEquals(len(section.paragraphs[0].sentences), 6)
        self.assertEquals(len(section.paragraphs[1].sentences), 4)
        self.assertEquals(len(section.paragraphs[2].sentences), 3)
        self.assertEquals(len(section.paragraphs[3].sentences), 5)
        self.assertEquals(section.paragraphs[3].sentences[3].text,
                          "Furthermore, the expanding shock waves from supernova "
                          "explosions can trigger the formation of new stars.")
        self.assertEquals(len(section.subsections), 12)

    def testSerialize(self):
        raw_converter = WikiHtmlFileRawConverter()
        document = raw_converter.convertToDocument(self.doc_source, self.doc_title)
        formatted_document = json.dumps(document, cls=DocumentJSONEncoder, indent=None, sort_keys=True)
        new_document = Document.fromDict(json.loads(formatted_document))
        self.assertEquals(document.header, new_document.header)
        for i in range(len(document.section.paragraphs)):
            self.assertEquals(document.section.paragraphs[i], new_document.section.paragraphs[i])
        self.assertEquals(document.section.header, new_document.section.header)
        for i in range(len(document.section.subsections)):
            self.assertEquals(document.section.subsections[i].header, new_document.section.subsections[i].header)
            self.assertEquals(document.section.subsections[i].paragraphs,
                              new_document.section.subsections[i].paragraphs)
            self.assertEquals(document.section.subsections[i].subsections,
                              new_document.section.subsections[i].subsections)
        self.assertEquals(document.section.subsections, new_document.section.subsections)
        self.assertEquals(document, new_document)
