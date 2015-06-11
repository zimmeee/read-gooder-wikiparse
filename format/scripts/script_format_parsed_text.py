"""
created by noah on 5/22/15
edited by beth on 6/11/15
"""
import json
import sys
import os

from nltk.parse import stanford

from formatters import StupidVstfFormatter
from openmind_format import Sentence, SentenceEncoder


def demo_stanford_parser(formatter):
    os.environ['STANFORD_PARSER'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'
    os.environ['STANFORD_MODELS'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'

    parser = stanford.StanfordParser(
        model_path="/Users/beth/Documents/openmind/stanford-parser-3.5.2/models/edu/"
                   "stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    sentences = parser.raw_parse_sents(("Hello, My name is Melroy.",
                                        "A train is a form of rail transport, consisting of a series of "
                                        "vehicles that usually, runs along a rail track to transport "
                                        "cargo or passengers."), verbose=False)

    # take all parsed sentences and format them according to the desired formatter
    for line in sentences:
        for sentence_tree in line:
            # print(sentence_tree.unicode_repr())
            result = formatter.format(sentence_tree)
            sentence = Sentence(H1="Headline", sentence_parts=result)
            print(sentence)
            print(json.dumps(sentence, cls=SentenceEncoder, indent=4))


def main():
    formatter = StupidVstfFormatter(4)  # vstf formatter with max 4 words per line
    demo_stanford_parser(formatter)


if __name__ == '__main__':
    sys.exit(main())