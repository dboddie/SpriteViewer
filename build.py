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
from Tools.makeandroidmanifest import *

# See docs/guide/topics/resources/runtime-changes.html
# android.content.pm.ActivityInfo
CONFIG_ORIENTATION = 0x0080
CONFIG_SCREEN_SIZE = 0x0400

app_name = "Sprite Viewer"
package_name = "uk.org.boddie.spriteviewer"

# The manifest is defined as a sequence of elements that will be passed as the
# description to the build helper instead of a dictionary with attributes for
# the Activity element.

activity_manifest = [
    Manifest({"package": package_name}, [
        # Features and permissions must be inserted here.
        Application({"android:icon": "@drawable/ic_launcher"}, [
            Activity({
                "android:name": "SpriteViewerActivity",
                "android:configChanges": CONFIG_ORIENTATION | CONFIG_SCREEN_SIZE
                }, [
                # Define subelements that describe intent filters.
                # The first one allows the application to be launched.
                IntentFilter({}, [
                    Action({"android:name": "android.intent.action.MAIN"}),
                    Category({"android:name": "android.intent.category.LAUNCHER"})
                    ]),
                # The second one specifies that the application can be used to
                # view files with certain patterns.
                IntentFilter({}, [
                    Data({"android:scheme": "file",
                          "android:mimeType": "*/*",
                          "android:pathPattern": r".*\.spr",
                          "android:host": "*"}),
                    Data({"android:scheme": "file",
                          "android:mimeType": "*/*",
                          "android:pathPattern": r".*\.ff9",
                          "android:host": "*"}),
                    Data({"android:scheme": "file",
                          "android:mimeType": "*/*",
                          "android:pathPattern": r".*,ff9",
                          "android:host": "*"}),
                    Action({"android:name": "android.intent.action.VIEW"}),
                    Category({"android:name": "android.intent.category.DEFAULT"}),
                    ])
                ])
            ])
        ])
    ]

res_files = {
    "drawable": {"ic_launcher": "Resources/icon.svg"}
    }
code_file = "Sources/spriteviewer.py"
include_paths = []
layout = None
features = []
this_dir = os.path.split(os.path.abspath(__file__))[0]
docs_dir = os.path.join(this_dir, "Docs")

# We need to allow external storage to be read just to be generally useful,
# but also need write access so that we can write temporary PNG files for other
# applications to display.
permissions = ["android.permission.READ_EXTERNAL_STORAGE",
               "android.permission.WRITE_EXTERNAL_STORAGE"]

# Define a page header for the documentation.
page_header = "<h1>Sprite Viewer</h1>\n\n"

if __name__ == "__main__":

    args = sys.argv[:]
    
    # Use the custom application template so that we can use the manifest we
    # defined above.
    result = buildhelper.main(__file__, app_name, package_name, res_files,
        layout, code_file, include_paths, features, permissions, args,
        app_template = "custom", description = activity_manifest,
        include_sources = False, docs_dir = docs_dir,
        doc_options = {"page header": page_header})
    
    sys.exit(result)
