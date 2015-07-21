from unittest import TestCase
from urllib.request import urlopen

from raw_converters import WikiHtmlFileRawConverter


class TestSection(TestCase):
    def setUp(self):
        source_url = "http://rest.wikimedia.org:80/en.wikipedia.org/v1/page/html/Supernova"
        doc_source = urlopen(source_url)
        doc_title = "Supernova"
        self.document = WikiHtmlFileRawConverter().convertToDocument(doc_source, doc_title)

    def testGetSentences(self):
        self.assertEquals(len(self.document.section.sentences()), 354)
        self.assertEquals(self.document.section.sentences()[0].text, "A supernova is a stellar "
                                                                     "explosion that briefly outshines "
                                                                     "an entire galaxy, radiating as much "
                                                                     "energy as the Sun or any ordinary star "
                                                                     "is expected to emit over its entire "
                                                                     "life span, before fading from view over "
                                                                     "several weeks or months.")
        self.assertEquals(self.document.section.sentences()[353].text, "\n")
