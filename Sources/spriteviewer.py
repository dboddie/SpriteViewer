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

"""The `spriteviewer` module provides the main activity class for the Sprite
Viewer application."""

from java.lang import String
from java.io import BufferedOutputStream, File, FileOutputStream

from android.content import Intent
from android.graphics import Bitmap
from android.os import Environment
from android.net import Uri
from android.view import Menu
from android.widget import AdapterView, Toast

from serpentine.activities import Activity
from serpentine.files import Files

from filebrowser import FileBrowser, FileOpenInterface
from spritebrowser import SpriteBrowser

"""The `SpriteViewerActivity` class represents the application and defines the
high level parts of the user interface using classes from the
[filebrowser](filebrowser.html) and [spritebrowser](spritebrowser.html) modules.
It also implements an interface defined in the [filebrowser](filebrowser.html)
module."""

class SpriteViewerActivity(Activity):

    __interfaces__ = [FileOpenInterface]
    
    __fields__ = {"temp_file": File}
    
    def __init__(self):
    
        Activity.__init__(self)
        self.showing = "files"
        self.temp_file = None
    
    """We reimplement the `onCreate` method to provide a user interface for the
    application and to record how the application was started. If it was
    launched normally, it will show a file browser. If it was run as the result
    of opening a spritefile in a file manager application, it will show the
    sprites contained in that spritefile."""
    
    def onCreate(self, bundle):
    
        Activity.onCreate(self, bundle)
        
        self.resources = self.getResources()
        
        self.fileBrowser = FileBrowser(self)
        self.fileBrowser.setHandler(self)
        
        self.spriteBrowser = SpriteBrowser(self)
        self.registerForContextMenu(self.spriteBrowser.getGrid())
        
        self.setContentView(self.fileBrowser)
        
        # Obtain the intent that caused the activity to be started and define
        # the initial view to be displayed.
        intent = self.getIntent()
        
        self.initial_view = "files"
        
        # If the application was started with an intent requesting a view
        # action then we show the sprite browser instead of the file browser.
        if intent.getAction() == Intent.ACTION_VIEW:
        
            uri = intent.getData()
            
            if uri.getScheme() == "file":
                self.initial_view = "sprites"
                self.handleFileOpen(File(uri.getPath()))
    
    def onResume(self):
    
        Activity.onResume(self)
    
    def onPause(self):
    
        Activity.onPause(self)
    
    """The reimplementation of the `onStop` method checks for the presence of
    a temporary file and deletes it."""
    
    def onStop(self):
    
        Activity.onStop(self)
        
        if self.temp_file != None:
            self.temp_file.delete()
    
    """The following method is used to respond to configuration changes, such
    as those caused by an orientation change, calling a custom method in the
    sprite browser view."""
    
    def onConfigurationChanged(self, config):
    
        Activity.onConfigurationChanged(self, config)
        self.spriteBrowser.updateLayout(config.screenWidthDp)
    
    """We reimplement the `onBackPressed` method to change the usual behaviour
    of the interface. If the view being displayed is the same as the one shown
    when the application started then the standard behaviour is used. Otherwise
    we show the file browser."""
    
    def onBackPressed(self):
    
        # If showing the initial view then exit, otherwise show the file browser.
        if self.showing == self.initial_view:
            Activity.onBackPressed(self)
        else:
            self.showing = "files"
            self.fileBrowser.rescan()
            self.setContentView(self.fileBrowser)
    
    """The following method is used to handle file open requests from the
    file browser, responding to them by changing the current view and opening
    the selected file in the sprite browser."""
    
    def handleFileOpen(self, file):
    
        self.spriteBrowser.openFile(file)
        self.showing = "sprites"
        self.setContentView(self.spriteBrowser)
    
    """We support the creation of a context menu with the following method
    which defines two menu items, storing them for later checks when a menu
    item is selected by the user."""
    
    def onCreateContextMenu(self, menu, view, menuInfo):
    
        self.viewItem = menu.add(Menu.NONE, 1, Menu.NONE, "Show full size")
        self.saveItem = menu.add(Menu.NONE, 2, Menu.NONE, "Save as PNG")
    
    """When a menu item is selected, we check it against the two defined items
    and either show the current sprite in an external application or save it to
    a file, depending on which item was selected."""
    
    def onContextItemSelected(self, item):
    
        menuInfo = CAST(item.getMenuInfo(), AdapterView.AdapterContextMenuInfo)
        position = menuInfo.position
        
        if item.getItemId() == self.viewItem.getItemId():
            self.viewSprite(self.spriteBrowser.getSpriteBitmap(position))
            return True
        
        elif item.getItemId() == self.saveItem.getItemId():
            self.saveSprite(self.spriteBrowser.getSpriteFileName(),
                            self.spriteBrowser.getSpriteName(position),
                            self.spriteBrowser.getSpriteBitmap(position))
            return True
        
        return False
    
    """The following method is used to handle sprite view requests. It saves
    the `Bitmap` passed to the method to a PNG file in the device's external
    storage. Finally, it broadcasts an intent to request that the newly saved
    file be displayed by a suitable application."""
    
    @args(void, [Bitmap])
    def viewSprite(self, bitmap):
    
        self.temp_file = Files.createExternalFile(Environment.DIRECTORY_DOWNLOADS,
            "SpriteViewer", ".temp", "", ".png")
        
        stream = BufferedOutputStream(FileOutputStream(self.temp_file))
        bitmap.compress(Bitmap.CompressFormat.PNG, 50, stream)
        stream.flush()
        # Closing the file with close() will cause an exception.
        
        intent = Intent()
        intent.setAction(Intent.ACTION_VIEW)
        intent.setDataAndType(Uri.parse("file://" + self.temp_file.getPath()), "image/png")
        self.startActivity(intent)
    
    """This method saves a PNG file to a subdirectory of the `SpriteViewer`
    directory in the device's external storage. It shows a transient message
    to indicate that it has saved a file."""
    
    @args(void, [String, String, Bitmap])
    def saveSprite(self, spritefileName, spriteName, bitmap):
    
        # Create a subdirectory of the SpriteViewer directory for the current
        # set of sprites.
        subDir = File(Environment.DIRECTORY_DOWNLOADS, "SpriteViewer")
        
        outputFile = Files.createExternalFile(subDir.getPath(),
            spritefileName, spriteName, "", ".png")
        
        stream = BufferedOutputStream(FileOutputStream(outputFile))
        bitmap.compress(Bitmap.CompressFormat.PNG, 50, stream)
        stream.flush()
        
        Toast.makeText(self, "Saved " + outputFile.getPath(), Toast.LENGTH_LONG).show()
