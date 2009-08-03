
class Rectangle(object):
    """
    """
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
    
    def far_corner(self):
        left, top, right, bottom = self.as_quad()
        return (right, bottom)
    
    def as_quad(self):
        left, top = self.pos
        width, height = self.size
        return (left, top, left + width, top + height)

  