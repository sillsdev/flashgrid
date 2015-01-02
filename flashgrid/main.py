
#from anki.hooks import wrap  #using this is the recommended option, but seems less transparent to me. -Jon
#from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, askUserDialog, getFile
from aqt.utils import mungeQA, getBase, openLink, tooltip, askUserDialog
from anki.utils import json

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

def myShowAnswerPlain(self, card, view):
    c = card
    origState = self.state
    self.state = "answer"
    
    a = c.a()
    # play audio?  # NO, not in the grid (except maybe on hover?)
    #if self.autoplay(c):
    #    playFromText(a)
    # render and update bottom
    a = self._mungeQA(a)
    tmp = "_updateQA(%s, true);" % json.dumps(a)
    #self.web.eval(tmp)  # NO, instead of the Reviewer doing this, have the view do it
    view.page().mainFrame().evaluateJavaScript(tmp)
    #self._showEaseButtons() # NO, not in the grid
    # user hook
    #runHook('showAnswer')  # NO, we assume other addons' behavior here is unwanted
        
    self.state = origState

def myShowQuestion(self):
    origShowQuestion(self) # we're wrapping this, so still running it

    #showInfo("pretend this is a grid")
    w = GridDlg(self)
    v = w.ui.gridView  # type of v: AnkiWebView

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
<html><head><style></style>
</head>
<body class=""><table>
<tr>
<td><iframe src="%s"></iframe></td>
<td><iframe src="%s"></iframe></td>
</tr>
<tr>
<td><iframe src="%s"></iframe></td>
<td><iframe src="%s"></iframe></td>
</tr>
</table></body></html>""" % ("frame1.html",  "temp.tmp.html",  "frame1.html",  "frame1.html")

    '''
    from aqt.webview import AnkiWebView
    v1 = AnkiWebView()
    v1.stdHtml(self._revHtml, self._styles(),
        loadCB=lambda x: self._showAnswerPlain(self.card, v),
        head=base)  # needs to be _showAnswerPlain
    '''
    # DON'T show answer / ease buttons

    #QWebView.setHtml(v, html)

    #v.stdHtml('', loadCB=lambda x: self._showAnswerPlain(self.card, v), head=base)
    v.stdHtml(self._revHtml, self._styles(),
        loadCB=lambda x: self._showAnswerPlain(self.card, v),
        head=base) 

    #h = v.page().mainFrame().toHtml()
    #showInfo(h)

    v.show()
    w.show()

    if w.exec_():
        pass
        #values = dlg.getValues()
    
origShowQuestion = Reviewer._showQuestion
Reviewer._showQuestion = myShowQuestion
Reviewer._showAnswerPlain = myShowAnswerPlain



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
