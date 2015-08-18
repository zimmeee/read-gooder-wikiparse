import abc

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
            features.append(scene.identifier)
        return features


