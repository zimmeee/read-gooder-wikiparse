"""

created by noah on 5/22/15
"""
import sys

import nltk
import nltk.tokenize
from nltk.tree import *

from nltk.parse import stanford
from nltk.compat import string_types, python_2_unicode_compatible, unicode_repr

from timeit import Timer

from copy import deepcopy

import os

import string


class SentencePart:
    def __init__(self, indent=0, parts=None):
        self.parts = list() if parts is None else parts
        self.indent = indent

    def __repr__(self):
        str_val = self.parts[0] if len(self.parts) == 1 else ' '.join(self.parts)
        return ' '*self.indent + str_val

    def append(self, token):

        if isinstance(token, unicode):
            if token in string.punctuation:
                self.parts[-1] += token
            else:
                self.parts.append(token)
        else:
            self.parts.extend(token)

    def len(self):
        return len(self.parts)


def vstf(source):
    sentences = None

    with open(source) as input:
        for line in input:
            sentences = nltk.sent_tokenize(line)

    for sentence in sentences:
        tree_tokenize(sentence)

def pos_tokenize(sentence):
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    print tagged


def tree_tokenize(sentence):
    t = Tree.fromstring(unicode(sentence))
    print(t)


def demo_stanford_parser():
    os.environ['STANFORD_PARSER'] = '/Applications/stanford-parser'
    os.environ['STANFORD_MODELS'] = '/Applications/stanford-parser'

    parser = stanford.StanfordParser(model_path="/Applications/stanford-parser/stanford-parser-3.5.2-models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    # sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "What is your fucking name?"))
    sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "A train is a form of rail transport consisting of a series of vehicles that usually runs along a rail track to transport cargo or passengers."))
    # print sentences

    for line in sentences:
        for sentence in line:
            # Skip the root node
            # x = traverse(sentence[0])
            # print(x)
            parts = stupid_vstf(sentence[0])
            for part in parts:
                print part


def stupid_vstf(sentence, depth=0, max=4):
    '''
    Stupid VSTF inserts line breaks after 4 words or punctuation
    Indentation is reset after punctuation
    :param sentence:
    :return:
    '''

    result = []
    part = SentencePart(indent=depth*2)

    for token in sentence:
        if len(token) == 1:
            string_token = ' '.join(token.leaves())
            if string_token in string.punctuation:
                part.append(string_token)
                # Create new part
                result.append(part)
                depth += 1
                part = SentencePart(indent=depth*2)
            else:
                part.append(string_token)
        else:
            if part.len() + len(token.leaves()) > max:
                result.append(part)
                part = stupid_vstf(token, depth=depth+1)[0]
            else:
                part.append(token.leaves())

    if part.len():
        result.append(part)

    return result



def stupid_vstf2(sentence, max=4):
    '''
    Stupid VSTF inserts line breaks after 4 words or punctuation
    Indentation is reset after punctuation
    :param sentence:
    :return:
    '''

    result = []
    part = []

    sresult = ''

    previous_token = None

    for token in sentence:
        if len(token) == 1:
            string_token = ' '.join(token.leaves())
            if string_token in string.punctuation:
                part[-1] += string_token
                # Create new part
                result.append(deepcopy(part))
                part = list()
            else:
                part.append(string_token)
        else:
            if len(part) + len(token) > max:
                result.append(deepcopy(part))
                part = list()

            part.extend(token.leaves())

        previous_token = token

    if part:
        result.append(part)

    print result


    # chunks = sentence.leaves()
    #
    # for token in sentence.leaves():
    #     if len(part) > max:
    #         result.append(deepcopy(part))
    #     else:
    #         if token in string.punctuation:
    #             part[-1] += token
    #             result.append(deepcopy(part))
    #             part = []
    #         else:
    #           part.append(token)
    #
    # if len(result) == 1:
    #     return result[0]
    # else:
    #     return result

    return 'me'



# def traverse(tree, margin=70, indent=0, max_length=4):
#
#     s = ''
#
#     for child in tree:
#         # indent += 2
#         if isinstance(child, Tree):
#             if len(child) > max_length:
#                 s += ' ' * indent + traverse(child, margin, indent+2)
#             else:
#                 s += ' '.join(child.leaves())
#         elif isinstance(child, tuple):
#             s += ' ' * indent + "/".join(child)
#         elif isinstance(child, string_types):
#             if child in string.punctuation:
#                 print 'found punctuation'
#             s += '\n' + ' ' * indent + '%s' % child
#         else:
#             s += ' ' * indent + unicode_repr(child)
#
#     return s

def traverse(t):
    try:
        t.label()
    except AttributeError:
        print t,
    else:
        # Now we know that t.node is defined
        print '(' + t.label(),
        for child in t:
            traverse(child)
        print ')',


def main():
    # vstf("static/Train.txt")
    t = Timer( "demo_stanford_parser()", "from __main__ import demo_stanford_parser")
    print t.timeit(number=1)


if __name__ == '__main__':
    sys.exit(main())