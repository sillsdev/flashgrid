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
from main import GridDlg, gridHtml

# This workaround doesn't work all that well yet. It's here because Anki triggers showQuestion too often. 
Reviewer._cardJustShown = None 
def staleCard(card):
    #global _cardJustShown
    sh = Reviewer._cardJustShown
    if sh and sh == card.id:
        # Bail. They probably just opened and closed a dialog box.
        #print 'bail'
        return True
    #tmp = 'showing %s %s ...' % ( sh, card.note().values() )
    #print tmp  #showInfo(tmp)  #Anki messagebox / msgbox
    Reviewer._cardJustShown = card.id
    return False

def reset():
    Reviewer._cardJustShown = None    

# Returns True if we should advance to the Answer (because user clicked the correct answer cell)
def doGrid():
    
    if not GridDlg.gridOn: return False

    rev = mw.reviewer
    
    if not rev.state == "question":  # did the user just click to get a new question?
        return False # No
    # Probably Yes
    
    if staleCard(rev.card):
        return False # No, actually. We already just showed this card

    print 'show grid'

    #import time
    #time.sleep(2)

    w = GridDlg(rev)
    screen = QDesktopWidget().screenGeometry()
    w.setGeometry(0, 0, screen.width(), screen.height())
    #w.resize(800, 530)  # dialog window size: W, H
    #w.move(224,150) # TODO: automate this based on screen size, but remember (this session) if the user moves/resizes it. Simplest option is to not to destroy the object on close. 
    w.move(0, 0)
    
    v = w.ui.gridView  # type of v: QtWebKit.QWebView or its AnkiWebView subclass

    #see also: Reviewer._initWeb()
    base = getBase(rev.mw.col)  # this is necessary, or the images won't display; however, it complicates links  

    klass = "card card%d" % (rev.card.ord+1)
    html = gridHtml(rev._css, base, klass) #... we insert this once for the whole grid

    callback = lambda x: w.showAnswerGrid(rev.card, rev)

    v.setHtml(html, callback)  # pass in the 'empty' container, plus the function that'll fill it in

    v.show()
    w.show()

    if w.exec_():
        # show the next flashcard
        return True
    return False

# Of _showAnswer() and _showAnswerHack(), which is better?

# A. Using the standard hook Anki provides.
def onShowQuestion():
    rev = mw.reviewer
    if doGrid():
        rev._showAnswerHack() # WARNING: I suspect that calling this repeatedly could eventually cause a stack overflow, but there's currently no hook for asking Anki to do this for us. -Jon

from anki.hooks import addHook
addHook('showQuestion', onShowQuestion)
addHook('reviewCleanup', reset)

# B. Using a monkey patch.
'''
Reviewer._origShowQuestion = Reviewer._showQuestion
def myShowQuestion(self):
    Reviewer._origShowQuestion(self)
    rev = mw.reviewer
    if doGrid():
        rev._showAnswerHack()
Reviewer._showQuestion = myShowQuestion
'''

# This MONKEY PATCH fixes a bug where the Anki code is in the wrong order
# BUG: first card does not auto-advance when the user clicks the correct grid cell. Subsequent cards do.
'''
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

Reviewer._initWeb = myInitWeb  # apply the patch
'''
