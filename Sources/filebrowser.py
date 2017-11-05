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

"""The `filebrowser` module provides classes and views for displaying a list of
spritefiles."""

from java.io import File
from java.lang import String
from java.util import List

from android.os import Environment
from android.util import TypedValue
from android.view import View, ViewGroup
from android.widget import AdapterView, LinearLayout, ListView, TextView

from serpentine.adapters import FileListAdapter

"""The following class defines an adapter that exposes names of files in a
directory with particular file suffixes."""

class SpriteFileListAdapter(FileListAdapter):

    @args(void, [File, List(String)])
    def __init__(self, directory, suffixes):
    
        FileListAdapter.__init__(self, directory, suffixes)
    
    def getView(self, position, convertView, parent):
    
        view = FileListAdapter.getView(self, position, convertView, parent)
        CAST(view, TextView).setTextSize(TypedValue.COMPLEX_UNIT_SP, float(20))
        return view
    
    """We define a method to obtain a new list of file names and report whether
    the list has changed."""
    
    @args(bool, [])
    def update(self):
    
        items = self.items
        self.items = []
        
        for suffix in self.suffixes:
            self.addFiles(suffix)
        
        for item1, item2 in zip(items, self.items):
            if item1 != item2:
                return True
        
        return False


"""We define an interface that other components can implement to handle a
callback when a file is selected by the user. The `handleFileOpen` method of
a registered component will be called with a `File` object that corresponds to
the file that the user selected."""

class FileOpenInterface:

    @args(void, [File])
    def handleFileOpen(self, file):
        pass


"""The following class provides a `View` that encapsulates the adapter that
exposes file information and the `ListView` that presents them to the user.
It allows registration of a handler that implements the `FileOpenInterface` and
will call the method defined in that interface for files that are selected
using a click. This mechanism is how file open requests are communicated to
the main activity.
"""

class FileBrowser(LinearLayout):

    __interfaces__ = [AdapterView.OnItemClickListener]
    __fields__ = {"handler": FileOpenInterface}
    
    def __init__(self, context):
    
        LinearLayout.__init__(self, context)
        
        self.handler = None
        
        envDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        self.fileAdapter = SpriteFileListAdapter(envDir, [".spr", ",ff9", ".ff9"])
        
        self.fileView = ListView(context)
        self.fileView.setOnItemClickListener(self)
        self.fileView.setAdapter(self.fileAdapter)
        
        self.addView(self.fileView, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT))
    
    """We provide a method that the activity can use to request a new list of
    file names, only refreshing the view if the list has changed."""
    
    def rescan(self):
    
        if self.fileAdapter.update():
            self.fileView.setAdapter(self.fileAdapter)
    
    """This method is called when the user clicks a file name in the
    `ListView`, responding by calling the appropriate method of the registered
    handler object."""
    
    @args(void, [AdapterView, View, int, long])
    def onItemClick(self, parent, view, position, id):
    
        file = self.fileAdapter.items[position]
        
        if self.handler != None:
            self.handler.handleFileOpen(file)
    
    """The following method handles registration of an object that implements
    the `FileOpenInterface` interface."""
    
    @args(void, [FileOpenInterface])
    def setHandler(self, handler):
    
        self.handler = handler
