"""
Various conversion routines.

Some of these are based on code from:

   http://wiki.wxpython.org/index.cgi/WorkingWithImages
"""
import wx
import Image

def img_to_wxbmp(pil):
    ":: Image.Image -> wx.Bitmap"
    return wximg_to_wxbmp(img_to_wximg(pil))

def img_to_wximg(pil):
    ":: Image.Image -> wx.Image"
    image = wx.EmptyImage(pil.size[0], pil.size[1])
    image.SetData(pil.convert('RGB').tostring())
    return image

def wximg_to_wxbmp(image):
    ":: wx.Image -> wx.Bitmap"
    return image.ConvertToBitmap()


## these are mine:

def strings_to_img(strings):
    "[ String ] -> Image.Image"
    height = len(strings)
    img = Image.new('1', (len(strings[0]), height))
    for y, line in enumerate(strings):
        for x, char in enumerate(line):
            img.putpixel((x, y), 1 if char=="#" else 0)

