#!/usr/bin/env bash

# To run this script from the command line: ./CopyFilesToAddons.sh
# Linux script. Run this after editing the addon's files. Then restart Anki. 
# Don't make edits over there in addons directly, as VCS won't see them, and as Anki or an addon upgrade might destroy them.

mkdir -p ~/Anki/addons
cp -r -u -v flashgrid.py ~/Anki/addons/
