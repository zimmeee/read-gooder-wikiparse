import abc
from collections import defaultdict
from math import log

from nltk import wordpunct_tokenize, word_tokenize, pos_tag
from nltk.parse.stanford import StanfordParser

from screenplay import Screenplay
from movie import Movie


class FeatureExtractor:
    def __init__(self):
        self.features = defaultdict(dict)

    @abc.abstractmethod
    # returns an array of features
    def get_features(self, movie):
        if not isinstance(movie, Movie):
            raise Exception("Cannot extract features from non-movie object: " + str(movie))
        return


class DocumentPositionFeatureExtractor(FeatureExtractor):
    def get_features(self, movie):
        super(DocumentPositionFeatureExtractor, self).get_features(movie)
        position = 0
        for visual_scene in movie.visual_scenes:
            self.features[visual_scene.identifier] = {"position": position}
            position += 1
            print("DocumentPositionFeatureExtractor scene ", visual_scene.identifier)
        return self.features


class OverallLengthFeatureExtractor(FeatureExtractor):
    def get_features(self, movie):
        super(OverallLengthFeatureExtractor, self).get_features(movie)
        for visual_scene in movie.visual_scenes:
            scene_length = 0
            for visual_scene_element in visual_scene.visual_scene_elements:
                words = wordpunct_tokenize(visual_scene_element.text_string)
                scene_length += len(words)
            self.features[visual_scene.identifier] = {"overall_length": scene_length}
            print("OverallLengthFeatureExtractor scene ", visual_scene.identifier)
        return self.features



class AverageWordLengthFeatureExtractor(FeatureExtractor):
    def get_features(self, movie):
        super(AverageWordLengthFeatureExtractor, self).get_features(movie)
        for visual_scene in movie.visual_scenes:
            total_word_length = 0
            total_num_words = 0
            for visual_scene_element in visual_scene.visual_scene_elements:
                words = wordpunct_tokenize(visual_scene_element.text_string)
                for word in words:
                    total_word_length += len(word)
                    total_num_words += 1
            self.features[visual_scene.identifier] = {"avg_word_length": float(total_word_length) / total_num_words}
            print("AverageWordLengthFeatureExtractor scene ", visual_scene.identifier)
        return self.features


class WordEntropyFeatureExtractor(FeatureExtractor):
    def get_features(self, movie):
        super(WordEntropyFeatureExtractor, self).get_features(movie)

        for visual_scene in movie.visual_scenes:
            word_frequencies = defaultdict(int)
            total_words = 0
            for visual_scene_element in visual_scene.visual_scene_elements:
                words = wordpunct_tokenize(visual_scene_element.text_string)
                for word in words:
                    word_frequencies[word] += 1
                    total_words += 1
            entropy = 0.0
            for word in word_frequencies:
                p = float(word_frequencies[word]) / total_words
                entropy += p * log(p)
            self.features[visual_scene.identifier] = {"word_entropy": -1.0 * entropy}
            print("WordEntropyFeatureExtractor scene ", visual_scene.identifier)

        return self.features


class ParseTreeFeatureExtractor(FeatureExtractor):
    def __init__(self, parser):
        super().__init__()
        if not isinstance(parser, StanfordParser):
            raise Exception("Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree

    def get_features(self, movie):
        super(ParseTreeFeatureExtractor, self).get_features(movie)

        for visual_scene in movie.visual_scenes:
            max_tree_len = 0
            max_tree_height = 0
            for visual_scene_element in visual_scene.visual_scene_elements:
                input_trees = self.parser.raw_parse(visual_scene_element.text_string)
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
            self.features[visual_scene.identifier] = {"max_tree_length": max_tree_len,
                                                      "max_tree_height": max_tree_height}
            print("ParseTreeFeatureExtractor scene ", visual_scene.identifier)
        return self.features


class PartsOfSpeechFeatureExtractor(FeatureExtractor):
    def get_features(self, movie):
        super(PartsOfSpeechFeatureExtractor, self).get_features(movie)

        for visual_scene in movie.visual_scenes:
            pos_tag_features = defaultdict(int)
            for visual_scene_element in visual_scene.visual_scene_elements:
                words = word_tokenize(visual_scene_element.text_string)
                pos_tags = pos_tag(words)
                for tag in pos_tags:
                    pos_tag_features[tag[1]] += 1
            self.features[visual_scene.identifier] = pos_tag_features
            print("PartsOfSpeechFeatureExtractor scene ", visual_scene.identifier)
        return self.features


class POSEntropyFeatureExtractor(FeatureExtractor):
    def get_features(self, movie):
        super(POSEntropyFeatureExtractor, self).get_features(movie)

        for visual_scene in movie.visual_scenes:
            pos_tag_features = defaultdict(int)
            total_features = 0
            for visual_scene_element in visual_scene.visual_scene_elements:
                words = word_tokenize(visual_scene_element.text_string)
                pos_tags = pos_tag(words)
                for tag in pos_tags:
                    pos_tag_features[tag[1]] += 1
                    total_features += 1
            # calculate entropy
            entropy = 0.0
            for tag in pos_tag_features:
                p = float(pos_tag_features[tag]) / total_features
                entropy += p * log(p)
            self.features[visual_scene.identifier] = {"pos_entropy": -1.0 * entropy}
            print("POSEntropyFeatureExtractor scene ", visual_scene.identifier)
        return self.features


class NeighboringSceneFeatureExtractor(FeatureExtractor):
    def __init__(self, relative_position, base_feature_extractor):
        super().__init__()
        self.relative_position = relative_position
        self.base_feature_extractor = base_feature_extractor

    def get_features(self, movie):
        super(NeighboringSceneFeatureExtractor, self).get_features(movie)
        features = self.base_feature_extractor.get_features(movie)
        shifted_features = defaultdict(lambda: defaultdict())
        for identifier in features:
            shifted_identifier = identifier - self.relative_position
            for key in features[identifier]:
                shifted_key = key + "_" + str(self.relative_position)
                shifted_features[shifted_identifier][shifted_key] = features[identifier][key]
        return shifted_features


class MultiFeatureExtractor(FeatureExtractor):
    def __init__(self, list_of_feature_extractors):
        super().__init__()
        self.extractors = list_of_feature_extractors

    def get_features(self, movie):
        super(MultiFeatureExtractor, self).get_features(movie)
        features_by_id_combined = defaultdict(dict)
        for extractor in self.extractors:
            features_by_id = extractor.get_features(movie)  # dict of dicts scene_id:{features}
            for feature_id in features_by_id:
                features_by_id_combined[feature_id].update(features_by_id[feature_id])

        # make combined feature set
        features_combined = []
        for scene_id in features_by_id_combined:
            features = features_by_id_combined[scene_id]
            features["identifier"] = scene_id
            features_combined.append(features)
        return features_combined

class SceneWidthFeatureExtractor(FeatureExtractor):
    def get_features(self, movie):
        super(SceneWidthFeatureExtractor, self).get_features(movie)

        for visual_scene in movie.visual_scenes:
            sum_of_scene_widths = 0
            for visual_scene_element in visual_scene.visual_scene_elements:
                sum_of_scene_widths += visual_scene_element.width

            self.features[visual_scene.identifier] = {"avg_visual_scene_element_width": float(sum_of_scene_widths) / len(visual_scene.visual_scene_elements) }
            print("SceneWidthFeatureExtractor scene ", visual_scene.identifier)

        return self.features

