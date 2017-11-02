# Copyright (C) 2017 David Boddie <david@boddie.org.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from java.io import BufferedOutputStream, File, FileOutputStream
from android.content import Intent
from android.graphics import Bitmap
from android.os import Environment
from android.net import Uri

from serpentine.activities import Activity
from serpentine.files import Files

from app_resources import R

from filebrowser import FileBrowser, FileOpenInterface
from spritebrowser import SpriteBrowser, SpriteViewInterface

class SpriteViewerActivity(Activity):

    __interfaces__ = [FileOpenInterface, SpriteViewInterface]
    
    def __init__(self):
    
        Activity.__init__(self)
        self.showing = "files"
    
    def onCreate(self, bundle):
    
        Activity.onCreate(self, bundle)
        
        self.resources = self.getResources()
        
        self.fileBrowser = FileBrowser(self)
        self.fileBrowser.setHandler(self)
        
        self.spriteBrowser = SpriteBrowser(self)
        self.spriteBrowser.setHandler(self)
        
        self.setContentView(self.fileBrowser)
    
    def onResume(self):
    
        Activity.onResume(self)
    
    def onPause(self):
    
        Activity.onPause(self)
    
    def onConfigurationChanged(self, config):
    
        Activity.onConfigurationChanged(self, config)
        #self.gamePage.updateLayout(config.screenWidthDp, config.screenHeightDp)
    
    def onBackPressed(self):
    
        # If showing the file browser then exit, otherwise show the file browser.
        if self.showing == "files":
            Activity.onBackPressed(self)
        else:
            self.showing = "files"
            self.setContentView(self.fileBrowser)
    
    def handleFileOpen(self, file):
    
        self.spriteBrowser.openFile(file)
        self.showing = "sprites"
        self.setContentView(self.spriteBrowser)
    
    def handleSpriteView(self, bitmap):
    
        file = Files.createExternalFile(Environment.DIRECTORY_DOWNLOADS,
            "SpriteViewer", "temp", "", ".png")
        
        stream = BufferedOutputStream(FileOutputStream(file))
        bitmap.compress(Bitmap.CompressFormat.PNG, 50, stream)
        stream.flush()
        # Closing the file with close() will cause an exception.
        
        intent = Intent()
        intent.setAction(Intent.ACTION_VIEW)
        intent.setDataAndType(Uri.parse("file://" + file.getPath()), "image/png")
        self.startActivity(intent)
