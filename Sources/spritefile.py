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

from java.io import DataInputStream, File, FileInputStream, InputStream, \
                    IOException, RandomAccessFile
from java.lang import Byte, Exception, Object, String
from java.nio import ByteBuffer, ByteOrder
from java.util import List, Map

class SpritefileError(Exception):

    def __init__(self):
        Exception.__init__(self)
    
    @args(void, [String])
    def __init__(self, details):
        Exception.__init__(self, details)


class Sprite(Object):

    __fields__ = {
        "name": String,
        "h_words": int, "v_lines": int,
        "first_bit": int, "last_bit": int,
        "bpp": int, "log2bpp": int,
        "xdpi": int, "ydpi": int,
        "width": int, "height": int,
        "mode": String,
        "palette": Palette,
        "rgba": [byte]
        }
    
    def __init__(self):
    
        Object.__init__(self)


class Palette(Object):

    __fields__ = {
        "entries": List(PaletteEntry)
        }
    
    def __init__(self):
    
        Object.__init__(self)
        self.entries = []
    
    @args(void, [PaletteEntry])
    def add(self, entry):
        self.entries.add(entry)
    
    @args(PaletteEntry, [int])
    def getEntry(self, index):
        return self.entries[index]
    
    @args(bool, [])
    def hasEntries(self):
        return len(self.entries) != 0
    
    @args(int, [])
    def size(self):
        return len(self.entries)


class PaletteEntry(Object):

    __fields__ = {
        "primary": List(int),
        "secondary": List(int)
        }
    
    @args(void, [List(int), List(int)])
    def __init__(self, primary, secondary):
    
        Object.__init__(self)
        self.primary = primary
        self.secondary = secondary


class Spritefile(Object):

    __fields__ = {
        "file": File,
        "sprites": Map(String, Sprite)
        }
    
    @args(void, [])
    def __init__(self):
    
        Object.__init__(self)
        
        self.file = None
        self.init()
    
    @args(void, [File])
    def __init__(self, file):
    
        Object.__init__(self)
        
        self.file = file
        self.init()
        self.read(file)
    
    def init(self):
    
        # Define scaling factors for 8 bits per pixel and 16 bits per pixel colour.
        self.scale8  = 255.0/15.0
        self.scale16 = 255.0/31.0
        
        # Constants
        self.HEADER = 60
        
        # Mode information dictionary (log2bpp, x scale, y scale)
        self.mode_info = {
                    0: (0, 1, 2), 1: (1, 2, 2), 2: (2, 3, 2), 3: (1, 1, 2),
                    4: (0, 2, 2), 5: (1, 3, 2), 6: (1, 2, 2), 7: (2, 2, 2),
                    8: (1, 1, 2), 9: (2, 2, 2), 10: (3, 3, 2), 11: (1, 1, 2),
                    12: (2, 1, 2), 13: (3, 2, 2), 14: (2, 1, 2), 15: (3, 1, 2),
                    16: (2, 1, 2), 17: (2, 1, 2), 18: (0, 1, 1), 19: (1, 1, 1),
                    20: (2, 1, 1), 21: (3, 1, 1), 22: (2, 0, 1), 23: (0, 1, 1),
                    24: (3, 1, 2), 25: (0, 1, 1), 26: (1, 1, 1), 27: (2, 1, 1),
                    28: (3, 1, 1), 29: (0, 1, 1), 30: (1, 1, 1), 31: (2, 1, 1),
                    32: (3, 1, 1), 33: (0, 1, 2), 34: (1, 1, 2), 35: (2, 1, 2),
                    36: (3, 1, 2), 37: (0, 1, 2), 38: (1, 1, 2), 39: (2, 1, 2),
                    40: (3, 1, 2), 41: (0, 1, 2), 42: (1, 1, 2), 43: (2, 1, 2),
                    44: (0, 1, 2), 45: (1, 1, 2), 46: (2, 1, 2), 47: (3, 2, 2),
                    48: (2, 2, 1), 49: (3, 2, 1)
                }
        
        self.palette16 = [
                    (0xff, 0xff, 0xff), (0xdd, 0xdd, 0xdd),
                    (0xbb, 0xbb, 0xbb), (0x99, 0x99, 0x99),
                    (0x77, 0x77, 0x77), (0x55, 0x55, 0x55),
                    (0x33, 0x33, 0x33), (0x00, 0x00, 0x00),
                    (0x00, 0x44, 0x99), (0xee, 0xee, 0x00),
                    (0x00, 0xcc, 0x00), (0xdd, 0x00, 0x00),
                    (0xee, 0xee, 0xbb), (0x55, 0x88, 0x00),
                    (0xff, 0xbb, 0x00), (0x00, 0xbb, 0xff)
                ]
        
        self.palette4 = [
                    (0xff, 0xff, 0xff), (0xbb, 0xbb, 0xbb),
                    (0x77, 0x77, 0x77), (0x00, 0x00, 0x00)
                ]
    
    def new(self):
    
        self.sprites = {}
    
    @args(int, [int, RandomAccessFile])
    def str2num(self, size, f):
    
        i = 0
        n = 0
        
        buf = ByteBuffer.allocate(4)
        buf.order(ByteOrder.LITTLE_ENDIAN)
        
        read = 0
        while read < size:
            r = f.read(buf.array(), read, size - read)
            if r == -1:
                raise IOException()
            read += r
        
        while read < 4:
            buf.put(read, byte(0))
            read += 1
        
        return buf.getInt()
    
    @args(int, [RandomAccessFile])
    def read_byte(self, f):
    
        b = f.read()
        v = Byte(b).intValue()
        if v < 0: v += 256
        return v
    
    @args(int, [RandomAccessFile, int])
    def read_details(self, f, offset):
    
        # Go to start of this sprite
        f.seek(offset)
        
        next = self.str2num(4, f)
        
        sprite = Sprite()
        
        name = array(byte, 12)
        f.read(name)
        
        for i in range(12):
            if name[i] == 0:
                name = name[:i]
                break
        
        sprite.name = String(name, "ASCII")
        
        # Read width of sprite in words and height in scan lines.
        # These is stored in the Spritefile as width-1 and height-1.
        h_words = self.str2num(4, f) + 1
        v_lines = self.str2num(4, f) + 1

        sprite.h_words = h_words
        sprite.v_lines = v_lines
        
        # The bits used in each word.
        first_bit_used = self.str2num(4, f)
        last_bit_used   = self.str2num(4, f)

        sprite.first_bit = first_bit_used
        sprite.last_bit = last_bit_used
        
        # The pointers to the image and mask are found from the offsets
        # relative to the start of the sprite; i.e. from the next sprite
        # offset.
        image_ptr = offset + self.str2num(4, f)
        mask_ptr  = offset + self.str2num(4, f)
        
        # The mode number of the sprite.
        mode = self.str2num(4, f)
        
        bpp = (mode >> 27)
        log2bpp = xdpi = ydpi = 0
        
        if bpp == 0:
        
            mode = mode & 0x3f
            
            # Information on commonly used modes
            try:
                log2bpp, xscale, yscale = self.mode_info[mode]
                # Old modes have a maximum of 90 dots per inch.
                xdpi = int(90/xscale)
                ydpi = int(90/yscale)
                bpp = 1 << log2bpp
                
                # Sprites for old screen modes are all converted to RGB format.
                sprite.mode = 'RGB'
            
            except KeyError:
                raise SpritefileError('Unknown mode number.')
        else:
            if bpp < 7:
                sprite.mode = 'RGB'
            else:
                sprite.mode = 'CMYK'
            
            if bpp == 1:
                log2bpp = 0
            elif bpp == 2:
                log2bpp = 1
            elif bpp == 3:
                bpp = 4
                log2bpp = 2
            elif bpp == 4:
                bpp = 8
                log2bpp = 3
            elif bpp == 5:
                bpp = 16
                log2bpp = 4
            elif bpp == 6:
                bpp = 32
                log2bpp = 5
            elif bpp == 7:
                bpp = 32
                log2bpp = 5
            else:
                raise SpritefileError('Unknown number of bits per pixel.')
            
            xdpi = ((mode >> 1) & 0x1fff)
            ydpi = ((mode >> 14) & 0x1fff)
        
        sprite.bpp = bpp
        sprite.log2bpp = log2bpp
        sprite.xdpi = xdpi
        sprite.ydpi = ydpi
        
        has_palette = False
        
        palette = Palette()
        
        # Read palette, if present, putting the values into a list
        while f.getFilePointer() < image_ptr:
        
            f.skipBytes(1)
            # First entry (red, green, blue)
            entry1 = [self.read_byte(f),
                      self.read_byte(f),
                      self.read_byte(f)]
            
            f.skipBytes(1)
            # Second entry (red, green, blue)
            entry2 = [self.read_byte(f),
                      self.read_byte(f),
                      self.read_byte(f)]
            
            palette.add(PaletteEntry(entry1, entry2))
        
        if palette.hasEntries():
        
            if bpp == 8 and len(palette) < 256:
            
                if len(palette) == 16:
                
                    # Each four pairs of entries describes the variation
                    # in a particular colour: 0-3, 4-7, 8-11, 12-15
                    # These sixteen colours describe the rest of the 256
                    # colours.
                    
                    for j in range(16, 256, 16):
                    
                        for i in range(16):
                        
                            entry = palette.getEntry(i)
                            primary = entry.primary
                            
                            # Generate new colours using the palette
                            # supplied for the first 16 colours
                            red   = (((j + i) & 0x10) >> 1) | (primary[0] >> 4)
                            green = (((j + i) & 0x40) >> 3) | \
                                    (((j + i) & 0x20) >> 3) | (primary[1] >> 4)
                            blue  = (((j + i) & 0x80) >> 4) | (primary[2] >> 4)
                            red   = int(red * self.scale8)
                            green = int(green * self.scale8)
                            blue  = int(blue * self.scale8)
                            
                            # Append new entries
                            entry = PaletteEntry([red, green, blue],
                                                 [red, green, blue])
                            palette.add(entry)
                
                elif len(palette) == 64:
                
                    for j in range(64, 256, 64):
                    
                        for i in range(64):
                        
                            entry = palette.getEntry(i)
                            primary = entry.primary
                            
                            red   = (((j + i) & 0x10) >> 1) | (primary[0] >> 4)
                            green = (((j + i) & 0x40) >> 3) | \
                                    (((j + i) & 0x20) >> 3) | (primary[1] >> 4)
                            blue  = (((j + i) & 0x80) >> 4) | (primary[2] >> 4)
                            red   = int(red * self.scale8)
                            green = int(green * self.scale8)
                            blue  = int(blue * self.scale8)
                            
                            # Append new entries
                            entry = PaletteEntry([red, green, blue],
                                                 [red, green, blue])
                            palette.add(entry)
            
            sprite.palette = palette
        else:
            sprite.palette = None
        
        # The width of the sprite is the number of words used divided by the
        # bits per pixel of the sprite. Additionally, the parts of the sprite
        # unused at the ends are subtracted.
        width = (h_words * (32 >> sprite.log2bpp)) - \
                (first_bit_used >> sprite.log2bpp) - \
                ((31-last_bit_used) >> sprite.log2bpp)
        height = v_lines
        
        sprite.width = width
        sprite.height = height
        
        # Obtain image data
        f.seek(image_ptr)
        
        if sprite.mode == 'RGB':
            self.sprite2rgb(f, sprite)
        
        elif sprite.mode == 'CMYK':
            self.sprite2cmyk(f, sprite)
        
        # Obtain mask data
        if mask_ptr != image_ptr:
        
            f.seek(mask_ptr)
            
            self.mask2rgba(f, sprite)
            
            # The image is stored in RGBA form.
            sprite.mode = 'RGBA'
        
        self.sprites[sprite.name] = sprite
        
        return next
    
    @args(void, [File])
    def read(self, file):
    
        f = RandomAccessFile(file, "r")
        size = f.length()
        
        # Examine the sprites
        number = self.str2num(4, f)
        offset = self.str2num(4, f) - 4
        free   = self.str2num(4, f) - 4
        
        self.sprites = {}
        
        while offset < free:
        
            next = self.read_details(f, offset)
            offset = offset + next
    
    @args(void, [RandomAccessFile, Sprite])
    def sprite2rgb(self, f, sprite):
    
        # Convert sprite to RGB values
        
        has_palette = (sprite.palette != None) and sprite.palette.hasEntries()
        
        rgb = array(byte, sprite.width * sprite.height * 4)
        ptr = f.getFilePointer() * 8    # bit offset
        rgb_i = 0
        
        for j in range(sprite.height):
        
            # bit offset into the image
            row_ptr = ptr + sprite.first_bit
            
            for i in range(0, sprite.width):
            
                ### To be updated when shr_long instruction generation is fixed.
                f.seek(int(row_ptr) >> 3)
                
                # Conversion depends on bpp value
                if sprite.bpp == 32:

                    red = self.read_byte(f)
                    green = self.read_byte(f)
                    blue = self.read_byte(f)
                    row_ptr = row_ptr + 32
                
                elif sprite.bpp == 16:
                
                    value = self.str2num(2, f)
                    red   = int((value & 0x1f) * self.scale16)
                    green = int(((value >> 5) & 0x1f) * self.scale16)
                    blue  = int(((value >> 10) & 0x1f) * self.scale16)
                    row_ptr = row_ptr + 16
                
                elif sprite.bpp == 8:
                
                    if not has_palette:
                        # Standard VIDC 256 colours
                        value = self.read_byte(f)
                        red   = ((value & 0x10) >> 1) | (value & 7)
                        green = ((value & 0x40) >> 3) | \
                                ((value & 0x20) >> 3) | (value & 3)
                        blue  = ((value & 0x80) >> 4) | \
                                ((value & 8) >> 1) | (value & 3)
                        red   = int(red * self.scale8)
                        green = int(green * self.scale8)
                        blue  = int(blue * self.scale8)
                    else:
                        # 256 entry palette
                        value = self.read_byte(f)
                        red, green, blue = sprite.palette.getEntry(value).primary
                    
                    row_ptr = row_ptr + 8
                
                elif sprite.bpp == 4:
                
                    value = (self.read_byte(f) >> (int(row_ptr) % 8)) & 0xf
                    
                    if not has_palette:
                        # Standard 16 desktop colours
                        # Look up the value in the standard palette.
                        red, green, blue = self.palette16[value]
                    else:
                        # 16 entry palette
                        red, green, blue = sprite.palette.getEntry(value).primary
                    
                    row_ptr = row_ptr + 4
                
                elif sprite.bpp == 2:
                
                    value = (self.read_byte(f) >> (int(row_ptr) % 8)) & 0x3
                    
                    if not has_palette:
                        # Greyscales
                        red, green, blue = self.palette4[value]
                    else:
                        # 4 entry palette
                        red, green, blue = sprite.palette.getEntry(value).primary
                    
                    row_ptr = row_ptr + 2
                
                elif sprite.bpp == 1:
                
                    value = (self.read_byte(f) >> (int(row_ptr) % 8)) & 1
                    
                    if not has_palette:
                        # Black and white
                        red = green = blue = (255*(1-value))
                    else:
                        # 2 entry palette
                        red, green, blue = sprite.palette.getEntry(value).primary
                    
                    row_ptr = row_ptr + 1
                else:
                    red = green = blue = 0
                
                rgb[rgb_i] = red
                rgb[rgb_i + 1] = green
                rgb[rgb_i + 2] = blue
                rgb[rgb_i + 3] = 255
                rgb_i += 4
            
            ptr = ptr + (sprite.h_words * 32)
        
        sprite.rgba = rgb
    
    @args(void, [RandomAccessFile, Sprite])
    def sprite2cmyk(self, f, sprite):

        # Read a CMYK sprite - currently just reuse the data verbatim.

        ptr = f.getFilePointer() * 8    # bit offset
        
        rgb = array(byte, sprite.width * sprite.height * 4)
        rgb_i = 0
        
        for j in range(sprite.height):

            for i in range(sprite.width):

                rgb[rgb_i] = self.read_byte(f)
                rgb[rgb_i + 1] = self.read_byte(f)
                rgb[rgb_i + 2] = self.read_byte(f)
                rgb[rgb_i + 3] = self.read_byte(f)
                rgb_i += 4
        
        sprite.rgba = rgb
    
    @args(void, [RandomAccessFile, Sprite])
    def mask2rgba(self, f, sprite):
    
        rgba = array(byte, sprite.width * sprite.height * 4)
        
        # Colour depths below 16 bpp have the same number of bpp in the mask.
        bpp = sprite.bpp
        
        if bpp == 32 or bpp == 16:
            bpp = 1
        
        bits = bpp * sprite.width
        
        row_size = bits >> 5        # number of 32-bit words
        if bits % 32 != 0:
            row_size = row_size + 1
        
        ptr = f.getFilePointer() * 8    # bit offset
        image_ptr = 0
        
        for j in range(sprite.height):
        
            # bit offset into the image
            row_ptr = int(ptr) + sprite.first_bit
            
            for i in range(sprite.width):
            
                f.seek(row_ptr >> 3)
                
                # Conversion depends on bpp value
                if bpp == 8:
                
                    value = self.read_byte(f)
                    if value != 255:
                        value = 0
                    row_ptr += 8
                
                elif bpp == 4:
                
                    value = (self.read_byte(f) >> (row_ptr % 8)) & 0xf
                    if value == 15:
                        value = 0xff
                    else:
                        value = 0
                    row_ptr += 4
                
                elif bpp == 2:
                
                    value = (self.read_byte(f) >> (row_ptr % 8)) & 0x3
                    if value == 3:
                        value = 0xff
                    else:
                        value = 0
                    row_ptr += 2
                
                elif bpp == 1:

                    # Black and white
                    value = (self.read_byte(f) >> (row_ptr % 8)) & 1
                    value = value * 0xff
                    row_ptr += 1
                else:
                    # We should never reach here. This is included only to
                    # ensure that value is defined outside the if scope.
                    value = 0
                
                # Only keep the colour components if the mask value is non-zero
                # because the Android API requires that the components are
                # pre-multiplied which, for this case, simply means multiplying
                # by 0 or 1.
                if value != 0:
                    red, green, blue, x = sprite.rgba[image_ptr:image_ptr + 4]
                else:
                    red = green = blue = byte(0)
                
                rgba[image_ptr] = red
                rgba[image_ptr + 1] = green
                rgba[image_ptr + 2] = blue
                rgba[image_ptr + 3] = value
                
                image_ptr += 4
            
            ptr += row_size * 32
        
        sprite.rgba = rgba
