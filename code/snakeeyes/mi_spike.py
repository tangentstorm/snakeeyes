"""
This is some old code I was using one day when I
was trying to recover the text of Mentally Incontinent
from an image. (Mostly for my own amusement, though I
think Joe was actually having some problem at the time.)

The main advantage here is that it "sort of" recognizes
anti-aliased text.
"""
from .scrape import guess_lines, scan_line
from . import convert
from PIL import Image


#:: img -> font -> int -> bool -> gen [(x, y, w, h, glyph_as_int ) ]
def glyphs(img, font, cutoff=1, train=False):
    """
    This is slightly more "advanced" OCR that I used
    when trying to re-assemble joe's  book

    It attempts to deal with anti-aliased text.

    However, the method it uses is rather silly.

    generates (x,y, width, height, char) tuples for each glyph in an image.
    glyphs may contain several characters because this system cannot
    compensate for ligatures/kerning. This doesn't really
    work too well yet.
    """
    for top, baseLine, bottom in guess_lines(img.convert('1')):

        scanH = top-bottom #16 #top-bottom
        fakeTop = top #baseLine - 14
        fakeBot = bottom # baseLine + 3

        def hasInk(a, b):
            return img.getpixel((a,b+fakeTop)) <= cutoff # re-alias for clarity

        w,h = img.size

        x = 0
        for charW, bmp in scan_line(w, scanH, hasInk):

            if bmp > 0:

                icon = iconify(img.copy().crop((x, top, x+charW, top+scanH)))
                code = icon2num(icon)

                if code in font:
                    char = font[code]
                elif train:
                    print(bmp)
                    print(convert.glint_to_strings(bmp, scanH))
                    char = input("what is it?")
                    font[code]=char
                else:
                    char = code

                yield x, top, charW, scanH, char

            elif bmp == 0 and not train:
                yield x, top, charW, scanH, ' '

            x += charW


#:: string -> IO ()
def recognize(filename):
    """
    dumps the text from an image to stdout
    """
    import sys

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





#:: img -> img
def iconify(im):
    """
    sometimes there can be hundreds of subtly different pixel
    representations of the same characters, thanks to anti-aliasing.
    This is an attempt to reduce the complexity by converting
    each character to a 5x5 2-bit icon.

    ( Not an entirely awful idea, but only a first step.
      What you really want to do is map this to a vector
      search engine. )

    """
    def cutoff(pixel):
        return 255 if pixel > 240 else 0
    return Image.eval(im.resize((5, 5)), cutoff).convert('1')


#:: img -> glint
def icon2num(icon):
    def normalize(pixel):
        return str(pixel/255)
    return int(''.join(map(normalize, icon.getdata())),2)




