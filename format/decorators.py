import abc
from copy import copy

from screenplay import Screenplay


class Decorator(object):
    @abc.abstractmethod
    def decorate_screenplay(self, screenplay):
        if not isinstance(screenplay, Screenplay):
            raise TypeError("Argument is not a screenplay.")
        return


class FirstLastSceneAddDecorator(Decorator):
    def decorate_screenplay(self, screenplay):
        first_scene = copy(screenplay.scenes[0])
        last_scene = copy(screenplay.scenes[len(screenplay.scenes) - 1])
        screenplay.scenes.insert(0, first_scene)
        screenplay.scenes.append(last_scene)

        # redo identifiers
        scene_id = 0
        for scene in screenplay.scenes:
            scene.identifier = scene_id
            scene_id += 1

        return screenplay
