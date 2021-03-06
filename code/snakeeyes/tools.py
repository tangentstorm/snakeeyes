"""
Created on Aug 2, 2009

@author: michal
"""
from PIL.Image import Image
from typing import Callable
from . import scrape


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
    @staticmethod
    def recognize(_img):
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

    def predicate(self, img: Image) -> Callable[[int, int], bool]:
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

    @TODO: assumes origin is part of background. parametrize!
    """

    @staticmethod
    def find_dark_ink(img, thresh=150):
        def pred(a, b):
            return max(img.getpixel((a, b))) < thresh
        return pred

    @staticmethod
    def find_light_ink(img, thresh=150):
        def pred(a, b):
            return max(img.getpixel((a, b))) > thresh
        return pred
    
    def predicate(self, img):
        bg_dark = max(img.getpixel((0, 0))) < 150  # max of r, g, b
        return self.find_light_ink(img) if bg_dark else self.find_dark_ink(img)


class TextTool(StringTool):
    """
    Handles a scrolling chat box.
    """
    # @TODO: un-hard-code font metrics and line count!
    def recognize(self, img):
        lines = scrape.calc_lines(scrape.font_metrics(), num_lines=6)
        res = []
        for (ceil, base, floor) in lines:
            line_img = img.crop((0, ceil, img.size[0], floor + 1))
            res.append(scrape.str_from_img(line_img, self.font, 
                                           self.predicate(line_img)))
        return "\n".join(res)
