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

    #:: Image.Image -> (int -> int -> bool)
    def predicate(self, img):
        if img.mode == "1":
            def pixel_check(a, b):
                return img.getpixel((a, b)) == 0 
        else:
            def pixel_check(a, b):
                return max(img.getpixel((a, b))) < self.thresh
        return pixel_check
    
    def recognize(self, img):
        return scrape.str_from_img(img, self.font, self.predicate(img))
    
    
class ContrastStringTool(StringTool):
    """
    If the background of the origin pixel
    is light, it looks for dark pixels, and vice versa.
    Helpful if the text tends to have a blinking
    inverse effect.

    @TODO: assumes origin is part of background. parameterize!
    """

    def find_dark_ink(self, img, thresh=150):
        def pred(a,b):
            return max(img.getpixel((a, b))) < thresh
        return pred

    def find_light_ink(self, img, thresh=150):
        def pred(a,b):
            return max(img.getpixel((a, b))) > thresh
        return pred
    
    def predicate(self, img):
        
        if max(img.getpixel( (0, 0) )) < 150:
            return self.find_light_ink(img)
        else:
            return self.find_dark_ink(img)  
             