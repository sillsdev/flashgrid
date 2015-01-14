import string, random
from aqt.utils import showInfo
from aqt import mw
from aqt.qt import *
#from aqt.utils import showInfo, askUserDialog, getFile
#from aqt.utils import mungeQA, getBase, openLink, tooltip, askUserDialog
#from anki.utils import json
from aqt.webview import AnkiWebView
from grid import Ui_gridDialog

# from PyQt4.QtGui import QMessageBox  #done for us already?


class GridDlg(QDialog):

    def myLinkHandler(self, url):
        ''' Method for AnkiWebView. Currently being patched into the view object in our dialog.
        Consider subclassing instead.
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
            
    def __init__(self, reviewer, gridSize):
        QDialog.__init__(self)
        
        # Create the UI dialog (created using Qt Designer)
        self.ui = Ui_gridDialog()
        self.ui.setupUi(self)

        v = self.ui.gridView
        #v._linkHandler = self.myLinkHandler
        v.setLinkHandler(self.myLinkHandler)
        #was v.setLinkHandler(self._linkHandler)
        
        self.correct = random.randint(1, gridSize*gridSize)

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
    
        tmp = '''
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
/* need to add styling to remove blue underlining from a tags */
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
        return tmp

# old junk...

    '''
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
</table></body></html>''' % ("./frame1.html",  "../frame1.html",  "C:\\Users\\user57\\Documents\\Anki\\User 1\\collection.media\\frame1.html")

GridDlg.gridOn = True

def onGridOffOnClicked():
    GridDlg.gridOn = not GridDlg.gridOn
    showInfo("Ok, toggled. (Use grids = %s)" % (GridDlg.gridOn))  # msgbox / messagebox

def onSizeClicked():
    from aqt.reviewer import Reviewer
    Reviewer.toggleGridSize()
    
# TODO: Need another menu item for toggling "Grid Mode" on and off    

class StringGridOffOn(str):
    def __str__(self):
        changeTo = 'off' if GridDlg.gridOn else 'on'
        return "FlashGrid: turn grid drilling %s" % changeTo
        #before, after = 2, 3
        #tmp = "Toggle grid size to %s x %s (currently %s x %s)"
    def __repr__(self):
        changeTo = 'off' if GridDlg.gridOn else 'on'
        return "FlashGrid: turn grid drilling %s" % changeTo
    
# create a new menu item in Anki
action = QAction("FlashGrid toggle off/on", mw)
# set it to call our function when it's clicked
mw.connect(action, SIGNAL("triggered()"), onGridOffOnClicked)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

stringGen = StringGridOffOn('asdf')
action = QAction(stringGen, mw)
mw.connect(action, SIGNAL("triggered()"), onGridOffOnClicked)
mw.form.menuTools.addAction(action)

action = QAction("FlashGrid toggle grid size", mw)
mw.connect(action, SIGNAL("triggered()"), onSizeClicked)
mw.form.menuTools.addAction(action)


'''
# We probably won't get enough info/power to be able to just use the hook.
from anki.hooks import addHook
def onShowQuestion():
    showInfo("pretend this is a grid")

addHook('showQuestion', onShowQuestion)
'''
