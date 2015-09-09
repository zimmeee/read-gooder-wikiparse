"""
Blockers - responsible for turning screenplays into movies (currently for display in Unity only)
blocking: the precise movement and staging of actors on a stage
created by beth on 9/7/15
"""
import abc

from movie import VisualScene, VisualSceneElement, Movie
from screenplay import Screenplay


class Blocker(object):
    @abc.abstractmethod
    # returns a list of DisplayFrame objects
    def block_screenplay(self, screenplay):
        if not isinstance(screenplay, Screenplay):
            raise Exception("Yo, this is not a screenplay: " + str(screenplay))
        return


class BasicBlocker(Blocker):

    # Valid overflow_modes: [Overflow, Ellipsis, Masking, Truncate, ScrollRect, Page]
    def __init__(self, width=250, overflow_mode="Overflow"):
        self.width = width
        self.overflow_mode = overflow_mode

    def block_screenplay(self, screenplay):
        visual_scenes = []

        for scene in screenplay.scenes:
            visual_scene = VisualScene()

            visual_scene_element = VisualSceneElement()
            visual_scene_element.overflow_mode = self.overflow_mode
            visual_scene_element.width = self.width
            visual_scene_element.alignment = "TopLeft"
            visual_scene_element.color = (1.0, 1.0, 1.0, 1.0)
            visual_scene_element.font_name = "Garamond Regular SDF"
            visual_scene_element.font_size = 120.0
            visual_scene_element.font_style = "Normal"
            visual_scene_element.height = 200.0
            visual_scene_element.kerning = False
            visual_scene_element.line_spacing = 0.0
            visual_scene_element.outline_color = (0.5, 0.5, 0.5, 1.0)
            visual_scene_element.outline_width = 0.2
            visual_scene_element.rotation = (0.0, 0.0, 0.0, 1.0)
            visual_scene_element.word_wrapping = True

            visual_scene_element.relative_X_position = 0.0
            visual_scene_element.relative_Y_position = 0.0
            visual_scene_element.relative_Z_position = 0.0

            visual_scene_element.identifier = ""
            visual_scene_element.text_string = ""

            for scene_element in scene.elements:
                visual_scene_element.identifier += scene_element.name + " "
                visual_scene_element.text_string += " " * scene_element.priority + scene_element.content + "\n"

            visual_scene.addElement(visual_scene_element)

            visual_scene.duration = scene.duration
            visual_scene.identifier = scene.identifier

            visual_scenes.append(visual_scene)

        return Movie(visual_scenes, screenplay.screenplay_uuid)
