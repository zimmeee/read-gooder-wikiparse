import json
import os
import sys

from feature_extractors import *
from raw_converters import BookNewlineFileRawConverter
from screenplay import ScreenplayJSONEncoder
from screenwriters import BasicScreenwriter, RandomizedScreenwriter

text_file = sys.argv[1]
document_title = sys.argv[2]
output_screenplay_file_stem = sys.argv[3]
output_features_file = sys.argv[4]

# convert raw text to document format
document = BookNewlineFileRawConverter().convertToDocument(open(text_file, "r").read(),
                                                           document_title)
print("Converted to document...")

# convert document to screenplay format
screenplay = BasicScreenwriter().write_screenplay(document)

# output screenplay to file
with open(output_screenplay_file_stem + ".json", "w") as output_file:
    output_file.write(json.dumps(screenplay, cls=ScreenplayJSONEncoder, indent=4))

print("Converted to screenplay...")

# randomized versions of screenplay
for i in range(5):
    randomized_screenplay = RandomizedScreenwriter().write_screenplay(document)
    with open(output_screenplay_file_stem + "r" + str(i) + ".json", "w") as output_file:
        output_file.write(json.dumps(randomized_screenplay, cls=ScreenplayJSONEncoder, indent=4))

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

print("Extracted features from screenplay...")

# output features to file
with open(output_features_file, "w") as output_file:
    output_file.write(json.dumps({"screenplay_id": str(screenplay.uuid),
                                  "features": features}, indent=4))
