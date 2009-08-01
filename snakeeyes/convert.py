'''
http://wiki.wxpython.org/index.cgi/WorkingWithImages
'''
import wx

def pilToBitmap(pil):
    return imageToBitmap(pilToImage(pil))

def pilToImage(pil):
    image = wx.EmptyImage(pil.size[0], pil.size[1])
    image.SetData(pil.convert('RGB').tostring())
    return image

def imageToBitmap(image):
    return image.ConvertToBitmap()

