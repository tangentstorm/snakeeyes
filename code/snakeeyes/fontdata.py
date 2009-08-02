import os
import shelve

SPACE_GLYPH = 0
NULL_GLYPH = -1


class NeedTraining(Exception):
    def __init__(self, font, glyph):
        super(NeedTraining, self).__init__()
        self.font = font
        self.glyph = glyph

class FontData(object):
    """
    A dictionary mapping glyphs (bitmaps for individual symbols)
    to strings characters. Essentially, the converse of a bitmap font.
    """
    def __init__(self, dict):
        self.data = dict
        self.training_mode = False
        
    def contains(self, glyph):
        return self.data.has_key(glyph.tostring())
    
    def learn(self, glyph, value):
        self.data[glyph.tostring()] = value
        
    def recall(self, glyph):
        try:
            return self.data[glyph.tostring()]
        except KeyError:
            if self.training_mode:
                raise NeedTraining(font=self, glyph=glyph)
            else:
                pass



class OldFontData(dict):
    """
    This is just a dict-like class for storing
    the glyphs for a font in a simple file format.
    """
    def __init__(self, filename=None):
        super(OldFontData, self).__init__()
        
        self.filename = filename
        if os.path.exists(self.filename):
            self.load(self.filename)
        else:
            # create an empty font:
            self[NULL_GLYPH] = ''
            self[SPACE_GLYPH]  = ' '
            
    def load(self, filename):
        """
        Loads the glyphs into memory from a text file.
        This class remembers the filename and will keep
        it updated as you teach it about new glyphs.
        """
        self.filename = filename
        for line in open(self.filename).readlines():

            # some of the old fontd files have comments:
            if line.strip() == '' or line.startswith("#"):
                continue
            
            gbmp_string, chars = line.split("=", 1)
            gbmp = (hex(gbmp_string) if gbmp_string.startswith('0x') 
                    else int(gbmp_string))
            
            dict.__setitem__(self, gbmp, chars[:-1])
        
    def __setitem__(self, gbmp, chars):
        """
        saves to disk as you update the data
        """
        dict.__setitem__(self, gbmp, chars)
        learn = open(self.filename, "a")
        learn.write("%s=%s" % (hex(gbmp), chars))
        learn.close()

