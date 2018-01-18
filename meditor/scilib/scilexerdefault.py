import logging

from PyQt5 import Qsci
from PyQt5.QtGui import QColor, QFont

logger = logging.getLogger(__name__)


class QsciLexerDefault(Qsci.QsciLexerCustom):
    styles = {
        "Default": 0,
        "Comment": 1,
        "Keyword": 2,
        "String": 3,
        "Number": 4,
    }

    def __init__(self, parent=None):
        super(QsciLexerDefault, self).__init__(parent)
        self.setDefaultColor(QColor('#000000'))
        self.setDefaultPaper(QColor('#ffffff'))
        self.setDefaultFont(QFont())

        self.setColor(QColor('#000000'), self.styles['Default'])
        self.setColor(QColor('#007f00'), self.styles['Comment'])
        self.setColor(QColor('#00007f'), self.styles['Keyword'])
        self.setColor(QColor('#7f007f'), self.styles['String'])
        self.setColor(QColor('#007f7f'), self.styles['Number'])

    def language(self):
        return 'Defaut Text'

    def description(self, style_idx):
        for description, idx in self.styles.items():
            if idx == style_idx:
                return description
        return ''

    def styleText(self, start, end):
        if not self.editor():
            return
        self.startStyling(start)
        text = self.parent().text()[start:end]
        self.setStyling(len(bytearray(text, 'utf-8')), self.styles['Default'])
