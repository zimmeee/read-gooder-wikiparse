"""
created by beth on 6/12/15
"""

import json
import sys
import os

from nltk.parse import stanford
from nltk.tokenize import sent_tokenize

from formatters import StupidVstfFormatter
from openmind_format import Sentence, Document, DocumentEncoder


if __name__ == '__main__':
    text_file = sys.argv[1]
    text = open(text_file, "r").read()
    sentences = sent_tokenize(text, language='english')

    os.environ['STANFORD_PARSER'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'
    os.environ['STANFORD_MODELS'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'

    parser = stanford.StanfordParser(
        model_path="/Users/beth/Documents/openmind/stanford-parser-3.5.2/models/edu/"
                   "stanford/nlp/models/lexparser/englishPCFG.ser.gz")

    parsed_sentences = parser.raw_parse_sents(sentences)

    formatter = StupidVstfFormatter(4)  # vstf formatter with max 4 words per line

    # take all parsed sentences and format them according to the desired formatter
    sentence_list = []
    total_words = 0
    for line in parsed_sentences:
        for sentence_tree in line:
            result = formatter.format(sentence_tree)
            sentence = Sentence(H1="Headline", H2="Headline 2", sentence_parts=result)
            print(sentence)
            sentence_list.append(sentence)
            for part in result:
                total_words += part.len()
    document = Document(title=text_file, numsentences=len(sentence_list), numwords=total_words, sentences=sentence_list)

    fout = open(sys.argv[2], "w")
    fout.write(json.dumps(document, cls=DocumentEncoder, indent=4))
    fout.flush()
    fout.close()