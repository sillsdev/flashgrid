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
    origShowQuestion(self) # we're wrapping this, so we'll still run it
    if not GridDlg.gridOn: return
    
    #showInfo(self.state)
    #return

    if not self.state == "question":  # did the user just click to get a new question?
        # Yes  
        return
    # Probably not. # TODO: find something that blocks this when in "question" mode (e.g. on closing the Fields dialog) 

    #import time
    #time.sleep(2)

    #showInfo("pretend this is a grid")
    w = GridDlg(self)
    w.resize(1024, 600)  # dialog window size: W, H
    w.move(100,30) # TODO: automate this based on screen size, but remember (this session) if the user moves/resizes it. Simplest option is to not to destroy the object on close. 
    
    v = w.ui.gridView  # type of v: QtWebKit.QWebView or its AnkiWebView subclass

    #see also: Reviewer._initWeb()
    base = getBase(self.mw.col)  # this is necessary, or the images won't display  

    html = GridDlg.gridHtml(self._css, base) #... we insert this once for the whole grid

    callback = lambda x: self._showAnswerGrid(self.card, w)

    v.setHtml(html, callback)  # pass in the 'empty' container, plus the function that'll fill it in

    v.show()
    w.show()
        
    #showInfo("The answer is %s" % w.correct)

    if w.exec_():
        # if it returns 1, show the next flashcard
        self._showAnswer() # WARNING: this could eventually cause a stack overflow, I think, but there's currently no hook for asking Anki to do this for us. -Jon  


def myShowAnswerGrid(self, card, dialog):
    
    view = dialog.ui.gridView
    
    #view.setHtml( self.web.page().mainFrame().toHtml() )  # DELETE THIS LINE (just a test)
    #return
    
    gridSize = Reviewer.gridSize()

    deckName = mw.col.decks.current()['name']
    cards = mw.col.findCards("-is:suspended deck:%s" % deckName)
    #e.g.  mw.col.findCards('-is:suspended deck:indonesian-lift-dictionary-Orig')

    toInsert = ''
    i = 1
    for c in cards:  # at most; but usually we'll quit at gridSize^2
        if (c == card.id):
            continue
        if (i == dialog.correct):
            cellCard = card
        else:
            cellCard = mw.col.getCard(c) # mw.col.findCards("cid:%s" % c)
            if not cellCard or (cellCard.template() != card.template()):
                continue  # something went wrong finding that card (throw exception?)

        html = renderOneAnswer(self, cellCard)
        toInsert += GridDlg.gridHtmlCell(i, html)  # this += isn't likely to ever get slow, but if so, build an ins[] list and later do ''.join(ins)
        if ((i % gridSize == 0) and (i < gridSize*gridSize)):  # use modulus to identify/create end of row
            toInsert += GridDlg.gridHtmlBetweenRows()

        if (i >= gridSize*gridSize):
            break
        i += 1

    klass = "card card%d" % (card.ord+1)
    toInsert = '<table class="%s"><tbody><tr>%s</tr></tbody></table>' % (klass, toInsert) 
    #test: toInsert += '<img src="file:///c:/Users/user57/Documents/Anki/User 1/collection.media/lift-dictionary_abu.png" />'
    tmp = json.dumps(toInsert)
    tmp = '_append("%s", %s);' % ('insertGridHere', tmp)

    #tmp = '_updateA("%s", %s);' % (str(cellId), html)
    #self.web.eval(tmp)  # NO, instead of the Reviewer doing this, have the view do it
    view.page().mainFrame().evaluateJavaScript(tmp)

    cardFrontHtml = renderOneAnswer(self, card)
    tmp = json.dumps(cardFrontHtml)
    tmp = '_append("%s", %s);' % ('insertFrontHere', tmp)
    view.page().mainFrame().evaluateJavaScript(tmp)

    #self._showEaseButtons() # NO, not in the grid
   
    h = view.page().mainFrame().toHtml()
    h = h.encode('utf-8')
    f = open('gridtemp.tmp.html', 'w')
    f.write(h)
    f.close()
   
    '''
    callback = renderOneAnswer(self, card, view, "1")
    actualCard = AnkiWebView()  # a view we won't actually display, but it renders (off-screen) one cell's HTML for us
    actualCard.stdHtml(self._revHtml, self._styles(),
        loadCB=callback,
        head=base)

    callback = renderOneAnswer(self, card, view, 4)
    actualCard = AnkiWebView()  # a view we won't actually display, but it renders one cell's HTML for us
    actualCard.stdHtml(self._revHtml, self._styles(),
        loadCB=callback,
        head=base)
    '''
    
    
    #frames = v.page().mainFrame().childFrames()
    #for frame in frames:
    #    frame.setHtml(h1)
    #frames[0].setHtml(h2)
    #v.setHtml(h2)
    
    '''
    # need a loop here
    flakCard = AnkiWebView()  # again, a view we won't actually display, but it renders a cell's HTML for us
    flakCard.stdHtml(self._revHtml, self._styles(),
        loadCB=callback,
        head=base)
    '''


def renderOneAnswer(self, card):
    ''' Creates HTML to plug directly in as the specified <TD> table cell.
    '''

    origState = self.state
    self.state = "answer"  # necessary to get correct results from _mungeQA()
    
    c = card
    
    #a = c._getQA()['a'] # without the style info
    a = c.a() # with the style info
    
    # play audio?  # NO, not in the grid (except maybe on hover?)
    #if self.autoplay(c):
    #    playFromText(a)
    # render and update bottom
    
    a = self._mungeQA(a)
    klass = "card card%d" % (c.ord+1)
    #tmp = "_updateA(%s, true, %s);" % (json.dumps(a), klass)

    # DON'T show answer / ease buttons

    self.state = origState

    html = a
    # html = json.dumps(a) # NOT until we've added our html

    # user hook
    #runHook('showAnswer')  # NO, we assume other addons' behavior here is unwanted

    div = '<div class="%s">%s</div>'
    tmp = div % (klass, html)
    return tmp
        
@staticmethod
def myGridSize():
    return Reviewer._gridSize

@staticmethod
def myToggleGridSize():
    Reviewer._gridSize = 3 if (Reviewer._gridSize == 2) else 2
    showInfo("Ok. Toggled to %s x %s." % (Reviewer._gridSize, Reviewer._gridSize))  # msgbox / messagebox

# Do some monkey patching to wrap more functionality around _showQuestion    

origShowQuestion = Reviewer._showQuestion
Reviewer._showQuestion = myShowQuestion

Reviewer._showAnswerGrid = myShowAnswerGrid

# TODO: consider moving gridSize() over to main.py where it would be more legit (i.e. no monkey patch)
Reviewer._gridSize = 2
Reviewer.toggleGridSize = myToggleGridSize
Reviewer.gridSize = myGridSize
