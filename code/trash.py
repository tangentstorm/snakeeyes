"""
putting my old trash code here as i go along.
will 
"""

#:: ... -> IO()
def learnFromImage(fontd, image):
    """
    This just called img.show() and prompted you for the text.
    (obsolete now thanks to gui.GlyphWindow)
    """
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


#:: ... -> IO ()
def learnNewChar(fontd, bmp, height, sofar):
    "another console-based prompt"
    print "context: {%s}" % ''.join(sofar)
    #print glint_to_strings(bmp, height)
    char = raw_input("what is it?")
    print "fontd[%s]=%s" % (bmp, char)
    fontd[bmp]=char
    sofar.append(char)
    return char




