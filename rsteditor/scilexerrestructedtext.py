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
        'transition': 4,
        'paragraph': 31,
        'bullet': 5,
        'enumerated': 5,
        'definition': 6,
        'field': 6,
        'option': 7,
        'literal': 8,
        'line': 9,
        'quote': 10,
        'doctest': 11,
        'table1': 12,
        'table2': 12,
        'footnote': 13,
        'target': 14,
        'directive': 15,
        'newline': 31,
    }
    properties = {
        0:  'fore:#808080',
        1:  'fore:#007f00,back:#efefff',
        2:  'fore:#f00000',
        3:  'fore:#f0f000',
        4:  'fore:#808080',
        5:  'fore:#f00010',
        6:  'fore:#f00080',
        7:  'fore:#f000f0',
        8:  'fore:#f01010',
        9:  'fore:#f01080',
        10: 'fore:#f010f0',
        11: 'fore:#f08010',
        12: 'fore:#f08080',
        13: 'fore:#f080f0',
        14: 'fore:#f0f010',
        15: 'fore:#00f080',
        29: 'fore:#f00000,back:#00f000',
        30: 'fore:#000000,back:#f00000',
        31: 'fore:#f0f000,back:#0000f0',
    }
    tokens = [
        ('comment', r'''\.\. +(?!_|\[)(?!.+::).+(\n{0,2} {3,}.+)*\n'''),
        ('title',   r'''[=`'"~^_*+#-]{2,}\n.+\n[=`'"~^_*+#-]{2,}\n\n'''),
        ('section', r'''.+\n[=`'"~^_*+#-]{2,}\n'''),
        ('transition', r'''[=`'"~^_*+#-]{4,}\n\n'''),
        #('paragraph', r'''[^ \t\-+*:]+(\n[^ \t\-+*:]+)*\n\n'''),
        ('bullet',     r''' *[\-+*] +.+(\n+ +.+)*\n\n'''),
        ('enumerated', r''' *\(?[0-9a-zA-Z#]+(\.|\)) +.+(\n+ +.+)*\n\n'''),
        ('definition', r'''[^ \t\-\n]+( +: +.+)?\n +.+(\n+ +.+)*\n'''),
        ('field',   r''':[^:]+:[ \t\n]+.+(\n+ +.+)*\n'''),
        ('option',  r'''[\-/]+.+(  .+)?(\n+ +.+)*\n'''),
        ('literal',  r'''.+(\n.+)*::\n(\n+[ >]+.*)+\n\n'''),
        ('line',  r''' *\|( +.+)?(\n +.+)*\n'''),
        ('quote',  r''' {2,}.+(\n +.+)*\n\n'''),
        ('doctest', r'''>>>.+\n'''),
        ('table1',   r''' *[\-=+]{2,}(\n[\|+].+)+\n\n'''),
        ('table2',   r''' *[\-=]{2,} [\-= ]+(\n.+)+\n\n'''),
        ('footnote', r'''\.\. +\[[^\n\]]+\] +.+(\n+ +.+)*\n\n'''),
        ('target', r'''\.\. +_.+:(\n +)*.*\n'''),
        ('directive', r'''\.\. +(?!_|\[).+::.*(\n+ +.+)*\n'''),
        ('newline', r'''\n'''),
        ('space',   r''' +'''),
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

