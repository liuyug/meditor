
import logging

from PyQt5 import QtCore, QtWidgets

from .ui.ui_findreplace import Ui_FindReplaceDialog


logger = logging.getLogger(__name__)


class FindReplaceDialog(QtWidgets.QDialog):
    find_next = QtCore.pyqtSignal(str, bool, bool)
    find_previous = QtCore.pyqtSignal(str, bool, bool)
    replace_next = QtCore.pyqtSignal(str, str, bool, bool)
    replace_all = QtCore.pyqtSignal(str, str, bool, bool)
    _readonly = False

    def __init__(self, *args, **kwargs):
        super(FindReplaceDialog, self).__init__(*args, **kwargs)
        self.ui = Ui_FindReplaceDialog()
        self.ui.setupUi(self)

        self.ui.lineEdit_find.textChanged.connect(self.enableButton)
        self.ui.lineEdit_replace.textChanged.connect(self.enableButton)

        self.ui.pushButton_close.clicked.connect(self.handleButton)
        self.ui.pushButton_find_next.clicked.connect(self.handleButton)
        self.ui.pushButton_find_previous.clicked.connect(self.handleButton)
        self.ui.pushButton_replace.clicked.connect(self.handleButton)
        self.ui.pushButton_replaceall.clicked.connect(self.handleButton)
        self.setMinimumWidth(640)

    def setReadOnly(self, readonly):
        self._readonly = readonly
        self.enableButton()

    def handleButton(self):
        if self.sender() == self.ui.pushButton_close:
            self.close()
        elif self.sender() == self.ui.pushButton_find_next:
            self.find_next.emit(
                self.getFindText(),
                self.isCaseSensitive(),
                self.isWholeWord(),
            )
        elif self.sender() == self.ui.pushButton_find_previous:
            self.find_previous.emit(
                self.getFindText(),
                self.isCaseSensitive(),
                self.isWholeWord(),
            )
        elif not self._readonly and self.sender() == self.ui.pushButton_replace:
            self.replace_next.emit(
                self.getFindText(),
                self.getReplaceText(),
                self.isCaseSensitive(),
                self.isWholeWord(),
            )
        elif not self._readonly and self.sender() == self.ui.pushButton_replaceall:
            self.replace_all.emit(
                self.getFindText(),
                self.getReplaceText(),
                self.isCaseSensitive(),
                self.isWholeWord(),
            )

    def enableButton(self):
        enable = True if self.getFindText() else False
        self.ui.pushButton_find_next.setEnabled(enable)
        self.ui.pushButton_find_previous.setEnabled(enable)
        self.ui.pushButton_replace.setEnabled(not self._readonly and enable)
        self.ui.pushButton_replaceall.setEnabled(not self._readonly and enable)

    def getFindText(self):
        return self.ui.lineEdit_find.text()

    def getReplaceText(self):
        return self.ui.lineEdit_replace.text()

    def isCaseSensitive(self):
        return self.ui.checkBox_case_sensitive.isChecked()

    def isWholeWord(self):
        return self.ui.checkBox_whole_words.isChecked()
