from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciLexerCustom

from rsteditor.util import toUtf8


class SciLexerReStructedText(QsciLexerCustom):
    ID_DEFAULT = 0
    ID_COMMENT = 1

    def language(self):
        return 'ReStructedText'

    def description(self, style):
        if style == self.ID_DEFAULT:
            return 'ID_DEFAULT'
        if style == self.ID_COMMENT:
            return 'ID_COMMENT'
        print(style)
        return ''

    def styleText(self, start, end):
        if not self.editor():
            return
        line_s, index_s = self.editor().lineIndexFromPosition(start)
        line_e, index_e = self.editor().lineIndexFromPosition(end)
        print(line_s, index_s, line_e, index_e)
        for line in range(line_s, line_e + 1):
            offset = self.editor().positionFromLineIndex(line, 0)
            text = toUtf8(self.editor().text(line))
            print(text)
            if text.startswith('.. '):
                self.startStyling(offset)
                self.setStyling(len(text), self.ID_COMMENT)
                print('comment')
            else:
                self.startStyling(offset)
                self.setStyling(len(text), self.ID_DEFAULT)
                print('default')
            print(offset, end)

    def color(self, style):
        if style == self.ID_DEFAULT:
            return QtGui.QColor('#e00000')
        if style == self.ID_COMMENT:
            return QtGui.QColor('#00e000')
        return super(SciLexerReStructedText, self).color(style)


