"""
Various conversion routines.

Some of these are based on code from:

   http://wiki.wxpython.org/index.cgi/WorkingWithImages
"""
import wx
from PIL import Image

def img_to_wxbmp(pil):
    """:: Image.Image -> wx.Bitmap"""
    return wximg_to_wxbmp(img_to_wximg(pil))

def img_to_wximg(pil):
    """:: Image.Image -> wx.Image"""
    image = wx.EmptyImage(pil.size[0], pil.size[1])
    image.SetData(pil.convert('RGB').tostring())
    return image

def wximg_to_wxbmp(image):
    """:: wx.Image -> wx.Bitmap"""
    return image.ConvertToBitmap()


## these are mine:

def strings_to_img(strings):
    """[ String ] -> Image.Image"""
    height = len(strings)
    img = Image.new('1', (len(strings[0]), height))
    for y, line in enumerate(strings):
        for x, char in enumerate(line):
            img.putpixel((x, y), 1 if char=="#" else 0)
    return img



# type Glint = Int       -- glint means "glyph int"
#:: Int -> Int -> Int -> Glint
def pixel_to_glint(x, y, img_height):
    """
    Returns a big long binary number with only one bit turned on.
    Glint means 'glyph integer'.
    
    Basically, we want every (x, y) location to map to a number
    between 0 and n-1, where n is the number of pixels in the 
    image. Or in other words, n = w * h
    
    Given such a mapping, we can convert any coordinate on the 
    image to a position on a line. Since each pixel in the image
    is either on or off, we can think of each pixel as a bit,
    and then our mapping is from x,y coordinates to position in
    a line of bits.
    
    If we have a line of bits, we can pretend it's a binary 
    number. If we number the line starting at the right, then
    to set the nth bit in our bitmap, we just add 2^n.

    So, all we need is a mapping scheme, and the easiest way is
    just do something like this:
    """
    n = y + (x * img_height)
    
    # Now we just take a single bit (the number 1)
    # and stick n zeros after it. This is another
    # way of saying "multiply by (2 ^ n)".
    bitmap = 1 << n  # == 2 ** n
    
    # The resulting bitmap represents a single pixel. To combine
    # two bitmaps, you can just OR them. (Which in our case,
    # corresponds to adding them.)
    #
    # The main problem with this encoding scheme, unfortunately,
    # is that I didn't leave space in the bitmap to record the
    # height of the original image, so you have to remember that
    # height elsewhere if you ever want to turn the bitmap back
    # into an image!
    #
    # It's much easier to just store the original image as a
    # string anyway. :)
    return bitmap


#:: Glint -> [String]
def glint_to_strings(glint, height):
    """
    The only problem with this is that you have to
    know the height of the original image, and I 
    never recorded that in the old font files I made!

    There's not much use for this anyway, except in 
    the function above. Once Glyph works right we should
    be able to toss glints entirely and this will go away.
    
    I probably won't need those old font files, and even if I do,
    I should probably rebuild them with the new Image
    based GUI tools.
    """
    lines = []
    for x in range(height):
        lines.append([])

    count = 0
    
    shrink = glint
    while shrink:
        shrink, bit = (shrink /2), (shrink %2)
        if bit:
            lines[count % height].append("#")
        else:
            lines[count % height].append(".")
        count += 1

    # draw the baseline:
    lines.insert(-2,'-'*len(lines[0]))
    return "\n".join(["".join(line) for line in lines])


#:: Glint -> Int -> Image
def glint_to_img(glint, width, height):
    img = Image.new('1', (width, height), 1)
    for x in range(width):
        for y in range(height):
            test = pixel_to_glint(x, y, height)
            if test > glint:
                break # last column, no more bits 
            elif test & glint:
                img.putpixel((x, y), 0)
    return img
