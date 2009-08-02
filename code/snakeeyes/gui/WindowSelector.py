"""
Created on Jul 31, 2009

@author: michal
"""
import wx
import windows

class WindowSelector(wx.Frame):
    """
    Allows you to select an open window for whatever
    nefarious purpose you can imagine (but probably 
    for screen scraping).
    """

    def __init__(self, callback):
        super(WindowSelector, self).__init__(None, -1, "select window")
        self.filterText = wx.TextCtrl(self, -1, "5-Card")
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.filterText)

        self.tree = wx.TreeCtrl(self, size=(200,300),
                                style=wx.TR_HIDE_ROOT)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self.updateTree()
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.filterText)
        box.Add(self.tree)
        self.SetSizerAndFit(box)
        
        self.callback = callback
    
    def updateTree(self):
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
            
    def OnTextChange(self, e):
        print "in here"
        self.updateTree()
                
    def OnActivate(self, e):
        self.callback(self.tree.GetPyData(e.GetItem()))
    
    
if __name__ == "__main__":
    
    selector = None
    
    def make_profile(win):
        global selector
        print "making new window for", win.text
        import ProfileBuilder
        reload(ProfileBuilder)
        win.bringToFront()
        path = 'w:/app/poker/scrapecfg/pokerstars/classic/5cd_792x546.scrape'
        pb = ProfileBuilder.ProfileBuilder(path, win, selector)
        pb.Show()
    
    app = wx.App(redirect=False)
    
    selector = WindowSelector(make_profile)
    selector.Show()
    app.MainLoop()   
