'''
Created on Aug 1, 2009

@author: michal
'''
import wx
import convert
from handy import spawn_thread
import  wx.lib.mixins.listctrl  as  listmix
from wx.py.shell import Shell
import ImageDraw
from pprint import pformat

class ProfileList(wx.ListCtrl, 
                  listmix.ListCtrlAutoWidthMixin,
                  listmix.TextEditMixin):

    def __init__(self, *a, **kw):
        wx.ListCtrl.__init__(self, *a, **kw)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.TextEditMixin.__init__(self)

        self.InsertColumn(0, "region")
        self.InsertColumn(1, "value")
        self.InsertColumn(2, "position")
        self.InsertColumn(3, "size")
        self.InsertColumn(4, "font")
        self.InsertColumn(5, "expr")

class Region(object):
    def __init__(self, value, position, size, font, expr):
        self.value = value
        self.position = position
        self.size = size
        self.font = font
        self.expr = expr
    def slots(self):
        return ("value","position","size","font","expr")

class Profile(dict):
    def __init__(self, name, size):
        self.name = name
        self.size = size
                    

class ProfileWindow(wx.Frame):
    def __init__(self, *a, **kw):
        super(ProfileWindow, self).__init__(*a, **kw)        
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.regions = []
            
        newRegionButton = wx.Button(self, -1, "add region")
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.list, 0, wx.EXPAND)
        box.Add(newRegionButton)
        
        self.SetSizerAndFit(box)
        


class ProfileBuilder(wx.Frame):
    """
    Interactively build a scraping profile.
    """
    def __init__(self, scrapefile, win, parent=None, *a, **kw):
        super(ProfileBuilder, self).__init__(parent, *a, **kw) 
        
        
        self.SetTitle("profile builder: %s" % scrapefile)
        self.win = win
        self.bmp = wx.StaticBitmap(self, size=(win.size))
        self.shell = Shell(self)
        self.profileName = wx.StaticText(self, -1, scrapefile)
        self.scrapefile = scrapefile
        
  
        
        self.reload_profile()

        self.refresh = wx.Button(self, wx.NewId(), "refresh")
        self.refresh.Bind(wx.EVT_BUTTON, self.on_refresh_button)

        self.hwnd = wx.TextCtrl(self, -1, str(win.hwnd))
                
        self.layout()
        self.updateImage()
        self.Show()
        
        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.on_tick)
        self.timer.Start(500, wx.TIMER_CONTINUOUS)


    def layout(self):
        "Arranges the controls inside the window."
        box = wx.BoxSizer(wx.VERTICAL)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.profileName)
        row.Add(self.refresh)
        row.AddSpacer(20)
        row.Add(wx.StaticText(self, -1, "hwnd:"))
        row.Add(self.hwnd)
        box.Add(row)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.bmp, 0, wx.EXPAND)
        box.Add(row, 0, wx.EXPAND)
        self.shell.SetSizeHints(500,-1)
        box.Add(self.shell, 1, wx.EXPAND)
        self.SetSizerAndFit(box)


        
    def draw_boxes(self):
        """
        this is a debug function that draws boxes on the
        screen grab for each of the text input areas
        """
        draw = ImageDraw.Draw(self.img)
        for value, position, size, font, color in self.profile:
            x,y = position
            w,h = size
            draw.rectangle([(x,y), (x+w, y+h)], outline=color)        
        
    def on_refresh_button(self, e):
        self.reload_profile()
        self.updateImage()
        
    def reload_profile(self):
        self.profile=eval(open(self.scrapefile).read())
        self.shell.clear()
        self.shell.AppendText(pformat(self.profile))

    def updateImage(self):
        self.img = self.win.as_image()
        self.draw_boxes()
        self.bmp.SetBitmap(convert.pilToBitmap(self.img))
        self.Fit()
        self.Refresh()


    def on_tick(self, e):
        self.on_refresh_button(e)
