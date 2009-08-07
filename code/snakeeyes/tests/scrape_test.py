"""
Test scanning (for lines, words, etc)
"""
import unittest
from narrative import testcase
from snakeeyes import scrape
from handy import trim
from snakeeyes.fontdata import SPACE

class StringImage(object):
    """
    We'll represent bitmaps using strings for these tests.
    """
    def __init__(self, string):
        lines = trim(string).split("\n")
        self.width = max(len(line) for line in lines)
        self.height= len(lines) 
        self.lines = lines
        
    @property
    def size(self):
        return (self.width, self.height)

    def ink_p(self, x, y):
        ":: x -> y -> boolean"
        return self.lines[y][x] == "#"


def grid(string):
    "short constructor"
    return StringImage(string)



@testcase
def test_scan_dot_in_line(self):
    "Okay! a single line. Find the ink."

    img = grid(#01234567890123456
               '..#....##.....###')

    found = list( scrape.glyphs_from_line(img, img.ink_p) )
    
    self.assertEquals( 3, len(found))

    the_x,  \
    the_xx, \
    the_xxx = found

    self.assertEqual(1, the_x.width)
    self.assertEqual(2, the_xx.width)
    self.assertEqual(3, the_xxx.width)
    
    self.assertEqual((2, 0), the_x.pos)
    self.assertEqual((1, 1), the_x.size)

    self.assertEqual((7, 0), the_xx.pos)
    self.assertEqual((2, 1), the_xx.size)
    
    self.assertEqual((14, 0), the_xxx.pos)
    self.assertEqual((3, 1), the_xxx.size)



@testcase
def test_full_grid(self):

    # the word For from a scan of Mentally Incontinent
    img = grid(
        """
        ....................................
        ....................................
        ....................................
        .......#######......................
        ......########......................
        ......###...........................
        ......###.......#####...######......
        ......######...##..###..#####.......
        ......#######.##....##..##..........
        ......###.....##....###.##..........
        ......###.....##....###.##..........
        ......###.....##....##..##..........
        ......###.....###...##..##..........
        ......###......#######..##..........
        .......#........#####...#...........
        ....................................
        ....................................""")
    #  0|     6|             17|1|   6|     6|

    

    # the old-style glints:
    fo = 11656954525901520401809650090941306687965691406109462313538109468335093405284899504112
    r  = 2475936747400903850442391488
    
    found = list(scrape.glyphs_from_line(img, img.ink_p))
    the_fo, the_r = found
    self.assertEquals((17, fo), the_fo) # 1 char, 1 in binary
    self.assertEquals((6,   r), the_r)

    self.assertEquals(img.size[1], the_fo.size[1]) # heights should match!
    
    
    
@testcase
def test_tokenize(self):
    
    img = grid(#01234567890123456
               '.#.#.#..#.#.#')

    found = list( scrape.glyphs_from_line(img, img.ink_p))

    assert len(found) == 6    

    spaced = list(scrape.spaced(found, space_width=2))
    self.assertEquals(len(spaced), 7)
    self.assertEquals(spaced[3], SPACE)
    

if __name__=="__main__":
    unittest.main()
