"""
Created on Aug 1, 2009

App to help you build scraping profiles interactively.

@author: michal
"""
import os, sys
from importlib import reload

import wx
from wx.py.shell import Shell
import wx.lib.mixins.listctrl as listmix
from PIL import ImageOps

from snakeeyes import convert
from snakeeyes.fontdata import NeedTraining
import snakeeyes
import snakeeyes.Region
import snakeeyes.gui.glyphs as glyph_gui
import snakeeyes.gui.fonts as font_gui
from snakeeyes.gui.WindowSelector import WindowSelector
from snakeeyes.tools import * # for use in the configs


class ScrapeDataCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    """
    A ListCtrl that shows data from the scrape.
    """
    def __init__(self, scraper, *a, **kw):
        wx.ListCtrl.__init__(self, style=wx.LC_REPORT, *a, **kw)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, "name")
        self.InsertColumn(1, "value")

        self.scraper = scraper
        self.repopulate()

    def repopulate(self):
        self.DeleteAllItems()
        for i, (name, region) in enumerate(sorted(self.scraper.items())):
            index = self.InsertItem(i, name)
            self.SetItem(index, 1, region.last_value or '--')


class ConfigBuilder(wx.Frame):
    """
    Interactively build a scraping profile.
    """
    def __init__(self, scrapefile, win, parent=None, *a, **kw):
        """
        @param scrapefile the config file to use
        @param win the window object (may be none)
        """
        super(ConfigBuilder, self).__init__(parent, *a, **kw)

        self.SetTitle("profile builder: %s" % scrapefile)

        self.win = win
        self.scrapefile = scrapefile
        self.use_simple = True

        self.bmp = wx.StaticBitmap(self, size=(win.size if win else (792, 546)))  # @TODO: parametrize

        vars = {'self': self}
        vars.update(self.__dict__)
        self.shell = Shell(self, locals = vars,
                           introText="SnakeEyes v0.0a\n")
        self.shell.AppendText("REF: ''.join(sorted(self.scraper['chat_box'].tool.font.data.values()))")

        self.refresh = wx.Button(self, wx.NewId(), "refresh")
        self.refresh.Bind(wx.EVT_BUTTON, self.on_refresh_button)

        self.make_scraper()
        self.live_data = ScrapeDataCtrl(self.scraper, self)
        self.live_data.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item)

        if self.win is None:
            self.ticking = False
        else:
            self.timer = wx.Timer()
            self.timer.Bind(wx.EVT_TIMER, self.on_tick)
            self.ticking = True
            self.timer.Start(500, wx.TIMER_CONTINUOUS)

        # this is just so the mono image stands out
        self.SetBackgroundColour(wx.Colour(0x33, 0x33, 0x99))
        self.SetForegroundColour(wx.Colour(0xFF, 0xFF, 0xFF))

        self.values = {}

        self.layout()
        self.Show()

    def layout(self):
        """Arranges the controls inside the window."""
        box = wx.BoxSizer(wx.VERTICAL)

        # top row
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(wx.StaticText(self, -1, self.scrapefile))
        row.Add(self.refresh)
        row.AddSpacer(20)
        row.Add(wx.StaticText(self, -1, "hwnd:"))
        if self.win is not None:
            row.Add(wx.TextCtrl(self, -1, str(self.win.hwnd)))
        box.Add(row)

        # image itself
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.bmp, 0, wx.EXPAND)
        self.live_data.SetSizeHints(200, -1)
        row.Add(self.live_data, 1, wx.EXPAND)
        box.Add(row, 0, wx.EXPAND)

        # bottom row (shell)
        self.shell.SetSizeHints(500,-1)
        box.Add(self.shell, 1, wx.EXPAND)
        self.SetSizerAndFit(box)

    def on_item(self, e):
        item = self.live_data.GetItem(e.m_itemIndex, 0).GetText() # item, column

        reload(glyph_gui)
        reload(font_gui)

        wx_bmp = convert.img_to_wxbmp(self.scraper[item].last_snapshot)
        dlg = glyph_gui.GlyphDialog(wx_bmp, self, -1,
                               title="current glyph in region '%s'" % item)
        dlg.ShowModal()

    def on_refresh_button(self, e):
        self.live_coding_hook()
        self.reload_modules()
        self.make_scraper()
        self.set_image(self.screen)

    @staticmethod
    def reload_modules():
        reload(snakeeyes.config)
        reload(snakeeyes.Region)
        reload(snakeeyes)
        reload(glyph_gui)
        reload(font_gui)


    def live_coding_hook(self):
        # this is a little livecoding thing:
        pass #exec open("c:/temp/textregion.py").read() in locals()

    def make_scraper(self):
        self.scraper = snakeeyes.load_config(self.scrapefile)

    def collect_values(self, img):
        try:
            self.scraper.collect_values(img)
        except snakeeyes.fontdata.NeedTraining as e:
            self.request_training(e.font, e.glyph)

    def paste_snaps(self, onto):
        for region in self.scraper.values():
            onto.paste(region.last_snapshot, region.rect.pos)

    def update_image(self):
        """
        this captures the new image from the window.
        """
        meth = self.win.as_image_simple if self.use_simple else self.win.as_image
        self.set_image(meth())

    def set_image(self, image):
        """
        this takes any image as a parameter
        """
        self.screen = image
        img = ImageOps.grayscale(self.screen).convert("RGB")

        try:
            self.values = self.scraper.collect_values(self.screen)
        except NeedTraining as e:
            self.request_training(e.font, e.glyph)
        else:
            self.paste_snaps(onto=img)

        self.live_data.repopulate()
        self.scraper.draw_boxes(img)
        self.bmp.SetBitmap(convert.img_to_wxbmp(img))

        self.Refresh()

    def on_tick(self, e):
        if self.ticking:
            self.update_image()

    def request_training(self, font, glyph):
        if not self.ticking: return
        self.ticking = False
        reload(glyph_gui)
        wx_bmp = convert.img_to_wxbmp(glyph)

        dlg = glyph_gui.GlyphDialog(wx_bmp, self, -1,
                                    "train me!")
        dlg.when_done = self.training_done
        dlg.font = font
        dlg.glyph = glyph
        dlg.Show()

    def training_done(self, dlg, which_button):
        if which_button == wx.ID_OK:
            self.dlg = dlg # only for the shell
            print("OK! learning new value!", dlg.txt.GetValue())
            dlg.font.learn(dlg.glyph, dlg.txt.GetValue())
        self.ticking = True


if __name__ == "__main__":

    SELECTOR = None

    def make_builder(win):
        """
        replace this with whatever you want.

        @param win: snakeeyes.windows.Window
        """
        print("making new window for", win.text)

        # this next line is just so I don't have to restart the entire
        # app every time I make a change to the source code.
        # instead, just re-open the window
        from snakeeyes.gui import builder; reload(builder)

        win.bring_to_front()
        path = '.'  # c:/temp/shots/'
        os.chdir(path)
        builder.ConfigBuilder('scrape_cfg.py', win, SELECTOR).Show()

    app = wx.App(redirect=False)

    SELECTOR = WindowSelector(make_builder)
    SELECTOR.Show()
    app.MainLoop()


