"""
created by beth on 6/15/15
"""
import argparse
import json
import os
from urllib.request import urlopen
import sys

from nltk.parse import stanford

from formatters import LineLengthSentenceFormatter, StupidVstfSentenceFormatter, DefaultSentenceFormatter, \
    ConstituentHeightSentenceFormatter, ConstituentTokenLengthSentenceFormatter
from openmind_format import DocumentJSONEncoder
from raw_converters import WikiHtmlFileRawConverter, BasicTextFileRawConverter


def main():
    endpoint = "http://rest.wikimedia.org:80/en.wikipedia.org/v1/page/html/"

    # handle command line arguments
    arg_parser = argparse.ArgumentParser(description="Convert a wikipedia page into OpenMind JSON format")

    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--title", help="fetch the wikipedia article with this title from the Wikimedia REST API")
    group.add_argument("-f", "--file", help="convert the local HTML file at this path")

    arg_parser.add_argument("-sf", "--sentenceformatter", help="which sentence formatter class to use")
    arg_parser.add_argument("-n", "--ntokens", help="number of tokens for this type of formatter")
    arg_parser.add_argument("-nmin", "--ntokensmin", help="min number of tokens for this type of formatter")
    arg_parser.add_argument("-nmax", "--ntokensmax", help="max number of tokens for this type of formatter")

    arg_parser.add_argument("-p", "--stanford_parser_directory", help="directory of stanford parser jar")
    arg_parser.add_argument("-m", "--stanford_parser_models", help="directory for stanford parser model files")

    arg_parser.add_argument("-o", "--output_file", help="output file for OpenMind JSON")
    args = arg_parser.parse_args()

    source = None

    if not (args.title or args.file):
        arg_parser.print_help()
        return

    if args.title:
        doc_title = args.title
        source = urlopen(endpoint + args.title)
    elif args.file:
        doc_title = args.file
        source = open(args.file, 'r')
    else:
        arg_parser.error("hello world")
        doc_title = None

    # get stanford parser
    os.environ['STANFORD_PARSER'] = args.stanford_parser_directory
    os.environ['STANFORD_MODELS'] = args.stanford_parser_models

    stanfordParser = stanford.StanfordParser(
        model_path=os.path.join(os.environ['STANFORD_MODELS'],
                                "models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"))

    # set sentence formatter class
    if args.sentenceformatter == "linelength":
        formatter = LineLengthSentenceFormatter(int(args.ntokens))
    elif args.sentenceformatter == "stupidvstf":
        formatter = StupidVstfSentenceFormatter(int(args.ntokens), stanfordParser)
    elif args.sentenceformatter == "constituentheight":
        if args.ntokens:
            formatter = ConstituentHeightSentenceFormatter(stanfordParser, constituent_height=int(args.ntokens))
        else:
            formatter = ConstituentHeightSentenceFormatter(stanfordParser)
    elif args.sentenceformatter == "constituentlength":
        formatter = ConstituentTokenLengthSentenceFormatter(stanfordParser, int(args.ntokensmin), int(args.ntokensmax))
    else:
        formatter = DefaultSentenceFormatter()

    # get raw converter for wiki file
    # raw_converter = WikiHtmlFileRawConverter(formatter)
    raw_converter = BasicTextFileRawConverter(formatter)

    if source:
        text = source.read()
        document = raw_converter.convertToDocument(text, doc_title)
        # document = raw_converter.convertToDocument(source, doc_title)
        fout = open(args.output_file, "w")
        fout.write(json.dumps(document, cls=DocumentJSONEncoder, indent=4, sort_keys=True, ensure_ascii=False))
        fout.flush()
        fout.close()


if __name__ == '__main__':
    sys.exit(main())