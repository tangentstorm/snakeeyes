"""
Created on Aug 1, 2009

@author: michal
"""
import wx
from snakeeyes import convert


class GlyphDialog(wx.Dialog):
    """
    Prompts you for the string associated with a glyph.
    """
    def __init__(self, wx_bmp, *a, **kw):
        super(GlyphDialog, self).__init__(*a, **kw)

        self.bmp = wx.StaticBitmap(self, -1, wx_bmp)

        ok = wx.Button(self, wx.ID_OK)
        cancel = wx.Button(self, wx.ID_CANCEL)

        self.txt = wx.TextCtrl(self, -1)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.bmp)
        box.Add(wx.StaticText(self, -1, "what the hell is it?"))
        box.Add(self.txt)                
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(ok)
        row.Add(cancel)
        box.Add(row)
        self.SetSizerAndFit(box)

        self.txt.SetFocus()

        # parent can set this to whatever they want:
        self.when_done = lambda me, res: None
        ok.Bind(wx.EVT_BUTTON, self.on_ok)
        cancel.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_ok(self, _evt):
        self.Hide()
        self.when_done(self, wx.ID_OK)

    def on_cancel(self, _evt):
        self.Hide()
        self.when_done(self, wx.ID_CANCEL)
