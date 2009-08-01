"""
Created on Jul 31, 2009

@author: michal
"""
import win32gui, win32ui
import ImageGrab
import re

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
        left, top, right, bottom = self.bounds
        return (right-left, bottom-top)
        
    @property
    def bounds(self):
        "returns (left, top, right, bottom)"    
        return win32gui.GetWindowRect(self.hwnd)
    
    def as_image(self):
        return ImageGrab.grab(self.bounds)



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
        