"""
created by noah on 5/22/15
edited by beth on 6/11/15
"""
import json
import sys
import os

from nltk.parse import stanford

from formatters import StupidVstfSentenceFormatter
from openmind_format import Sentence, SentenceJSONEncoder


def demo_stanford_parser(formatter):
    sentences = ["Hello, My name is Melroy.",
                 "A train is a form of rail transport, consisting of a series of "
                 "vehicles that usually, runs along a rail track to transport "
                 "cargo or passengers."]

    # take all parsed sentences and format them according to the desired formatter
    for sentence in sentences:
        result = formatter.format(sentence)
        sentence = Sentence(sentence_parts=result, numwords=sum([len(frag.tokens) for frag in result]))
        print(json.dumps(sentence, cls=SentenceJSONEncoder, indent=4))


def main():
    os.environ['STANFORD_PARSER'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'
    os.environ['STANFORD_MODELS'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'

    parser = stanford.StanfordParser(
        model_path="/Users/beth/Documents/openmind/stanford-parser-3.5.2/models/edu/"
                   "stanford/nlp/models/lexparser/englishPCFG.ser.gz")

    formatter = StupidVstfSentenceFormatter(max_words_per_part=4, parser=parser)  # vstf formatter with max 4 words per line
    demo_stanford_parser(formatter)


if __name__ == '__main__':
    sys.exit(main())