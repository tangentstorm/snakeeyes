"""
This is an interactive GUI for building scrape regions
"""
import wx
from wxhelpers import menu, menuBar


class ScrapeMaker(wx.Frame):
    def init(self):
        self.SetMenuBar(self.makeMenu())
        self.screenShot()

    def makeMenu(self):
        return menuBar(
            ("&File", menu("&Open")))


if __name__=="__main__":
    app = wx.App(redirect=False)
    win = ScrapeMaker(None, pos=(820,0), size=(1024,768))
    win.init()
    win.Show()
    app.MainLoop()
