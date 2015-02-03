import string, random, re
from aqt.utils import showInfo
from anki.utils import json
from aqt.utils import restoreGeom, saveGeom
from aqt import mw
from aqt.qt import *
#from aqt.utils import showInfo, askUserDialog, getFile
#from aqt.utils import mungeQA, getBase, openLink, tooltip, askUserDialog
from aqt.webview import AnkiWebView
from aqt.reviewer import Reviewer
from anki.sound import playFromText, clearAudioQueue
from grid import Ui_gridDialog
   # TODO in grid.ui: CHANGES TO REDO IN DESIGNER: use of AnkiWebView; removal of Ok/Cancel buttons
   # OR, eliminate grid.py altogether (it's just one UI element anyway)

def msgBox(m):
    text = '{}\n\n- {}'.format(m, GridDlg._appLabel)
    showInfo(text)

class GridDlg(QDialog):

    _appLabel="FlashGrid v0.14"
    _gridSize = 2
    _gkey = "FlashGridPopup" 
    
    @staticmethod
    def toggleGridSize():
        GridDlg._gridSize = 3 if (GridDlg._gridSize == 2) else 2
        msgBox("Ok. Toggled to %s x %s." % (GridDlg._gridSize, GridDlg._gridSize))  # msgbox / messagebox

    def _myLinkHandler(self, url):
        ''' Handles when the user clicks on a table cell or the Replay Audio link
        '''
        url = url.lower()
        if "closepopup" in url:
            ret = 0
            try:
                label, val = url.split(":")
                val = int(val)
                if (val > 0):
                    ret = val
            except ValueError:
                pass # i.e. ret = 0
            self.closeMaybe(ret)
        
        if "replayaudio" in url:
            mw.reviewer.replayAudio()
            
    def _myKeyHandler(self, evt):
        #key = evt.key()
        key = evt.text().lower()
        if key == u'r':
            mw.reviewer.replayAudio()
            return

        ua = unicode(string.lowercase, errors='ignore')
        if key and key in ua:
            number = GridDlg.toNumber(key)
            self.closeMaybe(number)
                

    def closeMaybe(self, n):
        self.saveGeo()
        if (n == 0 or n == self.correct):  # 0 = cancel
            self.done(n)
            
    def __init__(self, reviewer):
        QDialog.__init__(self)
        
        # Create the UI dialog (created using Qt Designer)
        self.ui = Ui_gridDialog()
        self.ui.setupUi(self)

        v = self.ui.gridView
        v.setLinkHandler(self._myLinkHandler)
        v.setKeyHandler(self._myKeyHandler)
        
        # WARNING: the following could interfere with other addons, or future versions of Anki
        #reviewer.web.setKeyHandler(self._myKeyHandler) # just for convenience, when the grid isn't showing
        
        self.correct = random.randint(1, GridDlg._gridSize**2)  # e.g. a number from 1 to 4 (inclusive)

        # Connect up the buttons.
        #self.ui.okButton.clicked.connect(self.accept)
        #self.ui.cancelButton.clicked.connect(self.reject)    

        # Prepare the HTML container (i.e. grid without flashcard content)

    def setGeo(self):
        gkey = GridDlg._gkey
        mem = gkey + "Geom" in mw.pm.profile
        if not mem:
            # I have no memory of this...
            screen = QDesktopWidget().screenGeometry()
            screen = QDesktopWidget().availableGeometry() 
            width = screen.width() - 10
            height = screen.height() - 20
            self.setGeometry(0, 0, width, height) # may be too big, esp. if primary monitor is not the highest res
            self.show() # detect and adjust if the window got sized down by the OS (usually it's just a few pixels)
            self.move(0, 0)
        else:
            # I remember a size and location
            restoreGeom(self, gkey, offset=None, adjustSize=False)
            self.show()

    def saveGeo(self):
        saveGeom(self, GridDlg._gkey)  # remember this size and location for next time

    @staticmethod
    def resetGeo():
        tmp = mw.pm.profile.pop(GridDlg._gkey + "Geom", None)  # forget any size/location info we might have
        return tmp
         
    
    @staticmethod
    def toLetter(n):
        letters = string.lowercase  #OR alphabet = string.letters[26:52] # grabbing the lowercase ones 
        tmp = letters[n-1]
        return tmp
    
    @staticmethod
    def toNumber(c):
        tmp = ord(c) - ord('a') + 1   # our numbering scheme is not zero-based
        return tmp
    
    def showAnswerGrid(self, card, rev):
        dialog = self
        
        view = dialog.ui.gridView
    
        cardFrontHtml = renderOneQA(rev, card, "question")
        tmp = json.dumps(cardFrontHtml)
        tmp = '_append("%s", %s);' % ('fgCardFront', tmp)
        view.page().mainFrame().evaluateJavaScript(tmp)
       
        gridw = GridDlg._gridSize
        gridh = gridw # still assuming a square grid (for now anyway)
        size = gridh*gridw
        
        dummy = '''
not found
'''
        cards = [dummy for i in range(size)] # i.e. 4 or 9 dummies
        cards[dialog.correct-1] = renderOneQA(rev, card, "answer")  # put in the real answer 
    
        deckName = mw.col.decks.current()['name']
        search = '-is:suspended deck:"%s"' % deckName
        cardsFound = mw.col.findCards(search)  #e.g.  '-is:suspended deck:indonesian-lift-dictionary-Orig'
        random.shuffle(cardsFound)
        cardsFound = cardsFound or []
        
        i = 0
        for c in cardsFound:  # at most; but usually we'll quit after gridw*gridh
            id = i+1  # these are offset by one since grid's id-numbering is 1-based but array is 0-based
            if (id > size):
                break
            if (c == card.id) or (id == dialog.correct):  # don't use current card nor steal its cell
                i += 1
                continue
            else:
                cellCard = mw.col.getCard(c) # mw.col.findCards("cid:%s" % c)
                if not cellCard or (cellCard.template() != card.template()):
                    # do NOT increment i
                    continue  # something went wrong finding that card (throw exception?)
    
            cards[i] = renderOneQA(rev, cellCard, "answer")
    
            i += 1
        
        klass = "card card%d" % (card.ord+1)

        for i in range(size):
            txt = cards[i]
            id = i+1
            cards[i] = '<td class="%s">%s</td>' % (klass, gridHtmlCell(id, txt))
            if ((id % gridw == 0) and (id < size)):  # use modulus to identify/create end of row
                cards[i] += gridHtmlBetweenRows()

        toInsert = '\n'.join(cards)
    
        toInsert = '''<table class="%s"><tbody><tr>
        %s
        </tr></tbody></table>''' % (klass, toInsert) 

        tmp = json.dumps(toInsert)
        tmp = '_append("%s", %s);' % ('fgCardGridArea', tmp)
    
        #self.web.eval(tmp)  # NO, instead of the Reviewer doing this, have the popup view do it
        view.page().mainFrame().evaluateJavaScript(tmp)
    
        #self._showEaseButtons() # NO, not in the grid
       
        h = view.page().mainFrame().toHtml()
        h = h.encode('utf-8')
        f = open('gridtemp.tmp.html', 'w')  # this file is very helpful when debugging, because you can open it in a browser, experiment with its CSS, etc. 
        f.write(h)
        f.close()
        
def renderOneQA(rev, card, qa = "answer"):
    ''' Creates HTML to plug into the specified grid cell.
    '''

    origState = rev.state
    rev.state = qa  # necessary to get correct results from _mungeQA()
    
    c = card
    
    if qa == "answer":
        html = c.a()  #BACK

        #if there's a way to reach in and remove CardFront
        #before it is rendered to html, that would be better.
        '''
        afmt = c.template()['afmt']
        if GridDlg.needRemoveFront(afmt):
            af = removeFront(afmt)
            # temporarily swap afmt and af
        '''
    else:
        html = c.q()  #FRONT
    
    # play audio?  # NO, not in the grid
    
    html = rev._mungeQA(html)
    html = removeFront(html)
    a = html
    klass = "card card%d" % (c.ord+1)
    #tmp = "_updateA(%s, true, %s);" % (json.dumps(a), klass)

    # DON'T show answer / ease buttons

    rev.state = origState

    html = a
    # html = json.dumps(a) # NOT until we've added our html

    # user hook
    #runHook('showAnswer')  # NO, we assume other addons' behavior here is unwanted

    return html

    tmp = '<div class="%s">%s</div>' % (klass, html)  # problem: it's hard to stretch this div vertically to fill its containing td
    return tmp

    #Would using frames (iframes) allow us to zoom out instead of trying to resize images and fonts?        
    #frames = v.page().mainFrame().childFrames()
    #for frame in frames:
    #    frame.setHtml(h1)
    #frames[0].setHtml(h2)
    #v.setHtml(h2)
    

'''    
def needRemoveFront(cardString):
    return ("{{FrontSide}}" in cardString) or ("<hr" in cardString) 
'''

def removeFront(cardString):
    s2 = s = cardString
    #pat = '(?s){{FrontSide}}.*<hr.*?>'
    #s2 = re.sub(pat, '', s)
    #pat = '(?s)({{FrontSide}}|<hr.*?>)'  # use this if we get the monkey patch working
    pat = '(?s)</style>.*?<hr.*?>'  # for now, just chop off anything preceding the first <hr>, if one exists 
    s3 = re.sub(pat, '</style>', s2)
    return s3

'''    
def extractStyle(html):
    s, h = '', html
    import re
    pat = "(?s)<style>.*?</style>"
    match = re.search(pat, html)
    if match:
        s = match.group(0)
        html = re.sub(pat, '', html)
    return s, h
'''
   
def gridHtmlCell(cellId, content, linkLabel=None):
    ''' To get no label, you must explicitly pass in an empty string.
    '''
    if (linkLabel != ''):
        cellLetter = GridDlg.toLetter(cellId)
        linkLabel = '%s.' % cellLetter
    else:
        linkLabel = ''
    
    #cellLetter = GridDlg.toLetter(cellId)
    
    tmp = '''<a href="closePopup:%s">
  %s <br/>
%s</a>
''' % (cellId, linkLabel, content)
    return tmp
    
    tmp = '''
<div id="%s" class="card" style="cursor:pointer">
  <a href="closePopup:%s">
  %s <br/>
%s</a>
</div>
''' % (cellId, cellId, linkLabel, content)
    return tmp

def gridHtmlBetweenRows(): 
    return '''
</tr><tr>
'''
        
        
def gridHtml(style='', head='', klass='card', width=800-20, height=600-40):
    # TODO: find a way to use % rather than px in the CSS, yet still handle vertical spacing
    
    buffer = 20
    maxCellW = (width / (GridDlg._gridSize + 1)) - buffer
    maxImgW = int( maxCellW * 0.8 )  # image shouldn't use more than 80% of a cell's width
    maxCellH = (height / GridDlg._gridSize) - buffer
    maxImgH = int( maxCellH * 0.7 )
    
    # works for img, but not sure how to use maxImgH to enforce the max cell height
    
    rowHeight = int (100 / GridDlg._gridSize)  # gives a pct: 50% or 33%  
    
    
    replayAudio = '<a href="replayAudio">Replay Audio</a>'
    
    mainHtml = '''
<!doctype html>
<html>

<head><meta charset="utf-8"/>
<style>
/* from Anki: */
button {
font-weight: normal;
}

%s

/* unique to FlashGrid */
html, body, table { height:%spx; max-height:%spx; table-layout:fixed}  /* 100%% height doesn't appear to work; 'fixed' gives equal column widths */
img { max-width: %spx; max-height: %spx; }
#fgDialog {position:absolute; width:92%%; height:86%%}
  #fgFrontArea {position:absolute; width:20%%; height 100%%;}
    #fgCardFront  {width:100%%; }
    #typeans { width: 80%% }
  #fgCardGridArea {position:absolute; right:0; width:77%%; height 100%%;}
    table {width:100%%;}
      td {text-align:left; border:2px solid white;}
      tr {height: %s%%;}
      table.card td {vertical-align:top; cursor:pointer;}
      table.card td a {display:block; text-decoration:none; height:100%%;}
      table.card td:hover {background:#CCCCCC;color:#CCCCFF} /* */
</style>
<script>
function _append (id, t) {
  var target = document.getElementById(id);
  target.innerHTML += t;
}
</script>
%s
</head>
<body class="">
<!-- <div id=qa></div>
<p><a href="closePopup">close</a></p> -->

<div id="fgDialog">  <!-- outer 'table', 1x2 -->

  <!-- show front of main card on the left -->
  <div id="fgFrontArea">
    <div id="fgCardFront" class="%s"></div>
    <p>%s</p>
    <p>%s</p>
  </div>

  <!-- inner table, will be NxN based on gridSize setting -->


  <div id="fgCardGridArea"></div>


</div> 
</body>

</html>
''' % (style, height, height, maxImgW, maxImgH, rowHeight, head, klass, replayAudio, GridDlg._appLabel)
    return mainHtml

GridDlg.gridOn = True

def onGridOffOnClicked():
    GridDlg.gridOn = not GridDlg.gridOn
    if GridDlg.gridOn:
        tmp = "On."
    else: 
        tmp = "Off. Popup window size reset."
        GridDlg.resetGeo()
        
    msgBox("FlashGrids are now %s" % (tmp))  # msgbox / messagebox

def onSizeClicked():
    from aqt.reviewer import Reviewer
    GridDlg.toggleGridSize()

stringGen = "FlashGrid toggle off/on"
# create a new menu item in Anki
action = QAction(stringGen, mw)
# set it to call our function when it's clicked
mw.connect(action, SIGNAL("triggered()"), onGridOffOnClicked)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

action = QAction("FlashGrid toggle grid size", mw)
mw.connect(action, SIGNAL("triggered()"), onSizeClicked)
mw.form.menuTools.addAction(action)


