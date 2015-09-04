"""

created by noah on 9/4/15
"""
import os, sys, inspect
import json

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../format")))
print(cmd_subfolder)
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from screenplay import Screenplay, ScreenplayJSONEncoder

def main():
    screenplay_file = sys.argv[1]

    with open(screenplay_file) as serialized_screenplay:
        screenplay = Screenplay.fromDict(json.load(serialized_screenplay))
        # print(json.dumps(screenplay, cls=ScreenplayJSONEncoder, indent=4))

        for scene in screenplay.scenes:
            for element in scene.elements:
                str = ' ' * element.priority + element.content
                print(str)

    pass


if __name__ == '__main__':
    sys.exit(main())