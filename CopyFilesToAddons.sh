#!/usr/bin/env bash

# To run this script from the command line: ./CopyFilesToAddons.sh
# Linux script. Run this after editing the addon's files. Then restart Anki. 
# Don't make edits over there in addons directly, as VCS won't see them, and as Anki or an addon upgrade might destroy them.
# (Like Anki's own deployment, this does NOT remove any files. The simplest way to do so manually here is to delete the addons folder, then re-run.)

mkdir -p ~/Anki/addons
cp -r -u -v flashgrid.py ~/Anki/addons/
