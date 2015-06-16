"""
created by beth on 6/11/15
"""

import string
import abc
from math import ceil

from nltk import WhitespaceTokenizer

from nltk.parse.stanford import StanfordParser

from openmind_format import SentenceFragment


class SentenceFormatter(object):
    @abc.abstractmethod
    # returns a list of SentenceFragment objects
    def format(self, inputString):
        if not isinstance(inputString, str):
            raise Exception("Yo, this is not a sentence string: " + str(inputString))
        return


# most basic formatter - there is just one part, and it is the entire sentence
class DefaultSentenceFormatter(SentenceFormatter):
    def __init__(self):
        return

    def format(self, inputString):
        result = []
        tokens = WhitespaceTokenizer().tokenize(inputString)
        result.append(SentenceFragment(indent=0, tokens=tokens, text=inputString))
        return result


# line length formatter
# taken from Noah's original line_length_converter method in simplify_wiki_html
class LineLengthSentenceFormatter(SentenceFormatter):
    def __init__(self, line_length):
        self.desired_line_length = line_length

    def format(self, inputString):
        result = []

        words = WhitespaceTokenizer().tokenize(inputString)
        num_words = len(words)

        if num_words > 0:
            num_sentence_parts = ceil(num_words / self.desired_line_length)

            for i in range(0, num_sentence_parts):
                start = i * self.desired_line_length
                end = start + self.desired_line_length if start + self.desired_line_length < num_words else num_words
                result.append(SentenceFragment(indent=0, text=' '.join(words[start:end]), tokens=words[start:end]))
        return result


# naive implementation of vstf: trees are flattened and returned as lists of SentenceFragment objects
class StupidVstfSentenceFormatter(SentenceFormatter):
    def __init__(self, max_words_per_part, parser):
        self.max_words_per_part = max_words_per_part
        if not isinstance(parser, StanfordParser):
            raise Exception("StupidVstfFormatter: Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree

    def format(self, inputString):
        # parse the sentence into a tree
        inputTrees = self.parser.raw_parse(inputString)

        result = []

        for treeSet in inputTrees:
            for tree in treeSet:
                depth = 0
                part = SentenceFragment(indent=depth * 2)

                # the "flattened" tree is just a list of the tokens, in order
                for string_token in tree.flatten():
                    if string_token in string.punctuation:
                        part.append(string_token)
                        part.text = ' '.join(part.tokens)
                        result.append(part)
                        depth = 1  # only the very first line in the sentence is flush left; the rest are at depth = 1
                        part = SentenceFragment(indent=depth * 2)
                    elif part.len() >= self.max_words_per_part:
                        part.text = ' '.join(part.tokens)
                        result.append(part)
                        depth += 1
                        part = SentenceFragment(indent=depth * 2)
                        part.append(string_token)
                    else:
                        part.append(string_token)

        return result


# every constituent in the parse is returned in order of size as a SentenceFragment
class ConstituentSentenceFormatter(SentenceFormatter):
    def __init__(self, parser):
        if not isinstance(parser, StanfordParser):
            raise Exception("StupidVstfFormatter: Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree

    def format(self, inputString):
        inputTree = self.parser.parse(inputString)

        # set max height
        max_height = 0
        for subtree in inputTree.subtrees():
            if subtree.height() > max_height:
                max_height = subtree.height()

        # get constituents
        result = []

        for height in range(max_height):
            for subtree in inputTree.subtrees(lambda t: t.height() == height):
                result.append(SentenceFragment(indent=0, tokens=subtree.leaves()))

        return result