"""
Created on Jul 31, 2009

@author: michal
"""
import wx
from snakeeyes import windows


class WindowSelector(wx.Frame):
    """
    Allows you to select an open window for whatever
    nefarious purpose you can imagine (but probably 
    for screen scraping).

    Invokes `callback(win)`, where `win` is a
    `snakeeyes.windows.Window` instance.
    """

    def __init__(self, callback):
        """
        @param callback: snakeeyes.windows.Window -> ()
        @return:
        """
        super(WindowSelector, self).__init__(None, -1, "select window")
        self.filterText = wx.TextCtrl(self, -1, "")
        self.Bind(wx.EVT_TEXT, self.on_text_change, self.filterText)

        self.tree = wx.TreeCtrl(self, size=(200,300),
                                style=wx.TR_HIDE_ROOT)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate)
        self.rebuild_tree()
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.filterText)
        box.Add(self.tree, 1, wx.EXPAND)
        self.SetSizerAndFit(box)
        
        self.callback = callback
    
    def rebuild_tree(self):
        """
        rebuild the tree of windows.
        @TODO: actually make it a tree! :)
        [right now it just puts everything at the top level]
        """
        tree = self.tree
        tree.DeleteAllItems()
        root = tree.AddRoot("windows")
        def cond(win):
            text = win.text.lower()
            filter = self.filterText.GetValue().lower()
            try:
                return bool(text.count(filter))
            except:
                return False # @TODO: handle unicode errors
        for win in windows.where(cond):
            item = tree.AppendItem(root, win.text)
            tree.SetItemData(item, win)
            
    def on_text_change(self, e):
        """rebuild tree as you type"""
        self.rebuild_tree()
                
    def on_activate(self, e):
        self.callback(self.tree.GetItemData(e.GetItem()))
