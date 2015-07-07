import os
import unittest

from nltk.parse import stanford

from formatters import ConstituentHeightSentenceFormatter, StanfordParserSentenceFormatter
from openmind_format import SentenceFragment


__author__ = 'beth'


class ConstituentFormatterTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['STANFORD_PARSER'] = "/Users/beth/Documents/openmind/stanford-parser-3.5.2"
        os.environ['STANFORD_MODELS'] = "/Users/beth/Documents/openmind/stanford-parser-3.5.2"

        self.stanfordParser = stanford.StanfordParser()

    def runTest(self):
        formatter = ConstituentHeightSentenceFormatter(self.stanfordParser, constituent_height=2)
        sentence_fragments = formatter.format("This is a sentence.")
        self.assertEquals(len(sentence_fragments), 5)
        formatter = ConstituentHeightSentenceFormatter(self.stanfordParser, constituent_height=3)
        sentence_fragments = formatter.format("This is a sentence.")
        self.assertEquals(len(sentence_fragments), 2)


class StanfordParserFormatterTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['STANFORD_PARSER'] = "/Users/beth/Documents/openmind/stanford-parser-3.5.2"
        os.environ['STANFORD_MODELS'] = "/Users/beth/Documents/openmind/stanford-parser-3.5.2"

        self.stanfordParser = stanford.StanfordParser()

    def runTest(self):
        formatter = StanfordParserSentenceFormatter(4, self.stanfordParser)
        sentence_fragments = formatter.format("Nearly a century ago, \"biologists\" found that if they separated an "
                                              "invertebrate animal embryo into two parts at an early stage of its "
                                              "life (early), it would survive and develop as \"two normal embryos\".")
        true_fragments = [SentenceFragment(indent=2, tokens=["Nearly", "a", "century", "ago,"],
                                           text="Nearly a century ago,"),
                          SentenceFragment(indent=2, tokens=["``"], text="\""),
                          SentenceFragment(indent=2, tokens=["biologists"], text="biologists"),
                          SentenceFragment(indent=2, tokens=["''"], text="\""),
                          SentenceFragment(indent=4, tokens=["found"], text="found"),
                          SentenceFragment(indent=6, tokens=["that"], text="that"),
                          SentenceFragment(indent=10, tokens=["if"], text="if"),
                          SentenceFragment(indent=12, tokens=["they"], text="they"),
                          SentenceFragment(indent=14, tokens=["separated"], text="separated"),
                          SentenceFragment(indent=14, tokens=["an", "invertebrate", "animal", "embryo"],
                                           text="an invertebrate animal embryo"),
                          SentenceFragment(indent=14, tokens=["into", "two", "parts"], text="into two parts"),
                          SentenceFragment(indent=14, tokens=["at", "an", "early", "stage", "of", "its", "life",
                                                              "-LRB-", "early", "-RRB-,"],
                                           text="at an early stage of its life (early),"),
                          SentenceFragment(indent=8, tokens=["it"], text="it"),
                          SentenceFragment(indent=8, tokens=["would", "survive", "and", "develop", "as", "two",
                                                             "normal", "embryos."], text="would survive and develop "
                                                                                         "as two normal embryos.")]
        for fragment in sentence_fragments:
            print(" " * fragment.indent + fragment.text)
        # self.assertEquals(sentence_fragments, true_fragments)
