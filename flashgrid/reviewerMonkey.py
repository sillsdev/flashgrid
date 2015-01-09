''' This is an addon (/extension/plugin) to the Reviewer class found in reviewer.py
It adds a grid dialog (currently as a popup window)
'''
from aqt.reviewer import Reviewer
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, askUserDialog, getFile
from aqt.utils import mungeQA, getBase, openLink, tooltip, askUserDialog
from anki.utils import json
from aqt.webview import AnkiWebView
#from grid import Ui_gridDialog
from main import GridDlg

def myShowQuestion(self):
    rev = self
    origShowQuestion(self) # we're wrapping this, so we'll still run it
    if not GridDlg.gridOn: return
    
    #showInfo(rev.state)
    #return

    if not rev.state == "question":  # did the user just click to get a new question?
        # Yes  
        return
    # Probably not. # TODO: find something that blocks this when in "question" mode (e.g. on closing the Fields dialog) 

    #import time
    #time.sleep(2)

    #showInfo("pretend this is a grid")
    w = GridDlg(rev)
    screen = QDesktopWidget().screenGeometry()
    w.setGeometry(0, 0, screen.width(), screen.height())
    #w.resize(800, 530)  # dialog window size: W, H
    #w.move(224,150) # TODO: automate this based on screen size, but remember (this session) if the user moves/resizes it. Simplest option is to not to destroy the object on close. 
    w.move(0, 0)
    
    v = w.ui.gridView  # type of v: QtWebKit.QWebView or its AnkiWebView subclass

    #see also: Reviewer._initWeb()
    base = getBase(rev.mw.col)  # this is necessary, or the images won't display  

    html = GridDlg.gridHtml(rev._css, base) #... we insert this once for the whole grid

    callback = lambda x: w.showAnswerGrid(rev.card, rev)

    v.setHtml(html, callback)  # pass in the 'empty' container, plus the function that'll fill it in

    v.show()
    w.show()
        
    #showInfo("The answer is %s" % w.correct)

    if w.exec_():
        # if it returns 1, show the next flashcard
        rev._showAnswer() # WARNING: this could eventually cause a stack overflow, I think, but there's currently no hook for asking Anki to do this for us. -Jon  



origShowQuestion = Reviewer._showQuestion
Reviewer._showQuestion = myShowQuestion




# This UGLY MONKEY PATCh is because the actual code is in the wrong order:

def myInitWeb(self):
    self._reps = 0
    self._bottomReady = False
    base = getBase(self.mw.col)
    # show answer / ease buttons
    self.bottom.web.show()
    self.bottom.web.stdHtml(
        self._bottomHTML(),
        self.bottom._css + self._bottomCSS,
        loadCB=lambda x: self._showAnswerButton())
    # main window
    self.web.stdHtml(self._revHtml, self._styles(),
        loadCB=lambda x: self._showQuestion(),
        head=base)

Reviewer._initWeb = myInitWeb

