import re

from PyQt4 import QtGui
from PyQt4.Qsci import QsciLexerCustom

from rsteditor.util import toUtf8


class SciLexerReStructedText(QsciLexerCustom):
    styles = {
        'string': 29,
        'space': 30,
        'comment': 1,
        'title': 2,
        'section': 3,
        'field': 4,
        'newline': 31,
    }
    properties = {
        0:  'fore:#808080',
        1:  'fore:#007f00,back:#efefff',
        2:  'fore:#f00000',
        3:  'fore:#f0f000',
        4:  'fore:#f00010',
        29: 'fore:#f00000,back:#00f000',
        30: 'fore:#000000,back:#f00000',
        31: 'fore:#f0f000,back:#0000f0',
    }
    tokens = [
        ('comment', r'''\.\. .*(\n[ \t]+.*)*\n'''),
        ('title',   r'''[=`'"~^_*+#-]{2,}\n.*\n[=`'"~^_*+#-]{2,}\n'''),
        ('section', r'''.*\n[=`'"~^_*+#-]{2,}\n'''),
        ('field',   r''':[^:]+:[ \t]+.+(\n[ \t]+.*)*\n'''),
        ('newline', r'''\n'''),
        ('space',   r'''[ \t]+'''),
        ('string',  r'''[^ \t\n\r\v\f]+'''),
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
            m_string = text[offset:mo.end()]
            print(line, typ, m_string)
            line_fix = m_string.count('\n')
            if line_fix > 0:    # calculate length in last line
                index_end = len(m_string) - m_string.rfind('\n') - 1
            else:
                index_end = index + len(m_string)
            m_start = self.editor().positionFromLineIndex(line, index)
            m_end = self.editor().positionFromLineIndex(line + line_fix,
                                                        index_end)
            self.startStyling(m_start)
            self.setStyling(m_end - m_start, self.styles[typ])
            print('match:', line, index, text[offset:mo.end()])
            print('style:',m_start, m_end, index, index_end)
            line += line_fix
            index = index_end
            offset = mo.end()
            mo = self.get_token(text, offset)
            print('next chars:', line, index, text[offset:offset + 10], offset, text_length)
        #self.startStyling(end)
        #self.setStyling(end, self.styles['newline'])
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

