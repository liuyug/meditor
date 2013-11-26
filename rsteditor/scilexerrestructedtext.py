import re

from PyQt4 import QtGui
from PyQt4.Qsci import QsciLexerCustom

from rsteditor.util import toUtf8


class SciLexerReStructedText(QsciLexerCustom):
    styles = {
        'default': 0,
        'comment': 1,
        'newline': 31,
        'indent': 31,
    }
    properties = {
        0: 'fore:#808080',
        1: 'fore:#007f00,back:#efefff',
        31: '',
    }
    tokens = [
        ('comment', r'^\.\. .*\s*'),
        ('newline', r'^[\n\r]+'),
        ('indent', r'^[ \t]+.*\s*'),
        ('default', r'^.+\s*'),
    ]
    get_token = None

    def __init__(self, *args, **kwargs):
        super(SciLexerReStructedText, self).__init__(*args, **kwargs)
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.tokens)
        self.get_token = re.compile(tok_regex).match

    def language(self):
        return 'ReStructedText'

    def description(self, style):
        for k, v in self.styles.items():
            if v == style:
                return k
        print(style)
        return ''

    def styleText(self, start, end):
        """
        1. ReStructedText is context syntax struct, so I have to scan all text
        everytimes to config style. It reduce some performance.
        2. It must use line match bacuase can not get line number from
        character position.
        3. To support non-latin character, function 'positionFromLineIndex'
        will be called for difference length between latin and non-latin.
        """
        if not self.editor():
            return
        start = 0
        end = self.editor().length()
        start_line, start_index = self.editor().lineIndexFromPosition(start)
        end_line, end_index = self.editor().lineIndexFromPosition(end)
        last_typ = 'default'
        for line in range(start_line, end_line + 1):
            text = toUtf8(self.editor().text(line))
            offset = 0
            mo = self.get_token(text)
            while mo is not None:
                typ = mo.lastgroup
                m_start = self.editor().positionFromLineIndex(line, offset)
                m_end = self.editor().positionFromLineIndex(line, mo.end())
                print(line, typ, text[offset:mo.end()], offset, mo.end())
                if typ in ['indent']:
                    typ = last_typ
                self.startStyling(m_start)
                self.setStyling(m_end - m_start, self.styles[typ])
                last_typ = typ
                offset = mo.end()
                mo = self.get_token(text, offset)
            if offset < len(text):
                print(line, 'unknown', text[offset:len(text)])
                #print(line, offset, len(text))
                #m_start = self.editor().positionFromLineIndex(line, offset)
                #m_end = self.editor().positionFromLineIndex(line, len(text))
                #print(line, 'default', text[offset:len(text)])
                #self.startStyling(offset)
                #self.setStyling(m_end - m_start, self.styles['default'])
                #print(m_start, m_end)
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

