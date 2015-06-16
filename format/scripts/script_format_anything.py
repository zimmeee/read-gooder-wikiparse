"""
created by beth on 6/15/15
"""
import argparse
import json
import os
from urllib.request import urlopen
import sys

from nltk.parse import stanford

from formatters import LineLengthFormatter
from openmind_format import DocumentJSONEncoder
from raw_converters import WikiHtmlFileRawConverter


def main():
    endpoint = "http://rest.wikimedia.org:80/en.wikipedia.org/v1/page/html/"

    parser = argparse.ArgumentParser(description="Convert a wikipedia page into OpenMind JSON format")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--title", help="fetch the wikipedia article with this title from the Wikimedia REST API")
    group.add_argument("-f", "--file", help="convert the local HTML file at this path")
    args = parser.parse_args()

    source = None

    if not (args.title or args.file):
        parser.print_help()
        return

    if args.title:
        doc_title = args.title
        source = urlopen(endpoint + args.title)
    elif args.file:
        doc_title = args.file
        source = open(args.file)
    else:
        parser.error("hello world")
        doc_title = None

    os.environ['STANFORD_PARSER'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'
    os.environ['STANFORD_MODELS'] = '/Users/beth/Documents/openmind/stanford-parser-3.5.2'

    stanfordParser = stanford.StanfordParser(
        model_path="/Users/beth/Documents/openmind/stanford-parser-3.5.2/models/edu/"
                   "stanford/nlp/models/lexparser/englishPCFG.ser.gz")

    # formatter = StupidVstfFormatter(4, stanfordParser)
    # formatter = DefaultFormatter()
    formatter = LineLengthFormatter(4)
    raw_converter = WikiHtmlFileRawConverter(formatter)

    if source:
        document = raw_converter.convertToDocument(source, doc_title)
        print(json.dumps(document, cls=DocumentJSONEncoder, indent=4, sort_keys=True, ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())