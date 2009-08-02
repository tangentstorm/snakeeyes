"""
Tests use of the system for recognizing text.
"""
import unittest


class OCRTest(unittest.TestCase):
    """
    Optical Character Recognition. 
    
    For this test suite, we will limit ourselves to crisp 
    black pixels (no anti-aliasing) on a white background.
    
    For converting images "in the wild" to this 
    format, see ink_test.py.
    """

    def test_glyphs(self):
        """
        Given a picture of a word, our first task is to
        decompose the word into glyphs.
    
        (A glyph is just a symbol representing one or more
        characters. See http://en.wikipedia.org/wiki/Glyph )
        """
        




if __name__ == "__main__":
    unittest.main()