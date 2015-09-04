"""
OpenMind Screenplay format - Documents are converted to this format prior to entry to Unity
created by beth on 7/22/15
"""
from json import JSONEncoder
import uuid


class Screenplay(object):
    def __init__(self, scenes=None, title=None):
        self.scenes = scenes
        self.title = title
        self.uuid = uuid.uuid1()  # randomly generated uuid for this screenplay

    @staticmethod
    def fromDict(dict_object):
        screenplay = Screenplay()
        screenplay.scenes = [Scene.fromDict(scene) for scene in dict_object["scenes"]]
        screenplay.title = dict_object["title"]
        screenplay.uuid = uuid.UUID(dict_object["screenplay_id"])
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

"""
A scene is the unit of display: something that gets displayed for a fixed amount of time
It is made up of SceneElements
"""
class Scene(object):
    def __init__(self, elements=None, duration=0.0, identifier=0):
        self.elements = elements
        self.duration = duration
        self.identifier = identifier

    @staticmethod
    def fromDict(dict_object):
        scene = Scene()
        scene.elements = [SceneElement.fromDict(cp) for cp in dict_object["elements"]]
        scene.duration = float(dict_object["duration"])
        scene.identifier = int(dict_object["identifier"])
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

"""
The components that make up a Scene (e.g. sentence chunks).
Priority gives an indication to the Blocker class of how to display this SceneElement
"""
class SceneElement(object):
    def __init__(self, content=None, name=None, priority=0):
        self.content = content
        self.name = name
        self.priority = priority
        # can be other qualities here, representing different properties of the element (strength, importance, etc.)

    @staticmethod
    def fromDict(dict_object):
        element = SceneElement()
        element.content = dict_object["content"]
        element.name = dict_object["name"]
        element.priority = dict_object["priority"]
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
        serialized_scene_element = {"content": obj.content,
                                    "name": obj.name,
                                    "priority": obj.priority}
        return serialized_scene_element


class SceneJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Scene):
            raise Exception("Cannot use this encoder to encode non-Scene class.")
        scene_element_encoder = SceneElementJSONEncoder()  # for serializing individual scene elements
        serialized_scene = {"duration": obj.duration,
                            "elements": [scene_element_encoder.default(e) for e in obj.elements],
                            "identifier": obj.identifier}
        return serialized_scene


class ScreenplayJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Screenplay):
            raise Exception("Cannot use this encoder to encode non-Screenplay class.")
        scene_encoder = SceneJSONEncoder()  # for serializing individual scenes
        serialized_screenplay = {"title": obj.title,
                                 "scenes": [scene_encoder.default(scene) for scene in obj.scenes],
                                 "screenplay_id": str(obj.uuid)}
        return serialized_screenplay
