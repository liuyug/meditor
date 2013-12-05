import re

from PyQt4 import QtGui
from PyQt4.Qsci import QsciLexerCustom

from rsteditor.util import toUtf8


class SciLexerReStructedText(QsciLexerCustom):
    styles = {
        'string': 0,
        'comment': 1,
        'title': 2,
        'section': 2,
        'transition': 4,
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
        'target1': 14,
        'target2': 14,
        'directive': 15,
        'colon': 0,
        'space': 0,
        'newline': 0,
    }
    properties = {
        0:  'fore:#000000',
        1:  'fore:#3f813f,back:#f0f0f0',
        2:  'fore:#712704,bold',
        3:  'fore:#000000',
        4:  'fore:#d4d4d4',
        5:  'fore:#aa0000',
        6:  'fore:#dd3311',
        7:  'fore:#04477c',
        8:  'fore:#04477c',
        9:  'fore:#a73800',
        10: 'fore:#a73800',
        11: 'fore:#04477c',
        12: 'fore:#04477c',
        13: 'fore:#4c4c4c',
        14: 'fore:#036803',
        15: 'fore:#4c4c4c',
    }
    token_regex = [
        ('comment',     r'''^\.\. (?!_|\[)(?!.+::).+(?:\n{0,2} {3,}.+)*\n'''),
        ('title',       r'''^([=`'"~^_*+#-]{2,})\n.+\n\1\n'''),
        ('section',     r'''^.+\n[=`'"~^_*+#-]{2,}\n'''),
        ('transition',  r'''^\n[=`'"~^_*+#-]{4,}\n\n'''),
        ('bullet',      r'''^ *[\-+*] +.+(?:\n+ +.+)*\n'''),
        ('enumerated',  r'''^ *\(?[0-9a-zA-Z#](?:\.|\)) +.+(?:\n+ +.+)*\n'''),
        ('definition',  r'''^(?!\.\. |[ \|\-=+]).+\n( +).+(?:\n+\1.+)*\n'''),
        ('field',       r'''^:[^:]+:[ \n]+.+(?:\n+ +.+)*\n'''),
        ('option',      r'''^[\-/]+.+(?:  .+)?(?:\n+ +.+)*\n'''),
        ('literal',     r'''::\n\n([ >]+).+(?:\n+\1.*)*\n\n'''),
        ('line',        r'''^ *\|(?: +.+)?(?:\n +.+)*\n'''),
        ('quote',       r'''^( {2,}).+(?:\n\1.+)*\n\n'''),
        ('doctest',     r'''^>>>.+\n'''),
        ('table1',      r'''^( *)[\-=+]{2,}(\n\1[\|+].+)+\n\n'''),
        ('table2',      r'''^( *)[\-=]{2,} [\-= ]+(\n\1.+)+\n\n'''),
        ('footnote',    r'''^\.\. \[[^\n\]]+\][ \n]+.+(\n+ +.+)*\n\n'''),
        ('target1',      r'''^\.\. _.+:(\n +)*.*\n'''),
        ('target2',      r'''^__(?: .+)*\n'''),
        ('directive',   r'''^\.\. (?!_|\[).+::.*(\n+ +.+)*\n'''),
        ('newline',     r'''\n'''),
        ('space',       r''' +'''),
        ('string',      r'''[^: \n]+'''),
        ('colon',       r''':'''),
    ]
    tokens = []

    def __init__(self, *args, **kwargs):
        super(SciLexerReStructedText, self).__init__(*args, **kwargs)
        for key, regex in self.token_regex:
            self.tokens.append((key, re.compile(regex, re.U | re.M).match))
        return

    def language(self):
        return 'ReStructedText'

    def description(self, style):
        for k, v in self.styles.items():
            if v == style:
                return k
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
        offset = 0  # character position at text
        line = 0    # line number
        index = 0   # character position at line
        mo = None
        typ = ''
        while True:
            for key, get_token in self.tokens:
                mo = get_token(text, offset)
                if mo:
                    typ = key
                    break
            if not mo:
                break
            m_string = text[offset:mo.end()]
            #print(line, typ, m_string)
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
            #print('match:', line, index, text[offset:mo.end()])
            #print('style:',m_start, m_end, index, index_end)
            line += line_fix
            index = index_end
            offset = mo.end()
            #print('next chars:', line, index, text[offset:offset + 10], offset, text_length)
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
                font = super(SciLexerReStructedText, self).defaultFont(style)
                if prop == 'bold':
                    font.setBold(True)
                elif prop == 'italic':
                    font.setItalic(True)
                elif prop == 'underline':
                    font.setUnderline(True)
                return font
        return super(SciLexerReStructedText, self).defaultFont(style)

    def getProperty(self, style):
        if style in self.properties:
            prop_list = self.properties[style].split(',')
            return prop_list
        return []

