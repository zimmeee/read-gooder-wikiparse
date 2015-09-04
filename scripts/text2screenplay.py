"""

created by noah on 9/4/15
"""
import json
import sys
import os

from raw_converters import BookNewlineFileRawConverter
from screenplay import ScreenplayJSONEncoder
from screenwriters import BasicScreenwriter, PartOfSpeechSplitScreenwriter
from nltk.parse.stanford import StanfordParser

def main():
    text_file = sys.argv[1]
    document_title = sys.argv[2]
    output_screenplay_file_stem = sys.argv[3]

    # convert raw text to document format
    document = BookNewlineFileRawConverter().convertToDocument(open(text_file, "r").read(),
                                                               document_title)
    print("Converted to document...")

    stanford_parser_directory = "../resources"
    stanford_parser_models_directory = "../resources"
    os.environ['STANFORD_PARSER'] = stanford_parser_directory
    os.environ['STANFORD_MODELS'] = stanford_parser_models_directory

    # convert document to screenplay format
    # screenplay = BasicScreenwriter().write_screenplay(document)
    screenplay = PartOfSpeechSplitScreenwriter(StanfordParser()).write_screenplay(document)

    # output screenplay to file
    with open(output_screenplay_file_stem + ".json", "w") as output_file:
        output_file.write(json.dumps(screenplay, cls=ScreenplayJSONEncoder, indent=4))

    pass

if __name__ == '__main__':
    sys.exit(main())
