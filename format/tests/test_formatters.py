import os
import unittest

from nltk.parse import stanford

from formatters import ConstituentHeightSentenceFormatter, VstfSentenceFormatter


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


class VSTFFormatterTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['STANFORD_PARSER'] = "/Users/beth/Documents/openmind/stanford-parser-3.5.2"
        os.environ['STANFORD_MODELS'] = "/Users/beth/Documents/openmind/stanford-parser-3.5.2"

        self.stanfordParser = stanford.StanfordParser()

    def runTest(self):
        formatter = VstfSentenceFormatter(4, self.stanfordParser)
        sentence_fragments = formatter.format("Nearly a century ago, biologists found that if they separated an "
                                              "invertebrate animal embryo into two parts at an early stage of its "
                                              "life, it would survive and develop as two normal embryos.")
        for fragment in sentence_fragments:
            print(" ".join([" "] * fragment.indent) + " ".join(fragment.tokens))
