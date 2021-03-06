"""
This pulls in scraper configuration from a python file.
"""
import os

from .fontdata import FontData
from PIL import ImageDraw
import shelve

_KNOWN_FONTS = {}


# config file vocabulary
#-------------------------------------------------------

# some of these are not used in this file, but they
# should be in scope for use by the config files themselves:
from .Region import *
from .tools import Tool, NullTool, StringTool, ContrastStringTool, TextTool


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
        self.config = {}
        if path:
            self.read_from(path)

    def read_from(self, path):
        """
        path points to a file containing a single python expression
        which should evaluate to a dict with type:

               { name : ( (x,y), (w, h), tool, color }

        """
        if os.path.exists(path):
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

    def collect_values(self, img):
        """:: Image.Image -> { str : str }"""
        # we've assumed you've grabbed the entire window
        # maybe it would be better to grab only the pieces
        # you need directly from the screen, but for 
        # now this is fine
        res = {}
        for key, region in self.items():
            res[key] = region.scrape(img)
        return res
