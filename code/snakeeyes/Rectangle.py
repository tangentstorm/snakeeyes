
class Rectangle(object):
    """
    A simple data class.
    """
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
    
    def far_corner(self):
        """:: self -> (right, bottom)"""
        _, _, right, bottom = self.as_quad()
        return tuple([right, bottom])
    
    def as_quad(self):
        """:: self -> (left, top, right, bottom)"""
        left, top = self.pos
        width, height = self.size
        return tuple([left, top, left + width, top + height])

    @property
    def center(self):
        x, y = self.pos
        w, h = self.size
        return tuple([int(x + w / 2), int(y + h / 2)])
