#!/usr/bin/python
# -*- coding: utf-8 -*-

# Load an iPod database, then go through each MP3. If the MP3 has cover art
# on the iPod, skip it. If not, check for an embedded image in the ID3 tag
# data, and if one is found, save it as the iPod cover art. Then, write the
# iPod database and close it.
# Requires python-eyeD3, python-gpod
# Adam Greig, Jun 2009
# Unlimited personal use and modification permitted.
# All other rights reserved.
# iPod is a registered trademark of Apple Inc.

import optparse
import eyeD3
import gpod

usage = "usage: %prog <mounted_ipod_directory>"
parser = optparse.OptionParser(usage)
(options, args) = parser.parse_args()

if len(args) != 1:
    parser.error("You must supply a path to a mounted iPod.")
else:
    ipod = args[0]

try:
    db = gpod.Database(ipod)
except gpod.ipod.DatabaseException:
    parser.error("Invalid iPod path or error loading the iPod.")

print "iPod database loaded, checking songs..."
x = -1
for track in db:
    x += 1
    print "Processing " + track['artist'] + " - " + track['title'] + '...',
    if track.get_coverart():
        print "Cover art already found, skipping."
        continue
    else:
        tag = eyeD3.Tag()
        if not tag.link(track.ipod_filename()):
            print "Error reading ID3 data, skipping."
            continue
        if len(tag.getImages()) == 0:
            print "No embedded cover art found, skipping."
            continue
        image = tag.getImages()[0]
        image.writeFile('/tmp', name=str(x)+'.jpg')
        try:
            track.set_coverart_from_file('/tmp/'+str(x)+'.jpg')
            db.copy_delayed_files()
        except TypeError:
            pass    # This seems to happen and seems to be harmless.
        print 'Done.'

print "All songs processed, saving database..."
db.close()

print "All done."
