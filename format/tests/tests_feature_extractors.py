import os
import unittest

from nltk.parse import stanford

from feature_extractors import DocumentPositionFeatureExtractor, OverallLengthFeatureExtractor, \
    AverageWordLengthFeatureExtractor, WordEntropyFeatureExtractor, ParseTreeFeatureExtractor, \
    PartsOfSpeechFeatureExtractor, MultiFeatureExtractor
from screenwriters import BasicScreenwriter
from raw_converters import BasicTextFileRawConverter


class FeatureExtractorTestCase(unittest.TestCase):
    def setUp(self):
        doc_source = "Supernovas are among the most energetic events in the universe and result in the " \
                     "complete disruption of stars at the end of their lives. Originally, the distinction " \
                     "between Type I and Type II supernovas was based solely on the presence or absence of " \
                     "hydrogen atoms (hydrogen lines). Supernovas without hydrogen lines were called Type I, " \
                     "while those with hydrogen lines were Type II. Subsequent analysis of many of these events " \
                     "revealed that this empirical classification schema instead reflected two different mechanisms " \
                     "for the supernova explosion. Type I supernovas happen in binary stars — two stars that orbit " \
                     "closely each other — when one of the two binary stars is a small, dense, white dwarf star. " \
                     "If the companion star ranges too close to the white dwarf that it is orbiting, the white dwarf’s " \
                     "gravitational pull will draw matter from the other star. When the white dwarf acquires enough " \
                     "matter to become at least 1.4 times as big as the Sun, it collapses and explodes in a supernova. " \
                     "Type II supernovas occur when a star, much more massive than the Sun, ends its life. " \
                     "When such a star begins burning out, the core of the star quickly collapses releasing amazing " \
                     "energy in the form of neutrinos, a kind of particle smaller than even an atom. Electromagnetic " \
                     "radiation — energy that is electric and magnetic — causes the star to explode in a supernova. " \
                     "Whereas Type I supernovas typically destroy their parent stars, Type II explosions usually leave " \
                     "behind the stellar core. The classification schema regarding the mechanism for supernova " \
                     "explosions helps to more succinctly answer the question: Is the Sun in danger of becoming a " \
                     "supernova? Neither does our Sun have a companion star orbiting it nor does our Sun have the mass " \
                     "necessary to become a supernova. Furthermore, it will be another billion years until the Sun runs " \
                     "out of fuel and swells into a red giant star before going into a white dwarf form."
        doc_title = "Supernova"
        document = BasicTextFileRawConverter().convertToDocument(doc_source, doc_title)
        converter = BasicScreenwriter()
        self.screenplay = converter.write_screenplay(document)
        self.stanford_parser_directory = "/Users/beth/Documents/openmind/read-gooder-wikiparse/resources"
        self.stanford_parser_models_directory = "/Users/beth/Documents/openmind/read-gooder-wikiparse/resources"


class DocumentPositionFeatureExtractorTests(FeatureExtractorTestCase):
    def testExtractFeatures(self):
        self.feature_extractor = DocumentPositionFeatureExtractor()
        features = self.feature_extractor.get_features(self.screenplay)
        self.assertEquals(features, [{'position': 0}, {'position': 1}, {'position': 2},
                                     {'position': 3}, {'position': 4}, {'position': 5},
                                     {'position': 6}, {'position': 7}, {'position': 8},
                                     {'position': 9}, {'position': 10}, {'position': 11},
                                     {'position': 12}, {'position': 13}])


class OverallLengthFeatureExtractorTests(FeatureExtractorTestCase):
    def testExtractFeatures(self):
        self.feature_extractor = OverallLengthFeatureExtractor()
        features = self.feature_extractor.get_features(self.screenplay)
        self.assertEquals(features, [{'overall_length': 25}, {'overall_length': 26},
                                     {'overall_length': 18}, {'overall_length': 23},
                                     {'overall_length': 33}, {'overall_length': 31},
                                     {'overall_length': 29}, {'overall_length': 19},
                                     {'overall_length': 34}, {'overall_length': 19},
                                     {'overall_length': 20}, {'overall_length': 27},
                                     {'overall_length': 23}, {'overall_length': 30}])


class AverageWordLengthFeatureExtractorTests(FeatureExtractorTestCase):
    def testExtractFeatures(self):
        self.feature_extractor = AverageWordLengthFeatureExtractor()
        features = self.feature_extractor.get_features(self.screenplay)
        true_avg_lengths = [{'avg_word_length': 4.52}, {'avg_word_length': 4.730769230769231},
                            {'avg_word_length': 4.666666666666667},
                            {'avg_word_length': 6.304347826086956},
                            {'avg_word_length': 3.787878787878788},
                            {'avg_word_length': 4.096774193548387},
                            {'avg_word_length': 3.7586206896551726},
                            {'avg_word_length': 3.6315789473684212},
                            {'avg_word_length': 4.176470588235294},
                            {'avg_word_length': 4.842105263157895},
                            {'avg_word_length': 5.2}, {'avg_word_length': 5.2592592592592595},
                            {'avg_word_length': 4.217391304347826}, {'avg_word_length': 4.0}]
        for i in range(len(features)):
            self.assertEquals(features[i], true_avg_lengths[i])


class LeastCommonWordFeatureExtractorTests(FeatureExtractorTestCase):
    def testExtractFeatures(self):
        self.feature_extractor = WordEntropyFeatureExtractor()
        features = self.feature_extractor.get_features(self.screenplay)
        self.assertEquals(features, [{'least_common_word_freq': 1, 'least_common_word_length': 3},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 10},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 7},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 10},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 6},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 2},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 8},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 5},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 4},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 15},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 7},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 3},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 7},
                                     {'least_common_word_freq': 1, 'least_common_word_length': 11}])


class ParseTreeFeatureExtractorTests(FeatureExtractorTestCase):
    def testExtractFeatures(self):
        os.environ['STANFORD_PARSER'] = self.stanford_parser_directory
        os.environ['STANFORD_MODELS'] = self.stanford_parser_models_directory
        stanfordParser = stanford.StanfordParser()

        self.feature_extractor = ParseTreeFeatureExtractor(stanfordParser)
        features = self.feature_extractor.get_features(self.screenplay)
        self.assertEquals(features, [{'max_tree_height': 16, 'max_tree_length': 3},
                                     {'max_tree_height': 11, 'max_tree_length': 5},
                                     {'max_tree_height': 10, 'max_tree_length': 3},
                                     {'max_tree_height': 9, 'max_tree_length': 3},
                                     {'max_tree_height': 13, 'max_tree_length': 4},
                                     {'max_tree_height': 10, 'max_tree_length': 5},
                                     {'max_tree_height': 13, 'max_tree_length': 5},
                                     {'max_tree_height': 10, 'max_tree_length': 3},
                                     {'max_tree_height': 15, 'max_tree_length': 6},
                                     {'max_tree_height': 10, 'max_tree_length': 3},
                                     {'max_tree_height': 7, 'max_tree_length': 6},
                                     {'max_tree_height': 16, 'max_tree_length': 3},
                                     {'max_tree_height': 12, 'max_tree_length': 3},
                                     {'max_tree_height': 14, 'max_tree_length': 5}])


class PartsOfSpeechFeatureExtractorTests(FeatureExtractorTestCase):
    def testExtractFeatures(self):
        self.feature_extractor = PartsOfSpeechFeatureExtractor()
        features = self.feature_extractor.get_features(self.screenplay)
        self.assertEquals([len(f) for f in features],
                          [11, 13, 9, 10, 15, 15, 18, 12, 13, 11, 12, 12, 13, 15])


class MultiFeatureExtractorTests(FeatureExtractorTestCase):
    def testExtractFeatures(self):
        f1 = DocumentPositionFeatureExtractor()
        f2 = OverallLengthFeatureExtractor()
        f3 = WordEntropyFeatureExtractor()
        self.feature_extractor = MultiFeatureExtractor([f1, f2, f3])
        features = self.feature_extractor.get_features(self.screenplay)
        self.assertEquals(features, [{'position': 0, 'least_common_word_length': 3,
                                      'overall_length': 25, 'least_common_word_freq': 1},
                                     {'position': 1, 'least_common_word_length': 10,
                                      'overall_length': 26, 'least_common_word_freq': 1},
                                     {'position': 2, 'least_common_word_length': 7,
                                      'overall_length': 18, 'least_common_word_freq': 1},
                                     {'position': 3, 'least_common_word_length': 10,
                                      'overall_length': 23, 'least_common_word_freq': 1},
                                     {'position': 4, 'least_common_word_length': 6,
                                      'overall_length': 33, 'least_common_word_freq': 1},
                                     {'position': 5, 'least_common_word_length': 2,
                                      'overall_length': 31, 'least_common_word_freq': 1},
                                     {'position': 6, 'least_common_word_length': 8,
                                      'overall_length': 29, 'least_common_word_freq': 1},
                                     {'position': 7, 'least_common_word_length': 5,
                                      'overall_length': 19, 'least_common_word_freq': 1},
                                     {'position': 8, 'least_common_word_length': 4,
                                      'overall_length': 34, 'least_common_word_freq': 1},
                                     {'position': 9, 'least_common_word_length': 15,
                                      'overall_length': 19, 'least_common_word_freq': 1},
                                     {'position': 10, 'least_common_word_length': 7,
                                      'overall_length': 20, 'least_common_word_freq': 1},
                                     {'position': 11, 'least_common_word_length': 3,
                                      'overall_length': 27, 'least_common_word_freq': 1},
                                     {'position': 12, 'least_common_word_length': 7,
                                      'overall_length': 23, 'least_common_word_freq': 1},
                                     {'position': 13, 'least_common_word_length': 11,
                                      'overall_length': 30, 'least_common_word_freq': 1}])
