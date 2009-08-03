'''
Created on Aug 2, 2009

@author: michal
'''
class Tool(object):
    """
    A Tool combines FontData and a GlyphFilter
    """
    def __init__(self, font, filter=None):
        self.font = font
        self.filter = filter
        
    def recognize(self, glyph):
        return self.font.recall(glyph)
    
    
class NullTool(object):
    """
    A dummy tool that does nothing.
    """
    def recognize(self, glyph):
        return None    
    

   
 