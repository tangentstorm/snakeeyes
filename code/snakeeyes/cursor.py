"""
These classes represent a cursor that can navigate back and forth in a list.
It's used in snakeeyes.gui.pngscraper for navigating between images in a list.
"""

class Cursor(object):

    def __init__(self, view):
        self.view = view
        self.moveToTop()

    def moveToTop(self):
        self.position = self.view.indexFirst()

    def moveToBottom(self):
        self.position = self.view.indexLast()

    def moveUp(self):
        try:
            self.position = self.view.indexPrevious(self.position)
        except LookupError:
            pass

    def moveDown(self):
        try:
            self.position = self.view.indexNext(self.position)
        except LookupError:
            pass


    # or if you prefer a non-spatial metaphor:
    def moveNext(self): self.moveDown()
    def movePrevious(self): self.moveUp()
    def moveToStart(self): self.moveToTop()
    def moveToEnd(self): self.moveToBottom()


    def value(self):
        return self.view[self.position]



class ListView(object):

    def __init__(self, data):
        self.data = data
        self.zoomed = False

    def indexFirst(self):
        return self.indexNext(-1)

    def indexLast(self):
        return self.indexPrevious(len(self.data))

    def isVisible(self, i):
        return True

    def __getitem__(self, key):
        return self.data[key]

    ## cursor interface

    def indexNext(self, index):
        for next in range( index +1, len(self.data)):
            if self.isVisible(next): return next
        return index

    def indexPrevious(self, index):
        for next in range(index - 1, -1, -1):
            if self.isVisible(next): return next
        return index
