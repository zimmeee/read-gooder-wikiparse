import os
import unittest

from nltk.parse import stanford

from formatters import ConstituentHeightSentenceFormatter


__author__ = 'beth'


class ConstituentFormatterTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['STANFORD_PARSER'] = "/Users/beth/Documents/openmind/stanford-parser-3.5.2"
        os.environ['STANFORD_MODELS'] = "/Users/beth/Documents/openmind/stanford-parser-3.5.2"

        self.stanfordParser = stanford.StanfordParser(
            model_path=os.path.join(os.environ['STANFORD_PARSER'],
                                    "models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"))

    def runTest(self):
        formatter = ConstituentHeightSentenceFormatter(self.stanfordParser, constituent_height=2)
        sentence_fragments = formatter.format("This is a sentence.")
        self.assertEquals(len(sentence_fragments), 5)
        formatter = ConstituentHeightSentenceFormatter(self.stanfordParser, constituent_height=3)
        sentence_fragments = formatter.format("This is a sentence.")
        self.assertEquals(len(sentence_fragments), 2)
