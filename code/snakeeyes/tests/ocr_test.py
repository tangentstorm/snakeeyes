"""
Tests use of the system for recognizing text.
"""
import unittest
import Image, ImageDraw, ImageFont
from snakeeyes import scrape

class OCRTest(unittest.TestCase):
    """
    Optical Character Recognition. 
    """

    def setUp(self):
        """
        For this test suite, we will limit ourselves to crisp 
        black pixels (no anti-aliasing) on a white background.
        
        For converting images "in the wild" to this 
        format, see ink_test.py.
        """
        self.img = Image.new("1", (300, 200), "white")
        self.draw = ImageDraw.Draw(self.img)
        self.font = ImageFont.load_default()
             
    def put_text(self, text, at=(25,25)):
        "helper routine to put the text on our image"
        self.draw.text(at, text, font=self.font, fill="black")

    def _show(self):
        # you might want to have bmp open in mspaint by default
        # and have it running already, so image doensn't halt.
        # before you hit the debugger
        from subprocess import Popen
        from snakeeyes import windows
        f = "ocr_test.bmp"
        self.img.save(open(f, "wb"), "bmp")
        pid = Popen(["mspaint", f]).pid
        windows.named(f).move_to(-200, 100)
        import pdb; pdb.set_trace()
        windows.named(f).close()

    ##############################################################
                
    def test_glyph(self):
        """
        Our first task is to be able to detect a single glyph.
    
        (A glyph is just a symbol representing one or more
        characters. See http://en.wikipedia.org/wiki/Glyph )
        """

        glyph = "a"
        self.put_text(glyph)

        #found = list(scrape.glyphs(self.img))
        #assert len(found) == 1, found
                
        #self._show()        



if __name__ == "__main__":
    unittest.main()