'''
Created on Aug 3, 2009

@author: michal
'''
from Rectangle import Rectangle

class Glyph(Rectangle):

    def __init__(self, pos, width, glint):
        '''
        Constructor
        '''
        height = 1
        super(Glyph, self).__init__(pos, (width, height))
        self.width = width
        self.glint = glint

    def as_tuple(self):
        return (self.width, self.glint)

    def __getitem__(self, idx):
        return self.as_tuple()[idx]
    
    def __eq__(self, other):
        return self.as_tuple() == other

