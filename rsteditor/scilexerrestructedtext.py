from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciLexerCustom

from rsteditor.util import toUtf8


class SciLexerReStructedText(QsciLexerCustom):
    styles = {
        'default':0,
        'comment':1,
    }
    properties = {
        0: 'fore:#000000',
        1: 'fore:#007f00,back:#efefff',
    }

    def language(self):
        return 'ReStructedText'

    def description(self, style):
        for k, v in self.styles.items():
            if v == style:
                return k
        print(style)
        return ''

    def styleText(self, start, end):
        if not self.editor():
            return
        line_s, index_s = self.editor().lineIndexFromPosition(start)
        line_e, index_e = self.editor().lineIndexFromPosition(end)
        for line in range(line_s, line_e + 1):
            offset = self.editor().positionFromLineIndex(line, 0)
            text = toUtf8(self.editor().text(line))
            if text.startswith('.. '):
                self.startStyling(offset)
                self.setStyling(len(text), self.styles['comment'])
                print('comment:', text)
            else:
                self.startStyling(offset)
                self.setStyling(len(text), self.styles['default'])
                print('default:', text)
        return

    def defaultColor(self, style):
        prop_list = self.getProperty(style)
        for prop in prop_list:
            if prop.startswith('fore:'):
                color = prop.split(':')[1]
                return QtGui.QColor(color)
        return super(SciLexerReStructedText, self).defaultColor(style)

    def defaultPaper(self, style):
        prop_list = self.getProperty(style)
        for prop in prop_list:
            if prop.startswith('back:'):
                color = prop.split(':')[1]
                return QtGui.QColor(color)
        return super(SciLexerReStructedText, self).defaultPaper(style)

    def defaultFont(self, style):
        prop_list = self.getProperty(style)
        for prop in prop_list:
            if ':' in prop:
                if prop.startswith('face:'):
                    font = prop.split(':')[1]
                    return QtGui.QFont(font)
            else:
                return QtGui.QFont(prop)
        return super(SciLexerReStructedText, self).defaultFont(style)

    def getProperty(self, style):
        if style in self.properties:
            prop_list = self.properties[style].split(',')
            return prop_list
        return []

