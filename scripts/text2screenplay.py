"""

created by noah on 9/4/15
"""
import json
import sys

from nltk.parse.stanford import StanfordParser

from scripts.Configurator import configure_stanford_parser
from raw_converters import BookNewlineFileRawConverter
from screenplay import ScreenplayJSONEncoder
from screenwriters import PartOfSpeechSplitScreenwriter


def main():
    text_file = sys.argv[1]
    document_title = sys.argv[2]
    output_screenplay_file_stem = sys.argv[3]

    # convert raw text to document format
    document = BookNewlineFileRawConverter().convertToDocument(open(text_file, "r").read(),
                                                               document_title)
    print("Converted to document...")

    configure_stanford_parser()

    # convert document to screenplay format
    # screenplay = BasicScreenwriter().write_screenplay(document)
    screenplay = PartOfSpeechSplitScreenwriter().write_screenplay(document)

    # output screenplay to file
    with open(output_screenplay_file_stem + ".json", "w") as output_file:
        output_file.write(json.dumps(screenplay, cls=ScreenplayJSONEncoder, indent=4))

    pass

if __name__ == '__main__':
    sys.exit(main())
