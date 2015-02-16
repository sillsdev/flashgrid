from aqt import mw
from aqt.qt import *
from anki.db import DB
from anki.notes import Note
#from anki.models import ModelManager
from anki.decks import DeckManager
import copy

from anki.utils import checksum, intTime
import time

def noteTypes(deck):
    
    db = mw.col.db
    did = deck['id']
    
    q = "select distinct notes.mid from cards, notes where cards.nid = notes.id and cards.did = %s" % (did)
    L = db.list(q)
    print L
    L2 = [mw.col.models.get(mid) for mid in L]
    return L2

    #BAD:        
    models = mw.col.models
    relevant = set(models)

    for m in models:
        #any notes of this type in our deck?
        mid = m.mid
        q = "select count() from cards, notes where cards.nid = notes.id and cards.did = %s and notes.mid = %s" % (did, mid)
        print q
        c = db.list(q)
        print c
        print
        if int(c) < 1:
            relevant.remove(m)
        
        #q = "select count() from cards, notes where cards.did=%s and notes.mid=%s" % (mid, self._ankiDeckId)

    print "Final set: %s" % relevant
    return list(relevant)

def getUniqueName(name, otherNames):
    newName = name
    for d in otherNames:  
        if newName == d:
            newName += "-" + checksum(str(time.time()))[:5]
            break
    if newName != name:
        # we had to change the name; probably unique
        return getUniqueName(newName, otherNames)   # to be truly failsafe, this function is recursive, just in case the new name isn't unique either. -Jon C
    else:
        # verified unique
        return newName

class DeckDuper(object):
    
    def __init__(self, ankiDeck):
        self._ankiDeck = ankiDeck  # an object
        #self._ankiDeckId =ankiDeck['id']   # an ID
        self.reset()
        
    def reset(self):
        self.errors = set()
        self.errorCount = 0
        self.notesCopied = 0
        self.cardsCopied = 0
        #self._alreadyCopiedNotes = set() # set of IDs
        
    def dupNote(self, note, model, deckId):
        ''' Parameters should be objects (not IDs)
        Returns the new note, or None on failure
        '''
        
        mw.col.models.setCurrent(model)
        
        # TODO: To really copy the whole thing, not just the data fields, we could 
        # deepcopy the whole note, then get unique IDs by creating a temp Note just to steal its id and guid,
        # then delete the temp note. (I tried that and couldn't get it to work, so far.)
        '''
        n2tmp = Note(mw.col, model)
        n2 = copy.deepcopy(note)  
        n2.id = n2tmp.id 
        n2.guid = n2tmp.guid
        del n2tmp  # just being explicit
        # overwrite model info
        n2._model = model
        n2.mid = model['id']
        '''
         
        n2 = Note(mw.col, model)
        assert( len(n2.model()['flds']) >= len(note.fields) )

        # copy data
        n2.fields = copy.deepcopy(note.fields)
        n2.tags = copy.deepcopy(note.tags)
        # anything else??
        
        n2.flush(intTime()) #save
        #n2.load()
        
        # Copying its cards technically shouldn't be necessary since they should auto-generate. (Make sure they do? Orphaned notes are inaccessible in Anki's UI.)

        # It would be nice to copy c.queue , at least if it's -1 (suspended)
        
        # But we do need actual cards in order to specify a target deck.
        cardCount = mw.col.addNote(n2)
        if cardCount:
            q = "select distinct cards.id from cards where cards.nid = %s" % (n2.id)
            cards = mw.col.db.list(q)
            for cid in cards:
                c = mw.col.getCard(cid)
                c.did = deckId  # Move card into the target deck
                c.flush()
                self.cardsCopied += 1
            return n2
        self.errors.add('Copy Note failed.')
        self.errorCount += 1
        print "Copy failed for: %s" % note
        return None


    def processCard(self, c, targetDeckId, targetModel, noteMap):
        '''
        Side effects: noteMap will be updated, and the new card will point to the newly copied note
        (a given new note may be shared by more than one of new cards, hence the noteMap)
        Card and note will be saved.
        '''
        
        #c = mw.col.getCard(cardId)
        
        #model = mw.col.models.get(targetModelId)  # = mw.col.db.getModel(targetModelId)
    
        # copy note if necessary
        key = unicode(c.nid)
        if key in noteMap.keys():
            # one of the original cards copied earlier was linked to the same note; use the copy of that note
            nid2 = noteMap[key]
            note2 = mw.col.getNote(nid2)
        else:
            # need to copy note
            note = mw.col.getNote(c.nid)  # orig
            note2 = self.dupNote(note, targetModel, targetDeckId)
            if not note2:
                return None
            nid2 = note2.id
            mw.col.flush()  # save
            # mw.col.genCards([nid2])
            
            noteMap[key] = nid2
            self.notesCopied += 1



    def dupDeck(self, dupNoteTypes=[]):
        ''' Copies all CARDS and NOTES from this deck into a new deck.
        Technically, we shouldn't need to copy the CARDS (they should auto-generate).
        
        Expects the model ID's to be unicode strings. (In the data they are longs.)
        '''
        
        self.reset()
        db = mw.col.db
        
        # first, dup any note types that need to be
        mappings = {}
        models = mw.col.models.all()
        for m in models:
            mid = unicode(m['id'])  # otherwise we get a mix of string and unicode keys
            mappings[mid] = m  # map to self ("no dup")
            if mid in dupNoteTypes:
                m2 = mw.col.models.copy(m) # copy the model 
                #mw.col.models.flush() # save (shouldn't be necessary)
                mappings[mid] = m2  # map to the new copy
        
        # dup the deck
        origDeck = self._ankiDeck
        existingNames = mw.col.decks.allNames()
        newName = getUniqueName(origDeck['name'], existingNames)
        newDeckId = mw.col.decks.id(newName, create=True, type=origDeck)
        mw.col.decks.flush()  # save
        mw.col.decks.select(newDeckId)  # set "current" to the new deck (does this work?)
        mw.col.decks.flush()  # save
        
        # TODO: Should we ask user whether to copy deck config too? Probably not important.
        #did = origDeck['id']
        #srcConf = mw.col.decks.confForDid(did)
        # d2id = mw.col.decks.confId(name, cloneFrom=srcConf)
        
        q = "select distinct cards.id from cards where cards.did = %s" % (origDeck['id'])
        cards = db.list(q)
        
        # dup the cards (and their notes)
        noteMap = dict()  # allows multiple new cards to point to a single new note
        for cid in cards:
            c = mw.col.getCard(cid)
            m = c.note().model()
            mkey = unicode(m['id'])
            mtarg = mappings[mkey]
            self.processCard(c, newDeckId, mtarg, noteMap)
        
        '''
        # dup the notes
        q = "select distinct notes.id from cards, notes where cards.nid = notes.id and cards.did = %s" % (did)
        notes = db.list(q)
        for nid in notes:
            n = mw.col.getNote(nid)
            mid = n.model()['id']
            mtarg = mappings[mid]
            self.dupNote(n, mtarg, newDeckId)
        '''
            
        # sanity check
        q = "select count() from cards where cards.did = %s" % (origDeck['id'])
        count1 = db.scalar(q)
        q = "select count() from cards where cards.did = %s" % (newDeckId)
        count2 = db.scalar(q)
        
        if (count1 != count2):
            showInfo("There seems to be a problem: the new deck has %s cards and the original has %s" % (count1, count2))


        return newDeckId



# The UI. Could be split into a separate file.   
from aqt.utils import showInfo, askUserDialog

def onCopyDeckClicked():
    
    deck = mw.col.decks.current()
    models = noteTypes(deck) # models to consider copying
    
    if not models:
        showInfo('Data models not found. Aborted. Try selecting a deck.')
        return
    dupMids = [unicode(m['id']) for m in models]  # assume "Clone all"

    modelNames = [m['name'] for m in models]
    q = ''' The current deck (%s) uses these Note Types:
%s
Do you want the copied deck to share these settings, or
do you want to clone the settings?
(Either way, media files will be shared, not cloned.)
    ''' % (deck['name'], ', '.join(modelNames))
    buttons = ['Clone all', 'Share all', 'Ask', 'Cancel']
    dlg = askUserDialog(q, buttons)
    dlg.setIcon(4)
    a = dlg.run()
    if a == 'Cancel':
        return
    elif a == 'Share all':
        dupMids = []
    elif a == 'Ask':
        q = 'Clone model %s?'
        buttons = ['Clone', 'Share', 'Cancel']
        for i in range(len(dupMids)-1, -1, -1):
            m = dupMids[i]
            dlg = askUserDialog(q % modelNames[i], buttons)
            dlg.setIcon(4)
            a = dlg.run()
            if a == 'Cancel':
                return
            elif a == 'Share':
                dupMids.pop(i)  # remove

        # TODO: Also ask whether to copy the media files. This is much trickier as it would have to modify the data to match.

    dd = DeckDuper(deck)
    _tmp = dd.dupDeck(dupMids)
    
    
    # refresh the screen so the new deck is visible
    mw.moveToState("deckBrowser")

    msg = 'Successfully copied %s notes, and generated %s cards (with fresh scheduling info). \n' % (dd.notesCopied, dd.cardsCopied)
    if dd.errorCount:
        s = list(dd.errors)
        summary = ' '.join(s)
        msg += 'Encountered %s errors. \n' % dd.errorCount
        msg += 'Summary: %s \n' % summary

    showInfo(msg)


action = QAction("Copy deck...", mw)
mw.connect(action, SIGNAL("triggered()"), onCopyDeckClicked)
mw.form.menuTools.addAction(action)

import apkgWarning




def isCompatible(model, target):
    ''' Returns True iff model equals target or is a subset of target
    Expects two Anki models (note types)
    '''
    return False  #unimplemented (not needed for mere copying)
