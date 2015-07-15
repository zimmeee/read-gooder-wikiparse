"""
created by beth on 6/11/15
"""

import string
import abc
from math import ceil
import re

from nltk import WhitespaceTokenizer, Tree
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


# print tokens as they emerge from Stanford Parser's formatting (pformat)
class StanfordParserSentenceFormatter(SentenceFormatter):
    def __init__(self, max_words_per_part, parser):
        self.max_words_per_part = max_words_per_part
        if not isinstance(parser, StanfordParser):
            raise Exception("VstfSentenceFormatter: Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree

    def format(self, inputString):
        inputTrees = self.parser.raw_parse(inputString)

        for treeSet in inputTrees:
            formatted_string = self.pformat(treeSet[0], margin=70, indent=0, nodesep='', parens='()')
            fragments = []
            for string_fragment in formatted_string.split('\n'):
                fragments.append(SentenceFragment(indent=self.getIndent(string_fragment),
                                                  tokens=self.getTokens(string_fragment),
                                                  text=self.getText(string_fragment)))

            # first pass - eliminate empty rows
            clean_fragments = self.eliminateEmptyRows(fragments)

            # second pass - clean up individual fragments
            clean_fragments = self.cleanIndividualFragments(clean_fragments)

            # third pass - connect fragments
            clean_fragments = self.connectFragments(clean_fragments)

            return clean_fragments

    def eliminateEmptyRows(self, fragment_list):
        clean_fragments = []
        for fragment in fragment_list:
            if not fragment.text:
                continue
            clean_fragments.append(fragment)
        return clean_fragments

    def cleanIndividualFragments(self, fragment_list):
        clean_fragments = []
        for fragment in fragment_list:
            new_text = fragment.text.replace("-LRB- ", "(").replace(" -RRB-", ")")
            new_text = new_text.replace("``", "\"").replace("''", "\"")
            for quoted_part in re.findall(r'\".+?\"', new_text):
                new_text = new_text.replace(quoted_part, quoted_part.replace('\" ', '\"').replace(' \"', '\"'))
            new_fragment = SentenceFragment(indent=fragment.indent,
                                            tokens=self.getTokens(new_text),
                                            text=new_text)
            clean_fragments.append(new_fragment)
        return clean_fragments

    def connectFragments(self, fragment_list):
        temp = []
        open_quote = False
        connected_fragment = []
        for fragment in fragment_list:
            if re.match("[.,;:]", fragment.text):
                connected_fragment.append(fragment)
                temp.append(connected_fragment)
                connected_fragment = []
            elif re.match("\"", fragment.text):
                if open_quote:
                    connected_fragment.append(fragment)
                    temp.append(connected_fragment)
                    connected_fragment = []
                    open_quote = False
                else:
                    if len(connected_fragment) > 0:
                        temp.append(connected_fragment)
                    connected_fragment = [fragment]
                    open_quote = True
            else:
                if len(connected_fragment) > 0 and not open_quote:
                    temp.append(connected_fragment)
                    connected_fragment = [fragment]
                else:
                    connected_fragment.append(fragment)
        clean_fragments = []
        for c in temp:
            clean_fragments.append(SentenceFragment(indent=max([f.indent for f in c]),
                                                    tokens=[t for f in c for t in f.tokens],
                                                    text="".join([f.text for f in c])))
        return clean_fragments

    def getIndent(self, a):
        return len(a) - len(a.lstrip(' '))

    def getTokens(self, a):
        return [e for e in a.split()]

    def getText(self, a):
        return a.lstrip()

    # stolen from NLTK tree pformat
    def pformat(self, tree, margin=70, indent=0, nodesep='', parens='()'):
        s = self._pformat_flat(tree, nodesep, parens)
        if len(s) + indent < margin:
            return s

        # If it doesn't fit on one line, then write it on multi-lines.
        s_lines = []
        for child in tree:
            if isinstance(child, Tree):
                s_lines.append('\n' + ' ' * (indent + 2) + self.pformat(child, margin, indent + 2, nodesep, parens))
            elif isinstance(child, tuple):
                s_lines.append('\n' + ' ' * (indent + 2) + "/".join(child))
            else:
                s_lines.append('\n' + ' ' * (indent + 2) + '%s' % child)
        return "".join(s_lines)

    # stolen from NLTK tree _pformat_flat
    def _pformat_flat(self, tree, nodesep, parens):
        childstrs = []
        for child in tree:
            if isinstance(child, Tree):
                childstrs.append(self._pformat_flat(child, nodesep, parens))
            elif isinstance(child, tuple):
                childstrs.append("/".join(child))
            else:
                childstrs.append('%s' % child)
        return " ".join(childstrs)


# every constituent in the parse is returned in order of size as a SentenceFragment
class ConstituentHeightSentenceFormatter(SentenceFormatter):
    def __init__(self, parser, constituent_height=None):
        if not isinstance(parser, StanfordParser):
            raise Exception("ConstituentSentenceFormatter: Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree
        self.constituent_height = constituent_height

    def format(self, inputString):
        # parse the sentence into a tree
        inputTrees = self.parser.raw_parse(inputString)
        result = []

        for treeSet in inputTrees:
            for tree in treeSet:
                # if no constituent height set, take all constituents in order of height
                if not self.constituent_height:
                    max_height = 0
                    for subtree in tree.subtrees():
                        if subtree.height() > max_height:
                            max_height = subtree.height()
                    for height in range(max_height):
                        for subtree in tree.subtrees(lambda t: t.height() == height):
                            result.append(SentenceFragment(indent=subtree.height(), tokens=subtree.leaves(),
                                                           text=' '.join(subtree.leaves())))
                else:
                    for subtree in tree.subtrees(lambda t: t.height() == self.constituent_height):
                        result.append(SentenceFragment(indent=subtree.height(), tokens=subtree.leaves(),
                                                       text=' '.join(subtree.leaves())))
        return result


# only constituents of a certain length in tokens are returned
class ConstituentTokenLengthSentenceFormatter(SentenceFormatter):
    def __init__(self, parser, min_length=0, max_length=20):
        if not isinstance(parser, StanfordParser):
            raise Exception("ConstituentSentenceFormatter: Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree
        self.min_length = min_length
        self.max_length = max_length

    def format(self, inputString):
        inputTrees = self.parser.raw_parse(inputString)
        result = []

        for treeSet in inputTrees:
            for tree in treeSet:
                for subtree in tree.subtrees(lambda t: self.min_length <= len(t.leaves()) <= self.max_length):
                    result.append(SentenceFragment(indent=len(subtree.leaves()), tokens=subtree.leaves(),
                                                   text=' '.join(subtree.leaves())))
        return result