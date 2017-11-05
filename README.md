Sprite Viewer
=============

This application allows RISC OS spritefiles to be opened and their contents
viewed on Android devices.

![A screenshot of the application](SpriteViewer.png)

Opening sprites from the viewer
-------------------------------

When launched as an application the viewer will show a selection of files with
recognised file extensions (`.spr`, `.ff9` and `,ff9`). Clicking on a file name
will show thumbnails of the sprites it contains. Sprites can be viewed at their
full resolution by long clicking on them to display them in an external viewer
application.

Pressing the device's back button will cause the file list to be shown again.

Opening sprites from a file browser
-----------------------------------

The viewer will respond to a request to open files with recognised file
extensions. However, this only seems to work on certain versions of Android.
On versions where it does work, clicking on a recognised file in a file
browser will cause the sprite viewer to be launched and the sprites in the
file to be displayed.

Pressing the device's back button when the viewer has been launched in this way
will cause the viewer to exit.
