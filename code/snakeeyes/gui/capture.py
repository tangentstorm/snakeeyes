"""
This app lets you collect snapshots of a window for
processing later.

Select a window from the list, and then click the button
to take a picture.

@TODO: move output directory config into the GUI
"""

import os
import wx

from wx.py.shell import ShellFrame

from snakeeyes import windows
from .WindowSelector import WindowSelector

IMGROOT = "/tmp"
WAITING, CAPTURED = 0, 1


class CaptureFrame(wx.Frame):
    """
    Click the button to take a picture. :)
    """
    def __init__(self, hwnd, *a, **kw):

        wx.Frame.__init__(self, *a, **kw)
        self.im = None  # holds captured image

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticText(self, -1, 'enter the hwnd and click capture'))
        self.txt = wx.TextCtrl(self, -1, str(hwnd))
        box.Add(self.txt, 0, wx.EXPAND)

        b = wx.Button(self, wx.NewIdRef(), "capture")
        self.Bind(wx.EVT_BUTTON, self.capture, b)
        box.Add(b, 5, wx.EXPAND)

        self.SetSizer(box)
        self.SetAutoLayout(True)

        self.locals = {
            'self': self,
            'wx': wx,
            'hwnd': hwnd}
        self.shellFrame = ShellFrame(None, -1, "pyshell", locals=self.locals)
        self.locals['shell'] = self.shellFrame.shell

        self.lastCount = None

        self.state = WAITING
        self.Bind(wx.EVT_IDLE, self.on_idle)

    def image_dir(self):
        imdir = "%shwnd%s" % (IMGROOT, self.hwnd)
        if not os.path.exists(imdir):
            os.mkdir(imdir)
        return imdir

    @staticmethod
    def is_time_to_capture():
        # @TODO: override this to schedule the captures
        return False

    def on_idle(self, _evt):
        if not self.hwnd: return
        # and give the window a chance to redraw:
        time_to_capture = self.is_time_to_capture()
        if time_to_capture and self.state == WAITING:
            self.state = CAPTURED
            self.capture()

        elif self.state == CAPTURED and not time_to_capture:
            self.state = WAITING

    @property
    def hwnd(self):
        return int(self.txt.Value)

    def next_name(self):

        if self.lastCount is None:
            files = sorted([
                f for f in os.listdir(self.image_dir())
                if f.endswith('.png')])
            if files:
                self.lastCount = int(files[-1].split('.')[0])
            else:
                self.lastCount = -1

        self.lastCount += 1
        return '%s/%05i.png' % (self.image_dir(), self.lastCount)

    def capture(self, _evt=None):
        self.im = windows.Window(self.hwnd).as_image_simple()
        name = self.next_name()
        self.im.save(name)
        print("saved %s" % name)
        if _evt is None:  # so we can call interactively or as an event handler
            return self.im


if __name__ == '__main__':

    def make_capture(win):
        hwnd = str(win.hwnd)
        frame = CaptureFrame(hwnd, None, -1, "capture")
        frame.Show()

    app = wx.App(redirect=False)
    sel = WindowSelector(make_capture)
    sel.Show()
    app.MainLoop()
