from collections import defaultdict
import json
import sys

with open(sys.argv[1], "r") as filename:
    screenplay = json.loads(filename.read())

with open(sys.argv[2], "r") as filename:
    timings = json.loads(filename.read())

if screenplay["screenplay_id"] != timings["screenplay_id"]:
    print("Screenplay ID not the same for screenplay and timings files.")

# adjust timings and reprint screenplay
new_times = defaultdict(float)
for timing in timings["timings"]:
    scene_id = timing["scene_id"]
    time = timing["time"]
    new_times[scene_id] = time

for scene in screenplay["scenes"]:
    scene["duration"] = new_times[scene["identifier"]]

with open(sys.argv[3], "w") as filename:
    filename.write(json.dumps(screenplay, indent=4))
