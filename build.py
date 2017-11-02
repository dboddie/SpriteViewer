#!/usr/bin/env python

"""
Copyright (C) 2017 David Boddie <david@boddie.org.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json, os, sys

from Tools import buildhelper

# See docs/guide/topics/resources/runtime-changes.html
# android.content.pm.ActivityInfo
CONFIG_ORIENTATION = 0x0080
CONFIG_SCREEN_SIZE = 0x0400

app_name = "Sprite Viewer"
activity_dict = {
    "android:configChanges": CONFIG_ORIENTATION | CONFIG_SCREEN_SIZE
    }
package_name = "uk.org.boddie.spriteviewer"
res_files = {
    "drawable": {"ic_launcher": "Resources/icon.svg"},
    #"raw": {"sample": "Resources/sample.jef"}
    }
code_file = "Sources/spriteviewer.py"
include_paths = []
layout = None
features = []
permissions = ["android.permission.READ_EXTERNAL_STORAGE",
               "android.permission.WRITE_EXTERNAL_STORAGE"]

if __name__ == "__main__":

    args = sys.argv[:]
    
    result = buildhelper.main(__file__, app_name, package_name, res_files,
        layout, code_file, include_paths, features, permissions, args,
        description = activity_dict, include_sources = False)
    
    sys.exit(result)
