"""
Created on Jul 31, 2009

@author: michal
"""
import win32gui, win32ui
from PIL import Image, ImageGrab
from win32gui import GetWindowRect, GetClientRect, ClientToScreen, MoveWindow
from ctypes import windll


class Window(object):
    """
    A wrapper around the win32 hwnd API
    """
    def __init__(self, hwnd):
        self.hwnd = hwnd
        
    @property
    def text(self):
        """
        generally corresponds to the title
        but also applies to labels, etc
        """
        return win32gui.GetWindowText(self.hwnd)
    
    @property
    def size(self):
        """
        Note: this returns the CLIENT size (the drawable area)
        """
        left, top, right, bottom = self.bounds
        return tuple([right-left, bottom-top])
        
    @property
    def bounds(self):
        """"
        returns (left, top, right, bottom) of client area
        in screen coordinates
        """
        (cl, ct, cr, cb) = GetClientRect(self.hwnd)
        (sl, st) = ClientToScreen(self.hwnd, (cl, ct))
        (sr, sb) = ClientToScreen(self.hwnd, (cr, cb))
        return tuple([sl, st, sr, sb])

    @property
    def width(self):
        x, y, x2, y2 = GetWindowRect(self.hwnd)
        return x2-x
        
    @property
    def height(self):
        x, y, x2, y2 = GetWindowRect(self.hwnd)
        return y2 - y

    @property
    def position(self):
        x, y, x2, y2 = GetWindowRect(self.hwnd)
        return tuple([x, y])

    def as_image_simple(self):
        """
        This uses ImageGrab to return a screenshot, but it only works
        when the image is visible onscreen.
        @return: Image.Image
        """
        return ImageGrab.grab(self.bounds)

    def _make_dc(self):
        """Creates a Win32 drawing context"""
        # this would be a property except we have to manually manage
        # the garbage collection on this thing.
        # this is used by as_image
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        return win32ui.CreateDCFromHandle(self.hwndDC)

    def as_image(self):
        """
        This returns a screenshot of the window, and should work even
        when the window is not visible on the screen, i.e., positioned
        offscreen, or obscured by another window.

        (Does not appear to work for minimized windows, though -
        it just returns a blank image.)

        @return: Image.Image
        """
        # technique taken from:
        # http://stackoverflow.com/questions/19695214
        self_dc = self._make_dc()
        save_dc = self_dc.CreateCompatibleDC()
        save_bmp = win32ui.CreateBitmap()
        save_bmp.CreateCompatibleBitmap(self_dc, self.width, self.height)
        save_dc.SelectObject(save_bmp)

        # 0=whole window, 1=client area
        windll.user32.PrintWindow(self.hwnd, save_dc.GetSafeHdc(), 1)

        bmp_info = save_bmp.GetInfo()
        bmp_bits = save_bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB',
                               (bmp_info['bmWidth'], bmp_info['bmHeight']),
                               bmp_bits, 'raw', 'BGRX', 0, 1)

        win32gui.DeleteObject(save_bmp.GetHandle())
        save_dc.DeleteDC()
        self_dc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)
        return img

    def bring_to_front(self):
        win32gui.SetForegroundWindow(self.hwnd)
        
    def move_to(self, x, y):
        MoveWindow(self.hwnd, x, y, self.width, self.height, True)

    def resize_client(self, w, h):
        cx1, cy1, cx2, cy2 = GetClientRect(self.hwnd)
        wx1, wy1, wx2, wy2 = GetWindowRect(self.hwnd)
        dx = (wx2 - wx1) - cx2
        dy = (wy2 - wy1) - cy2
        MoveWindow(self.hwnd, wx1, wy1, w+dx, h+dy, True)

    def grab_pixel(self, x, y):
        """ x,y -> (r,g,b) """
        win = win32ui.CreateWindowFromHandle(self.hwnd)
        dc = win.GetWindowDC()
        px = hex(dc.GetPixel(x, y))
    
        # @TODO: just do the math :)
        # note that the values are "backwards" from rgb
        if len(px) < 4: px += ("0" * (8-len(px)))
        b = int(px[2:4], 16)
        g = int(px[4:6], 16)
        r = int(px[6:8], 16)
        
        return tuple([r, g, b])


def all_hwnds(condition=lambda a: True):
    """
    returns a list containing hwnds for all open windows
    """
    res = []

    def keep(hwnd, _extra):
        if condition(hwnd):
            res.append(hwnd) 

    win32gui.EnumWindows(keep, None)
    return res
    

def all_windows():
    """Returns a list of Window objects"""
    return [Window(hwnd) for hwnd in all_hwnds()]
    

def where(condition):
    cond = condition if condition else lambda a: True
    return [win for win in all_windows() if cond(win)]


def named(txt):
    return where(lambda win: win.text.count(txt))


def grab_pixel(hwnd, xy: (int, int)):
    return Window(hwnd).grab_pixel(*xy)
