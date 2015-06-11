import json
import unittest

from nltk import Tree

from formatters import StupidVstfFormatter
from openmind_format import Sentence, SentenceEncoder


__author__ = 'beth'


class StupidVstfFormatterEncodeDecodeTest(unittest.TestCase):
    def setUp(self):
        self.tree = Tree('ROOT', [Tree('S', [Tree('INTJ', [Tree('UH', ['Hello'])]), Tree(',', [',']),
                                             Tree('NP', [Tree('PRP$', ['My']), Tree('NN', ['name'])]),
                                             Tree('VP', [Tree('VBZ', ['is']), Tree('ADJP', [Tree('JJ', ['Melroy'])])]),
                                             Tree('.', ['.'])])])

    def runTest(self):
        formatter = StupidVstfFormatter(4)
        original_sentence = Sentence(H1="Sentence heading", sentence_parts=formatter.format(self.tree))
        original_as_string = json.dumps(original_sentence, cls=SentenceEncoder, indent=4)
        retrieved_object = Sentence.fromDict(dict_object=json.loads(original_as_string))

        self.assertTrue(isinstance(retrieved_object, Sentence))  # the retrieved object is in fact a Sentence
        self.assertEquals(original_sentence, retrieved_object)  # the retrieved object is identical to the original
