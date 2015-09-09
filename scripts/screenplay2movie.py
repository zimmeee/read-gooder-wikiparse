"""

created by beth on 9/8/15
"""
import json
import sys
import Configurator

Configurator.runnable_from_command_line()

from blockers import BasicBlocker
from movie import MovieJSONEncoder
from screenplay import Screenplay


def main():
    screenplay_file = sys.argv[1]
    output_movie_file = sys.argv[2]
    width = sys.argv[3] if len(sys.argv) == 4 else 250
    overflow_mode = sys.argv[4] if len(sys.argv) == 5 else "Overflow"

    # convert screenplay to movie
    screenplay = Screenplay.fromDict(json.loads(open(screenplay_file, "r").read()))
    movie = BasicBlocker(width=width, overflow_mode=overflow_mode).block_screenplay(screenplay)

    print("Made movie from screenplay...")

    # output screenplay to file
    with open(output_movie_file, "w") as output_file:
        output_file.write(json.dumps(movie, cls=MovieJSONEncoder, indent=4))


if __name__ == '__main__':
    sys.exit(main())
