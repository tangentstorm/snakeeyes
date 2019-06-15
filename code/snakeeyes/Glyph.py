"""
Created on Aug 3, 2009

@author: michal
"""
from .Rectangle import Rectangle

class Glyph(Rectangle):

    def __init__(self, pos, size, glint):
        """
        Constructor
        """
        super(Glyph, self).__init__(pos, size)
        self.width = size[0]
        self.glint = glint
        self.img = None


    # image interface:
    def tostring(self):
        return self.img.tostring()
    
    def convert(self, *a, **kw):
        return self.img.convert(*a, **kw)


    # old (width, glint) interface:
    def as_tuple(self):
        return tuple([self.width, self.glint])

    def __getitem__(self, idx):
        return self.as_tuple()[idx]
    
    def __eq__(self, other):
        return self.as_tuple() == other

