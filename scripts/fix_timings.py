import json
import sys

with open(sys.argv[1], "r") as filename:
    screenplay = json.loads(filename.read())

with open(sys.argv[2], "r") as filename:
    timings = json.loads(filename.read())

print(screenplay)
print(timings)

# todo: finish