"""
This contains the basic algorithms for scraping text from images.
"""
import sys
import Image

#@TODO: remove these constants. Let Chunker infer by glyph coordinates    
NEW_GLYPH = 0
SPACE = -1


#:: img -> gen [ (top, baseline, bottom) ]
def lines(img):
    """
    this yields a sequence of top,baseline,bottom y pixels for the image
    """
    assert img.mode in ('1','L'), 'must be grayscale for now'
    w,h = img.size

    lastBlankLine = 0
    alreadyOnText = False
    lastCount = 0
    baseLine = None

    for y in range(h):

        countDarks = w - img.transform((w,1), Image.EXTENT, 
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



#:: img:Image -> ink_p:(x:int -> y:int -> bool) -> [glyph]
def glyphs_from_line(img, pred):
    """
    This is the new interface I want to use.
    @TODO: better yet, drop img and just use ink_p:pred
    """
    (w, h) = img.size
    return scan_line(w, h, pred)


    
    
#:: w:int, h:int, pred:(x->y->bool) ->  gen [(bitmap_number, width)]
def scan_line(w, h, pred, space_size=3):
    """
    @TODO: remove w and h
    
    @param pred: a function that takes arguments (x,y)
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

    bitmap = 0
    charX  = 0 # x offset of the current character
    inSpace = True # we need the initial leading space
    
    for x in range(w):

        hasInk = False
        spaceW = 0
        for y in range(h):

            if pred(x,y):
                hasInk = True

                if inSpace and not spaceW:
                    spaceW = charX
                    charX = 0
                
                bitmap += 1 << (y + (charX * h))

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




#:: int -> int -> FontData -> pred -> &bool -> gen (int, glyph_as_int)
def getchars_g(w, h, fontd, pred, train=True):
    """
    yields glints
    """
    for charW, glint in scan_line(w, h, pred):
        yield charW, fontd[glint]




#:: int -> int -> FontData -> pred -> bool -> str
def getstring(w, h, fontd, pred, train):
    """
    
    """
    return ''.join([c for w, c in 
                    getchars_g(w, h, fontd, pred, train)])


    

#:: char -> char -> int -> int -> FontData -> pred -> bool 
def getBoundedString(start, end, width, height, fontd, pred, train=True):
    """
    This is designed for capturing a solid box that
    changes width over a fixed background. To use, assign
    chars in the font to the vertical box line and (I use '|')
    and pass those chars in as the bounds
    
    @TODO: locate box with flood fill, then use normal getstring 
    """
    res = []
    started = False
    for w, c in getchars_g(width, height, fontd, pred, False):
        if started and c == end:
            break
        elif started:
            res.append(c)
            return ''.join(res)
        elif c == start:
            started = True
