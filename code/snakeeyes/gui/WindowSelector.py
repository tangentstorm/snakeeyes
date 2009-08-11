"""
Created on Jul 31, 2009

@author: michal
"""
import wx, os
from snakeeyes import windows

class WindowSelector(wx.Frame):
    """
    Allows you to select an open window for whatever
    nefarious purpose you can imagine (but probably 
    for screen scraping).
    """

    def __init__(self, callback):
        super(WindowSelector, self).__init__(None, -1, "select window")
        self.filterText = wx.TextCtrl(self, -1, "5-Card")
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
            tree.SetPyData(item, win)
            
    def on_text_change(self, e):
        "rebuild tree as you type"
        self.rebuild_tree()
                
    def on_activate(self, e):
        self.callback(self.tree.GetPyData(e.GetItem()))
    
    
if __name__ == "__main__":
    
    SELECTOR = None
    
    def make_builder(win):
        "replace this with whatever you want."
        
        print "making new window for", win.text
        import builder; reload(builder)
        win.bringToFront()
        path = 'c:/svn/poker/assets/scrapecfg/pokerstars/classic/'
        os.chdir(path)
        builder.ConfigBuilder('5cd_792x546.scrape', win, SELECTOR).Show()
    
    app = wx.App(redirect=False)
    
    SELECTOR = WindowSelector(make_builder)
    SELECTOR.Show()
    app.MainLoop()   
