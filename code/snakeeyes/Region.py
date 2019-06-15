"""
Created on Aug 2, 2009

@author: michal
"""
from .Rectangle import Rectangle
from PIL import Image, ImageOps, ImageChops, ImageDraw, ImageColor

from . import scrape
import sys
import difflib

class Region(object):
    """
    This is the top level scraping tool.
    """
    def __init__(self, pos, size, tool=None, color=None):
        self.rect = Rectangle(pos, size)
        self.tool = tool
        self.color = color
        self.last_value = None
        
    def take_snapshot(self, screen):
        """
        screen:image -> cropped_area:image
        """
        self.last_snapshot = screen.crop(self.rect.as_quad())
        return self.last_snapshot
    
    def scrape(self, screen):
        """
        screen:image -> contents:(Maybe str)
        """
        self.take_snapshot(screen)
        self.last_value = self.tool.recognize(self.last_snapshot)
        return self.last_value



class StringRegion(Region):
    #@TODO: replace StringTool with StringRegion?
    # I need this here because I want to filter the image
    # inside the debug window, and the image isn't a 
    # member of a Tool. 
    def take_snapshot(self, screen):
        snap = super(StringRegion, self).take_snapshot(screen)
        thresh = Image.new("RGB", snap.size, "#999999")
        mono = ImageChops.darker(snap, thresh)
        mono = ImageOps.autocontrast(mono, 0)
        return mono # .resize((w *2, h * 2))



class TextRegion(StringRegion):
    """
    A multi-line text region
    """

    def take_snapshot(self, screen):
        mono = super(TextRegion, self).take_snapshot(screen)
        self.last_snapshot = self.draw_baselines(mono)
        return self.last_snapshot

    def draw_baselines(self, img_in):
        img_out = img_in.copy()
        draw = ImageDraw.Draw(img_out)
    
        prev_floor = 0
        w, h = img_out.size
    
        gap_color = ImageColor.getrgb('#ccccFF')
    
        lines = scrape.calc_lines(scrape.font_metrics(), 7)

        for i, (ceiling, base, floor) in enumerate(lines):

            # draw the baseline
            color = ImageColor.getrgb("#ffdddd")
            if not base:
                base = floor -2
                color = ImageColor.getrgb("red")
    
            draw.line([(0, base), (w, base)], fill=color)
            
            # shade gap between the lines
            draw.rectangle((0, prev_floor, w, ceiling), fill=gap_color)
            prev_floor = floor +1
                
        # shade final gap:
        draw.rectangle((0, prev_floor, w, h), fill=gap_color)
    
        # now draw the text back over the baselines:
        img_out = ImageChops.darker(img_in, img_out)

        # uncomment to zoom in for debugging
        # img_out = img_out.resize((w *2 , h* 2))

        return img_out
    
class ChatRegion(TextRegion):
    """
    This is a text region that scrolls. 
    The call back is called for every new line of
    text that appears.
    """
    def __init__(self, pos, size, tool=None, color=None, callback=None):
        super(ChatRegion, self).__init__(pos, size, tool, color)
        self.previous_text = ""
        self.callback = callback or (lambda lines: sys.stdout.write("\n".join(lines) + "\n"))

    def scrape(self, screen):
        text = super(ChatRegion, self).scrape(screen).split("\n")
        if text != self.previous_text:
            newlines = []
            for diff in difflib.ndiff(self.previous_text, text):
                if diff.startswith("+"):
                    newlines.append(diff[1:])
            self.callback(newlines)
            self.previous_text = text
        return "\n".join(text)
    
    

class BoxRegion(StringRegion):
    """
    This is text with a box around it, where the box
    and the text have the same color, which we may not
    be able to determine until we scrape (perhaps
    because the box is flashing).
    
    We subclass StringRegion so it auto-converts to 
    black and white for us.
    """
    pass


class ContrastRegion(Region):

    def take_snapshot(self, screen):
        """
        @TODO: refactor this mess.
        """
        snap = super(ContrastRegion, self).take_snapshot(screen)
        self.last_snapshot = snap
        return snap


class StretchBoxRegion(BoxRegion):
    """
    """
    def take_snapshot(self, screen):
        """
        When you use a stretch region, you should make your 
        scraping box wide enough to accommodate the longest
        expected text string. It will take a snapshot of the
        entire area, and then simply mask out the parts outside
        the left and right borders.
        """

        snap = super(StretchBoxRegion, self).take_snapshot(screen)

        # convert to black and white because i don't want to 
        # deal with "almost black" but tools.pixel_check 
        # assumes we're dealing with a tuple of colors,
        # so i have to convert it back to RGB
        snap = snap.convert("1")
        
        # now, starting at the top center pixel of
        # the box, find the true x and w
        snap_w, snap_h = snap.size
        center         = snap_w / 2

        border_color = snap.getpixel((center, 0))

        # start at the center and work left to find left edge,
        # looking ahead one pixel each time.
        left = center
        while left > 0 and snap.getpixel((left - 1, 0)) == border_color:
            left -= 1

        #if left == center:
        #    print "found no pixels to the left!"
        #    print "border color: ", border_color
        #    print "center_x-1: ", snap.getpixel((center -1, 0))

        # and the same thing moving right:
        right = center
        while right+1 < snap_w and snap.getpixel((right + 1, 0)) == border_color:
            right += 1
            
        # print "left:", left, "right:",right

        # now do the masking:
        snap = snap.convert("RGB") # for some reason it'll draw outline but not fill in mode 1
        draw = ImageDraw.Draw(snap)
        draw.rectangle((0, 0, left, snap_h), fill='white')
        draw.rectangle((right, 0, snap_w, snap_h), fill='white')
        
        # finally, mask the whole border, so it doesn't get
        # recognized as part of the font
        draw.rectangle((0, 0, snap_w, snap_h), outline='white')
        
        # import time; time.sleep(10)
        snap = snap.convert("1") # just to save space in the font, not that it really matters
        self.last_snapshot = snap
        return snap


    
