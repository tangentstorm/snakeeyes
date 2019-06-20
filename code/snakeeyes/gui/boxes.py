"""
Tool to add and draw boxes on the screen.
"""
from typing import Tuple, Optional

import wx


class BoxCanvas(wx.Panel):

    def __init__(self, *a, **kw):
        super(BoxCanvas, self).__init__(*a, **kw)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)  # for double buffering
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)

        self.index = -1
        self.held = None
        self.offset = wx.Point(0, 0)
        self.dragged = False

        self.rects = [wx.Rect(x, y, w, h) for x, y, w, h in [
            (10, 10, 50, 30),
            (20, 20, 50, 30)]]

    def find_index_at_point(self, x: int, y: int) -> int:
        for i, r in enumerate(reversed(self.rects)):
            if r.Contains(x, y):
                return len(self.rects) - (i + 1)
        return -1

    def on_mouse_down(self, e: wx.MouseEvent):
        self.dragged = False
        refresh = False
        index = self.find_index_at_point(e.x, e.y)
        if index != self.index:
            self.index = index
            refresh = True
        if index >= 0:
            self.held = self.rects[index]
            self.offset = wx.Point(self.held.x - e.x, self.held.y - e.y)
            refresh = True
        if refresh:
            self.Refresh()

    def on_mouse_up(self, e: wx.MouseEvent):
        self.held = None
        if not self.dragged:
            # click to select
            index = self.find_index_at_point(e.x, e.y)
            if index != self.index:
                self.index = index
                self.Refresh()

    def on_mouse_move(self, e: wx.MouseEvent):
        if self.held:
            self.dragged = True
            self.held.SetPosition((e.x + self.offset.x, e.y + self.offset.y))
            self.Refresh()

    def nudge(self, dx: int, dy: int):
        if self.index >= -1:
            box = self.rects[self.index]
            box.SetPosition(box.GetPosition() + wx.Point(dx, dy))
            self.Refresh()

    def on_key_up(self, e: wx.KeyEvent):
        if e.KeyCode == wx.WXK_UP:
            self.nudge(0, -1)
        elif e.KeyCode == wx.WXK_DOWN:
            self.nudge(0, +1)
        elif e.KeyCode == wx.WXK_LEFT:
            self.nudge(-1, 0)
        elif e.KeyCode == wx.WXK_RIGHT:
            self.nudge(+1, 0)

    def on_paint(self, _e: wx.MouseEvent):
        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(0xccaa55)))  # BGR hex code
        dc.Clear()
        for i, rect in enumerate(self.rects):
            dc.SetPen(wx.BLACK_PEN)
            dc.SetBrush(wx.YELLOW_BRUSH if i == self.index else wx.WHITE_BRUSH)
            dc.DrawRectangle(rect)


class BoxFrame(wx.Frame):
    def __init__(self, *a, **kw):
        super(BoxFrame, self).__init__(*a, **kw)
        self.canvas = BoxCanvas(self)


if __name__ == "__main__":
    app = wx.App(redirect=False)
    win = BoxFrame(None, title="Box Canvas")
    win.Show(True)
    app.MainLoop()
