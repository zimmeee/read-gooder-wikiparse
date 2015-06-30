"""

created by noah on 6/29/15
"""
import sys, os
import argparse
import yaml
import json

from urllib.request import urlopen

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
    elif config["sentence_formatter"] == "stupidvstf":
        formatter = StupidVstfSentenceFormatter(ntokens, parser)
    elif config["sentence_formatter"] == "constituentheight":
        if ntokens:
            formatter = ConstituentHeightSentenceFormatter(parser, constituent_height=ntokens)
        else:
            formatter = ConstituentHeightSentenceFormatter(parser)
    elif config["sentence_formatter"] == "constituentlength":
        formatter = ConstituentTokenLengthSentenceFormatter(parser, int(config["ntokensmin"]),
                                                            int(config["ntokensmax"]))
    else:
        formatter = DefaultSentenceFormatter()

    return formatter

def converter_factory(type, formatter):
    raw_converter = None

    if type == "Basic":
        raw_converter = BasicTextFileRawConverter(formatter)
    elif type == "Gibbon":
        raw_converter = GibbonHtmlFileRawConverter(formatter)
    elif type == "Wiki":
        raw_converter = WikiHtmlFileRawConverter(formatter)

    return raw_converter

def main():
    arg_parser = argparse.ArgumentParser(description="Convert a text document into OpenMind JSON format")
    arg_parser.add_argument("-c", "--config", required=True, help="Configuration file containing runtime parameters")

    args = arg_parser.parse_args()

    with open(args.config, 'r') as config_file:
        config = yaml.load(config_file)["Document"]

        source = None
        stanfordParser = None

        # Setup the Stanford parser
        if os.path.exists(config['stanford_parser_directory']) and \
                os.path.exists(config['stanford_parser_models_directory']) and \
                os.path.exists(os.path.join(config['stanford_parser_models_directory'],
                                             config['stanford_parser_model'])):
            os.environ['STANFORD_PARSER'] = config['stanford_parser_directory']
            os.environ['STANFORD_MODELS'] = config['stanford_parser_models_directory']
            model_path = os.path.join(config['stanford_parser_models_directory'], config['stanford_parser_model'])
            stanfordParser = stanford.StanfordParser(model_path=model_path)
        else:
            print("Couldn't find Stanford parser")
            return

        # Get a sentence formatter
        formatter = sentenceformatter_factory(config, stanfordParser)
        # Get a document converter
        raw_converter = converter_factory(config["raw_converter"], formatter)

        if config["wiki_rest_endpoint"] and config["wiki_article_title"] and config["raw_converter"] == 'Wiki':
            source_url = config["wiki_rest_endpoint"] + config["wiki_article_title"]
            source = urlopen(source_url)
            print("Parsing " + source_url)
            document = raw_converter.convertToDocument(source, config["wiki_article_title"])
        elif config["file"] is not None:
            with open(config["file"]) as input:
                title = os.path.basename(config["file"])
                print("Processing " + title)
                text = input.read()
                document = raw_converter.convertToDocument(text, title)

        with open(config["output_file"], "w") as output:
            output.write(json.dumps(document, cls=DocumentJSONEncoder, indent=4, sort_keys=True, ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())