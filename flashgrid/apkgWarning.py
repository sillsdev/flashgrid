from aqt.utils import showInfo

CLONE_MSG = '''clone the deck/note types/notes/cards. This will give them new unique IDs. 
Otherwise, Anki will try to merge the two decks if they ever end 
up on the same computer. '''

import aqt.importing

orig = aqt.importing.importFile

# wrap orig (a fairly non-brittle monkey patch)
def myImportFile(mw, file):
    
    if ".apkg" in file:
        cont = True
        # TODO: see if any IDs in the APKG file already exist in our collection
        # If so, tell the user, then set cont = result of asking whether to continue

        if cont:
            orig(mw, file)
            showInfo('''Done importing from APKG. If you are 'forking' your own 
separate copy of this deck, please explicitly use Tools / Copy Deck to 
''' + CLONE_MSG )
            
    else:
        orig(mw, file)


aqt.importing.importFile = myImportFile


from aqt.exporting import ExportDialog

origExport = ExportDialog.accept

# wrap orig (a fairly non-brittle monkey patch)
def myExportAccept(self):
    origExport(self)
    if self.isApkg:
        showInfo('''REMINDER: If anyone later imports this APKG file as a starting point 
for their own, separate deck, they should explicitly use Tools / Copy Deck to 
''' + CLONE_MSG )
 
ExportDialog.accept = myExportAccept
