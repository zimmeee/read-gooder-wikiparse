"""

created by noah on 6/29/15
"""
import sys
import os
import argparse
import logging
import logging.config
import json
from urllib.request import urlopen

import yaml
from nltk.parse import stanford

from formatters import LineLengthSentenceFormatter, StupidVstfSentenceFormatter, DefaultSentenceFormatter, \
    ConstituentHeightSentenceFormatter, ConstituentTokenLengthSentenceFormatter
from openmind_format import DocumentJSONEncoder
from raw_converters import WikiHtmlFileRawConverter, BasicTextFileRawConverter, GibbonHtmlFileRawConverter


def sentenceformatter_factory(config, parser):
    try:
        ntokens = int(config["ntokens"])
    except:
        ntokens = None

    # set sentence formatter class
    if config["sentence_formatter"] == "linelength":
        formatter = LineLengthSentenceFormatter(ntokens)
        logging.info("Using LineLengthSentenceFormatter sentence formatter with " + str(ntokens) + " tokens")
    elif config["sentence_formatter"] == "stupidvstf":
        formatter = StupidVstfSentenceFormatter(ntokens, parser)
        logging.info("Using StupidVstfSentenceFormatter sentence formatter with " + str(ntokens) + " tokens")
    elif config["sentence_formatter"] == "constituentheight":
        if ntokens:
            formatter = ConstituentHeightSentenceFormatter(parser, constituent_height=ntokens)
            logging.info("Using ConstituentHeightSentenceFormatter sentence formatter with " + str(ntokens) + " tokens")
        else:
            formatter = ConstituentHeightSentenceFormatter(parser)
            logging.info("Using ConstituentHeightSentenceFormatter sentence formatter")
    elif config["sentence_formatter"] == "constituentlength":
        formatter = ConstituentTokenLengthSentenceFormatter(parser, int(config["ntokensmin"]),
                                                            int(config["ntokensmax"]))
        logging.info("Using ConstituentTokenLengthSentenceFormatter sentence formatter with ntokensmin=" +
                     config["ntokensmin"] + " and ntokensmax=" + config["ntokensmax"])
    else:
        formatter = DefaultSentenceFormatter()
        logging.info("Using DefaultSentenceFormatter sentence formatter")

    return formatter


def converter_factory(converter_type, formatter):
    raw_converter = None

    if converter_type == "Basic":
        raw_converter = BasicTextFileRawConverter(formatter)
    elif converter_type == "Gibbon":
        raw_converter = GibbonHtmlFileRawConverter(formatter)
    elif converter_type == "Wiki":
        raw_converter = WikiHtmlFileRawConverter(formatter)
    else:
        logging.error("Unknown converter type " + converter_type)

    logging.info("Using " + type(raw_converter).__name__)
    return raw_converter


def stanfordparser_factory(config):
    stanfordParser = None

    # Setup the Stanford parser
    if os.path.exists(config['stanford_parser_directory']) and \
            os.path.exists(config['stanford_parser_models_directory']):
        os.environ['STANFORD_PARSER'] = config['stanford_parser_directory']
        os.environ['STANFORD_MODELS'] = config['stanford_parser_models_directory']
        stanfordParser = stanford.StanfordParser()
    else:
        logging.error("Could not find files required for the Stanford parser in: " +
                      config['stanford_parser_directory'] + " or " + config['stanford_parser_models_directory'])

    return stanfordParser

def setup_logging(logging_conf):
    if logging_conf:
        with open(logging_conf, 'rt') as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        print("No logging configuration specified. Using defaults")
        logging.basicConfig(level=logging.INFO)


def main():
    arg_parser = argparse.ArgumentParser(description="Convert a text document into OpenMind JSON format")
    arg_parser.add_argument("-c", "--config", required=True, help="Configuration file containing runtime parameters")
    arg_parser.add_argument("-l", "--logging", required=False, help="Configuration file for runtime logging parameters")

    args = arg_parser.parse_args()

    setup_logging(args.logging)

    logging.info("Starting conversion with " + str(vars(args)))

    with open(args.config, 'r') as config_file:
        document = None
        config = yaml.load(config_file)["Document"]

        # Get a parser instance
        stanfordParser = stanfordparser_factory(config)

        if stanfordParser:
            # Get a sentence formatter
            formatter = sentenceformatter_factory(config, stanfordParser)

            # Get a document converter
            raw_converter = converter_factory(config["raw_converter"], formatter)

            # If there is a information to pull article from a wiki, do that first
            if config["wiki_rest_endpoint"] and config["wiki_article_title"] and config["raw_converter"] == 'Wiki':
                source_url = config["wiki_rest_endpoint"] + config["wiki_article_title"]
                source = urlopen(source_url)
                logging.info("Processing URL: " + source_url)
                document = raw_converter.convertToDocument(source, config["wiki_article_title"])
            # Otherwise try to read from file
            elif config["file"] is not None:
                with open(config["file"]) as input:
                    title = os.path.basename(config["file"])
                    logging.info("Processing file: " + os.path.abspath(config["file"]))
                    text = input.read()
                    document = raw_converter.convertToDocument(text, title)

        if document:
            # Write out results
            with open(config["output_file"], "w") as output:
                output.write(
                    json.dumps(document, cls=DocumentJSONEncoder, indent=4, sort_keys=True, ensure_ascii=False))
                logging.info("Wrote output to: " + os.path.abspath(config["output_file"]))


if __name__ == '__main__':
    sys.exit(main())
