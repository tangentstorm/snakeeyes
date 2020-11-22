"""
GUI App to navigate through a list (directory) of screenshots for debugging the scraping tool.
"""
import os
import wx
import wx.py as py
from PIL import Image
from wx import xrc
from wx.xrc import XRCID, XRCCTRL

from snakeeyes.cursor import Cursor, ListView
from snakeeyes import scrape

ID_OPEN_FILE = wx.NewIdRef()
ID_OPEN_DIR = wx.NewIdRef()


def png_list(path):
    pngs = [f for f in os.listdir(path) if f[-4:] == ".png"]
    return [os.path.join(path, f) for f in pngs]


class PngScraperFrame(wx.Frame):
    """
    Frame for browsing through a list/directory of images, running a script on each.
    """

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.im: Image.Image = None
        self.pngs = []
        self.cursor = Cursor(ListView(self.pngs))
        self.coords: wx.TextCtrl = None
        self.color:  wx.TextCtrl = None
        self.scroll: wx.ScrolledWindow = None
        self.image: wx.Image = None
        self.which: wx.TextCtrl = None
        self.locals = {}
        self.shell: py.shell.Shell = None

    def init(self):
        self.coords = XRCCTRL(self, 'txt_coords')
        self.color = XRCCTRL(self, 'txt_color')
        self.scroll = XRCCTRL(self, 'box_scroll')

        self.image = XRCCTRL(self, 'bmp_image')
        self.image.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.image.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        #self.update_image()

        self.which = XRCCTRL(self, 'txt_which')
        self.update_which()

        # button handlers
        for btn in 'btn_first btn_prev btn_next btn_last'.split():
            self.Bind(wx.EVT_BUTTON, self.on_cursor_button, id=XRCID(btn))

        # menu handlers
        self.Bind(wx.EVT_MENU, self.on_exit, id=XRCID('cmd_exit'))
        self.Bind(wx.EVT_MENU, self.on_open_file, id=XRCID('cmd_open_file'))
        self.Bind(wx.EVT_MENU, self.on_open_dir, id=XRCID('cmd_open_dir'))
        self.Bind(wx.EVT_CLOSE, self.on_close_window)

        # -- manually add pyshell
        panel = XRCCTRL(self, 'shell_panel')

        self.locals = {'self': self, 'wx': wx, 'hook': lambda: None, 'gc': self.get_dc()}
        self.shell = py.shell.Shell(panel, locals=self.locals)

        sizer = wx.BoxSizer()
        sizer.Add(self.shell, 4, wx.EXPAND)
        self.shell.SetFocus()
        panel.SetSizer(sizer)
        sizer.Fit(panel)

    def on_cursor_button(self, evt):
        button_map = {
            "<<": "moveToStart",
            "<": "movePrevious",
            ">": "moveNext",
            ">>": "moveToEnd"}
        try:
            getattr(self.cursor, button_map[evt.GetEventObject().Label])()
            self.update_which()
            self.update_image()
            self.shell.run('hook()')
        except StopIteration:
            pass

    def on_open_file(self, _evt):
        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(),
            defaultFile="", wildcard='*.png',
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.pngs.insert(self.cursor.position, path)
            self.update_which()
            self.update_image()

    def on_open_dir(self, _evt):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           defaultPath=os.getcwd(),
                           style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            while self.pngs:
                self.pngs.pop()
            self.pngs.extend(png_list(path))
            self.cursor.moveToStart()
            self.update_which()
            self.update_image()
            self.shell.run('hook()')

    def on_exit(self, _evt):
        self.Close()

    def update_which(self):
        self.which.Value = "%s/%s" % (self.cursor.position, len(self.pngs))

    def update_image(self):

        if len(self.pngs):
            # set the visible bitmap
            img = wx.Image(self.pngs[self.cursor.position], wx.BITMAP_TYPE_PNG)
            self.image.SetBitmap(wx.Bitmap(img))

            self.scroll.SetVirtualSize(self.image.Size)

            # and make the pil image
            self.im = Image.new('RGB', tuple(self.image.Size))
            self.im.frombytes(bytes(self.image.GetBitmap().ConvertToImage().GetData()))

    def on_right_down(self, _e):
        self.image.Refresh()

    def on_left_down(self, e):
        point = (e.X, e.Y)
        self.coords.Value = "(%s,%s)" % point
        self.color.Value = "0x%s" % "".join(hex(v)[2:].upper()
                                            for v in self.im.getpixel(point))

        # draw crosshairs:
        dc = wx.ClientDC(self.image)
        dc.SetPen(wx.Pen("RED"))
        dc.DrawLine(e.X-2, e.Y, e.X, e.Y)
        dc.DrawLine(e.X, e.Y-2, e.X, e.Y)
        dc.DrawLine(e.X+2, e.Y, e.X, e.Y)
        dc.DrawLine(e.X, e.Y+2, e.X, e.Y)

    def get_dc(self):
        """return the client drawing context"""
        gc = wx.GCDC(wx.ClientDC(self.image))
        ink = wx.Colour(0x99, 0xcc, 0xff, 0x88)
        gc.SetPen(wx.Pen(ink))
        gc.SetBrush(wx.Brush(ink))
        return gc

    def draw_words(self):
        # @TODO: re-enable draw_words. it was cool. :)
        raise NotImplementedError

#        chars = self.chars()
#        inks = wx.Color(0x99, 0xcc, 0xff, 0x88) , wx.Color(0x99, 0xff, 0xcc, 0x88)
#
#        gc = self.getGC()
#
#        i = 0
#        for c in chars:
#            if c[4] not in ('', ' '):
#
#                ink = inks[i % 2]
#                i += 1
#
#                gc.SetPen(wx.Pen(ink))
#                gc.SetBrush(wx.Brush(ink))
#
#                gc.DrawRectangle(*c[:4])

#    def drawFirstUnkowns(self, cutoff=200, mode='L'):
#        "I *THINK* this was to show a new char to learn in context."
#        chars = self.chars(mode, cutoff)
#
#        seen = {}
#
#        gc = self.getGC()
#        ink = wx.Color(0xff, 0x00, 0x00, 0x88)
#        gc.SetPen(wx.Pen(ink))
#        gc.SetBrush(wx.Brush(ink))
#
#        i = 0
#        for c in chars:
#            if type(c[4]) in (int,long):
#                if c[4] not in seen:
#                    gc.DrawRectangle(*c[:4])
#                    seen[c[4]]=True
#
#    def chars(self, mode='L', cutoff=200):
#        return list(scrape.letters(self.im.convert(mode), cutoff))

    def draw_baselines(self, baseline_color='#99CCFF', linegap_color='#eeeeee'):
        img_out = self.im

        dc = self.get_dc()

        y = 0
        w, h = img_out.size
        for (top, base, bottom) in scrape.guess_lines(img_out):

            # draw the baseline
            dc.SetPen(wx.Pen(baseline_color))

            if not base:
                base = bottom - 2
                dc.SetPen(wx.RED_PEN)

            dc.DrawLines([(0, base), (w, base)])

            # shade out the other stuff
            dc.SetPen(wx.Pen(linegap_color))
            dc.SetBrush(wx.Brush(linegap_color))
            dc.DrawRectangle(0, y, w, top-y)
            y = bottom

        # shade bottom area
        dc.DrawRectangle(0, y, w, h-y)

    def on_close_window(self, _evt):
        self.Destroy()


class App(wx.App):
    def OnInit(self):
        res = xrc.XmlResource()
        res.Load('pngscraper.xrc')
        frame = res.LoadFrame(None, 'PngScraperFrame')
        frame.init()
        frame.Position = (0, 0)
        frame.Show(True)
        return True


if __name__ == "__main__":
    app = App(0)
    app.MainLoop()
