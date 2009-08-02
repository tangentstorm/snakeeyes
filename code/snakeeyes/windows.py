"""
Created on Jul 31, 2009

@author: michal
"""
import win32gui, win32ui
import ImageGrab
import re
from win32gui import GetWindowRect, GetClientRect, ClientToScreen

class Window(object):
    """
    A wrapper around the win32 hwnd API
    """
    def __init__(self, hwnd):
        self.hwnd = hwnd
        
    @property
    def text(self):
        return win32gui.GetWindowText(self.hwnd)
    
    @property
    def size(self):
        """
        Note: this returns the CLIENT size (the drawable area)
        """
        left, top, right, bottom = self.bounds
        return (right-left, bottom-top)
        
    @property
    def bounds(self):
        """"
        returns (left, top, right, bottom) of client area
        in screen coordinates
        """
        (cl, ct, cr, cb) = GetClientRect(self.hwnd)
        (sl, st) = ClientToScreen(self.hwnd, (cl, ct))
        (sr, sb) = ClientToScreen(self.hwnd, (cr, cb))
        return (sl, st, sr, sb)
    
    def as_image(self):
        return ImageGrab.grab(self.bounds)

    def bringToFront(self):
        win32gui.SetForegroundWindow(self.hwnd)


def all_hwnds(condition=lambda a:True):
    """
    returns a list containing hwnds for all open windows
    """
    res = []
    def keep(hwnd, extra):
        if condition(hwnd):
            res.append(hwnd) 
    win32gui.EnumWindows(keep, None)
    return res
    
def all():
    "Returns a list of Window objects"
    return [Window(hwnd) for hwnd in all_hwnds()]
    
def where(condition):
    cond = condition if condition else lambda a: True
    return [win for win in all() if cond(win)]



class WindowTree(object):
    """
    """
    def __init__(self, *args):
        '''
        Constructor
        '''
        