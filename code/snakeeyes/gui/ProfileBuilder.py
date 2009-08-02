'''
Created on Aug 1, 2009

@author: michal
'''
from handy import spawn_thread
from pprint import pformat
from wx.py.shell import Shell
import wx.lib.mixins.listctrl  as  listmix
import ImageDraw
import ImageOps
import convert
import snakeeyes
import snakeeyes.gui.glyphs as glyph_gui
import snakeeyes.gui.fonts as font_gui
import wx, sys

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
        for name, region in self.scraper.items():
            index = self.InsertStringItem(sys.maxint, name)
            self.SetStringItem(index, 1, region.last_value or '--' )

class ProfileBuilder(wx.Frame):
    """
    Interactively build a scraping profile.
    """
    def __init__(self, scrapefile, win, parent=None, *a, **kw):
        super(ProfileBuilder, self).__init__(parent, *a, **kw) 
        
        
        self.SetTitle("profile builder: %s" % scrapefile)
        
        self.win = win
        self.scrapefile = scrapefile

        self.bmp = wx.StaticBitmap(self, size=(win.size))
        
        vars = { 'self': self }
        vars.update(self.__dict__)
        self.shell = Shell(self, locals = vars,
                           introText = "SnakeEyes v0.0a\n")

        self.refresh = wx.Button(self, wx.NewId(), "refresh")
        self.refresh.Bind(wx.EVT_BUTTON, self.on_refresh_button)
        
        self.make_scraper()
        self.live_data = ScrapeDataCtrl(self.scraper, self)
        self.live_data.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item)
        

        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.on_tick)
        self.ticking = True
        self.timer.Start(500, wx.TIMER_CONTINUOUS)
        
        # this is just so the mono image stands out
        self.SetBackgroundColour(wx.Color(0x33, 0x33, 0x99))
        self.SetForegroundColour(wx.Color(0xFF, 0xFF, 0xFF))

        self.layout()
        self.Show()


    def layout(self):
        "Arranges the controls inside the window."
        box = wx.BoxSizer(wx.VERTICAL)

        # top row
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(wx.StaticText(self, -1, self.scrapefile))
        row.Add(self.refresh)
        row.AddSpacer(20)
        row.Add(wx.StaticText(self, -1, "hwnd:"))
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
        
        wx_bmp = convert.pilToBitmap(self.glyphs[item][1])
        dlg = glyph_gui.GlyphDialog(wx_bmp, self, -1, 
                               title="current glyph in region '%s'" % item)
        dlg.ShowModal()
        

    def on_refresh_button(self, e):
        #self.reload_modules()
        #self.make_scraper()
        self.update_image()
        self.live_data.repopulate()
        
    def reload_modules(self):
        import snakeeyes.config
        #reload(snakeeyes.config)
        reload(snakeeyes)
        reload(glyph_gui)
        reload(font_gui)
    
    def make_scraper(self):
        self.scraper = snakeeyes.load_config(self.scrapefile)
                
    def collect_glyphs(self, img):
        ":: Image.Image -> { str : ( Region, Image.Image) }"
        # we've assumed you've grabbed the entire window
        # maybe it would be better to grab only the pieces
        # you need directly from the screen, but for 
        # now this is fine
        res = {}
        for key, region in self.scraper.items():
            try:
                region.scrape(img) # -> region.last_value
                res[key] = region, region.last_snapshot
            except snakeeyes.fontdata.NeedTraining, e:
                self.request_training(e.font, e.glyph, key)
                break
        return res
            
    def paste_glyphs(self, onto):
        for key, (region, glyph) in self.glyphs.items():
            onto.paste(glyph, region.rect.pos)
            
    def update_image(self):
        self.screen = self.win.as_image()
        self.glyphs = self.collect_glyphs(self.screen)
        
        img = ImageOps.grayscale(self.screen).convert("RGB")
        self.paste_glyphs(onto=img)
        self.scraper.draw_boxes(img)
        
        self.bmp.SetBitmap(convert.pilToBitmap(img))
        self.Refresh()

    def on_tick(self, e):
        if self.ticking:
            self.on_refresh_button(e)

    def request_training(self, font, glyph, region_name):
        if not self.ticking: return
        self.ticking = False
        reload(glyph_gui)
        wx_bmp = convert.pilToBitmap(glyph)

        dlg = glyph_gui.GlyphDialog(wx_bmp, self, -1, 
                                    "train me (%s)!" % region_name)
        dlg.when_done = self.training_done
        dlg.font = font
        dlg.glyph = glyph
        dlg.Show()

    def training_done(self, dlg, which_button):
        if which_button == wx.ID_OK:
            self.dlg = dlg # only for the shell
            print "OK! learning new value!", dlg.txt.GetValue()
            dlg.font.learn(dlg.glyph, dlg.txt.GetValue())
        self.ticking = True
        
        


