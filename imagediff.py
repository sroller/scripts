#!/usr/bin/python

from SimpleCV import *
import glob

MIN_BLOB_SIZE = 10000

with open("diff.html", "w") as html:
    html.write("<!DOCTYPE html>\n<head>\n<title>Differences</title>\n<body>\n")
old_image = Image("tl000000.jpg")
for jpg in sorted(glob.glob("tl*.jpg")):
    new_image = Image(jpg)
    diff = new_image - old_image
    blobs = diff.findBlobs(minsize=MIN_BLOB_SIZE)
    if blobs:
        print(blobs, jpg)
        diff_name = "%s-diff.jpg" % jpg
        diff.save(diff_name)
        with open("diff.html", "a") as html:
                html.write('<a href="%s">%s</a><br />' % (diff_name, jpg))
    old_image = new_image



