import re

from PyQt4 import QtGui
from PyQt4.Qsci import QsciLexerCustom

from rsteditor.util import toUtf8


class SciLexerReStructedText(QsciLexerCustom):
    styles = {
        'string': 0,
        'space': 0,
        'comment': 1,
        'title': 2,
        'section': 3,
        'field': 4,
        'newline': 31,
    }
    properties = {
        0: 'fore:#808080',
        1: 'fore:#007f00,back:#efefff',
        2: 'fore:#f00000',
        3: 'fore:#f0f000',
        4: 'fore:#f00010',
        31: '',
    }
    tokens = [
        ('comment', r'\.\. .*'),
        ('title',   r'[=\-]+\n.*\n[=\-]+'),
        ('section', r'.*\n[=\-]+'),
        ('field',   r':[^:]+:[ \t]+.+'),
        ('newline', r'\n'),
        ('space',   r'[ \t]+'),
        ('string',  r'[^ \t\n\r\v\f]+'),
    ]
    get_token = None

    def __init__(self, *args, **kwargs):
        super(SciLexerReStructedText, self).__init__(*args, **kwargs)
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.tokens)
        self.get_token = re.compile(tok_regex, re.UNICODE).match

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
        2. To support non-latin character, function 'positionFromLineIndex'
        will be called for difference length between latin and non-latin.
        3. Must use match global for searching section
        """
        if not self.editor():
            return
        text = toUtf8(self.editor().text())
        text_length = len(text)
        offset = 0  # character position at text
        line = 0    # line number
        index = 0   # character position at line
        mo = self.get_token(text, offset)
        while mo is not None:
            typ = mo.lastgroup
            print(line, typ)
            if typ == 'newline':
                line += 1
                index = 0
            else:
                line_fix = 0
                if typ in ['section']:  # span multiline in section
                    line_fix = 1
                if typ in ['title']:
                    line_fix = 2
                m_length = mo.end() - offset
                m_start = self.editor().positionFromLineIndex(line, index)
                m_end = self.editor().positionFromLineIndex(line + line_fix,
                                                            index + m_length)
                self.startStyling(m_start)
                self.setStyling(m_end - m_start, self.styles[typ])
                print('match:', line, index, m_length, text[offset:mo.end()])
                line += line_fix
                index += m_length
            offset = mo.end()
            mo = self.get_token(text, offset)
            print('next chars:', line, index, text[offset:offset + 10], offset, text_length)
        self.startStyling(end)
        self.setStyling(end, self.styles['newline'])
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

