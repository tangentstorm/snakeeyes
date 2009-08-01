
# based on http://wiki.wxpython.org/wxStaticBitmap example

import wx, os, sys
import wx.py as py
import Image
sys.path.insert(0, 'w:/app/ceomatic')
from gridliner import Cursor, ListView
import scrape

#PNGDIR=r'W:\app\poker\hwnd6359358' # full tilt
PNGDIR=r'W:\app\poker\hwnd527812' # pokerstars

ID_OPEN_FILE = wx.NewId()
ID_OPEN_DIR = wx.NewId()

class PngScraperFrame(wx.Frame):
    def __init__(self, *args, **kwargs):

        wx.Frame.__init__(self, *args, **kwargs)


        self.createMenu()

        #self.pngs = ['c:/temp/mibook.png']
        self.pngs = GetPngList(PNGDIR)
        
        self.cursor = Cursor(ListView(self.pngs))

        box = wx.BoxSizer(wx.VERTICAL)

        # next button

        row = wx.BoxSizer(wx.HORIZONTAL)


        def CursorButton(label):
            b = wx.Button(self, label= label)
            b.Bind(wx.EVT_BUTTON, self.OnCursorButton)
            return b
            
        row.Add(CursorButton("<<"))
        row.Add(CursorButton("<"))

        self.which =  wx.TextCtrl(self, -1, '')
        self.updateWhich()
        row.Add(self.which)

        row.Add(CursorButton(">"))
        row.Add(CursorButton(">>"))

        # coords box
        self.coords = wx.TextCtrl(self, -1, '(0,0)')
        row.Add(self.coords, 0, wx.ALIGN_RIGHT)
        row.Add((20,20),1)

        # color box
        self.color = wx.TextCtrl(self, -1, '0x000000')
        row.Add(self.color, 0, wx.ALIGN_RIGHT)
        row.Add((20,20),1)
        
        box.Add(row, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # the image

        pane = wx.ScrolledWindow(self, -1, size=(300,400))
        box.Add(pane, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ADJUST_MINSIZE)
        
        self.image = wx.StaticBitmap(pane, bitmap=wx.EmptyBitmap(800, 600))
        self.image.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.image.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.updateImage()

        # the shell
        self.locals = {'self':self, 'wx':wx, 'hook': lambda:None, 'gc':self.getGC() }
        self.shell = py.shell.Shell(self, locals=self.locals)
        self.shell.SetMinSize((500,400))
        box.Add(self.shell, 4, wx.EXPAND)
        self.shell.SetFocus()
        
        self.SetSizerAndFit(box)
        wx.EVT_CLOSE(self, self.OnCloseWindow)


    def createMenu(self):   
        
        # Setting up the menu.
        filemenu= wx.Menu()
        filemenu.Append(ID_OPEN_FILE, "&Open File", "OpenFile")
        filemenu.Append(ID_OPEN_DIR, "Open &Directory", "OpenDir")
        
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()      
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        wx.EVT_MENU(self, wx.ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_OPEN_FILE, self.OnOpenFile)
        wx.EVT_MENU(self, ID_OPEN_DIR, self.OnOpenDir)


    def OnCursorButton(self, evt):
        buttonMap = {
            "<<":"moveToStart",
            "<" :"movePrevious",
            ">" :"moveNext",
            ">>":"moveToEnd",
        }
        try:
            getattr(self.cursor, buttonMap[evt.GetEventObject().Label])()
            self.updateWhich()
            self.updateImage()
            self.shell.run('hook()')
        except StopIteration:
            pass



    def OnOpenFile(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file", defaultDir=os.getcwd(), 
            defaultFile="", wildcard='*.png',
            style=wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.pngs.insert(self.cursor.position,path)
            self.updateWhich()
            self.updateImage()

    def OnOpenDir(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:",
                           defaultPath=os.getcwd(), 
                           style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            while self.pngs:
                self.pngs.pop()
            self.pngs.extend(GetPngList(path))
            self.cursor.moveToStart()
            self.updateWhich()
            self.updateImage()
            self.shell.run('hook()')
            
    def OnExit(self, evt):
        self.Close()

    def updateWhich(self):
        self.which.Value = "%s/%s" % (self.cursor.position, len(self.pngs))

    def updateImage(self):

        # set the visible bitmap
        img = wx.Image(self.pngs[self.cursor.position], wx.BITMAP_TYPE_PNG)
        self.image.SetBitmap(wx.BitmapFromImage(img))
        self.Fit()
        
        # and make the pil image
        self.im = im = Image.new('RGB', (self.image.Size))
        self.im.fromstring(wx.ImageFromBitmap(self.image.GetBitmap()).GetData())


    def OnRightDown(self, e):
        self.image.Refresh()
        
    def OnLeftDown(self, e):
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

    def getGC(self):
        gc = wx.GCDC(wx.ClientDC(self.image))
        ink = wx.Color(0x99, 0xcc, 0xff, 0x88)
        gc.SetPen(wx.Pen(ink))
        gc.SetBrush(wx.Brush(ink))
        return gc

    def drawWords(self):
        chars = self.chars()
        inks = wx.Color(0x99, 0xcc, 0xff, 0x88) , wx.Color(0x99, 0xff, 0xcc, 0x88)

        gc = self.getGC()

        i = 0
        for c in chars:
            if c[4] not in ('', ' '):

                ink = inks[i % 2]
                i += 1 
                
                gc.SetPen(wx.Pen(ink))
                gc.SetBrush(wx.Brush(ink))
                
                gc.DrawRectangle(*c[:4])


    def drawFirstUnkowns(self, cutoff=200, mode='L'):
        chars = self.chars(mode, cutoff) 

        seen = {}
        
        gc = self.getGC()
        ink = wx.Color(0xff, 0x00, 0x00, 0x88)
        gc.SetPen(wx.Pen(ink))
        gc.SetBrush(wx.Brush(ink))
                
        i = 0
        for c in chars:
            if type(c[4]) in (int,long):
                if c[4] not in seen:
                    gc.DrawRectangle(*c[:4])
                    seen[c[4]]=True
                

    def chars(self, mode='L', cutoff=200):
        return list(scrape.letters(self.im.convert(mode), cutoff))
        
    def lines(self, mode="L"):
        return list(scrape.lines(self.im.convert(mode)))

    def drawBaseLines(self, color='#99CCFF', gapcolor='#eeeeee',  mode='L'):
        y = 0
        w,h = self.im.size
        dc = self.getGC()
        for y1,base,y2 in self.lines(mode):

            # draw the baseline
            dc.SetPen(wx.Pen(color))

            if not base:
                base = y2 -2
                dc.SetPen(wx.RED_PEN)

            dc.DrawLines([(0,base),(w,base)])

            # shade out the other stuff
            dc.SetPen(wx.Pen(gapcolor))
            dc.SetBrush(wx.Brush(gapcolor))
            dc.DrawRectangle(0,y,w,y1-y)
            y = y2
            
        # shade bottom area
        dc.DrawRectangle(0,y,w,h-y)


    def OnCloseWindow(self, event):
        self.Destroy()


def GetPngList(dir):
    pngs = [f for f in os.listdir(dir) if f[-4:] == ".png"]
    return [os.path.join(dir, f) for f in pngs]


class App(wx.App):
    def OnInit(self):
        frame = PngScraperFrame(None, title="PNG Scraper")
        frame.Position = (0,0)
        frame.Show(True)
        return True

if __name__ == "__main__":
    app = App(0)
    app.MainLoop()

