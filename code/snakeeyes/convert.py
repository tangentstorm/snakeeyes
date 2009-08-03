"""
based on:
   http://wiki.wxpython.org/index.cgi/WorkingWithImages
"""
import wx
import Image

#@TODO: rename these... img for Image module, wxBmp and wxImg for wx

def pilToBitmap(pil):
    return imageToBitmap(pilToImage(pil))

def pilToImage(pil):
    image = wx.EmptyImage(pil.size[0], pil.size[1])
    image.SetData(pil.convert('RGB').tostring())
    return image

def imageToBitmap(image):
    return image.ConvertToBitmap()


## these are mine:

def strings_to_image(strings):
    height = len(strings)
    img = Image.new('1', (len(strings[0]), height))
    for y, line in enumerate(strings):
        for x, char in enumerate(line):
            img.putpixel((x, y), 1 if char=="#" else 0)


