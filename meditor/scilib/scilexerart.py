import sys
import logging

from PyQt5 import Qsci
from PyQt5.QtGui import QColor, QFont

logger = logging.getLogger(__name__)


class QsciLexerArt(Qsci.QsciLexerCustom):
    styles = {
        "Default": 0,
    }

    def __init__(self, parent=None):
        super(QsciLexerArt, self).__init__(parent)
        self.setDefaultColor(QColor('#000000'))
        self.setDefaultPaper(QColor('#ffffff'))

        if sys.platform == 'win32':
            font = QFont('consolas')
        else:
            font = QFont('monospace')
        font.setFixedPitch(True)
        self.setDefaultFont(font)

    def language(self):
        return 'Ascii Art'

    def description(self, style):
        if style == 0:
            return 'Default'
        else:
            return ''

    def styleText(self, start, end):
        if not self.editor():
            return
        self.editor().setIndentationGuides(False)
        self.editor().setExtraAscent(-2)
        self.editor().setExtraDescent(-1)
        self.startStyling(start)
        self.setStyling(end - start, 0)
