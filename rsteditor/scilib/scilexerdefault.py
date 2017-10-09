import logging

from PyQt5 import Qsci, QtGui, QtCore

logger = logging.getLogger(__name__)


class QsciLexerDefault(Qsci.QsciLexerCustom):
    def __init__(self, *args, **kwargs):
        super(QsciLexerDefault, self).__init__(*args, **kwargs)
        self.setDefaultFont(QtGui.QFont('Monospace', 12))

    def language(self):
        return 'defaut'

    def description(self, style):
        return 'default'

    def styleText(self, start, end):
        if not self.editor():
            return
        self.startStyling(self.editor().length())
