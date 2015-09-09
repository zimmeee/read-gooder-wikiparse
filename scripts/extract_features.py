"""

created by noah on 9/8/15
"""
import json
import sys
import Configurator
Configurator.runnable_from_command_line()

from feature_extractors import *


def main():
    movie_file = sys.argv[1]
    output_features_file = sys.argv[2]

    with open(movie_file) as movie_json:
        movie = Movie.fromDict(json.load(movie_json))

    Configurator.configure_stanford_parser("../resources")

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
    f10 = SceneWidthFeatureExtractor()
    features = MultiFeatureExtractor([f1, f2, f3, f4, f5, f6, f7, f8, f9, f10]).get_features(movie)

    print("Extracted features from movie...")

    # output features to file
    with open(output_features_file, "w") as output_file:
        output_file.write(json.dumps({"screenplay_id": str(movie.screenplay_id),
                                      "features": features}, indent=4))


if __name__ == '__main__':
    sys.exit(main())