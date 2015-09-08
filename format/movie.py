"""
OpenMind Movie format - Screenplays are converted to this format prior to entry to Unity
created by beth on 9/7/15
"""
from json import JSONEncoder
import uuid


class Movie(object):
    def __init__(self, visual_scenes=None, screenplay_id=None):
        self.visual_scenes = visual_scenes
        self.screenplay_id = screenplay_id

    @staticmethod
    def fromDict(dict_object):
        movie = Movie()
        movie.visual_scenes = [VisualScene.fromDict(visual_scene) for visual_scene in dict_object["visual_scenes"]]
        movie.screenplay_id = uuid.UUID(dict_object["screenplay_id"])
        return movie

    def addScene(self, visual_scene):
        if not self.visual_scenes:
            self.visual_scenes = []
        self.visual_scenes.append(visual_scene)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str(self.__dict__)


class VisualScene(object):
    def __init__(self, visual_scene_elements=None, duration=0.0, identifier=0):
        self.visual_scene_elements = visual_scene_elements
        self.duration = duration
        self.identifier = identifier

    @staticmethod
    def fromDict(dict_object):
        scene = VisualScene()
        scene.visual_scene_elements = [VisualSceneElement.fromDict(cp) for cp in dict_object["visual_scene_elements"]]
        scene.duration = float(dict_object["duration"])
        scene.identifier = int(dict_object["identifier"])
        return scene

    def addElement(self, visual_scene_element):
        if not self.visual_scene_elements:
            self.visual_scene_elements = []
        self.visual_scene_elements.append(visual_scene_element)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str(self.__dict__)


class VisualSceneElement(object):
    def __init__(self, alignment="TopLeft", color=(1.0, 1.0, 1.0, 1.0), font_name="Garamond Regular SDF",
                 font_size=120.0, font_style="Normal", height=200.0, kerning=False,
                 line_spacing=0.0, outline_color=(0.5, 0.5, 0.5, 1), outline_width=0.2,
                 overflow_mode="Overflow", rotation=(0.0, 0.0, 0.0, 1.0), width=250.0,
                 word_wrapping=True, relative_X_position=0.0, relative_Y_position=0.0,
                 relative_Z_position=0.0, identifier="", text_string=""):
        self.alignment = alignment
        self.color = color
        self.font_name = font_name
        self.font_size = font_size
        self.font_style = font_style
        self.height = height
        self.kerning = kerning
        self.line_spacing = line_spacing
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.overflow_mode = overflow_mode
        self.rotation = rotation
        self.width = width
        self.word_wrapping = word_wrapping

        self.relative_X_position = relative_X_position
        self.relative_Y_position = relative_Y_position
        self.relative_Z_position = relative_Z_position

        self.identifier = identifier
        self.text_string = text_string

    @staticmethod
    def fromDict(dict_object):
        element = VisualSceneElement()
        element.alignment = dict_object["alignment"]
        element.color = tuple(dict_object["color"])
        element.font_name = dict_object["font_name"]
        element.font_size = dict_object["font_size"]
        element.height = dict_object["height"]
        element.kerning = dict_object["kerning"]
        element.line_spacing = dict_object["line_spacing"]
        element.outline_color = tuple(dict_object["outline_color"])
        element.outline_width = dict_object["outline_width"]
        element.overflow_mode = dict_object["overflow_mode"]
        element.rotation = tuple(dict_object["rotation"])
        element.width = dict_object["width"]
        element.word_wrapping = dict_object["word_wrapping"]
        element.relative_X_position = dict_object["relative_X_position"]
        element.relative_Y_position = dict_object["relative_Y_position"]
        element.relative_Z_position = dict_object["relative_Z_position"]
        element.identifier = dict_object["identifier"]
        element.text_string = dict_object["text_string"]
        return element

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str(self.__dict__)


# JSON encoding #######################################################################################################


class VisualSceneElementJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, VisualSceneElement):
            raise Exception("Cannot use this encoder to encode non-Visual-Scene-Element class.")
        serialized_scene_element = {"alignment": obj.alignment,
                                    "color": obj.color,
                                    "font_name": obj.font_name,
                                    "font_size": obj.font_size,
                                    "font_style": obj.font_style,
                                    "height": obj.height,
                                    "kerning": obj.kerning,
                                    "line_spacing": obj.line_spacing,
                                    "outline_color": obj.outline_color,
                                    "outline_width": obj.outline_width,
                                    "overflow_mode": obj.overflow_mode,
                                    "rotation": obj.rotation,
                                    "width": obj.width,
                                    "word_wrapping": obj.word_wrapping,
                                    "relative_X_position": obj.relative_X_position,
                                    "relative_Y_position": obj.relative_Y_position,
                                    "relative_Z_position": obj.relative_Z_position,
                                    "identifier": obj.identifier,
                                    "text_string": obj.text_string}
        return serialized_scene_element


class VisualSceneJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, VisualScene):
            raise Exception("Cannot use this encoder to encode non-Visual-Scene class.")
        scene_element_encoder = VisualSceneElementJSONEncoder()  # for serializing individual visual scene elements
        serialized_scene = {"duration": obj.duration,
                            "visual_scene_elements": [scene_element_encoder.default(e)
                                                      for e in obj.visual_scene_elements],
                            "identifier": obj.identifier}
        return serialized_scene


class MovieJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Movie):
            raise Exception("Cannot use this encoder to encode non-Movie class.")
        scene_encoder = VisualSceneJSONEncoder()  # for serializing individual scenes
        serialized_movie = {"visual_scenes": [scene_encoder.default(scene) for scene in obj.visual_scenes],
                            "screenplay_id": str(obj.screenplay_id)}
        return serialized_movie
