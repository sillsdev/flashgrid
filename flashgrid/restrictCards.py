from aqt import mw
from aqt.qt import *


def onRestrictClicked():
    cardType = "Comprehension"
    noteType = "Word"
    deck = mw.col.decks.current()
    deckName = deck['name']
    
    query = 'card:"%s" note:"%s" deck:"%s"' % (cardType, noteType, deckName)
    mw.onCram(query) #  ('card:"my card type"')

action = QAction("FlashGrid: filtered deck for one card type", mw)
mw.connect(action, SIGNAL("triggered()"), onRestrictClicked)
mw.form.menuTools.addAction(action)
