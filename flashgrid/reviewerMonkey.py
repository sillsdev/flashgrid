''' This is a monkey patch on reviewer.py
It adds a grid dialog in a popup window
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
    #showInfo(self.state)
    #return

    if not self.state == "question":  # did the user just click to get a new question?
        # Yes  
        return
    # Probably not. # TODO: find something that blocks this when in "question" mode (e.g. on closing the Fields dialog) 

    #showInfo("pretend this is a grid")
    w = GridDlg(self, Reviewer.gridSize())
    w.resize(800, 600)  # W, H
    
    v = w.ui.gridView  # type of v: QtWebKit.QWebView or its AnkiWebView subclass

    #see also: Reviewer._initWeb()
    base = getBase(self.mw.col)  # this is necessary, or the images won't display  

    html = GridDlg.gridHtml(self._css, base) #... we insert this once for the whole grid

    callback = lambda x: self._showAnswerGrid(self.card, v)

    v.setHtml(html, callback)  # pass in the 'empty' container, plus the function that'll fill it in

    v.show()
    w.show()
        
    showInfo("The answer is %s" % w._correct)

    if w.exec_():
        # if it returns 1, show the next flashcard
        self._showAnswer() # WARNING: this could eventually cause a stack overflow, I think, but there's currently no hook for asking Anki to do this for us. -Jon  


def myShowAnswerGrid(self, card, view):
    
    #view.setHtml( self.web.page().mainFrame().toHtml() )  # DELETE THIS LINE (just a test)
    #return
    
    gridSize = Reviewer.gridSize()

    toInsert = ''
    for i in range(1, gridSize*gridSize+1):
        html = renderOneAnswer(self, card, view, i)  # TODO: remove view, i
        toInsert += GridDlg.gridHtmlCell(i, html)  # this += isn't likely to ever get slow, but if so, build an ins[] list and later do ''.join(ins)
        if ((i % gridSize == 0) and (i < gridSize*gridSize)):  # use modulus to identify/create end of row
            toInsert += GridDlg.gridHtmlBetweenRows()

    klass = "card card%d" % (card.ord+1)            
    toInsert = '<table class="%s"><tbody><tr>%s</tr><tbody></table>' % (klass, toInsert)
    #test: toInsert += '<img src="file:///c:/Users/user57/Documents/Anki/User 1/collection.media/lift-dictionary_abu.png" />'
    tmp = json.dumps(toInsert)
    tmp = '_append("%s", %s);' % ('insertHere', tmp)

    #tmp = '_updateA("%s", %s);' % (str(cellId), html)
    #self.web.eval(tmp)  # NO, instead of the Reviewer doing this, have the view do it
    view.page().mainFrame().evaluateJavaScript(tmp)

    #self._showEaseButtons() # NO, not in the grid
   
    h = view.page().mainFrame().toHtml()
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


def renderOneAnswer(self, card, view, cellId):
    ''' Creates HTML to plug directly in as the specified <TD> table cell.
    cellId is an integer ID or int as a string, e.g. 2 or "2"
    '''

    origState = self.state
    self.state = "answer"  # necessary to get correct results from _mungeQA()
    
    c = card
    
    #a = c._getQA()['a'] # without the style info
    a = c.a() # NO, we don't want the style info
    
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
    showInfo("Ok. Toggled to %s." % Reviewer._gridSize)

# Do some monkey patching to wrap more functionality around _showQuestion    

origShowQuestion = Reviewer._showQuestion
Reviewer._showQuestion = myShowQuestion

Reviewer._showAnswerGrid = myShowAnswerGrid

# TODO: consider moving gridSize() over to main.py where it would be more legit (no moenkey patch)
Reviewer._gridSize = 2
Reviewer.toggleGridSize = myToggleGridSize
Reviewer.gridSize = myGridSize
