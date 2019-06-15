'''
Created on Aug 1, 2009

@author: michal
'''
import wx
import sys
import wx.lib.mixins.listctrl  as  listmix
from snakeeyes.fontdata import FontData

class FontDataCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    """
    A ListCtrl that shows data from the scrape.
    """
    def __init__(self, fontData, *a, **kw):
        wx.ListCtrl.__init__(self,
                          #   style = wx.LC_REPORT
                          #         | wx.LC_SORT_ASCENDING,
                             *a, **kw)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, "glyph")
        self.InsertColumn(1, "value")

        self.fontData = fontData
        self.repopulate()

    def repopulate(self):
        self.DeleteAllItems()
        for gbmp, chars in self.fontData.items():
            if chars.strip(): # my test font had lots of whitespace saved
                item = self.InsertStringItem(sys.maxsize, chars)



class FontDataFrame(wx.Frame):
    '''
    shows a list of glyphs and their associated values for a font
    '''
    def __init__(self, fontData, *a, **kw):
        super(FontDataFrame, self).__init__(*a, **kw)
        self.SetLabel("font data for file: %s" % fontData.filename)

        refreshButton = wx.Button(self, -1, "refresh")
        refreshButton.Bind(wx.EVT_BUTTON, self.on_refresh_button)

        self.ctrl = FontDataCtrl(fontData, self)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.ctrl, 1, wx.EXPAND)
        box.Add(refreshButton)

        self.SetSizerAndFit(box)

    def on_refresh_button(self, e):
        self.ctrl.repopulate()

if __name__ == "__main__":
    app = wx.App(redirect=False)
    font = FontData('test.fontd')
    win = FontDataFrame(font, None)
    win.Show()
    app.MainLoop()
