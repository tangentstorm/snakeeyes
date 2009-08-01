
import wx
import os
import scrape
import fulltilt, pokerstars
from wx.py.shell import ShellFrame
import replayer
import time, math
import win32gui

fulltilt.learnNewChar = lambda fontd, bmp, height : '[@TOLEARN]'

IMGROOT = "w:/app/poker/"
WAITING, MYTURN = 0,1

class ThinkFrame(wx.Frame): # adapted from ceomatic.wxtimer
    def __init__(self, parent, id, title, **kw):
        kw.setdefault('size', (300,20))
        wx.Frame.__init__(self, parent, id, title,
                          style= wx.FRAME_NO_TASKBAR
                               | wx.FRAME_TOOL_WINDOW # no alt-tab
                               | wx.SIMPLE_BORDER
                               | wx.STAY_ON_TOP
                          ,**kw)

        # draw background image
        self.image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(435, 85))
        img = wx.Image("stopandthink.png", wx.BITMAP_TYPE_PNG)
        self.image.SetBitmap(wx.BitmapFromImage(img))
        self.Fit()

        # set up the clock display.
        self.clocktext = wx.StaticText(self.image, -1, "0:00", pos=(340, 6))
        self.clocktext.SetForegroundColour("white")
        self.clocktext.SetBackgroundColour("#254B66")        
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTick)
        self.timeLimit = 0
        self.startTime = 2 # this makes timeLeft return -1 by default

    def go(self, seconds=10):
        self.timeLimit = seconds
        self.startTime = time.time()
        self.timer.Start(1000) # 1 second intervals

        # show timer immediately
        self.onTick(None)
        self.Show()

    def timeLeft(self):
        return self.timeLimit - math.floor((time.time() - self.startTime))

    def onTick(self, evt):
        secs = self.timeLeft()
        mins = secs / 60
        smod = secs % 60
        self.clocktext.SetLabel("%02i:%02i" % (mins,smod))
        
        # time's up.
        if secs <= 0:
            self.onTimeOut()

    def onTimeOut(self):
        self.timer.Stop()
        self.Hide()

    def coverBottomRightCorner(self, hwnd):
        w, h = self.Size
        x,y,x2,y2=win32gui.GetWindowRect(hwnd)
        self.Position=(x2-w-4, y2-h-4)

class CaptureFrame(wx.Frame):
    def __init__(self, hwnd, *a, **kw):
        wx.Frame.__init__(self, *a, **kw)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticText(self, -1, 'enter the hwnd and click capture'))

        self.txt = wx.TextCtrl(self, -1, str(hwnd))
        box.Add(self.txt, 0, wx.EXPAND)

        b = wx.Button(self, wx.NewId(), "capture")
        self.Bind(wx.EVT_BUTTON, self.grabImage, b)
        box.Add(b, 5, wx.EXPAND)

        self.SetSizer(box)
        self.SetAutoLayout(True)

        self.thinker = ThinkFrame(self, -1, "stop and think!")
        
        self.locals = {
            'self':self,
            'wx': wx,
            'hwnd': hwnd,
            'scrape':scrape,
            'fulltilt':fulltilt
            }
        self.shellFrame = ShellFrame(None, -1, "pyshell", locals=self.locals)
        self.locals['shell'] = self.shellFrame.shell
        #self.shellFrame.Show()

        self.lastCount = None

        self.state = WAITING
        self.Bind(wx.EVT_IDLE, self.OnIdle)

    def imageDir(self):
        imdir = "%shwnd%s" % (IMGROOT, self.targetHwnd())
        if not os.path.exists(imdir):
            os.mkdir(imdir)
        return imdir

    def OnIdle(self, e):
        if not self.txt.Value: return
        if self.thinker.IsShown(): return
        # and give the window a chance to redraw:
        if self.thinker.timeLeft() > -2: return
        
        myturn = pokerstars.StarScraper.h_isMyTurn(self.targetHwnd())
        
        if myturn and self.state == WAITING:
            self.state = MYTURN
            self.grabImage()
            self.thinker.coverBottomRightCorner(self.targetHwnd())
            self.thinker.go(5)

            scr = pokerstars.StarScraper(self.im)
            print scr.asTable()

        elif self.state==MYTURN and not myturn:
            self.state = WAITING

    def targetHwnd(self):
        return int(self.txt.Value)

    def nextName(self):

        if self.lastCount is None:
            files = sorted([
                f for f in os.listdir(self.imageDir())
                if f.endswith('.png')])
            if files:
                self.lastCount = int(files[-1].split('.')[0])
            else:
                self.lastCount = -1

        self.lastCount += 1
        return '%s/%05i.png' % (self.imageDir(), self.lastCount)

    def grabImage(self, e=None):
        self.im = scrape.grabImage(self.targetHwnd())
        imName = self.nextName()
        self.im.save(imName)
        print "saved %s" % imName
        if e==None:
            return self.im


if __name__=='__main__':
    hwnd = ''
    for hwnd, name in pokerstars.tableWindows():
        if name.count("Table"):
            print hwnd, name
            break

    app = wx.App(redirect=False)
    frame = CaptureFrame(hwnd, None, -1, "capture")
    frame.Show()
    app.MainLoop()

