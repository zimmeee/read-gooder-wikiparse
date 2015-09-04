import json
import sys

from screenplay import Screenplay, Scene, SceneElement, ScreenplayJSONEncoder

output_uniform_screenplay = open(sys.argv[1], "w")

# make uniform scenes
uniform_scenes = []
for i in range(100):
    single_element = SceneElement(content="S%03d" % i, name="S%d" % i, priority=0)
    uniform_scenes.append(Scene(elements=[single_element], duration=100.0, identifier=i))

# assemble screenplay from scenes
screenplay = Screenplay(scenes=uniform_scenes, title="Uniform Screenplay")

# output to file
output_uniform_screenplay.write(json.dumps(screenplay, cls=ScreenplayJSONEncoder, indent=4))
