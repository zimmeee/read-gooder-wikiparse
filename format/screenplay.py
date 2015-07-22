"""
OpenMind Screenplay format - Documents are converted to this format prior to entry to Unity
created by beth on 7/22/15
"""
from json import JSONEncoder


class Screenplay(object):
    def __init__(self, scenes=None, title=None):
        self.scenes = scenes
        self.title = title

    @staticmethod
    def fromDict(dict_object):
        screenplay = Screenplay()
        screenplay.scenes = [Scene.fromDict(scene) for scene in dict_object["scenes"]]
        screenplay.title = dict_object["title"]
        return screenplay

    def addScene(self, scene):
        if not self.scenes:
            self.scenes = []
        self.scenes.append(scene)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Scene(object):
    def __init__(self, elements=None, duration=0.0):
        self.elements = elements
        self.duration = duration

    @staticmethod
    def fromDict(dict_object):
        scene = Scene()
        scene.elements = [SceneElement.fromDict(cp) for cp in dict_object["elements"]]
        scene.duration = float(dict_object["duration"])
        return scene

    def addElement(self, element):
        if not self.elements:
            self.elements = []
        self.elements.append(element)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class SceneElement(object):
    def __init__(self, content=None, identifier=None):
        self.content = content
        self.identifier = identifier
        # can be other qualities here, representing different properties of the element (strength, importance, etc.)

    @staticmethod
    def fromDict(dict_object):
        element = SceneElement()
        element.content = dict_object["content"]
        element.identifier = dict_object["identifier"]
        return element

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# JSON encoding #######################################################################################################


class SceneElementJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, SceneElement):
            raise Exception("Cannot use this encoder to encode non-Scene-Element class.")
        serialized_scene_element = {}
        if obj.content:
            serialized_scene_element["content"] = obj.content
        if obj.identifier:
            serialized_scene_element["identifier"] = obj.identifier
        return serialized_scene_element


class SceneJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Scene):
            raise Exception("Cannot use this encoder to encode non-Scene class.")
        serialized_scene = {}
        if obj.duration:
            serialized_scene["duration"] = obj.duration
        if obj.elements:
            scene_element_encoder = SceneElementJSONEncoder()  # for serializing individual scene elements
            serialized_scene["elements"] = [scene_element_encoder.default(e) for e in obj.elements]
        return serialized_scene


class ScreenplayJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Screenplay):
            raise Exception("Cannot use this encoder to encode non-Screenplay class.")
        serialized_screenplay = {}
        if obj.title:
            serialized_screenplay["title"] = obj.title
        if obj.scenes:
            scene_encoder = SceneJSONEncoder()  # for serializing individual scenes
            serialized_screenplay["scenes"] = [scene_encoder.default(scene) for scene in obj.scenes]
        return serialized_screenplay
