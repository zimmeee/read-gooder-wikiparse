import abc
from collections import defaultdict

from nltk import wordpunct_tokenize, word_tokenize, pos_tag
from nltk.parse.stanford import StanfordParser

from screenplay import Screenplay


class FeatureExtractor:
    def __init__(self):
        self.features = defaultdict(dict)

    @abc.abstractmethod
    # returns an array of features
    def get_features(self, screenplay):
        if not isinstance(screenplay, Screenplay):
            raise Exception("Cannot extract features from non-screenplay object: " + str(screenplay))
        return


class DocumentPositionFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        super(DocumentPositionFeatureExtractor, self).get_features(screenplay)
        position = 0
        for scene in screenplay.scenes:
            self.features[scene.identifier] = {"position": position}
            position += 1
            print("DocumentPositionFeatureExtractor scene ", scene.identifier)
        return self.features


class OverallLengthFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        for scene in screenplay.scenes:
            scene_length = 0
            for element in scene.elements:
                words = wordpunct_tokenize(element.content)
                scene_length += len(words)
            self.features[scene.identifier] = {"overall_length": scene_length}
            print("OverallLengthFeatureExtractor scene ", scene.identifier)
        return self.features


class AverageWordLengthFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        for scene in screenplay.scenes:
            total_word_length = 0
            total_num_words = 0
            for element in scene.elements:
                words = wordpunct_tokenize(element.content)
                for word in words:
                    total_word_length += len(word)
                    total_num_words += 1
            self.features[scene.identifier] = {"avg_word_length": float(total_word_length) / total_num_words}
            print("AverageWordLengthFeatureExtractor scene ", scene.identifier)
        return self.features


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
        for scene in screenplay.scenes:
            least_common_word = "bob"
            least_common_wordfreq = 1000
            for element in scene.elements:
                words = wordpunct_tokenize(element.content)
                for word in words:
                    if word_frequencies[word] < least_common_wordfreq:
                        least_common_wordfreq = word_frequencies[word]
                        least_common_word = word
            self.features[scene.identifier] = {"least_common_word_freq": least_common_wordfreq,
                                               "least_common_word_length": len(least_common_word),
                                               "identifier": scene.identifier}
            print("LeastCommonWordFeatureExtractor scene ", scene.identifier)

        return self.features


class ParseTreeFeatureExtractor(FeatureExtractor):
    def __init__(self, parser):
        super().__init__()
        if not isinstance(parser, StanfordParser):
            raise Exception("Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree

    def get_features(self, screenplay):
        for scene in screenplay.scenes:
            max_tree_len = 0
            max_tree_height = 0
            for element in scene.elements:
                input_trees = self.parser.raw_parse(element.content)
                for tree_set in input_trees:
                    for tree in tree_set:
                        if len(tree) > max_tree_len:
                            max_tree_len = len(tree)  # The length of a tree is the number of children it has.
                        if tree.height() > max_tree_height:
                            max_tree_height = tree.height()  # The height of a tree
                            # containing no children is 1; the height of a tree
                            # containing only leaves is 2; and the height of any other
                            # tree is one plus the maximum of its children's
                            # heights.
            self.features[scene.identifier] = {"max_tree_length": max_tree_len,
                                               "max_tree_height": max_tree_height}
            print("ParseTreeFeatureExtractor scene ", scene.identifier)
        return self.features


class PartsOfSpeechFeatureExtractor(FeatureExtractor):
    def get_features(self, screenplay):
        for scene in screenplay.scenes:
            pos_tag_features = defaultdict(int)
            for element in scene.elements:
                words = word_tokenize(element.content)
                pos_tags = pos_tag(words)
                for tag in pos_tags:
                    pos_tag_features[tag[1]] += 1
            self.features[scene.identifier] = pos_tag_features
            print("PartsOfSpeechFeatureExtractor scene ", scene.identifier)
        return self.features


class MultiFeatureExtractor(FeatureExtractor):
    def __init__(self, list_of_feature_extractors):
        super().__init__()
        self.extractors = list_of_feature_extractors

    def get_features(self, screenplay):
        features_by_id_combined = defaultdict(dict)
        for extractor in self.extractors:
            features_by_id = extractor.get_features(screenplay)  # dict of dicts scene_id:{features}
            for id in features_by_id:
                features_by_id_combined[id].update(features_by_id[id])

        # make combined feature set
        features_combined = []
        for scene_id in features_by_id_combined:
            features = features_by_id_combined[scene_id]
            features["identifier"] = scene_id
            features_combined.append(features)
        return features_combined
