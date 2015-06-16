import json
import unittest

from nltk import Tree

from formatters import StupidVstfFormatter
from openmind_format import Sentence, SentenceJSONEncoder


__author__ = 'beth'


class StupidVstfFormatterTest(unittest.TestCase):
    def setUp(self):
        self.tree = Tree('ROOT', [Tree('S', [Tree('INTJ', [Tree('UH', ['Hello'])]), Tree(',', [',']),
                                             Tree('NP', [Tree('PRP$', ['My']), Tree('NN', ['name'])]),
                                             Tree('VP', [Tree('VBZ', ['is']), Tree('ADJP', [Tree('JJ', ['Melroy'])])]),
                                             Tree('.', ['.'])])])

    def runTest(self):
        formatter = StupidVstfFormatter(4)
        result = formatter.format(self.tree)
        for sentence_fragment in result:
            self.assertTrue(sentence_fragment.len() <= 4)
            print(sentence_fragment)

        formatter = StupidVstfFormatter(2)
        result = formatter.format(self.tree)
        for sentence_fragment in result:
            self.assertTrue(sentence_fragment.len() <= 2)
            print(sentence_fragment)

        formatter = StupidVstfFormatter(1)
        result = formatter.format(self.tree)
        for sentence_fragment in result:
            self.assertTrue(sentence_fragment.len() <= 1)
            print(sentence_fragment)

        formatter = StupidVstfFormatter(4)
        print(json.dumps(Sentence(H1="Sentence heading", sentence_parts=formatter.format(self.tree)),
                         cls=SentenceJSONEncoder, indent=4))