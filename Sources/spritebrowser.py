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
from java.lang import Byte, Math, Object, String
from java.nio import ByteBuffer
from java.util import LinkedList, List

from android.graphics import Bitmap, Canvas, Color, Paint, \
                             PorterDuff, PorterDuffXfermode
from android.view import View, ViewGroup
from android.widget import AdapterView, BaseAdapter, ImageView, GridView, \
                           LinearLayout, TextView

from serpentine.adapters import FileListAdapter

from spritefile import Spritefile

class SpriteViewInterface:

    @args(void, [Bitmap])
    def handleSpriteView(self, bitmap):
        pass


class SpriteAdapter(BaseAdapter):

    __fields__ = {
        "spritefile": Spritefile,
        "items": List(String)
        }
    
    @args(void, [])
    def __init__(self):
    
        BaseAdapter.__init__(self)
        
        self.spritefile = None
        self.items = []
        self.size = 128
        self.paint = Paint()
        self.paint.setXfermode(PorterDuffXfermode(PorterDuff.Mode.SRC_OVER))
    
    @args(int, [])
    def getCount(self):
        return len(self.items)
    
    @args(Object, [int])
    def getItem(self, position):
        return None
    
    @args(long, [int])
    def getItemId(self, position):
        return long(0)
    
    @args(View, [int, View, ViewGroup])
    def getView(self, position, convertView, parent):
    
        context = parent.getContext()
        
        layout = LinearLayout(context)
        layout.setOrientation(LinearLayout.VERTICAL)
        
        imageView = ImageView(context)
        
        name = self.items[position]
        #renderer = PatternRenderer(f, self.colourInfo, imageView,
        #                           self.cache, self.positions)
        bitmap = self.getSpriteBitmap(position)
        width = bitmap.getWidth()
        height = bitmap.getHeight()
        
        xscale = self.size/float(width)
        yscale = self.size/float(height)
        scale = Math.min(xscale, yscale)
        
        if 0 < scale < 1:
            sw = Math.max(1, scale * width)
            sh = Math.max(1, scale * height)
            
            bitmap = Bitmap.createScaledBitmap(bitmap, sw, sh, True)
        
        elif scale >= 2:
            s = Math.min(int(Math.floor(scale)), 4)
            sw = Math.max(1, s * width)
            sh = Math.max(1, s * height)
            bitmap = Bitmap.createScaledBitmap(bitmap, sw, sh, False)
        
        preview = self.emptyBitmap(self.size, self.size)
        
        canvas = Canvas(preview)
        canvas.drawBitmap(bitmap, (self.size - bitmap.getWidth())/2,
            (self.size - bitmap.getHeight())/2, self.paint)
        
        imageView.setImageBitmap(preview)
        # Create a list then convert it to an array. The initial list
        # creation causes the items to be wrapped in Integer objects.
        #renderer.execute(array([self.size, self.size, position]))
        
        textView = TextView(context)
        textView.setText(name)
        textView.setGravity(0x01) # center_horizontal
        
        layout.addView(imageView)
        layout.addView(textView)
        
        return layout
    
    @args(void, [File])
    def setFile(self, file):
    
        self.spritefile = Spritefile(file)
        self.items = LinkedList(self.spritefile.sprites.keySet())
    
    @args(Bitmap, [int, int])
    def emptyBitmap(self, width, height):
    
        bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        canvas = Canvas(bitmap)
        paint = Paint()
        paint.setXfermode(PorterDuffXfermode(PorterDuff.Mode.SRC))
        
        i = 0
        for y in range(0, self.size, 16):
        
            j = 1 - i
            
            for x in range(0, self.size, 16):
                if j == 0:
                    paint.setARGB(255, 64, 64, 64)
                else:
                    paint.setARGB(255, 96, 96, 96)
                
                canvas.drawRect(x, y, x + 16, y + 16, paint)
                j = 1 - j
            
            i = 1 - i
        
        return bitmap
    
    @args(Bitmap, [int])
    def getSpriteBitmap(self, position):
    
        name = self.items[position]
        sprite = self.spritefile.sprites[name]
        bitmap = Bitmap.createBitmap(sprite.width, sprite.height, Bitmap.Config.ARGB_8888)
        bitmap.copyPixelsFromBuffer(ByteBuffer.wrap(sprite.rgba))
        
        if sprite.ydpi < sprite.xdpi:
            yscale = sprite.xdpi/sprite.ydpi
            bitmap = Bitmap.createScaledBitmap(bitmap, bitmap.getWidth(),
                bitmap.getHeight() * yscale, False)
        
        return bitmap


class SpriteBrowser(LinearLayout):

    __interfaces__ = [AdapterView.OnItemClickListener]
    __fields__ = {"handler": SpriteViewInterface}
    
    def __init__(self, context):
    
        LinearLayout.__init__(self, context)
        
        self.handler = None
        
        self.spriteAdapter = SpriteAdapter()
        
        self.grid = GridView(context)
        self.grid.setHorizontalSpacing(8)
        self.grid.setVerticalSpacing(8)
        self.grid.setNumColumns(2)
        self.grid.setAdapter(self.spriteAdapter)
        self.grid.setOnItemClickListener(self)
        self.addView(self.grid)
    
    @args(void, [AdapterView, View, int, long])
    def onItemClick(self, parent, view, position, id):
    
        bitmap = self.spriteAdapter.getSpriteBitmap(position)
        self.handler.handleSpriteView(bitmap)
    
    @args(void, [SpriteViewInterface])
    def setHandler(self, handler):
    
        self.handler = handler
    
    @args(void, [File])
    def openFile(self, file):
    
        self.spriteAdapter.setFile(file)
        self.grid.setAdapter(self.spriteAdapter)
