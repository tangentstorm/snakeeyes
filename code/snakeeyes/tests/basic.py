"""
Tests the basic use of the system.
"""
import unittest
import Image, ImageDraw
from snakeeyes import fontdata, config, scrape
from snakeeyes.scrape import Region, Rectangle

class Test(unittest.TestCase):


    def test_simple(self):
        """
        get a basic font working
        """

        # here is the glyph we want to recognize:
        # it's just a plus sign.
        def draw_plus( on_img, at, color):
            x, y = at
            draw = ImageDraw.Draw(on_img)
            draw.line(( x, y + 3, x + 4, y + 3 ), fill=color) # horizontal
            draw.line(( x + 3, y, x + 3, y + 4 ), fill=color) # vertical
        
        glyph = Image.new("RGB", (5, 5))
        draw_plus(on_img=glyph, at=(0, 0), color='red')

        # okay. now we want to see whether that image is
        # present somewhere else. Say we are monitoring
        # the screen continuously and we want to see 
        # whether or not the glyph is at coordinates (2,2)


        # now we need a font so we can teach the system about the glyph
        font = fontdata.FontData({})

        # it doesn't know about our font yet, but we can teach it:
        self.assertFalse(font.contains(glyph))
        font.learn(glyph, value='red +')
        self.assertTrue(font.contains(glyph))

        # note that we don't actually care about the 
        # Image object, only the actual data:
        self.assertTrue(font.contains(glyph.copy()))

        # and of course what we want back is the corresponding string
        self.assertEqual('red +', font.recall(glyph))


        # now that our FontData recognizes the shape,
        # we can set up a scrape region that detects it
        # see ScrapeConfig for how to make this simpler
        reg = Region(Rectangle((0, 0), glyph.size), scrape.Tool(font))
        
        # now here's our (blank) screen:
        screen = Image.new("RGB", (10, 10))

        # so let's take a snapshot to see what's there:        
        maybe_glyph = reg.take_snapshot(screen)
        self.assertEqual(maybe_glyph.size, glyph.size)
        
        # the screen is blank, so our font fails to recognize what's there:
        self.assertFalse(font.contains(maybe_glyph))
        
        # so... as far as our scraper is concerned,
        # the region contains nothing:
        self.assertEquals(None, reg.scrape(screen))

        # now let's draw the image:
        draw_plus(on_img=screen, at=(0, 0), color="red")

        # now, the scraping the region returns the correct text:
        self.assertEquals("red +", reg.scrape(screen))

        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_simple']
    unittest.main()