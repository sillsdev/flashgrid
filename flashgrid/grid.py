# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'grid.ui'
#
# Created: Thu Jan 01 23:06:04 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_gridDialog(object):
    def setupUi(self, gridDialog):
        gridDialog.setObjectName(_fromUtf8("gridDialog"))
        gridDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        gridDialog.resize(579, 484)
        gridDialog.setSizeGripEnabled(True)
        gridDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(gridDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        import aqt.webview
        self.gridView = aqt.webview.AnkiWebView(gridDialog)
        #self.gridView = QtWebKit.QWebView(gridDialog)
        self.gridView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.gridView.setObjectName(_fromUtf8("gridView"))
        self.verticalLayout.addWidget(self.gridView)
        self.buttonBox = QtGui.QDialogButtonBox(gridDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(gridDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), gridDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), gridDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(gridDialog)

    def retranslateUi(self, gridDialog):
        gridDialog.setWindowTitle(_translate("gridDialog", "Dialog", None))

from PyQt4 import QtWebKit
