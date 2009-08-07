import os
import shelve

SPACE = object()

class NeedTraining(Exception):
    """
    FontData throws this exception if it's in training 
    mode and encounters a glyph it doesn't know.
    """
    def __init__(self, font, glyph):
        super(NeedTraining, self).__init__()
        self.font = font
        self.glyph = glyph


class FontData(object):
    """
    A dictionary mapping glyphs (bitmaps for individual symbols)
    to strings characters. Essentially, the converse of a bitmap font.
    """
    def __init__(self, dict):
        self.data = dict
        self.training_mode = False
        
    #:: self -> Glyph -> Bool
    def contains(self, glyph):
        return self.data.has_key(glyph.tostring())


    #:: self -> Glyph -> String -> None
    def learn(self, glyph, grapheme):
        "use this to store a glyph"
        self.data[glyph.tostring()] = grapheme

        
    #:: self -> Glyph -> Maybe String
    def recall(self, glyph):
        "retrieves a character"
        if glyph is SPACE:
            return ' '
        try:
            return self.data[glyph.tostring()]
        except KeyError:
            if self.training_mode:
                raise NeedTraining(font=self, glyph=glyph)
            else:
                return None

