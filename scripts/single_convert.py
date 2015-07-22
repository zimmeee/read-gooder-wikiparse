"""
Script for converting a single file to Screenplay format
created by noah on 6/29/15
updated by beth on 7/22/15 to reflect new Screenplay format
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

from screenplay import ScreenplayJSONEncoder
from screenwriters import BasicScreenwriter
from raw_converters import WikiHtmlFileRawConverter, BasicTextFileRawConverter


def screenwriter_factory(screenwriter_name):
    if screenwriter_name == "basic":
        screenwriter = BasicScreenwriter()
        logging.info("Using BasicScreenwriter")
    else:
        screenwriter = BasicScreenwriter()
        logging.info("No recognized screenwriter name")
    return screenwriter


def raw_converter_factory(converter_type):
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


def do_conversion(screenwriter_type, raw_converter_type, document_source, document_title, output_file):
    raw_converter = raw_converter_factory(raw_converter_type)
    document = raw_converter.convertToDocument(document_source, document_title)

    if not document:  # if document could not be converted
        return

    screenwriter = screenwriter_factory(screenwriter_type)

    with open(output_file, "w") as output:
        output.write(
            json.dumps(screenwriter.write_screenplay(document), cls=ScreenplayJSONEncoder,
                       indent=4, sort_keys=True, ensure_ascii=False))
        logging.info("Wrote output to: " + os.path.abspath(output_file))


def main():
    arg_parser = argparse.ArgumentParser(description="Convert a text document into OpenMind Screenplay format")
    arg_parser.add_argument("-c", "--config", required=True, help="Configuration file containing runtime parameters")
    arg_parser.add_argument("-l", "--logging", required=False, help="Configuration file for runtime logging parameters")

    args = arg_parser.parse_args()

    setup_logging(args.logging)

    logging.info("Starting conversion with " + str(vars(args)))

    with open(args.config, 'r') as config_file:
        config = yaml.load(config_file)["Screenplay"]

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

        # convert the document
        do_conversion(config["screenwriter"], config["raw_converter"], document_source, document_title,
                      os.path.abspath(config["output_file"]))


if __name__ == '__main__':
    sys.exit(main())
