from typing import Optional
from snakeeyes.Glyph import Glyph

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
    def __init__(self, data: dict):
        self.data = data
        self.training_mode = False

    def contains(self, glyph: Glyph) -> bool:
        return glyph.tobytes() in self.data

    def learn(self, glyph: Glyph, grapheme: str):
        """use this to store a glyph"""
        self.data[glyph.tobytes()] = grapheme

    def recall(self, glyph: Glyph) -> Optional[str]:
        """retrieves a character"""
        if glyph is SPACE:
            return ' '
        try:
            return self.data[glyph.tobytes()]
        except KeyError:
            if self.training_mode:
                raise NeedTraining(font=self, glyph=glyph)
            else:
                return None
