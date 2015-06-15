"""
created by beth on 6/11/15
"""

import string
import abc

from nltk import Tree

from openmind_format import SentenceFragment


class Formatter(object):
    @abc.abstractmethod
    def format(self, aThing):
        return


# formats text presented as a tree
class TreeFormatter(Formatter):
    @abc.abstractmethod
    def format(self, inputTree):
        if not isinstance(inputTree, Tree):
            raise Exception("Yo, this is not a tree: " + str(inputTree))
        return super(TreeFormatter, self).format(inputTree)


# formats text presented as a string
class StringFormatter(Formatter):
    @abc.abstractmethod
    def format(self, inputString):
        if not isinstance(inputString, str):
            raise Exception("Yo, this is not a string: " + str(inputString))
        return super(StringFormatter, self).format(inputString)


# naive implementation of vstf: trees are flattened and returned as lists of SentenceFragment objects
class StupidVstfTreeFormatter(TreeFormatter):
    def __init__(self, max_words_per_part):
        self.max_words_per_part = max_words_per_part

    def format(self, inputTree):
        result = []

        depth = 0
        part = SentenceFragment(indent=depth * 2)

        # the "flattened" tree is just a list of the tokens, in order
        for string_token in inputTree.flatten():
            if string_token in string.punctuation:
                part.append(string_token)
                result.append(part)
                depth = 1  # only the very first line in the sentence is flush left; the rest are at depth = 1
                part = SentenceFragment(indent=depth * 2)
            elif part.len() >= self.max_words_per_part:
                result.append(part)
                depth += 1
                part = SentenceFragment(indent=depth * 2)
                part.append(string_token)
            else:
                part.append(string_token)

        return result


# every constituent in the parse is returned in order of size as a SentenceFragment
class ConstituentTreeFormatter(TreeFormatter):
    def format(self, inputTree):
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