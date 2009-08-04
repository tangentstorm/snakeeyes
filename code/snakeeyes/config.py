"""
Created on Aug 1, 2009

@author: michal
"""
from Rectangle import Rectangle
from Region import Region, TextRegion, StretchBoxRegion, ContrastRegion
from fontdata import FontData
import ImageDraw
import shelve

_KNOWN_FONTS = {}


# config file vocabulary
#-------------------------------------------------------

from tools import Tool, NullTool, StringTool, ContrastStringTool

def get_font(path):
    return _KNOWN_FONTS.setdefault(path, FontData(shelve.open(path)))

def get_font_tool(path):    
    return Tool(get_font(path))

def get_string_tool(path, darker_than=10):    
    return StringTool(get_font(path), darker_than)

def train(tool):
    tool.font.training_mode = True
    return tool


#-------------------------------------------------------


class ScrapeConfig(dict):
    """
    Essentially, a dictionary of ScrapeRegions.
    May be loaded in dynamically from an external file.
    """
    def __init__(self, path=None):
        """
        :: Maybe path:Str -> ScrapeConfig
        """
        super(ScrapeConfig, self).__init__()
        if path:
            self.read_from(path)

            
    def read_from(self, path):
        """
        path points to a file containing a single python expression
        which should evaluate to a dict with type:

               { name : ( (x,y), (w, h), tool, color }

        """
        self.config = eval(open(path).read())
        for name, region in self.config.items():
            self[name] = region
            
    def draw_boxes(self, img):
        """
        this is a debug function that draws boxes on the
        screen grab for each of the text input areas
        """
        draw = ImageDraw.Draw(img)
        for name, region in self.items():
            r = region.rect
            draw.rectangle([r.pos, r.far_corner()], outline=region.color)        


