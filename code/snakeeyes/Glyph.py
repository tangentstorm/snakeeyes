"""
Created on Aug 3, 2009

@author: michal
"""
from PIL.Image import Image
import abc

from .Rectangle import Rectangle


class ToBytes(abc.ABC):
    """abstract type for the tobytes() method"""
    @abc.abstractmethod
    def tobytes(self)-> bytes:
        pass


# FontData only cares about ToBytes, so point out that Image supports this.
ToBytes.register(Image)


class Glyph(Rectangle, ToBytes):

    def __init__(self, pos, size, glint):
        super(Glyph, self).__init__(pos, size)
        self.width = size[0]
        self.glint = glint
        self.img = None

    # image interface:

    def tobytes(self):
        return self.img.tobytes()
    
    def convert(self, *a, **kw):
        return self.img.convert(*a, **kw)

    def as_tuple(self):
        """old (width, glint) interface:"""
        return tuple([self.width, self.glint])

    def __getitem__(self, idx):
        return self.as_tuple()[idx]
    
    def __eq__(self, other):
        return self.as_tuple() == other

