import abc
from collections import defaultdict

from nltk import wordpunct_tokenize, word_tokenize, pos_tag
from nltk.parse.stanford import StanfordParser

from screenplay import Screenplay


class FeatureExtractor:
    @abc.abstractmethod
    # returns an array of features
    def get_features(self, screenplay):
        if not isinstance(screenplay, Screenplay):
            raise Exception("Cannot extract features from non-screenplay object: " + str(screenplay))
        return


class DocumentPositionFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        features = []
        for scene in screenplay.scenes:
            features.append({"position": scene.identifier})
        return features


class OverallLengthFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        features = []
        for scene in screenplay.scenes:
            scene_length = 0
            for element in scene.elements:
                words = wordpunct_tokenize(element.content)
                scene_length += len(words)
            features.append({"overall_length": scene_length})
        return features


class AverageWordLengthFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        features = []
        for scene in screenplay.scenes:
            total_word_length = 0
            total_num_words = 0
            for element in scene.elements:
                words = wordpunct_tokenize(element.content)
                for word in words:
                    total_word_length += len(word)
                    total_num_words += 1
            features.append({"avg_word_length": float(total_word_length) / total_num_words})
        return features


class LeastCommonWordFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        # calculate document-level word frequencies
        word_frequencies = defaultdict(int)
        for scene in screenplay.scenes:
            for element in scene.elements:
                words = wordpunct_tokenize(element.content)
                for word in words:
                    word_frequencies[word] += 1

        # extract features
        features = []
        for scene in screenplay.scenes:
            least_common_word = "bob"
            least_common_wordfreq = 1000
            for element in scene.elements:
                words = wordpunct_tokenize(element.content)
                for word in words:
                    if word_frequencies[word] < least_common_wordfreq:
                        least_common_wordfreq = word_frequencies[word]
                        least_common_word = word
            features.append({"least_common_word_freq": least_common_wordfreq,
                             "least_common_word_length": len(least_common_word)})
        return features


class ParseTreeFeatureExtractor(FeatureExtractor):
    def __init__(self, parser):
        if not isinstance(parser, StanfordParser):
            raise Exception("Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree

    def get_features(self, screenplay):
        features = []
        for scene in screenplay.scenes:
            max_tree_len = 0
            max_tree_height = 0
            for element in scene.elements:
                input_trees = self.parser.raw_parse(element.content)
                for tree_set in input_trees:
                    for tree in tree_set:
                        if len(tree) > max_tree_len:
                            max_tree_len = len(tree)
                        if tree.height() > max_tree_height:
                            max_tree_height = tree.height()
            features.append({"max_tree_length": max_tree_len,
                             "max_tree_height": max_tree_height})
        return features


class PartsOfSpeechFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        features = []
        for scene in screenplay.scenes:
            pos_tag_features = defaultdict(int)
            for element in scene.elements:
                words = word_tokenize(element.content)
                pos_tags = pos_tag(words)
                for tag in pos_tags:
                    pos_tag_features[tag[1]] += 1
            features.append(pos_tag_features)
        return features


class MultiFeatureExtractor(FeatureExtractor):
    def __init__(self, list_of_feature_extractors):
        self.extractors = list_of_feature_extractors

    def get_features(self, screenplay):
        all_features = []
        for extractor in self.extractors:
            all_features.append(extractor.get_features(screenplay))

        # make combined feature set
        features_combined = []
        for scene_id in range(len(all_features[0])):
            features = {}
            for featureset_id in range(len(all_features)):
                for key in all_features[featureset_id][scene_id]:
                    features[key] = all_features[featureset_id][scene_id][key]
            features_combined.append(features)
        return features_combined
