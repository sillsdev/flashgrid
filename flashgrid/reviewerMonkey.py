''' This is an addon (/extension/plugin) to the Reviewer class found in reviewer.py
It adds a grid dialog (currently as a popup window)
'''

# This 'monkey' file is responsible for loading FlashGrid and some workarounds.
# It no longer actually includes any monkey patches

from aqt.reviewer import Reviewer
from aqt import mw
from anki.utils import isWin
from flashgrid.main import GridDlg, msgBox
#import flashgrid.main

# This workaround doesn't work all that well yet. It's here because Anki triggers showQuestion too often. 
Reviewer._cardJustShown = None 
def staleCard(card):
    sh = Reviewer._cardJustShown
    if sh and sh == card.id:
        # Bail. They probably just opened and closed a dialog box.
        return True
    Reviewer._cardJustShown = card.id
    return False

def reset():
    Reviewer._cardJustShown = None    

# modified from old aqt.utils library
def getBase(col):
    base = col.media.dir()
    if base.endswith("\\") or base.endswith("/"):
        return base
    elif isWin:
        return base + "\\"
    else:
        return base + "/"

# Returns True if we should advance to the Answer (because user clicked the correct answer cell)
def doGrid():
    if not GridDlg.gridOn(): return False
    rev = mw.reviewer
    
    if not rev.state == "question":  # did the user just click to get a new question?
        return False # No
    # Probably Yes
    
    if staleCard(rev.card):
        return False # No, actually. We already just showed this card

    w = GridDlg(rev)
    w.setCloseCallback(onCloseCallback)
    w.setGeo()
    base = getBase(rev.mw.col)  # this is necessary, or the images won't display
    w.showAnswerGrid(rev.card, rev, base)
    #with open("flipgrid.tmp.html","w") as f:
    #    f.write(html)
    w.show()

# A. Using the standard hook Anki provides.
def onShowQuestion():
    doGrid()

def onCloseCallback(result):
    if result:
        rev = mw.reviewer
        rev._showAnswer()

from anki.hooks import addHook
addHook('showQuestion', onShowQuestion)
addHook('reviewCleanup', reset)

### ALL OLD CODE BELOW - DO NOT USE

# from aqt.qt import *
# from aqt.webview import AnkiWebView

# The following patch to Reviewer._initWeb works fine but is not guaranteed
# to work with future versions of Anki. Only enable it if there is a developer
# actively maintaining FlashGrid.

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

# This MONKEY PATCH fixes a bug where the Anki code is in the wrong order, resulting in this bug.
# BUG: first card does not auto-advance when the user clicks the correct grid cell. Subsequent cards do.
'''
def myInitWeb(self):
    self._reps = 0
    self._bottomReady = False
    #base = getBase(self.mw.col)
    base = self.mw.col
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

''' OLD CODE 

# from staleCard

    #tmp = 'showing %s %s ...' % ( sh, card.note().values() )
    #print tmp  #showInfo(tmp)  #Anki messagebox / msgbox

# from doGrid


    #html = gridHtml(rev._css, base, klass, width, height - buffer) #... we insert this once for the whole grid
    #v.setHtml(html, callback)  # pass in the 'empty' container, plus the function that'll fill it in
    # callback = lambda x: w.showAnswerGrid(rev.card, rev)

    # note: we expect type of v to be: (PDB updated QWebEngineView or AnkiWebView subcass)

    # would prefer Qt.ScrollBarAsNeeded but somehow this object thinks it's always needed
    # PDB off for now
    #v.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
    #v.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAsNeeded)

    #see also: Reviewer._initWeb()
    
# from getBase (which was copied from old awt.utils code after it was removed
    import urllib.parse
    
    #mdir = urllib.parse.quote(mdir.replace("\\", "/"), safe=":/")
    #if isWin and not mdir.startswith(r"//"):
    #    prefix = "file:///"
    #else:
    #    prefix = "file://"
    #base = prefix + mdir + "/"
    #if justURL:
    #    return base
    #else:
    #    return '<base href="%s" />' % base

'''
