
#from anki.hooks import wrap  #using this is the recommended option, but seems less transparent to me. -Jon
#from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, askUserDialog, getFile
from aqt.utils import mungeQA, getBase, openLink, tooltip, askUserDialog
from anki.utils import json
from aqt.webview import AnkiWebView
from grid import Ui_gridDialog

# from PyQt4.QtGui import QMessageBox  #done for us already?

class GridDlg(QDialog):
    def __init__(self, reviewer):
        QDialog.__init__(self)

        #self._reviewer = reviewer
        
        # Set up the user interface from Designer.
        self.ui = Ui_gridDialog()
        self.ui.setupUi(self)

        # Make some local modifications.
        #self.ui.colorDepthCombo.addItem("2 colors (1 bit per pixel)")

        # Connect up the buttons.
        #self.ui.okButton.clicked.connect(self.accept)
        #self.ui.cancelButton.clicked.connect(self.reject)    

# Do some monkey patching to wrap more functionality around _showQuestion    
from aqt.reviewer import Reviewer

def myShowAnswerGrid(self, card, view):
    c = card
    origState = self.state
    self.state = "answer"
    
    a = c.a()
    # play audio?  # NO, not in the grid (except maybe on hover?)
    #if self.autoplay(c):
    #    playFromText(a)
    # render and update bottom
    
    a = self._mungeQA(a)
    #klass = "card card%d" % (c.ord+1)
    #tmp = "_updateA(%s, true, %s);" % (json.dumps(a), klass)

    #a = '"test answer"'

    tmp = '_updateA("cell1", %s);' % (json.dumps(a))
       
    
    #self.web.eval(tmp)  # NO, instead of the Reviewer doing this, have the view do it
    view.page().mainFrame().evaluateJavaScript(tmp)
    tmp = '_updateA("cell4", %s);' % (json.dumps(a))
    view.page().mainFrame().evaluateJavaScript(tmp)
    #self._showEaseButtons() # NO, not in the grid
    # user hook
    #runHook('showAnswer')  # NO, we assume other addons' behavior here is unwanted
        
    self.state = origState

def myShowQuestion(self):
    origShowQuestion(self) # we're wrapping this, so still running it

    #showInfo("pretend this is a grid")
    w = GridDlg(self)
    self._popupGrid = w
    
    v = w.ui.gridView  # type of v: QtWebKit.QWebView or its AnkiWebView subclass
    v.setLinkHandler(self._linkHandler)

    #scratch pad:
    #import aqt.webview
    #aqt.webview.AnkiWebView().
    #from PyQt4 import QtCore, QtGui
    #from PyQt4 import QtWebKit
    #QtWebKit.QWebView().page().mainFrame().toHtml()
    
    
    #from PyQt4 import QtGui.QDialog, QtWebKit.
    #x = QtGui.QDialog().
 

    #equivalent to Reviewer._initWeb() : 
    base = getBase(self.mw.col)
    # main window
    
    #TEST:
    html = """
<!doctype html>
<html>

<head><style></style>
<script>
function _append (id, t) {
  var target = document.getElementById(id);
  target.innerHTML += t;
}

function _updateA (cell, answer) {
    _append(cell, answer);
};

</script>
</head>
<body class="">
<div id=qa></div>
<p><a href="closePopup">close</a></p>
<p>Table:
</p>
<table><tbody><tr>
  <td id="cell1" class="cell">1.</td>
  <td id="cell2" class="cell">2.</td>
</tr><tr>
  <td id="cell3" class="cell">3.</td>
  <td id="cell4" class="cell">4.</td>
</tr></tbody></table>
<script>
  _append("qa", ".");
  //var cells = document.getElementsByClassName('cell');
  //for (var i = 0; i < cells.length; ++i) {
  //  var cell = cells[i];
  //  _append(cell.id, " [card "+i+"]");  
}  
</script>
</body>

</html>
"""

    """
<br/>
<p id="p1"></p>
<p id="p2"></p>
<table>
<tr>
<td><iframe id="t00" src="about:blank"></iframe></td>
<td><iframe id="t01" src="%s"></iframe></td>
</tr>
<tr>
<td><iframe id="t10" src="%s"></iframe></td>
<td><iframe id="t11" src="%s"></iframe></td>
</tr>
</table></body></html>""" % ("./frame1.html",  "../frame1.html",  "C:\\Users\\user57\\Documents\\Anki\\User 1\\collection.media\\frame1.html")

    '''
    v1 = AnkiWebView()
    v1.stdHtml(self._revHtml, self._styles(),
        loadCB=lambda x: self._showAnswerGrid(self.card, v),
        head=base)  # needs to be _showAnswerGrid
    '''
    # DON'T show answer / ease buttons

    v.setHtml(html)

    callback = lambda x: self._showAnswerGrid(self.card, v)
    #callback = None

    t00 = AnkiWebView()
    t00.stdHtml(self._revHtml, self._styles(),
        loadCB=callback,
        head=base)
    
    #h1 = "[" + t00.page().mainFrame().toPlainText() + "]"  #.toHtml()
    h2 = t00.page().mainFrame().toHtml()

    #tmp = '_append("0a", "%s");' % h1  # h2 w/b a big mess
    #v.page().mainFrame().evaluateJavaScript(tmp) # eval on v, NOT on self

    self.card.tmpHtml = h2
    
    
    #frames = v.page().mainFrame().childFrames()
    #for frame in frames:
    #    frame.setHtml(h1)
    #frames[0].setHtml(h2)
    #v.setHtml(h2)


    v.show()
    w.show()

    if w.exec_():
        pass
        #values = dlg.getValues()
    
def myClosePopupGrid(self, r=0): 
    self._popupGrid.done(r)
    self._popupGrid = None
    
    
origShowQuestion = Reviewer._showQuestion
Reviewer._showQuestion = myShowQuestion
Reviewer._showAnswerGrid = myShowAnswerGrid


Reviewer._closePopupGrid = myClosePopupGrid

'''
# We probably won't get enough info/power to be able to just use the hook.
def onShowQuestion():
    import time
    time.sleep(1.5)
    showInfo("pretend this is a grid")

addHook('showQuestion', onShowQuestion)
'''

def on_menu_clicked():
    showInfo("u clicked me")

# create a new menu item in Anki
action = QAction("FlashGrid test", mw)
# set it to call our function when it's clicked
mw.connect(action, SIGNAL("triggered()"), on_menu_clicked)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
