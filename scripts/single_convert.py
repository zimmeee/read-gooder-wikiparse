"""

created by noah on 6/29/15
"""
import json
import sys
import os
import argparse
import logging
import logging.config
from urllib.request import urlopen

import yaml
from nltk.parse import stanford

from formatters import LineLengthSentenceFormatter, StupidVstfSentenceFormatter, DefaultSentenceFormatter, \
    ConstituentHeightSentenceFormatter, ConstituentTokenLengthSentenceFormatter, StanfordParserSentenceFormatter
from openmind_format import DocumentJSONEncoder
from raw_converters import WikiHtmlFileRawConverter, BasicTextFileRawConverter


def sentenceformatter_factory(formatter_name, parser, ntokens=None, ntokensmin=None, ntokensmax=None):
    if formatter_name == "linelength":
        formatter = LineLengthSentenceFormatter(ntokens)
        logging.info("Using LineLengthSentenceFormatter sentence formatter with " + str(ntokens) + " tokens")
    elif formatter_name == "stupidvstf":
        formatter = StupidVstfSentenceFormatter(ntokens, parser)
        logging.info("Using StupidVstfSentenceFormatter sentence formatter with " + str(ntokens) + " tokens")
    elif formatter_name == "constituentheight":
        if ntokens:
            formatter = ConstituentHeightSentenceFormatter(parser, constituent_height=ntokens)
            logging.info("Using ConstituentHeightSentenceFormatter sentence formatter with " + str(ntokens) + " tokens")
        else:
            formatter = ConstituentHeightSentenceFormatter(parser)
            logging.info("Using ConstituentHeightSentenceFormatter sentence formatter")
    elif formatter_name == "constituentlength":
        formatter = ConstituentTokenLengthSentenceFormatter(parser, ntokensmin, ntokensmax)
        logging.info("Using ConstituentTokenLengthSentenceFormatter sentence formatter with ntokensmin=" +
                     str(ntokensmin) + " and ntokensmax=" + str(ntokensmax))
    elif formatter_name == "stanfordparser":
        formatter = StanfordParserSentenceFormatter(ntokens, parser)
        logging.info("Using StanfordParserSentenceFormatter sentence formatter with " + str(ntokens) + " tokens")
    else:
        formatter = DefaultSentenceFormatter()
        logging.info("Using DefaultSentenceFormatter sentence formatter")
    return formatter


def converter_factory(converter_type):
    raw_converter = None

    if converter_type == "Basic":
        raw_converter = BasicTextFileRawConverter()
    elif converter_type == "Wiki":
        raw_converter = WikiHtmlFileRawConverter()
    else:
        logging.error("Unknown converter type " + converter_type)

    logging.info("Using " + type(raw_converter).__name__)
    return raw_converter


def stanfordparser_factory(stanford_parser_directory, stanford_parser_models_directory):
    stanfordParser = None

    # Setup the Stanford parser
    if os.path.exists(stanford_parser_directory) and os.path.exists(stanford_parser_models_directory):
        os.environ['STANFORD_PARSER'] = stanford_parser_directory
        os.environ['STANFORD_MODELS'] = stanford_parser_models_directory
        stanfordParser = stanford.StanfordParser()
    else:
        logging.error("Could not find files required for the Stanford parser in: " +
                      stanford_parser_directory + " or " + stanford_parser_models_directory)

    return stanfordParser


def setup_logging(logging_conf):
    if logging_conf:
        with open(logging_conf, 'rt') as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        print("No logging configuration specified. Using defaults")
        logging.basicConfig(level=logging.INFO)


def do_conversion(formatter, raw_converter_type, document_source, document_title, output_file):
    raw_converter = converter_factory(raw_converter_type)
    document = raw_converter.convertToDocument(document_source, document_title)

    # TODO: formatter enters here

    if not document:  # if document could not be converted
        return

    with open(output_file, "w") as output:
        output.write(
            json.dumps(document, cls=DocumentJSONEncoder, indent=4, sort_keys=True, ensure_ascii=False))
        logging.info("Wrote output to: " + os.path.abspath(output_file))


def main():
    arg_parser = argparse.ArgumentParser(description="Convert a text document into OpenMind JSON format")
    arg_parser.add_argument("-c", "--config", required=True, help="Configuration file containing runtime parameters")
    arg_parser.add_argument("-l", "--logging", required=False, help="Configuration file for runtime logging parameters")

    args = arg_parser.parse_args()

    setup_logging(args.logging)

    logging.info("Starting conversion with " + str(vars(args)))

    with open(args.config, 'r') as config_file:
        config = yaml.load(config_file)["Document"]

        # get text document
        if config["wiki_rest_endpoint"] and config["wiki_article_title"]:
            source_url = config["wiki_rest_endpoint"] + config["wiki_article_title"]
            logging.info("Processing URL: " + source_url)
            document_source = urlopen(source_url)
            document_title = config["wiki_article_title"]
        elif config["file"]:
            document_title = os.path.basename(config["file"])
            logging.info("Processing file: " + os.path.abspath(config["file"]))
            document_source = open(config["file"], "r").read()
        else:
            raise Exception("No input document source provided.")

        # get parser
        stanfordParser = stanfordparser_factory(config['stanford_parser_directory'],
                                                config['stanford_parser_models_directory'])
        if not stanfordParser:
            raise Exception("Stanford Parser instance needed for document conversion.")

        # get formatter
        formatter = sentenceformatter_factory(config["sentence_formatter"], stanfordParser,
                                              ntokens=int(config["ntokens"]) if "ntokens" in config else 0,
                                              ntokensmin=int(config["ntokensmin"]) if "ntokensmin" in config else 0,
                                              ntokensmax=int(config["ntokensmax"]) if "ntokensmax" in config else 0)

        # convert the document
        do_conversion(formatter, config["raw_converter"], document_source, document_title,
                      os.path.abspath(config["output_file"]))


if __name__ == '__main__':
    sys.exit(main())
