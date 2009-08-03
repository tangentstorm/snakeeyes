'''
Created on Aug 2, 2009

@author: michal
'''
import scrape

class Tool(object):
    """
    This is the simplest tool. It just maps
    an image directly to a string through a
    FontData object.
    """
    def __init__(self, font):
        self.font = font

    def recognize(self, img):
        return self.font.recall(img)
    
    
class NullTool(object):
    """
    A dummy tool that does nothing.
    """
    def recognize(self, img):
        return None    
    

   
class StringTool(Tool):
    """
    This tool breaks the image into glyphs and then
    parses them. It works for a single horizontal 
    line of text.
    """
    def __init__(self, font, darker_than=10):
        super(StringTool, self).__init__(font)
        self.thresh = darker_than
    
    def recognize(self, img):
        if img.mode == "1":
            def pixel_check(a, b):
                return img.getpixel((a, b)) == 0 
        else:
            def pixel_check(a, b):
                return max(img.getpixel((a, b))) < self.thresh
        return scrape.str_from_img(img, self.font, pixel_check)
