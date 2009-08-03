'''
Created on Aug 2, 2009

@author: michal
'''
class Region(object):
    """
    This is the top level scraping tool.
    """
    def __init__(self, rect, tool=None, color=None):
        self.rect = rect
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
