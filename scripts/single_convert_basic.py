import json
import os
import sys

from blockers import BasicBlocker
from decorators import FirstLastSceneAddDecorator
from feature_extractors import *
from movie import MovieJSONEncoder
from raw_converters import BasicTextFileRawConverter
from screenwriters import FixedDimensionScreenwriter

text_file = sys.argv[1]
document_title = sys.argv[2]
output_movie_file = sys.argv[3]
output_features_file = sys.argv[4]
height_in_lines = int(sys.argv[5])
width_in_chars = int(sys.argv[6])

# convert raw text to document format
document = BasicTextFileRawConverter().convertToDocument(open(text_file, "r").read(),
                                                         document_title)
print("Converted to document...")

# convert document to screenplay format
screenplay = FixedDimensionScreenwriter(height_in_lines, width_in_chars).write_screenplay(document)

print("Converted to screenplay...")

# add duplicate first and last scenes
decorator = FirstLastSceneAddDecorator()
screenplay = decorator.decorate_screenplay(screenplay)

# convert screenplay to a movie
blocker = BasicBlocker()
blocker.font_name = "Geometria-Light SDF"

movie = blocker.block_screenplay(screenplay)

# output movie to file
with open(output_movie_file, "w") as output_file:
    output_file.write(json.dumps(movie, cls=MovieJSONEncoder, indent=4))

# get Stanford Parser
stanford_parser_directory = "/Users/beth/Documents/openmind/read-gooder-wikiparse/resources"
stanford_parser_models_directory = "/Users/beth/Documents/openmind/read-gooder-wikiparse/resources"
os.environ['STANFORD_PARSER'] = stanford_parser_directory
os.environ['STANFORD_MODELS'] = stanford_parser_models_directory

# extract features from movie
f1 = DocumentPositionFeatureExtractor()
f2 = OverallLengthFeatureExtractor()
f3 = WordEntropyFeatureExtractor()
f4 = AverageWordLengthFeatureExtractor()
# f5 = ParseTreeFeatureExtractor(StanfordParser())
f6 = PartsOfSpeechFeatureExtractor()
f7 = POSEntropyFeatureExtractor()
f8 = NeighboringSceneFeatureExtractor(-1, OverallLengthFeatureExtractor())
f9 = NeighboringSceneFeatureExtractor(-1, POSEntropyFeatureExtractor())
features = MultiFeatureExtractor([f1, f2, f3, f4, f6, f7, f8, f9]).get_features(movie)

print("Extracted features from movie...")

# output features to file
with open(output_features_file, "w") as output_file:
    output_file.write(json.dumps({"screenplay_id": str(screenplay.doc_id), "features": features}, indent=4))
