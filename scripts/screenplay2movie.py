"""

created by beth on 9/8/15
"""
import json
import sys

from blockers import BasicBlocker
from movie import MovieJSONEncoder
from screenplay import Screenplay


def main():
    screenplay_file = sys.argv[1]
    output_movie_file = sys.argv[2]

    # convert screenplay to movie
    screenplay = Screenplay.fromDict(json.loads(open(screenplay_file, "r").read()))
    movie = BasicBlocker().block_screenplay(screenplay)

    print("Made movie from screenplay...")

    # output screenplay to file
    with open(output_movie_file, "w") as output_file:
        output_file.write(json.dumps(movie, cls=MovieJSONEncoder, indent=4))


if __name__ == '__main__':
    sys.exit(main())
