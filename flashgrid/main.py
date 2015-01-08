import string, random, re
from aqt.utils import showInfo
from anki.utils import json
from aqt import mw
from aqt.qt import *
#from aqt.utils import showInfo, askUserDialog, getFile
#from aqt.utils import mungeQA, getBase, openLink, tooltip, askUserDialog
from aqt.webview import AnkiWebView
from aqt.reviewer import Reviewer
from grid import Ui_gridDialog
   # TODO in grid.ui: CHANGES TO REDO IN DESIGNER: use of AnkiWebView; removal of Ok/Cancel buttons
   # OR, eliminate grid.py altogether (it's just one UI element anyway)


class GridDlg(QDialog):

    _gridSize = 2
    def toggleGridSize(self):
        GridDlg._gridSize = 3 if (GridDlg._gridSize == 2) else 2
        showInfo("Ok. Toggled to %s x %s." % (GridDlg._gridSize, GridDlg._gridSize))  # msgbox / messagebox

    def myLinkHandler(self, url):
        ''' Method for AnkiWebView. Currently being patched into the view object in our dialog.
        TODO: Consider subclassing instead.
        '''
        if url.lower().startswith("closePopup".lower()):
            ret = 0
            try:
                label, val = url.split(":")
                val = int(val)
                if (val > 0):
                    ret = val
            except ValueError:
                pass # i.e. ret = 0
            self.closeMaybe(ret)

    def closeMaybe(self, n):
        if (n == 0 or n == self.correct):  # 0 = cancel
            self.done(n)
            
    def __init__(self, reviewer):
        QDialog.__init__(self)
        
        # Create the UI dialog (created using Qt Designer)
        self.ui = Ui_gridDialog()
        self.ui.setupUi(self)

        v = self.ui.gridView
        #v._linkHandler = self.myLinkHandler
        v.setLinkHandler(self.myLinkHandler)
        #was v.setLinkHandler(self._linkHandler)
        
        gs = GridDlg._gridSize
        self.correct = random.randint(1, gs * gs)

        # Connect up the buttons.
        #self.ui.okButton.clicked.connect(self.accept)
        #self.ui.cancelButton.clicked.connect(self.reject)    

        # Prepare the HTML container (i.e. grid without flashcard content)


    '''    
    @staticmethod
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

    #alphabet = string.lowercase[:26] #string.letters[26:52] # grabbing the lowercase ones
    
    @staticmethod
    def toLetter(n):
        tmp = string.lowercase[n-1]
        #tmp = GridDlg._alphabet[n]
        return tmp
    
    @staticmethod
    def toNumber(c):
        tmp = ord(c) - ord('a') + 1   # our numbering scheme is not zero-based
        return tmp
    
    # TODO: provide KeyHandler that uses toNumber() to convert a keystroke into a call to closeMaybe()
    
    @staticmethod
    def gridHtmlCell(cellId, content, linkLabel=None):
        cellLetter = GridDlg.toLetter(cellId)
        linkLabel = linkLabel if (linkLabel == '') else '%s.' % cellLetter
        
        # alternative:
        tmp = '''
<td id="%s" onclick="document.location='closePopup:%s'" class="card" style="cursor:pointer">
  <p><a href="closePopup:%s">
  %s
%s</a></p>
</td>
''' % (cellId, cellId, cellId, linkLabel, content)
        tmp = '''
<td id="%s" class="card" style="cursor:pointer">
  <a href="closePopup:%s">
  %s <br/>
%s</a>
</td>
''' % (cellId, cellId, linkLabel, content)
        return tmp


    @staticmethod
    def gridHtmlBetweenRows(): 
        return '''
</tr><tr>
'''
        
        
    @staticmethod
    def gridHtml(style='', head=''):

        # alternative (snippet):
        '''
/* unique to FlashGrid */
table {width:100%%; height:100%%; }
td{background:gray;border:1px solid #000}
td a{display:block}
td a:hover{background:blue;color:#fff}
/* need to add styling to remove blue underlining from a tags */
'''
    
        mainHtml = '''
<!doctype html>
<html>

<head><style>
/* from Anki: */
button {
font-weight: normal;
}
%s
/* unique to FlashGrid */
table {width:100%%; }
.cardFront {width:30%%;}
td.card{background:gray;border:1px solid #000;width:50%%;}
td a{display:block; text-decoration:none}
td:hover{background:blue;color:#fff}
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

<table class="card"><tbody><tr>  <!-- outer table, 1x2 -->
  <td class="cardFront"><div id="insertFrontHere"></div></td><td width="10px">&nbsp;</td>  <!-- show front of main card on the left -->
  <!-- TODO: plus a Replay Audio button --> 
  <td><div id="insertGridHere"></div>  <!-- inner table, will be NxN based on gridSize setting -->
</td></tr></tbody></table> 

</body>

</html>
''' % (style, head)
        return mainHtml

GridDlg.gridOn = True

def onGridOffOnClicked():
    GridDlg.gridOn = not GridDlg.gridOn
    tmp = "On" if GridDlg.gridOn else "Off"
    showInfo("FlashGrids are now %s" % (tmp))  # msgbox / messagebox

def onSizeClicked():
    from aqt.reviewer import Reviewer
    GridDlg.toggleGridSize()

"""
class StringGridOffOn(str):
    ''' Trying to subclass string so we can pass in a dynamic object rather than
    a static string for the menu item text. Doesn't work yet, though.
    '''
    def __str__(self):
        changeTo = 'off' if GridDlg.gridOn else 'on'
        return "FlashGrid: turn grid drilling %s" % changeTo
        #before, after = 2, 3
        #tmp = "Toggle grid size to %s x %s (currently %s x %s)"
    def __repr__(self):
        changeTo = 'off' if GridDlg.gridOn else 'on'
        return "FlashGrid: turn grid drilling %s" % changeTo

stringGen = StringGridOffOn('asdf')
"""
    
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

