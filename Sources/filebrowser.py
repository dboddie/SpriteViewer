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

from java.io import File
from java.lang import String
from java.util import List

from android.os import Environment
from android.util import TypedValue
from android.view import View, ViewGroup
from android.widget import AdapterView, LinearLayout, ListView, TextView

from serpentine.adapters import FileListAdapter

class SpriteFileListAdapter(FileListAdapter):

    @args(void, [File, List(String)])
    def __init__(self, directory, suffixes):
    
        FileListAdapter.__init__(self, directory, suffixes)
    
    def getView(self, position, convertView, parent):
    
        view = FileListAdapter.getView(self, position, convertView, parent)
        CAST(view, TextView).setTextSize(TypedValue.COMPLEX_UNIT_SP, float(20))
        return view


class FileOpenInterface:

    @args(void, [File])
    def handleFileOpen(self, file):
        pass


class FileBrowser(LinearLayout):

    __interfaces__ = [AdapterView.OnItemClickListener]
    __fields__ = {"handler": FileOpenInterface}
    
    def __init__(self, context):
    
        LinearLayout.__init__(self, context)
        
        self.handler = None
        
        envDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        self.fileAdapter = SpriteFileListAdapter(envDir, [".spr", ",ff9", ".ff9"])
        
        self.fileView = ListView(context)
        self.fileView.setAdapter(self.fileAdapter)
        self.fileView.setOnItemClickListener(self)
        self.addView(self.fileView, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT))
    
    @args(void, [AdapterView, View, int, long])
    def onItemClick(self, parent, view, position, id):
    
        file = self.fileAdapter.items[position]
        self.handler.handleFileOpen(file)
    
    @args(void, [FileOpenInterface])
    def setHandler(self, handler):
    
        self.handler = handler
