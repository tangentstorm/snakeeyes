"""
Created on Aug 1, 2009

@author: michal
"""
import ImageDraw
from scrape import Region, Tool, Rectangle, NullTool
from fontdata import FontData
import shelve


def train(tool):
    tool.font.training_mode = True
    return tool


_KNOWN_FONTS = {}

def get_font_tool(path):
    if path in _KNOWN_FONTS:
        font = _KNOWN_FONTS[path]
    else:
        font = _KNOWN_FONTS.setdefault(path, FontData(shelve.open(path)))
    return Tool(font)


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

            
    def read_from(self,path):
        """
        """
        self.config = eval(open(path).read())
        for name, (pos, size, tool, color) in self.config.items():
            self[name] = Region(Rectangle(pos, size), tool, color)

    def draw_boxes(self, img):
        """
        this is a debug function that draws boxes on the
        screen grab for each of the text input areas
        """
        draw = ImageDraw.Draw(img)
        for name, region in self.items():
            r = region.rect
            draw.rectangle([r.pos, r.far_corner()], outline=region.color)        
