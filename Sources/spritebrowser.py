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
from java.util import Collections, LinkedList, List, Map, Queue

from android.graphics import Bitmap, Canvas, Color, Paint, \
                             PorterDuff, PorterDuffXfermode
from android.os import AsyncTask
from android.view import View, ViewGroup
from android.widget import AdapterView, BaseAdapter, ImageView, GridView, \
                           LinearLayout, TextView

from spritefile import Spritefile

"""We define an interface that classes can implement to indicate that they can
handle the action of viewing a sprite. The `handleSpriteView` method they
implement accepts the `Bitmap` representation of the sprite which can be
displayed or sent to a suitable component."""

class SpriteViewInterface:

    @args(void, [Bitmap])
    def handleSpriteView(self, bitmap):
        pass


"""We define a class to represent an entry in the cache that is used by the
`SpriteAdapter` class. It holds the name of a sprite and its bitmap
representation."""

class CacheEntry(Object):

    __fields__ = {"name": String, "bitmap": Bitmap}
    
    @args(void, [String, Bitmap])
    def __init__(self, name, bitmap):
    
        Object.__init__(self)
        self.name = name
        self.bitmap = bitmap


"""The following class exposes the contents of a spritefile to instances of
`AdapterView` subclasses, such as `ListView` or `GridView`. It defines a
constant preview size for the sprites that it represents, scaling each sprite
to fit within a square with sides of this length.

The class uses a cache with a constant maximum size to avoid having to render
sprites each time an item is requested by a view. Sprite rendering is performed
asynchronously using the `AsyncTask` class."""

class SpriteAdapter(BaseAdapter):

    __fields__ = {
        "spritefile": Spritefile,
        "items": List(String),
        "cache": Map(int, CacheEntry),
        "name_cache": Map(int, String),
        "positions": Queue(int)
        }
    
    preview_size = 128
    cache_size = 20
    
    @args(void, [])
    def __init__(self):
    
        BaseAdapter.__init__(self)
        
        self.spritefile = None
        self.items = []
        
        self.cache = {}
        self.positions = []
    
    @args(int, [])
    def getCount(self):
        return len(self.items)
    
    @args(Object, [int])
    def getItem(self, position):
        return None
    
    @args(long, [int])
    def getItemId(self, position):
        return long(0)
    
    """We implement the `getView` method to provide a `LinearLayout` view for
    each item, containing an `ImageView` and a `TextView`. For sprites in the
    cache, we obtain a `Bitmap` and include it in the layout. Sprites that
    need to be rendered are represented by a placeholder `Bitmap` and a
    background task is started to render the sprite. When rendering is
    complete, the `SpriteRenderer` object that performs the task will update
    the `ImageView` with a new `Bitmap`."""
    
    @args(View, [int, View, ViewGroup])
    def getView(self, position, convertView, parent):
    
        context = parent.getContext()
        
        layout = LinearLayout(context)
        layout.setOrientation(LinearLayout.VERTICAL)
        
        imageView = ImageView(context)
        
        if self.cache.containsKey(position):
            entry = self.cache[position]
            name = entry.name
            bitmap = entry.bitmap
            imageView.setImageBitmap(bitmap)
            
            if len(self.positions) > self.cache_size:
                self.cache.remove(self.positions.remove())
        
        else:
            name = self.items[position]
            renderer = SpriteRenderer(self.spritefile, name, imageView,
                                      self.cache, self.positions)
            
            # Create a placeholder bitmap to put into the view.
            bitmap = renderer.emptyBitmap(self.preview_size, self.preview_size,
                                          False)
            imageView.setImageBitmap(bitmap)
            
            # Create a list then convert it to an array. The initial list
            # creation causes the items to be wrapped in Integer objects.
            renderer.execute(array([self.preview_size, self.preview_size,
                                    position]))
        
        textView = TextView(context)
        textView.setText(name)
        textView.setGravity(0x01) # center_horizontal
        
        layout.addView(imageView)
        layout.addView(textView)
        
        return layout
    
    """This method is used to tell the adapter which file to examine. We create
    a `Spritefile` object for the given file and read the names of the sprites
    it contains. We also clear the structures used to hold cache information."""
    
    @args(void, [File])
    def setFile(self, file):
    
        try:
            self.spritefile = Spritefile(file)
            self.items = LinkedList(self.spritefile.sprites.keySet())
            Collections.sort(self.items)
        except:
            self.items = []
        
        self.cache = {}
        self.positions = []
    
    """This method is used to obtain a `Bitmap` for a sprite at a given
    position in the list of items held by the adapter."""
    
    @args(Bitmap, [int])
    def getSpriteBitmap(self, position):
    
        name = self.items[position]
        return SpriteRenderer.getSpriteBitmap(self.spritefile, name)


"""The following class is used to render each sprite asynchronously in a
background thread.
"""

class SpriteRenderer(AsyncTask):

    __item_types__ = [int, Bitmap, Bitmap]
    
    """The `__init__` method accepts the sprite to render, the `ImageView` used
    to display the resulting bitmap, a `Map` that contains cached bitmaps for
    sprites already rendered, and a queue of keys for bitmaps in the cache."""
    
    @args(void, [Spritefile, String, ImageView, Map(int, CacheEntry), Queue(int)])
    def __init__(self, spritefile, name, imageView, cache, queue):
    
        AsyncTask.__init__(self)
        
        self.spritefile = spritefile
        self.name = name
        self.imageView = imageView
        self.cache = cache
        self.queue = queue
        
        self.paint = Paint()
        self.paint.setXfermode(PorterDuffXfermode(PorterDuff.Mode.SRC_OVER))
    
    """We define a method to conveniently create new empty bitmaps."""
    
    @args(Bitmap, [int, int, bool])
    def emptyBitmap(self, width, height, ready):
    
        bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        canvas = Canvas(bitmap)
        paint = Paint()
        paint.setXfermode(PorterDuffXfermode(PorterDuff.Mode.SRC))
        
        if ready:
            b1 = Color.argb(255, 96, 96, 96)
            b2 = Color.argb(255, 128, 128, 128)
        else:
            b1 = Color.argb(255, 32, 32, 32)
            b2 = Color.argb(255, 64, 64, 64)
        
        i = 0
        for y in range(0, height, 16):
        
            j = 1 - i
            
            for x in range(0, width, 16):
                if j == 0:
                    paint.setColor(b1)
                else:
                    paint.setColor(b2)
                
                canvas.drawRect(x, y, x + 16, y + 16, paint)
                j = 1 - j
            
            i = 1 - i
        
        return bitmap
    
    """We define a method to obtain a sprite from the spritefile. This is
    potentially a slow operation, which is why it is called by the
    `doInBackground` method below."""
    
    @args(Bitmap, [])
    def getSpriteBitmap(self):
    
        return self.getSpriteBitmap(self.spritefile, self.name)
    
    @static
    @args(Bitmap, [Spritefile, String])
    def getSpriteBitmap(spritefile, name):
    
        sprite = spritefile.getSprite(name)
        
        bitmap = Bitmap.createBitmap(sprite.width, sprite.height, Bitmap.Config.ARGB_8888)
        bitmap.copyPixelsFromBuffer(ByteBuffer.wrap(sprite.rgba))
        
        if sprite.ydpi < sprite.xdpi:
            yscale = sprite.xdpi/sprite.ydpi
            bitmap = Bitmap.createScaledBitmap(bitmap, bitmap.getWidth(),
                bitmap.getHeight() * yscale, False)
        
        return bitmap
    
    """The following method performs work in a background thread. It accepts
    an array of the `Params` type, which we defined above as `int`, so it will
    receive an array of integers which describe the width and height of each
    bitmap to create, as well as the position of the bitmap in the adapter that
    uses the `SpriteRenderer`. The position is used as a key into the `Map` we
    use as a cache."""
    
    @args(Result, [[Params]])
    def doInBackground(self, params):
    
        w, h, self.position = params
        
        bitmap = self.getSpriteBitmap()
        
        width = bitmap.getWidth()
        height = bitmap.getHeight()
        
        xscale = w/float(width)
        yscale = h/float(height)
        scale = Math.min(xscale, yscale)
        
        if 0 < scale < 1:
            sw = Math.max(1, scale * width)
            sh = Math.max(1, scale * height)
            
            bitmap = Bitmap.createScaledBitmap(bitmap, sw, sh, True)
        
        elif scale >= 2:
            s = Math.min(int(Math.floor(scale)), 3)
            sw = Math.max(1, s * width)
            sh = Math.max(1, s * height)
            bitmap = Bitmap.createScaledBitmap(bitmap, sw, sh, False)
        
        preview = self.emptyBitmap(w, h, True)
        
        canvas = Canvas(preview)
        canvas.drawBitmap(bitmap, (w - bitmap.getWidth())/2,
            (h - bitmap.getHeight())/2, self.paint)
        
        return preview
    
    """As each sprite is drawn it is possible to report progress to the
    adapter that started this task. In this application we don't take
    advantage of this feature so the following method does nothing."""
    
    @args(void, [[Progress]])
    def onProgressUpdate(self, progress):
    
        pass
    
    """When all processing has finished, the following method is called by the
    application framework to allow the final result to be handled in the main
    UI thread. We update the bitmap cache with the new bitmap and add its
    position to the queue of keys to the cache. Then we update the `ImageView`
    to show the finished bitmap."""
    
    @args(void, [Result])
    def onPostExecute(self, result):
    
        self.cache[self.position] = CacheEntry(self.name, result)
        self.queue.add(self.position)
        self.imageView.setImageBitmap(result)


"""The following class provides a `View` that encapsulates both the adapter
that supplies rendered sprites and a grid in which to display them. It allows
registration of a handler that implements the `SpriteViewInterface` and will
call the method defined in that interface for sprites that are selected using
a long click. This mechanism is how sprite view requests are communicated to
the main activity."""

class SpriteBrowser(LinearLayout):

    __interfaces__ = [AdapterView.OnItemLongClickListener]
    __fields__ = {"handler": SpriteViewInterface}
    
    def __init__(self, context):
    
        LinearLayout.__init__(self, context)
        
        self.handler = None
        
        self.spriteAdapter = SpriteAdapter()
        
        self.grid = GridView(context)
        self.grid.setHorizontalSpacing(8)
        self.grid.setVerticalSpacing(8)
        self.grid.setNumColumns(3)
        self.grid.setAdapter(self.spriteAdapter)
        self.grid.setOnItemLongClickListener(self)
        self.addView(self.grid)
    
    """This method ensures that the view displays a reasonable number of
    columns in the grid when it is first shown."""
    
    def onSizeChanged(self, width, height, oldWidth, oldHeight):
    
        self.grid.setNumColumns(width/SpriteAdapter.preview_size)
    
    """This method is used to help the view adapt to configuration changes
    due to reorientation of the device running the application. It simply
    uses the size of the screen to determine how many columns can be shown."""
    
    @args(void, [int])
    def updateLayout(self, screenWidthDp):
    
        self.grid.setNumColumns(screenWidthDp/SpriteAdapter.preview_size)
    
    """In this method we acknowledge a long click on a sprite in the grid,
    obtain a `Bitmap` for the sprite and call the appropriate method of the
    registered handler object."""
    
    @args(bool, [AdapterView, View, int, long])
    def onItemLongClick(self, parent, view, position, id):
    
        bitmap = self.spriteAdapter.getSpriteBitmap(position)
        
        if self.handler != None:
            self.handler.handleSpriteView(bitmap)
        
        return True
    
    @args(void, [SpriteViewInterface])
    def setHandler(self, handler):
    
        self.handler = handler
    
    """The main activity calls this method to tell the browser to display the
    contents of the given file. We simply update the adapter to use the new
    file and refresh the grid by passing the adapter to it."""
    
    @args(void, [File])
    def openFile(self, file):
    
        self.spriteAdapter.setFile(file)
        self.grid.setAdapter(self.spriteAdapter)
