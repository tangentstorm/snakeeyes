"""
This contains the basic algorithms for scraping text from images.
"""
from Glyph import Glyph
import convert
import Image


def count_black_pixels_on_row(img, y):
    w, h = img.size
    #@TODO: replace next line with proper img.crop()
    #row_img = img.transform((w, 1), Image.EXTENT, (0, y, w, y + 1))
    row_img = img.crop((0, y, w, y + 1))
    return w - row_img.histogram()[-1]

#:: img -> gen [ (top, baseline, bottom) ]
def lines(img):
    """
    this yields a sequence of top,baseline,bottom y pixels for the image
    """
    assert img.mode in ('1','L'), 'must be grayscale for now'
    w, h = img.size

    last_empty_row = 0
    on_text = False
    ink_in_previous = 0
    baseline = None
    
    for y in range(h):

        ink_in_row = float(count_black_pixels_on_row(img, y))

        if ink_in_row > 0: # then there are some dark pixels

            if on_text:
                # if there's a 40% drop in pixels from one row to the next
                # across a line of text, chances are pretty good that we
                # found the baseline.
                # 1.7 == 1/.58  ... it's upside down to avoid dividing by zero 
                # (and also because I thought of it the other way around before)
                if (ink_in_previous / ink_in_row > 1.7) and baseline is None:
                    baseline = y
            else:
                on_text = True

            ink_in_previous = ink_in_row

        elif on_text: # was on text, now no ink, so..

            # if we haven't found the baseline yet, then this IS the
            # baseline. (Happens on lines with no low-hanging marks.)
            yield last_empty_row, baseline or y-1, y -1
            on_text = False
            baseline = None

        else:
            # moving through whitespace
            last_empty_row = y



#:: img:Image -> ink_p:(x:int -> y:int -> bool) -> [(width, glint)]
def glyphs_from_line(img, pred):
    """
    This is the new interface I want to use.
    @TODO: better yet, drop img and just use ink_p:pred
    """
    (w, h) = img.size
    for glyph in scan_line(w, h, pred):
        glyph.img = convert.glint_to_img(glyph.glint, *glyph.size)
        assert glyph.img.size == glyph.size
        yield glyph

    
IN_SPACE = 0
IN_GLYPH = 1
    
#:: w:int, h:int, pred:(x->y->bool) ->  gen [(width, glint)]
def scan_line(img_width, img_height, pred):
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
        
    Would anything really change if the language were not
    left-to right? Not in here. We could do a transformation
    on the incoming image and everything should work fine.

    So, assuming scan_height == 3 this:

    .#..#
    ##..#
    .#..#

    yields two glyphs.

    Note that in variable width fonts, characters may 
    run together due to kerning.

    That means the glyphs generated here may respond
    to any number of characters. At the moment, you'll
    have to train each possible combination manually.
    """

    glint = 0
    
    state = IN_SPACE
    since_x = 0

    for x in range(img_width):

        # scan all pixels in the column
        column_has_ink = False
        for y in range(img_height):

            if pred(x,y):
                column_has_ink = True # reaffirmed for every dark pixel in column
                 
                if (state==IN_SPACE):
                    state = IN_GLYPH
                    since_x = x
                    glint |= convert.pixel_to_glint(0, y, img_height)
                else:
                    glyph_w = x - since_x
                    glint |= convert.pixel_to_glint(glyph_w, y, img_height)

        if state == IN_GLYPH and (not column_has_ink):
            # we have passed through the rightmost side of the
            # glyph and encountered a column of whitespace.
            yield Glyph((since_x, 0), (x - since_x, img_height), glint)
            glint = 0

            # now that we've reported on the width, we can reset the column:
            state = IN_SPACE
            since_x = x

    # We've reached the right edge of the image.
    # We could still be in the middle of a glyph!
    if state==IN_GLYPH:
        yield Glyph((since_x, 0), (x + 1 - since_x, img_height), glint)




#:: int -> int -> FontData -> pred -> gen (int, glyph_as_int)
def getchars_g(w, h, fontd, pred):
    """
    yields glints
    """
    for charW, glint in scan_line(w, h, pred):
        yield charW, fontd[glint]




#:: int -> int -> FontData -> pred -> bool -> str
def getstring(w, h, fontd, pred):
    """
    
    """
    return ''.join([c for (w, c) in 
                    getchars_g(w, h, fontd, pred)])




#:: Image.Image -> FontData -> pred -> String
def str_from_img(img, fontd, pred):
    # for now...
    return "".join( fontd.recall( glyph ) 
                    for glyph in glyphs_from_line(img, pred) )

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
