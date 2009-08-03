"""
Test scanning (for lines, words, etc)
"""
import unittest
from narrative import testcase
from snakeeyes import scrape
from handy import trim

class StringImage(object):
    "We'll represent bitmaps using strings for these tests."
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
    
    # @TODO: get this test working again!
    # self.assertEquals( 3, len(found))
    
    # the result should be width/char pairs
    # in this case the chars are just the binary numbers
    #wcs = list(scrape.scan_line(w = len(g[0]), h=1, pred=has_ink, space_size=1))
    
    #self.assertEquals((2,0), wcs[0]) # 2 dots (space)
    #self.assertEquals((1,1), wcs[1]) # 1 char, 1 in binary
    #self.assertEquals((4,0), wcs[2])
    #self.assertEquals((2,3), wcs[3]) # 2 char, 1 in binary






#
#@testcase
#def multiline(self):
#
#    # the word For from a scan of Mentally Incontinent
#    testdata = ['....................................',
#                '....................................',
#                '....................................',
#                '.......#######......................',
#                '......########......................',
#                '......###...........................',
#                '......###.......#####...######......',
#                '......######...##..###..#####.......',
#                '......#######.##....##..##..........',
#                '......###.....##....###.##..........',
#                '......###.....##....###.##..........',
#                '......###.....##....##..##..........',
#                '......###.....###...##..##..........',
#                '......###......#######..##..........',
#                '.......#........#####...#...........',
#                '....................................',
#                '....................................']
#    #          0|     6|             17|1|   6|     6|
#
#    
#
#    fo = 11656954525901520401809650090941306687965691406109462313538109468335093405284899504112
#    r  = 2475936747400903850442391488
#    
#    # the result should be width/char pairs
#    # in this case the chars are just the binary numbers
#    wcs = list(scrape.scan_line(len(testdata[0]), len(testdata),
#                           (lambda a,b: testdata[b][a] == '#'), space_size=4))
#    
#    self.assertEquals((6,   0), wcs[0]) # 2 dots (space)
#    self.assertEquals((17, fo), wcs[1]) # 1 char, 1 in binary
#    self.assertEquals((6,   r), wcs[2])
#    self.assertEquals((6,   0), wcs[3]) # 2 char, 1 in binary


if __name__=="__main__":
    unittest.main()
