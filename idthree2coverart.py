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
import os
import tempfile

usage = "usage: %prog [-f] <mounted_ipod_directory>"
parser = optparse.OptionParser(usage)
parser.add_option('-f', '--force', action='store_true', dest='force',
                    help='Ignore existing iPod artwork, resetting all from ID3')
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

tempdir = tempfile.mkdtemp()
files = []

x = -1
for track in db:
    x += 1
    
    print "Processing " + track['artist'] + " - " + track['title'],
    print '(' + str(x+1) + ' of ' + str(len(db)) + ')...',
    
    if track.get_coverart() and not options.force:
        print "Cover art already found and -f not specified, skipping."
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
        image.writeFile(tempdir, name=str(x) + '.jpg')
        filename = "%s/%s.jpg" % (tempdir, str(x))
        files.append(filename)
        track['userdata']['charset'] = 'UTF-8'
        track.set_coverart_from_file(filename)
        db.copy_delayed_files()
        print 'Done.'

print "All songs processed, saving database..."
db.close()

print "Tidying up..."
for f in files:
    os.remove(f)
os.rmdir(tempdir)
print "All done."
