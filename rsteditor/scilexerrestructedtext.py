import os.path
import re

from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciLexerCustom

from rsteditor.util import toUtf8
from rsteditor import __home_data_path__


class SciLexerReStructedText(QsciLexerCustom):
    styles = {
        'string': 0,
        'colon': 0,
        'space': 0,
        'newline': 0,
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
        'in_emphasis': 16,
        'in_strong': 17,
        'in_literal': 18,
        'in_url1': 19,
        'in_url2': 19,
        'in_link1': 20,
        'in_link2': 20,
        'in_footnote': 21,
        'in_substitution': 22,
        'in_target': 23,
        'in_reference': 24,
    }
    properties = {
        0:  'fore:#000000',
        1:  'fore:#4e9a06',
        2:  'fore:#8f5902,bold',
        3:  'fore:#000000',
        4:  'fore:#888a85',
        5:  'fore:#5c3566',
        6:  'fore:#a40000',
        7:  'fore:#204a87',
        8:  'fore:#204a87,$(font.Monospace)',
        9:  'fore:#8f5902',
        10: 'fore:#8f5902',
        11: 'fore:#3465a4',
        12: 'fore:#ce5c00',
        13: 'fore:#555753',
        14: 'fore:#4e9a06',
        15: 'fore:#c4a000',
        16: 'italic',
        17: 'bold',
        18: 'fore:#204a87,$(font.Monospace)',
        19: 'fore:#4e9a06,underline',
        20: 'fore:#4e9a06,underline',
        21: 'fore:#555753',
        22: 'fore:#4e9a06',
        23: 'fore:#4e9a06',
        24: 'fore:#4e9a06',
    }
    token_regex = [
        # block markup
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
        ('target1',     r'''^\.\. _.+:(\n +)*.*\n'''),
        ('target2',     r'''^__(?: .+)*\n'''),
        ('directive',   r'''^\.\. (?!_|\[).+::.*(\n+ +.+)*\n'''),
        ('newline',     r'''\n'''),
        ('space',       r''' +'''),
        ('string',      r'''[^: \n]+'''),
        ('colon',       r''':'''),
        # inline markup
        ('in_emphasis', r'''(?<!\*)(\*\w.*\w\*)(?!\*)'''),
        ('in_strong',   r'''(\*\*\w.*\w\*\*)'''),
        ('in_literal',  r'''(``\w.*\w``)'''),
        ('in_url1',     r'''\W((?:http://|https://|ftp://)[\w\-\.:/]+)\W'''),
        ('in_url2',     r'''(`[^<]+<[^>]+>`_)'''),
        ('in_link1',    r'''(\w+_)\W'''),
        ('in_link2',    r'''(`\w.*\w`_)'''),
        ('in_footnote', r'''(\[[\w\*#]+\]_)'''),
        ('in_substitution', r'''(\|\w.*\w\|)'''),
        ('in_target',    r'''(_`\w.*\w`)'''),
        ('in_reference', r'''(:\w+:`\w+`)'''),
    ]

    def __init__(self, *args, **kwargs):
        super(SciLexerReStructedText, self).__init__(*args, **kwargs)
        self.setDefaultColor(QtGui.QColor('#000000'))
        self.setDefaultPaper(QtGui.QColor('#ffffff'))
        self.setDefaultFont(QtGui.QFont('Monospace', 12))
        prop_file = os.path.join(__home_data_path__, 'rst.properties')
        prop_settings = QtCore.QSettings(prop_file, QtCore.QSettings.IniFormat)
        for num in range(0, len(self.properties)):
            value = toUtf8(prop_settings.value('style.rst.%s' % num).toString())
            if not value:
                continue
            prop_list = value.split(',')
            fgcolor = self.defaultColor(num)
            bgcolor = self.defaultPaper(num)
            font = self.defaultFont(num)
            for prop in prop_list:
                if prop.startswith('face:'):
                    fgcolor = QtGui.QColor(prop.split(':')[1])
                    self.setColor(fgcolor, num)
                elif prop.startswith('back:'):
                    bgcolor = QtGui.QColor(prop.split(':')[1])
                    self.setPaper(bgcolor, num)
                else:
                    if prop.startswith('$(font.'):
                        mo = re.match(r'^\$\(font\.(.+)\)', prop)
                        font = QtGui.QFont(mo.group(1))
                    elif prop == 'bold':
                        font.setBold(True)
                    elif prop == 'italic':
                        font.setItalic(True)
                    elif prop == 'underline':
                        font.setUnderline(True)
                    self.setFont(font, num)

        self.block_tokens = []
        self.inline_tokens = []
        for key, regex in self.token_regex:
            if key.startswith('in_'):
                self.inline_tokens.append((key, re.compile(regex, re.U)))
            else:
                self.block_tokens.append((key, re.compile(regex, re.U | re.M)))
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
        bs = text.rfind('\n\n', 0, start)
        bs = start if bs == -1 else bs
        be = text.find('\n\n', end)
        be = end if be == -1 else be + 2
        bs_line, bs_index = self.editor().lineIndexFromPosition(bs)
        be_line, be_index = self.editor().lineIndexFromPosition(be)
        offset = bs  # character position at text
        line = bs_line    # line number
        index = 0   # character position at line
        mo = None
        # for block
        while True:
            for key, tok in self.block_tokens:
                mo = tok.match(text, offset, be)
                if mo:
                    break
            if mo is None:
                break
            m_string = text[offset:mo.end()]
            line_fix = m_string.count('\n')
            if line_fix > 0:    # calculate length in last line
                index_end = len(m_string) - m_string.rfind('\n') - 1
            else:
                index_end = index + len(m_string)
            m_start = self.editor().positionFromLineIndex(line, index)
            m_end = self.editor().positionFromLineIndex(line + line_fix,
                                                        index_end)
            self.startStyling(m_start)
            self.setStyling(m_end - m_start, self.styles[key])
            line += line_fix
            index = index_end
            offset = mo.end()
        # for inline
        for line in range(bs_line, be_line + 1):
            line_text = toUtf8(self.editor().text(line))
            for key, tok in self.inline_tokens:
                mo_list = tok.finditer(line_text)
                for mo in mo_list:
                    g_start = mo.start(1)
                    g_end = mo.end(1)
                    m_start = self.editor().positionFromLineIndex(line, g_start)
                    m_end = self.editor().positionFromLineIndex(line, g_end)
                    self.startStyling(m_start)
                    self.setStyling(m_end - m_start, self.styles[key])
        # move style position to end
        self.startStyling(end)
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
        font = super(SciLexerReStructedText, self).defaultFont(style)
        for prop in prop_list:
            if ':' in prop:
                continue
            if prop.startswith('$(font.'):
                mo = re.match(r'^\$\(font\.(.+)\)', prop)
                font = QtGui.QFont(mo.group(1))
            elif prop == 'bold':
                font.setBold(True)
            elif prop == 'italic':
                font.setItalic(True)
            elif prop == 'underline':
                font.setUnderline(True)
        return font

    def getProperty(self, style):
        if style in self.properties:
            prop_list = self.properties[style].split(',')
            return prop_list
        return []
