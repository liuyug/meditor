import os.path
import re

from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciLexerCustom

from rsteditor.util import toUtf8
from rsteditor import __home_data_path__


class SciLexerReStructedText(QsciLexerCustom):
    keywords = [
        'attention',
        'caution',
        'danger',
        'error',
        'hint',
        'important',
        'note',
        'tip',
        'warning',
        'admonition',
        'image', 'figure',
        'topic',
        'sidebar',
        'code',
        'math',
        'rubric',
        'epigraph',
        'highlights',
        'compound',
        'container',
        'table',
        'csv-table',
        'list-table',
        'contents',
        'sectnum', 'section-autonumbering',
        'section-numbering',
        'header', 'footer',
        'target-notes',
        'meta',
        'include',
        'raw',
        'class',
        'role',
        'default-role',
    ]
    styles = {
        'string': 0,
        'colon': 0,
        'space': 0,
        'newline': 0,
        'comment': 1,
        'title': 2,
        'section': 2,
        'transition': 3,
        'bullet': 4,
        'enumerated': 4,
        'definition1': 5,
        'definition2': 5,
        'field': 0,
        'in_field': 6,
        'option': 7,
        'literal1': 8,
        'literal2': 8,
        'line': 9,
        'quote': 10,
        'doctest': 11,
        'table1': 12,
        'table2': 12,
        'footnote': 13,
        'target1': 14,
        'target2': 14,
        'directive': 0,
        'in_directive': 15,
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
        2:  'fore:#204a87,bold',
        3:  'fore:#888a85',
        4:  'fore:#5c3566',
        5:  'fore:#845902',
        6:  'fore:#a40000',
        7:  'fore:#3465a4,back:#eeeeec',
        8:  'fore:#3465a4,back:#eeeeec,$(font.Monospace)',
        9:  'fore:#8f5902',
        10: 'fore:#8f5902',
        11: 'fore:#3465a4,back:#eeeeec',
        12: 'fore:#ce5c00',
        13: 'fore:#555753',
        14: 'fore:#4e9a06',
        15: 'fore:#a40000',
        16: 'italic',
        17: 'bold',
        18: 'fore:#3465a4,back:#eeeeec,$(font.Monospace)',
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
        ('definition1', r'''^\w+\n( +).+(?:\n+\1.+)*\n'''),
        ('definition2', r'''^\w+ *:.*\n( +).+(?:\n+\1.+)*\n'''),
        ('field',       r'''^:[^:]+:[ \n]+.+(?:\n+ +.+)*\n'''),
        ('option',      r'''^[\-/]+.+(?:  .+)?(?:\n+ +.+)*\n'''),
        ('literal1',    r'''::\n\n([ >]+).+(?:\n+\1.*)*\n'''),
        ('literal2',    r'''.. code::(?:.*)\n\n([ >]+).+(?:\n+\1.*)*\n'''),
        ('line',        r'''^ *\|(?: +.+)?(?:\n +.+)*\n'''),
        ('quote',       r'''^( {2,}).+(?:\n\1.+)*\n'''),
        ('doctest',     r'''^>>>.+\n'''),
        ('table1',      r'''^( *)[\-=+]{2,}(\n\1[\|+].+)+\n'''),
        ('table2',      r'''^( *)[\-=]{2,} [\-= ]+(\n\1.+)+\n'''),
        ('footnote',    r'''^\.\. \[[^\n\]]+\][ \n]+.+(\n+ +.+)*\n'''),
        ('target1',     r'''^\.\. _.+:(\n +)*.*\n'''),
        ('target2',     r'''^__(?: .+)*\n'''),
        ('directive',   r'''^\.\. (?!_|\[).+::.*(\n+ +.+)*\n'''),
        ('newline',     r'''\n'''),
        ('space',       r''' +'''),
        ('string',      r'''[^: \n]+'''),
        ('colon',       r''':'''),
        # inline markup
        ('in_emphasis', r'''(?<!\*)(\*\w.*?\w\*)(?!\*)'''),
        ('in_strong',   r'''(\*\*\w.*?\w\*\*)'''),
        ('in_literal',  r'''(``\w.*?\w``)'''),
        ('in_url1',     r'''\W((?:http://|https://|ftp://)[\w\-\.:/]+)\W'''),
        ('in_url2',     r'''(`[^<]+<[^>]+>`_)'''),
        ('in_link1',    r'''([\w\-]+_)\W'''),
        ('in_link2',    r'''(`\w.*?\w`_)'''),
        ('in_footnote', r'''(\[[\w\*#]+\]_)'''),
        ('in_substitution', r'''(\|\w.*?\w\|)'''),
        ('in_target',    r'''(_`\w.*?\w`)'''),
        ('in_reference', r'''(:\w+:`\w+`)'''),
        ('in_directive', r'''^\.\. (%s)::''' % '|'.join(keywords)),
        ('in_field',     r'''^:([^:]+?):(?!`)'''),
    ]
    text_styles = {}

    def __init__(self, *args, **kwargs):
        super(SciLexerReStructedText, self).__init__(*args, **kwargs)
        self.setDefaultColor(QtGui.QColor('#000000'))
        self.setDefaultPaper(QtGui.QColor('#ffffff'))
        self.setDefaultFont(QtGui.QFont('Monospace', 12))
        prop_file = os.path.join(__home_data_path__, 'rst.properties')
        prop_settings = QtCore.QSettings(prop_file, QtCore.QSettings.IniFormat)
        for num in range(0, len(self.properties)):
            value = toUtf8(prop_settings.value('style.rst.%s' % num).toStringList().join(','))
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
                self.inline_tokens.append((key, re.compile(
                    regex,
                    re.U |
                    re.I
                )))
            else:
                self.block_tokens.append((key, re.compile(
                    regex,
                    re.U |
                    re.M |
                    re.I
                )))
        return

    def language(self):
        return 'ReStructedText'

    def description(self, style):
        for k, v in self.styles.items():
            if v == style:
                return k
        return ''

    def getTextRange(self, start, end):
        if not self.editor():
            return ''
        bs_line, index = self.editor().lineIndexFromPosition(start)
        be_line, index = self.editor().lineIndexFromPosition(end)
        text = []
        for line in range(bs_line, be_line + 1):
            text.append(toUtf8(self.editor().text(line)))
        return ''.join(text)
        # FIXME: segment fault ??
        #text = self.editor().SendScintilla(QsciScintilla.SCI_GETTEXTRANGE, start, end)

    def getStyleText(self, start, end):
        if not self.text_styles:
            start = 0
        else:
            found = False
            for key in sorted(self.text_styles):
                if found:
                    del self.text_styles[key]
                elif start <= (key + self.text_styles[key][0]):
                    found = True
                    start = key
        end = self.editor().length()
        return (start, end, self.getTextRange(start, end))

    def parseText(self, start, end):
        tstart, tend, text = self.getStyleText(start, end)
        # line number
        # character position at line
        line, index = self.editor().lineIndexFromPosition(tstart)
        offset = index  # character position at text
        mo = None
        tstyles = {}
        # for block
        while True:
            for key, tok in self.block_tokens:
                mo = tok.match(text, offset)
                if mo:
                    break
            if mo is None:
                break
            m_string = text[offset:mo.end()]
            line_fix = m_string.count('\n')
            if line_fix > 0:    # calculate length in last line
                index_end = 0
            else:
                index_end = index + len(m_string)
            m_start = self.editor().positionFromLineIndex(line, index)
            m_end = self.editor().positionFromLineIndex(line + line_fix,
                                                        index_end)
            if m_end < m_start:
                print('[ERROR]', key, offset, mo.end(), text[offset:mo.end()])
                print('[ERROR]', m_start, m_end, line, index, line + line_fix, index_end)
            else:
                tstyles[m_start] = (m_end - m_start, self.styles[key])
            line += line_fix
            index = index_end
            offset = mo.end()
        return (tstart, max(tend, m_end), tstyles)

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
        tstart, tend, tstyles = self.parseText(start, end)
        for key, value in tstyles.items():
            self.startStyling(key)
            self.setStyling(*value)
        self.text_styles.update(tstyles)
        # for inline
        mo = None
        bs_line, index = self.editor().lineIndexFromPosition(tstart)
        be_line, index = self.editor().lineIndexFromPosition(tend)
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
