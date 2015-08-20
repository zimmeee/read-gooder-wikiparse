import json
import os
import sys

from feature_extractors import *
from raw_converters import BasicTextFileRawConverter
from screenplay import ScreenplayJSONEncoder
from screenwriters import BasicScreenwriter

text_file = sys.argv[1]
document_title = sys.argv[2]
output_screenplay_file = sys.argv[3]
output_features_file = sys.argv[4]

# convert raw text to document format
document = BasicTextFileRawConverter().convertToDocument(open(text_file, "r").read(),
                                                         document_title)

# convert document to screenplay format
screenplay = BasicScreenwriter().write_screenplay(document)

# get Stanford Parser
stanford_parser_directory = "/Users/beth/Documents/openmind/read-gooder-wikiparse/resources"
stanford_parser_models_directory = "/Users/beth/Documents/openmind/read-gooder-wikiparse/resources"
os.environ['STANFORD_PARSER'] = stanford_parser_directory
os.environ['STANFORD_MODELS'] = stanford_parser_models_directory

# extract features from screenplay
f1 = DocumentPositionFeatureExtractor()
f2 = OverallLengthFeatureExtractor()
f3 = LeastCommonWordFeatureExtractor()
f4 = AverageWordLengthFeatureExtractor()
f5 = ParseTreeFeatureExtractor(StanfordParser())
f6 = PartsOfSpeechFeatureExtractor()
features = MultiFeatureExtractor([f1, f2, f3, f4, f5, f6]).get_features(screenplay)

# output screenplay and features to file
with open(output_screenplay_file, "w") as output_file:
    output_file.write(json.dumps(screenplay, cls=ScreenplayJSONEncoder, indent=4))

with open(output_features_file, "w") as output_file:
    output_file.write(json.dumps({"screenplay_id": str(screenplay.uuid),
                                  "features": features}, indent=4))
