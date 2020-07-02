import string, random, re
from aqt.utils import showInfo
#from anki.utils import json
from aqt.utils import restoreGeom, saveGeom
from aqt import mw
from aqt.qt import *
from aqt.webview import AnkiWebView
from aqt.reviewer import Reviewer
from .grid import Ui_gridDialog
from PyQt5 import QtCore

   # TODO in grid.ui: CHANGES TO REDO IN DESIGNER: use of AnkiWebView; removal of Ok/Cancel buttons
   # OR, eliminate grid.py altogether (it's just one UI element anyway)
   # Modified 26 June 2020 to remove 'not found' messages - we eliminate the card in question
   # from the list.
def msgBox(m):
    text = '{}\n\n- {}'.format(m, GridDlg._appLabel)
    showInfo(text)

class GridDlg(QDialog):

    _appLabel = "FlashGrid v0.23"
    _gridSize = 2
    _gkey = "FlashGridPopup"
    _closepopupCommand = "http://closepopup"
    _replayaudioCommand = "http://replayaudio"

    @staticmethod
    def gridOn():
        if 'FlashGrid' not in mw.col.conf:
            mw.col.conf['FlashGrid'] = {'gridOn': True}
        return mw.col.conf['FlashGrid']['gridOn']

    @staticmethod
    def setGridOn(val):  # assumption: gridOn() will always have been called at least once before this
        mw.col.conf['FlashGrid']['gridOn'] = val
    
    @staticmethod
    def toggleGridSize():
        GridDlg._gridSize = 3 if (GridDlg._gridSize == 2) else 2
        msgBox("Ok. Toggled to %s x %s." % (GridDlg._gridSize, GridDlg._gridSize))  # msgbox / messagebox

    def setCloseCallback(self, cb):
        self._onClose = cb

    def handleLinkClick(self, url):
        # Handles when the user clicks on a table cell or the Replay Audio link
        url = url.lower()
        if GridDlg._closepopupCommand.lower() in url:
            ret = 0
            try:
                label, val = url.split("#")
                val = int(val[:-1]) # extract the user's clicked number
                if (val > 0):
                    ret = val
            except ValueError:
                pass # i.e. ret = 0
            self.closeMaybe(ret)
        
        if GridDlg._replayaudioCommand.lower() in url:
            mw.reviewer.replayAudio()
            
    def _myKeyHandler(self, evt):
        key = evt.text().lower()
        if key == 'r':
            mw.reviewer.replayAudio()
            return

        if key and key in string.ascii_lowercase:
            number = GridDlg.toNumber(key)
            self.closeMaybe(number)


    def closeMaybe(self, n):
        self.saveGeo()
        if n == 0: # 0 = cancel
            if self._onClose:
                self._onClose(False)
            self.done(n)
        elif n == self.correct:
            if self._onClose:
                self._onClose(True)
            self.done(n)


    def __init__(self, reviewer):
        QDialog.__init__(self)
        
        # Create the UI dialog (created using Qt Designer)
        self.ui = Ui_gridDialog()
        self.ui.setupUi(self)

        # set modal
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        v = self.ui.gridView
        v._page.setLinkHandler(self)
        self.keyPressEvent = self._myKeyHandler

        self.correct = random.randint(1, GridDlg._gridSize ** 2)  # e.g. a number from 1 to 4 or 9 (inclusive)


    def setGeo(self):
        gkey = GridDlg._gkey
        mem = gkey + "Geom" in mw.pm.profile
        if not mem:
            # I have no memory of this...
            screen = QDesktopWidget().screenGeometry()
            screen = QDesktopWidget().availableGeometry() 
            width = screen.width() - 10
            height = screen.height() - 25
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
        return mw.pm.profile.pop(GridDlg._gkey + "Geom", None)  # forget any size/location info we might have
         
    
    @staticmethod
    def toLetter(n):
        return string.ascii_lowercase[n - 1]

    
    @staticmethod
    def toNumber(c):
        return ord(c) - ord('a') + 1   # our numbering scheme is not zero-based
    
    def showAnswerGrid(self, card, rev, baseURL):
        dialog = self
        view = dialog.ui.gridView

        # set commands on the custom page to recognise special link handler
        view.page().setSpecialLinks([GridDlg._closepopupCommand, GridDlg._replayaudioCommand])

        cardFrontHtml = renderOneQA(rev, card, "question")

        klass = "card card{}".format(card.ord + 1)
        width = int(0.96 * self.size().width())
        height = int(0.96 * self.size().height())
        buffer = 60 # e.g. for the window's title bar, and a bottom 'margin'
        html = gridHtml('', klass, width, height - buffer)

        htmlFinal = html.replace("##fgCardFront##", cardFrontHtml)

        gridw = GridDlg._gridSize
        size = gridw ** 2 # still assuming a square grid (for now anyway)
        
        dummy = '\nnot found\n'
        cards = [dummy for i in range(size)] # i.e. 4 or 9 dummies
        cards[dialog.correct-1] = renderOneQA(rev, card, "answer")  # put in the real answer 
    
        deckName = mw.col.decks.current()['name']
        search = '-is:suspended deck:"{}"'.format(deckName)
        cardsFound = mw.col.findCards(search)  # e.g.  '-is:suspended deck:indonesian-lift-dictionary-Orig'
        cardsFound = cardsFound or [] # using object or evaluation to ensure list
        random.shuffle(cardsFound)
        
        i = 0
        for c in cardsFound:  # at most; but usually we'll quit after gridw*gridh
            if c is None: # If c is empty, do no more
                continue
            id = i + 1  # these are offset by one since grid's id-numbering is 1-based but array is 0-based
            if id > size:
                break
            if c == card.id or id == dialog.correct:  # don't use current card nor steal its cell
                i += 1
                continue
            else:
                cellCard = mw.col.getCard(c)
                if cellCard is None or (cellCard.template() != card.template()):
                    # do NOT increment i
                    continue  # something went wrong finding that card (throw exception?)
            thecard =  renderOneQA(rev, cellCard, "answer")
            if thecard is None:
                continue # Did not get a valid card, so get the next one
            cards[i] = thecard

            i += 1
        counter = 0 # We use a counter so we can handle missing cells
        for i in range(size):
            drop = True
            try:
                drop = cards[i] == '\nnot found\n'
            except IndexError:
                continue # Do nothing
            if drop:
               cards[i] = "" # empty cell?
            else:
                counter += 1 # increment
                id = i + 1
                cards[i] = '<td class="{}">{}</td>'.format(klass, gridHtmlCell(id, cards[i]))
            if counter % gridw == 0 and id < size:  # use modulus to identify/create end of row
                    cards[i] += gridHtmlBetweenRows()

        toInsert = '\n'.join(cards)
    
        toInsert = '''<table class="{}"><tbody><tr>
        {}
        </tr></tbody></table>'''.format(klass, toInsert)

        htmlFinal = htmlFinal.replace("##fgCardGridArea##", toInsert)
         # enable for debug saving:
        #  htmlRender(htmlFinal)
        view.page().setHtml(htmlFinal, QUrl.fromLocalFile(baseURL))

        # enable for debug saving:
        # htmlRender(htmlFinal)


def htmlRender(html):
    # this typically saves in the collections.media folder under the user app data
    with open('gridtemp.tmp.html', 'w', encoding='utf-8') as f:
        f.write(html)


def renderOneQA(rev, card, qa = "answer"):
    # Creates HTML to plug into the specified grid cell.

    origState = rev.state
    rev.state = qa  # necessary to get correct results from _mungeQA()

    # back or front of card depending on qa
    html = card.a() if qa == "answer" else card.q()
    
    # play audio?  # NO, not in the grid
    html = rev._mungeQA(html)
    html = removeFront(html)

    # DON'T show answer / ease buttons

    rev.state = origState

    return html


def removeFront(cardString):
    pat = '(?s)</style>.*?<hr.*?>'  # for now, just chop off anything preceding the first <hr>, if one exists
    return re.sub(pat, '</style>', cardString)

def gridHtmlCell(cellId, content, linkLabel=None):
    # To get no label, you must explicitly pass in an empty string.
    if linkLabel != '':
        cellLetter = GridDlg.toLetter(cellId)
        linkLabel = '{}.'.format(cellLetter)
    else:
        linkLabel = ''

    # PDB all url formats must start http:// to be a valid QUrl
    return '<a href="{}#{}/">{}<br/>{}</a>'.format(GridDlg._closepopupCommand, cellId, linkLabel, content)


def gridHtmlBetweenRows():
    return '\n</tr><tr>\n'

def gridHtml(style='', klass='card', width = 800-20, height = 600-40):
    # TODO: find a way to use % rather than px in the CSS, yet still handle vertical spacing
    buffer = 20
    maxCellW = (width / (GridDlg._gridSize + 1)) - buffer
    maxImgW = int( maxCellW * 0.8 )  # image shouldn't use more than 80% of a cell's width
    maxCellH = (height / GridDlg._gridSize) - buffer
    maxImgH = int( maxCellH * 0.7 )
    # works for img, but not sure how to use maxImgH to enforce the max cell height
    rowHeight = int (100 / GridDlg._gridSize)  # gives a pct: 50% or 33%
    replayAudio = '<a href="{}/">Replay Media</a>'.format(GridDlg._replayaudioCommand)
    mainHtml = '''
<!doctype html>
<html>

<head><meta charset="utf-8"/>
<style>
/* from Anki: */

/* note double braces here & through-out this literal in the python code for escaping */
button {{
font-weight: normal;
}}

{}

/* unique to FlashGrid */
html, body, table {{height:{}px; max-height:{}px; table-layout:fixed;}}  /* 100% height doesn't appear to work; 'fixed' gives equal column widths  */
img {{ max-width: {}px; max-height: {}px; }}
#fgDialog {{position:absolute; width:92%; height:86%}}
  #fgFrontArea {{position:absolute; width:20%; height 100%;}}
    #fgCardFront  {{width:100%; }}
    #typeans {{ width: 80% }}
  #fgCardGridArea {{position:absolute; right:0; width:77%; height 100%;}}
    table {{width:100%;}}
      td {{text-align:left; border:2px solid white;}}
      tr {{height: {}%;}}
      table.card td {{vertical-align:top; cursor:pointer;}}
      table.card td a {{display:block; text-decoration:none;}} /* height:100%; */
      table.card td:hover {{background:#CCCCCC;color:#CCCCFF}} /* */
</style>
</head>
<body class="">
<!-- <div id=qa></div>
<p><a href="http://closePopup/">close</a></p> -->

<div id="fgDialog">  <!-- outer 'table', 1x2 -->

  <!-- show front of main card on the left -->
  <div id="fgFrontArea">
    <div id="fgCardFront" class="{}">##fgCardFront##</div>
    <p>{}</p>
    <p>{}</p>
  </div>

  <!-- inner table, will be NxN based on gridSize setting -->


  <div id="fgCardGridArea">##fgCardGridArea##</div>


</div> 
</body>

</html>
'''.format(style, height, height, maxImgW, maxImgH, rowHeight, klass, replayAudio, GridDlg._appLabel)
    return mainHtml

def onGridOffOnClicked():
    GridDlg.setGridOn(not GridDlg.gridOn())  #toggle
    if GridDlg.gridOn():
        tmp = "On."
    else: 
        tmp = "Off. Popup window size reset."
        GridDlg.resetGeo()

    msgBox("FlashGrids are now {}".format(tmp))

def onSizeClicked():
    GridDlg.toggleGridSize()

mw.form.menuTools.addSeparator()
stringGen = "FlashGrid toggle off/on"
# create a new menu item in Anki
action = QAction(stringGen, mw)
# set it to call our function when it's clicked
action.triggered.connect(onGridOffOnClicked)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

action = QAction("FlashGrid toggle grid size", mw)
action.triggered.connect(onSizeClicked)
mw.form.menuTools.addAction(action)

''' OLD CODE

#from aqt.utils import showInfo, askUserDialog, getFile
#from aqt.utils import mungeQA, getBase, openLink, tooltip, askUserDialog
from anki.sound import playFromText, clearAudioQueue

from showAnswerGrid:
        # tmp = json.dumps(cardFrontHtml)
        # tmp = '_append("%s", %s);' % ('fgCardFront', tmp)
        #view.page().mainFrame().evaluateJavaScript(tmp)
        #PDB
        # view.eval(tmp)
        
        #tmp = json.dumps(toInsert)
        #tmp = '_append("%s", %s);' % ('fgCardGridArea', tmp)

        #view.page().mainFrame().evaluateJavaScript(tmp)
        # PDB
        #view.eval(tmp)
        #  view.page().toHtml(htmlRenderCallback)   
        
from gridHtml:

#cellLetter = GridDlg.toLetter(cellId)

from onSizeClicked:

    from aqt.reviewer import Reviewer

def extractStyle(html):
    s, h = '', html
    import re
    pat = "(?s)<style>.*?</style>"
    match = re.search(pat, html)
    if match:
        s = match.group(0)
        html = re.sub(pat, '', html)
    return s, h


from renderOneQA:


    a = html   
    html = a
        #if there's a way to reach in and remove CardFront
        #before it is rendered to html, that would be better.
        afmt = c.template()['afmt']
        if GridDlg.needRemoveFront(afmt):
            af = removeFront(afmt)
            # temporarily swap afmt and af   
    #tmp = "_updateA(%s, true, %s);" % (json.dumps(a), klass)


    tmp = '<div class="%s">%s</div>' % (klass, html)  # problem: it's hard to stretch this div vertically to fill its containing td
    return tmp

    #Would using frames (iframes) allow us to zoom out instead of trying to resize images and fonts?
    #frames = v.page().mainFrame().childFrames()
    #for frame in frames:
    #    frame.setHtml(h1)
    #frames[0].setHtml(h2)
    #v.setHtml(h2)

def needRemoveFront(cardString):
    return ("{{FrontSide}}" in cardString) or ("<hr" in cardString) 

from removeFront:
    s2 = s = cardString
    #pat = '(?s){{FrontSide}}.*<hr.*?>'
    #s2 = re.sub(pat, '', s)
    #pat = '(?s)({{FrontSide}}|<hr.*?>)'  # use this if we get the monkey patch working  

javascript from the html template in the head - no longer used

<script>
function _append (id, t) {
  var target = document.getElementById(id);
  target.innerHTML += t;
}
</script>

'''
