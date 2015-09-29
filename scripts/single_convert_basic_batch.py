import os

widths = [30, 40, 50, 60, 70]
heights = [5, 7, 9, 11, 13, 15]

os.system("export PYTHONPATH=/usr/local/lib/python3.4/site-packages:$PYTHONPATH")

for w in widths:
    for h in heights:
        os.system("python3 single_convert_basic.py " +
                  "\"/Users/beth/Google Drive/openmind/articles/return-of-seti/return-of-seti.txt\" " +
                  "\\\"Return\ of\ Seti\\\" " +
                  "\"/Users/beth/Google Drive/openmind/articles/return-of-seti/return-of-seti-%d-%d.json\" " % (w, h) +
                  "\"/Users/beth/Google Drive/openmind/articles/return-of-seti/return-of-seti-%d-%d-features.json\" " % (w, h) +
                  "%d %d" % (h, w))
