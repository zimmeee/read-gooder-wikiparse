"""

created by noah on 9/8/15
"""
import json
import os
import sys

from feature_extractors import *

def main():
    movie_file = sys.argv[1]
    output_features_file = sys.argv[2]

    with open(movie_file) as movie_json:
        movie = Movie.fromDict(json.load(movie_json))

    # get Stanford Parser
    stanford_parser_directory = "../resources"
    stanford_parser_models_directory = "../resources"
    os.environ['STANFORD_PARSER'] = stanford_parser_directory
    os.environ['STANFORD_MODELS'] = stanford_parser_models_directory

    # extract features from screenplay
    f1 = DocumentPositionFeatureExtractor()
    f2 = OverallLengthFeatureExtractor()
    f3 = WordEntropyFeatureExtractor()
    f4 = AverageWordLengthFeatureExtractor()
    f5 = ParseTreeFeatureExtractor(StanfordParser())
    f6 = PartsOfSpeechFeatureExtractor()
    f7 = POSEntropyFeatureExtractor()
    f8 = NeighboringSceneFeatureExtractor(-1, OverallLengthFeatureExtractor())
    f9 = NeighboringSceneFeatureExtractor(-1, POSEntropyFeatureExtractor())
    features = MultiFeatureExtractor([f1, f2, f3, f4, f5, f6, f7, f8, f9]).get_features(movie)

    print("Extracted features from movie...")

    # output features to file
    with open(output_features_file, "w") as output_file:
        output_file.write(json.dumps({"screenplay_id": str(movie.screenplay_id),
                                      "features": features}, indent=4))


if __name__ == '__main__':
    sys.exit(main())