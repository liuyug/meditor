import logging

from PyQt5 import Qsci
from PyQt5.QtGui import QColor, QFont

logger = logging.getLogger(__name__)


class QsciLexerDefault(Qsci.QsciLexerCustom):
    styles = {
        "Default": 0,
    }

    def __init__(self, parent=None):
        super(QsciLexerDefault, self).__init__(parent)
        self.setDefaultColor(QColor('#000000'))
        self.setDefaultPaper(QColor('#ffffff'))
        self.setDefaultFont(QFont())

    def language(self):
        return 'Defaut Text'

    def description(self, style):
        if style == 0:
            return 'Default'
        else:
            return ''

    def styleText(self, start, end):
        if not self.editor():
            return
        self.startStyling(start)
        self.setStyling(end - start, self.styles['Default'])
