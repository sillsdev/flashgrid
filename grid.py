# -*- coding: utf-8 -*-

# This file was originally generated from a .ui file created in Qt Designer with this command:
#   C:\Python27\Lib\site-packages\PyQt4\uic\pyuic.py grid.ui > grid.py
# but it was then manually tweaked
# - to add the URLClickPage class to intercept special link clicks
# - to use AnkiWebView (and replace the page on it with instance of URLClickPage
# - to remove Ok/Cancel buttons

# Form implementation generated from reading ui file 'grid.ui'
#
# Created: Thu Jan 01 23:06:04 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!
# Updated 26 June 2020 to fix Pull request warnings.

from PyQt5 import QtCore
#from PyQt5.QtWebEngineWidgets import QWebEngineCertificateError, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QApplication
import aqt.webview

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class URLClickPage(aqt.webview.AnkiWebPage):

    def acceptNavigationRequest(self, url, navType, isMainFrame):
        # a mechanism for identifying http://closepopup or http://replayaudio commands
        if self._specialLinks and self._linkHandler:
            for lnk in self._specialLinks:
                if url.toString().lower().startswith(lnk.lower()):
                    self._linkHandler.handleLinkClick(url.toString())
                    return False

        # otherwise default handling of link
        return super().acceptNavigationRequest(url, navType, isMainFrame)

    def setLinkHandler(self, handler):
        self._linkHandler = handler

    def setSpecialLinks(self, linksList):
        # will be diverted to the link handler if the link starts with text from this list
        self._specialLinks = list(linksList)

class Ui_gridDialog(object):
    def setupUi(self, gridDialog):
        gridDialog.setObjectName(_fromUtf8("gridDialog"))
        gridDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        gridDialog.setSizeGripEnabled(True)
        gridDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(gridDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridView = aqt.webview.AnkiWebView(gridDialog)  #MANUAL EDIT
        # PDB new page of inherited class URLClickPage to intercept the hyperlink clicks
        replPage = URLClickPage(self.gridView._onBridgeCmd)
        self.gridView._page = replPage
        self.gridView._page.setBackgroundColor(self.gridView._getWindowColor())  # reduce flicker
        self.gridView.setPage(replPage)
        self.gridView._page.profile().setHttpCacheType(QWebEngineProfile.NoCache)  # type: ignore

        #self.gridView = QtWebKit.QWebView(gridDialog)
        self.gridView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.gridView.setObjectName(_fromUtf8("gridView"))
        self.verticalLayout.addWidget(self.gridView)
        self.buttonBox = QDialogButtonBox(gridDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        #self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)    #MANUALLY DISABLED
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.retranslateUi(gridDialog)
        QtCore.QMetaObject.connectSlotsByName(gridDialog)

    def retranslateUi(self, gridDialog):
        gridDialog.setWindowTitle(_translate("gridDialog", "Dialog", None))

