"""
created by beth on 6/14/15
"""
import json
import os

from lxml import etree
from nltk import sent_tokenize
from nltk.parse import stanford
from formatters import ConstituentTreeFormatter
from openmind_format import Sentence, Document, DocumentJSONEncoder


def parseFile(directory_name, file_name, htmlParser, my_sentence_list, my_total_words):
    tree = etree.parse(os.path.join(directory_name, file_name), htmlParser)
    root = tree.getroot()
    text = []
    for child in root.iter('p', 'i', 'h2'):
        if not child.text:
            continue
        text.append(child.text)

    full_text = " ".join(text)
    print(len(full_text))

    sentences = sent_tokenize(full_text, language='english')
    print(len(sentences))
    for s in sentences:
        print(s)

    parser = stanford.StanfordParser(model_path="/Users/beth/Documents/openmind/stanford-parser-3.5.2/models/edu/"
                                                "stanford/nlp/models/lexparser/englishPCFG.ser.gz")

    parsed_sentences = parser.raw_parse_sents(sentences)
    formatter = ConstituentTreeFormatter()

    for line in parsed_sentences:
        for sentence_tree in line:
            result = formatter.format(sentence_tree)
            sentence = Sentence(sentence_parts=result)
            my_sentence_list.append(sentence)
            for part in result:
                my_total_words += part.len()

# TODO: we're missing a lot of stuff here - need better HTML parsing in the future

if __name__ == '__main__':
    os.environ['STANFORD_PARSER'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'
    os.environ['STANFORD_MODELS'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'

    dirname = "/Users/beth/Documents/openmind/text-samples/gibbon-decline-and-fall/files/"

    my_parser = etree.HTMLParser(encoding="latin-1")

    sentence_list = []
    total_words = 0

    parseFile(dirname, "890/890-h/890-h.htm", my_parser, sentence_list, total_words)
    parseFile(dirname, "891/891-h/891-h.htm", my_parser, sentence_list, total_words)
    parseFile(dirname, "892/892-h/892-h.htm", my_parser, sentence_list, total_words)
    parseFile(dirname, "893/893-h/893-h.htm", my_parser, sentence_list, total_words)
    parseFile(dirname, "894/894-h/894-h.htm", my_parser, sentence_list, total_words)
    parseFile(dirname, "895/895-h/895-h.htm", my_parser, sentence_list, total_words)

    # take all parsed sentences and format them according to the desired formatter
    output_file = open("/Users/beth/Documents/openmind/text-samples/gibbon-decline-and-fall/full-text-concatenated.txt",
                       "w")

    document = Document(title="gibbon", numsentences=len(sentence_list), numwords=total_words, sentences=sentence_list)

    output_file.write(json.dumps(document, cls=DocumentJSONEncoder, indent=4))
    output_file.flush()
    output_file.close()