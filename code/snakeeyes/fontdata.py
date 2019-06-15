from typing import Optional
from snakeeyes.Glyph import ToBytes

SPACE = object()

# TODO: get rid of ToBytes and just use Glyphs. (this breaks tests.img_test)


class NeedTraining(Exception):
    """
    FontData throws this exception if it's in training
    mode and encounters a glyph it doesn't know.
    """
    def __init__(self, font, glyph: ToBytes):
        super(NeedTraining, self).__init__()
        self.font = font
        self.glyph = glyph


class FontData(object):
    """
    A dictionary mapping images (bitmaps for individual symbols)
    to strings characters. Essentially, the converse of a bitmap font.
    """
    def __init__(self, data: dict):
        self.data = data
        self.training_mode = False

    def contains(self, img: ToBytes) -> bool:
        return img.tobytes() in self.data

    def learn(self, img: ToBytes, grapheme: str):
        """use this to store an image"""
        self.data[img.tobytes()] = grapheme

    def recall(self, img: ToBytes) -> Optional[str]:
        """retrieves a character"""
        if img is SPACE:
            return ' '
        try:
            return self.data[img.tobytes()]
        except KeyError:
            if self.training_mode:
                raise NeedTraining(font=self, glyph=img)
            else:
                return None
