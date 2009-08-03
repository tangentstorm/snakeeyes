
from wx.py.shell import ShellFrame
import scrape, windows
import math, os, time, math, wx
import win32gui

IMGROOT = "/tmp"
WAITING, CAPTURED = 0,1


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
       
        self.locals = {
            'self':self,
            'wx': wx,
            'hwnd': hwnd,
            'scrape':scrape,
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

    def is_time_to_capture(self):
        # @TODO: override this to schedule the captures
        return False

    def OnIdle(self, e):
        if not self.txt.Value: return
        # and give the window a chance to redraw:
        
        time_to_capture = self.is_time_to_capture()
        if time_to_capture and self.state == WAITING:
            self.state = CAPTURED
            self.grabImage()

        elif self.state==CAPTURED and not time_to_capture:
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
        self.im = windows.Window(self.targetHwnd()).as_image()
        imName = self.nextName()
        self.im.save(imName)
        print "saved %s" % imName
        if e==None:
            return self.im


if __name__=='__main__':
    hwnd = ''
    app = wx.App(redirect=False)
    frame = CaptureFrame(hwnd, None, -1, "capture")
    frame.Show()
    app.MainLoop()

