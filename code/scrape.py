# scrape a win32 window or image so we can see what's on screen

import os
import win32gui, win32ui
import Image, ImageGrab, ImageDraw


## window finding ##########################################

def listwindows():
    res = []
    def record(hwnd, extra):
        res.append(hwnd)
    win32gui.EnumWindows(record, None)
    return res


## screen capture ##########################################

def grabImage(hwnd):
    bounds = win32gui.GetWindowRect(hwnd)
    im = ImageGrab.grab(bounds)
    return im

def grabPixel(hwnd, (x, y)):
    win = win32ui.CreateWindowFromHandle(hwnd)
    dc = win.GetWindowDC()
    px = hex(dc.GetPixel(x, y))

    # @TODO: just do the math :)
    # note that the values are "backwards" from rgb
    if len(px) < 4: px += ("0" * (8-len(px)))
    b = int(px[2:4], 16)
    g = int(px[4:6], 16)
    r = int(px[6:8], 16)
    
    return (r,g,b)
    
            
## OCR stuff (very primitive) ##############################

def lines(im):
    """
    this yields a sequence of top,baseline,bottom y pixels for the image
    """
    assert im.mode in ('1','L'), 'must be grayscale for now'
    w,h = im.size

    lastBlankLine = 0
    alreadyOnText = False
    lastCount = 0
    baseLine = None

    for y in range(h):

        countDarks = w - im.transform((w,1), Image.EXTENT, 
                                      (0,y,w,y+1)).histogram()[-1]

        if countDarks > 0: # then there are some dark pixels

            if alreadyOnText:
                if float(lastCount)/countDarks > 1.7 and baseLine is None:
                    baseLine = y
            else:
                alreadyOnText = True
            lastCount = countDarks

        elif alreadyOnText:

            # if we haven't found the baseline yet, then this IS the
            # baseline. (Happens on lines with no low-hanging marks.)
            yield lastBlankLine, baseLine or y-1, y -1
            alreadyOnText = False
            baseLine = None
            countWhitePixels = None

        else:
            # moving through whitespace
            lastBlankLine = y

            


def scan_matrix(scan_width, scan_height, xy_test, space_size=3):
    """
    xy_test is a function that takes arguments (x,y)
    and returns true or false. The idea is that it
    should return True if the pixel at x,y is part
    of a character, probably by checking the color
    in an image somewhere.
    
    THIS function basically scans columns of pixels
    from left to right, top to bottom, and yields a
    number representing the bitmap whenever a vertical
    gap is found.

    So, assuming scan_height == 3 this:

    .X..X
    X...X
    .X..X

    yields: [int('010101',2) , int('111', 2)]

    Note that in In fixed width fonts, there are gaps
    between each character, but in variable width fonts,
    the characters will run together due to kerning.

    That means the bitmaps generated here may respond
    to any number of strung-together-characters, each of
    which you'll have to decipher manually.
    """

    #lines = [[] for _ in range(scan_height)]

    bitmap = 0
    charX  = 0 # x offset of the current character
    inSpace = True # we need the initial leading space
    
    for x in range(scan_width):

        hasInk = False
        spaceW = 0
        for y in range(scan_height):

            if xy_test(x,y):
                hasInk = True

                if inSpace and not spaceW:
                    spaceW = charX
                    charX = 0
                
                bitmap += 1 << (y + (charX * scan_height))

        if hasInk:                
            if spaceW > space_size:
                yield spaceW, 0 # blank bitmap (a space)
                spaceW = 0
            elif spaceW:
                yield spaceW, -1 # blank bitmap (a space)
                spaceW = 0
        else:
            if bitmap:
                yield charX, bitmap
                bitmap = 0
                charX = 0

        inSpace = not hasInk
        charX += 1


    if charX:
        if bitmap:
            yield charX, bitmap
        else:
            yield charX, 0 



## test case

import unittest
from narrative import testcase

@testcase
def testscan(self):
    testdata = '..1....11.....111'

    # the result should be width/char pairs
    # in this case the chars are just the binary numbers
    wcs = list(scan_matrix(len(testdata), 1, (lambda a,b: testdata[a] == '1'), space_size=1))
    
    self.assertEquals((2,0), wcs[0]) # 2 dots (space)
    self.assertEquals((1,1), wcs[1]) # 1 char, 1 in binary
    self.assertEquals((4,0), wcs[2])
    self.assertEquals((2,3), wcs[3]) # 2 char, 1 in binary


@testcase
def multiline(self):

    # the word For from a scan of Mentally Incontinent
    testdata = ['....................................',
                '....................................',
                '....................................',
                '.......#######......................',
                '......########......................',
                '......###...........................',
                '......###.......#####...######......',
                '......######...##..###..#####.......',
                '......#######.##....##..##..........',
                '......###.....##....###.##..........',
                '......###.....##....###.##..........',
                '......###.....##....##..##..........',
                '......###.....###...##..##..........',
                '......###......#######..##..........',
                '.......#........#####...#...........',
                '....................................',
                '....................................']
    #          0|     6|             17|1|   6|     6|

    

    fo = 11656954525901520401809650090941306687965691406109462313538109468335093405284899504112
    r  = 2475936747400903850442391488
    
    # the result should be width/char pairs
    # in this case the chars are just the binary numbers
    wcs = list(scan_matrix(len(testdata[0]), len(testdata),
                           (lambda a,b: testdata[b][a] == '#'), space_size=4))
    
    self.assertEquals((6,   0), wcs[0]) # 2 dots (space)
    self.assertEquals((17, fo), wcs[1]) # 1 char, 1 in binary
    self.assertEquals((6,   r), wcs[2])
    self.assertEquals((6,   0), wcs[3]) # 2 char, 1 in binary


if __name__=="__main__":
    unittest.main()







## font data storage #######################################

class FontData(dict):
    """
    This is just a dict-like class for storing
    font data. It stores
    """
    def __init__(self, filename=None):
        self.filename = filename
        if os.path.exists(self.filename):
            self.load(self.filename)
        else:
            self[-1]='' # init with null char (gap between letters)
            self[0]=' ' # init with space char


    def load(self, filename):
        self.filename = filename
        for line in open(self.filename).readlines():
            if line.strip() == '' or line.startswith("#"): continue
            bmp, chars = line.split("=",1)
            dict.__setitem__(self, int(bmp), chars[:-1])
        
    def __setitem__(self, bmp, chars):
        dict.__setitem__(self, bmp, chars)

        learn = open(self.filename, "a")
        print >> learn, "%s=%s" % (bmp, chars)
        learn.close()


## training ################################################

        
def matrix_from_bmp(bmp, height):
    """
    This takes one of the bitmaps returned from scan_matrix
    and renders it as a multi-line string.
    """
    lines = []
    for x in range(height):
        lines.append([])

    count = 0
    
    shrink = bmp
    while shrink:
        shrink, bit = (shrink /2), (shrink %2)
        if bit:
            lines[count % height].append("#")
        else:
            lines[count % height].append(".")
        count += 1

    # draw the baseline:
    lines.insert(-2,'-'*len(lines[1]))
    return "\n".join(["".join(line) for line in lines])


def learnNewChar(fontd, bmp, height, sofar):
    print "context: {%s}" % ''.join(sofar)
    print matrix_from_bmp(bmp, height)
    char = raw_input("what is it?")
    print "fontd[%s]=%s" % (bmp, char)
    fontd[bmp]=char
    sofar.append(char)
    return char

def learnFromImage(fontd, image):
    if not image.__class__.__name__=="Image":
        image = image.copy()
    else: pass
    h = hash(tuple(image.getdata()))
    if h in fontd:
        return fontd[h]
    else:
        image.show()
        char = raw_input("showing image. what is it?")
        print "fontd[%s]=%s" % (h, char)
        fontd[h]=char
        return char

def getchars_g(w, h, fontd, checker, train=True):
    sofar = []
    for charW, bmp in scan_matrix(w, h, checker):
        if bmp in fontd:
            sofar.append(fontd[bmp])
            yield charW, fontd[bmp]
        elif train:
            yield charW, learnNewChar(fontd, bmp, h, sofar)
        else:
            yield charW, bmp


def getstring(*a, **kw):
    return ''.join([c for w, c in getchars_g(*a, **kw)])


def getBoundedString(start, end, w, h, fontd, checker, train=True):
    """
    This is designed for capturering a solid box that
    changes width over a fixed background. To use, assign
    chars in the font to the vertical box line and (I use '|')
    and pass those chars in as the bounds
    """
    res = []
    started = False
    for w, c in getchars_g(w, h, fontd, checker, False):
        if started and c == end:
            break
        elif started:
            if type(c) in (int, long):
                if train:
                    res.append(learnNewChar(fontd, c, h))
                else: pass # ignore out of bounds data
            else:
                res.append(c)
        elif c == start:
            started = True
    return ''.join(res)

def train(filename):
    for each in glyphs(Image.open(filename).convert('L'), 200, train=True):
        print each

def recognize(filename):
    lastTop = 0
    
    for each in glyphs(Image.open(filename).convert('L'), 200, train=False):

        x, top, charW, scanH, char = each
        
        if lastTop and (top != lastTop):            
            sys.stdout.write("\n") # line break
            if top - lastTop > 20:
                sys.stdout.write("\n") # paragraph break
                
        lastTop = top

        if type(char) == str:
            sys.stdout.write(char)
        else:
            sys.stdout.write('#')





## "advanced" ocr... attempts to deal with antialiased text

def glyphs(png, cutoff, train=False):
    """
    generates (x,y, width, height, char) tuples for each glyph in an image.
    glyphs may contain several characters because this system cannot
    compensate for kerning. This doesn't really work too well yet.
    """
    for top, baseLine, bottom in lines(png.convert('1')):

        scanH = top-bottom #16 #top-bottom
        fakeTop = top #baseLine - 14
        fakeBot = bottom # baseLine + 3

        def hasInk(a,b):
            return png.getpixel((a,b+fakeTop)) < cutoff # re-alias for clarity

        w,h = png.size

        x = 0
        for charW, bmp in scan_matrix(w, scanH, hasInk):

            if bmp > 0:

                icon = iconify(png.copy().crop((x, top, x+charW, top+scanH)))
                code = icon2num(icon)

                if code in miFont:
                    char = miFont[code]
                elif train:
                    print bmp
                    print matrix_from_bmp(bmp, scanH)
                    char = raw_input("what is it?")
                    miFont[code]=char
                else:
                    char = code
                
                yield x, top, charW, scanH, char

            elif bmp == 0 and not train:
                yield x, top, charW, scanH, ' '
                
            x += charW




## normalization

"""
sometimes there can be hundreds of subtly different pixel
representations of the same characters, thanks to anti-aliasing.
This is an attempt to reduce the complexity by converting
each character to a 5x5 2-bit icon.

That still provides for 33,554,432 possible characters, but
the hope is that 
"""

def iconify(im):
    """
    converts an image to a 5x5 icon
    """
    def cutoff(pixel):
        return 255 if pixel > 240 else 0
    return Image.eval(im.resize((5,5)), cutoff).convert('1')

def icon2num(icon):
    def normalize(pixel):
        return str(pixel/255)
    return int(''.join(map(normalize, icon.getdata())),2)

