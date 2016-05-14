import re
import logging

from PyQt5 import Qsci, QtGui, QtCore

from rsteditor.util import toUtf8

logger = logging.getLogger(__name__)


class QsciLexerRest(Qsci.QsciLexerCustom):
    keyword_list = [
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
        'definition': 5,
        'field': 0,
        'in_field': 6,
        'option': 7,
        'literal1': 8,
        'literal2': 8,
        'literal3': 8,
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
        'in_unusedspace': 25,
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
        25: 'back:#ef2929',
    }
    token_regex = [
        # block markup
        ('directive',   r'''^\.\. +[\-\w]+::.*\n'''),
        ('comment',     r'''^\.\. +[\-\w].*\n(\n* .*\n)*\n'''),
        # end with \n
        ('title',       r'''^([=`'"~^_*+#-]+)\n.+\n\1\n'''),
        # end with \n
        ('section',     r'''^\w.*\n[=`'"~^_*+#-]+\n'''),
        ('transition',  r'''^\n[=`'"~^_*+#-]{4,}\n\n'''),
        ('bullet',      r'''^ *[\-+*] +.+\n(\n* {2,}.+\n)*\n'''),
        ('enumerated',  r'''^ *[(]?[0-9a-zA-Z#]+[.)] +.+\n( *[(]?[0-9a-zA-Z#]+[.)] +.+\n)*\n'''),
        ('definition', r'''^\w.*\n( +).+\n(\n*\1.+\n)*(\w.*\n( +).+\n(\n*\1.+\n)*)*\n'''),
        ('field',       r'''^:[ \w\-]+:.*\n(\n* .+\n)*(:[ \w\-]+:.*\n(\n* .+\n)*)*\n'''),
        ('option',      r'''^[\-/]+\w[^\n]+\n(\n* +.*\n)*([\-/]+\w[^\n]+\n(\n* +.*\n)*)*\n'''),
        ('literal1',    r'''::\n\n( +).+\n(\n*\1.+\n)*\n'''),
        ('literal2',    r'''^>.*\n(>.*\n)*\n'''),
        ('literal3',    r'''^.. code::.*\n\n( +).+\n(\1.+\n)*\n'''),
        ('quote',       r'''^( {2,})\w.+\n(\n*\1.+\n)*\n'''),
        ('line',        r'''^ *\|( +.+)?\n( {2,}.*\n)*( *\|( +.+)?\n( {2,}.*\n)*)*\n'''),
        ('doctest',     r'''^>>> .+\n'''),
        ('table1',      r'''^( *)[\-=+]{2,}\n(\1[\|+].+\n)+\n'''),
        ('table2',      r'''^( *)[\-=]{2,} [\-= ]+\n(\1.+\n)+\n'''),
        ('footnote',    r'''^\.\. \[[^\]]+\] .+\n(\n* {3,}.+\n)*\n'''),
        ('target1',     r'''^\.\. _[^:]+:( .+)*\n'''),
        ('target2',     r'''^__ .+\n'''),
        ('newline',     r'''\n'''),
        ('space',       r''' +'''),
        ('string',      r'''[^: \n]+'''),
        ('colon',       r''':'''),

        # inline markup
        ('in_emphasis', r'''(\*\w[^*\n]*\*)'''),
        ('in_strong',   r'''(\*\*\w[^*\n]*\*\*)'''),
        ('in_literal',  r'''(``\w[^`\n]*``)'''),
        ('in_url1',     r'''\W((http://|https://|ftp://)[\w\-\.:/]+)\W'''),
        ('in_url2',     r'''(`[^<\n]+<[^>\n]+>`_)'''),
        ('in_link1',    r'''\W(\w+_)\W'''),
        ('in_link2',    r'''(`\w[^`\n]*`_)'''),
        ('in_footnote', r'''(\[[\w*#]+\]_)'''),
        ('in_substitution', r'''(\|\w[^\|]*\|)'''),
        ('in_target',    r'''(_`\w[^`\n]*`)'''),
        ('in_reference', r'''(:\w+:`\w+`)'''),
        ('in_directive', r'''^\.\. +(%s)::''' % '|'.join(keyword_list)),
        ('in_field',     r'''^:([^:]+):[ \n]'''),
        ('in_unusedspace', r'''( +)\n'''),
    ]

    def __init__(self, *args, **kwargs):
        super(QsciLexerRest, self).__init__(*args, **kwargs)
        self.setDefaultColor(QtGui.QColor('#000000'))
        self.setDefaultPaper(QtGui.QColor('#ffffff'))
        self.setDefaultFont(QtGui.QFont('Monospace', 12))
        self.rstyles = dict(zip(*(self.styles.values(), self.styles.keys())))
        # to store global styleing
        self.styled_text = {}
        self.block_tokens = []
        self.inline_tokens = []
        for key, regex in self.token_regex:
            if key.startswith('in_'):
                self.inline_tokens.append((key, re.compile(
                    regex,
                    re.UNICODE | re.IGNORECASE,
                )))
            else:
                self.block_tokens.append((key, re.compile(
                    regex,
                    re.UNICODE | re.MULTILINE | re.IGNORECASE,
                )))
        return

    def language(self):
        return 'rst'

    def description(self, style):
        return self.rstyles.get(style, '')

    def getStyleAt(self, pos):
        return self.editor().SendScintilla(Qsci.QsciScintilla.SCI_GETSTYLEAT, pos)

    def getTextRange(self, start, end):
        if not self.editor():
            return ''
        bs_line, _ = self.editor().lineIndexFromPosition(start)
        be_line, _ = self.editor().lineIndexFromPosition(end)
        text = []
        for x in range(bs_line, be_line):
            text.append(self.editor().text(x))
        return toUtf8(''.join(text))

    def getStylingPosition(self, start, end):
        """
        inline style and global style is confilicted at calling.
        Need a list to store global style position
        """
        styled_keys = sorted(self.styled_text.keys())
        if not styled_keys:
            return (start, end)
        new_start = 0
        new_end = self.editor().length()
        for x in range(len(styled_keys)):
            pos = styled_keys[x]
            if start < pos:
                x = max(x - 2, 0)
                while x >= 0:
                    new_start = styled_keys[x]
                    style_key = self.styled_text[new_start]['style']
                    # find first non-string style
                    if self.styles[style_key] != self.styles['string']:
                        break
                    x -= 1
                break
        for y in range(len(styled_keys)):
            pos = styled_keys[y]
            if end < pos:
                y = min(y + 1, len(styled_keys) - 1)
                while y < len(styled_keys):
                    new_end = styled_keys[y]
                    style_key = self.styled_text[new_end]['style']
                    # find last non-string style
                    if self.styles[style_key] != self.styles['string']:
                        break
                    y += 1
                break
        for k in styled_keys[x:y]:
            del self.styled_text[k]
        logger.debug('old: %s - %s, new: %s - %s' % (start, end, new_start, new_end))
        return (new_start, new_end)

    def do_StylingText(self, start, end):
        """
        To support non-latin character, function 'positionFromLineIndex'
        will be called for difference length between latin and non-latin.
        """
        text = self.getTextRange(start, end)
        logger.debug('styling text: %s', repr(text))
        line, index = self.editor().lineIndexFromPosition(start)
        m_start = start
        offset = 0
        self.startStyling(start)
        while offset < len(text):
            mo = None
            for key, tok in self.block_tokens:
                mo = tok.match(text, offset)
                if mo:
                    break
            assert(mo)
            m_string = text[offset:mo.end()]
            line_fix = m_string.count('\n')
            end_line = line + line_fix
            if line_fix > 0:    # calculate length in last line
                end_index = 0
            else:
                end_index = index + len(m_string)
            m_end = self.editor().positionFromLineIndex(end_line, end_index)
            message = '%s(%s,%s): %s' % (key, m_start, m_end, repr(m_string))
            logger.debug(message)
            if (m_end - m_start) > 0:
                self.setStyling(m_end - m_start, self.styles[key])
                self.styled_text[m_start] = {
                    'length': m_end - m_start,
                    'style': key,
                }
            else:
                logger.error('*** !!! length < 0 !!! ***')
                logger.debug('Error: match %s from %s(%s,%s) to %s(%s,%s)' % (
                    repr(m_string),
                    m_start, line, index,
                    m_end, end_line, end_index,
                ))
            # next position
            m_start = m_end
            line = end_line
            index = end_index
            offset = mo.end()

    def do_InlineStylingText(self, start, end):
        bs_line, index = self.editor().lineIndexFromPosition(start)
        be_line, index = self.editor().lineIndexFromPosition(end)
        for line in range(bs_line, be_line):
            line_text = toUtf8(self.editor().text(line))
            for key, tok in self.inline_tokens:
                mo_list = tok.finditer(line_text)
                for mo in mo_list:
                    l_start = mo.start(1)
                    l_end = mo.end(1)
                    m_start = self.editor().positionFromLineIndex(line, l_start)
                    m_end = self.editor().positionFromLineIndex(line, l_end)
                    assert(m_end - m_start)
                    message = '%s(%s,%s): %s' % (key, line + 1, l_start, repr(line_text[l_start:l_end]))
                    logger.debug(message)
                    self.startStyling(m_start)
                    self.setStyling(m_end - m_start, self.styles[key])

    def styleText(self, start, end):
        if not self.editor():
            return
        logger.debug('=' * 80)
        s_start, s_end = self.getStylingPosition(start, end)
        self.do_StylingText(s_start, s_end)
        self.do_InlineStylingText(s_start, s_end)
        # tell to end styling
        self.startStyling(self.editor().length())

    def defaultStyle(self):
        return self.styles['string']

    def defaultColor(self, style):
        prop_list = self.getProperty(style)
        for prop in prop_list:
            if prop.startswith('fore:'):
                color = prop.split(':')[1]
                return QtGui.QColor(color)
        return super(QsciLexerRest, self).defaultColor(style)

    def defaultPaper(self, style):
        prop_list = self.getProperty(style)
        for prop in prop_list:
            if prop.startswith('back:'):
                color = prop.split(':')[1]
                return QtGui.QColor(color)
        return super(QsciLexerRest, self).defaultPaper(style)

    def defaultFont(self, style):
        prop_list = self.getProperty(style)
        font = super(QsciLexerRest, self).defaultFont(style)
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

    def setDebugLevel(self, logging_level):
        pass

    def readConfig(self, rst_prop_file):
        prop_settings = QtCore.QSettings(rst_prop_file, QtCore.QSettings.IniFormat)
        for num in range(0, len(self.properties)):
            value = toUtf8(prop_settings.value(
                'style.%s.%s' % (self.language(), num),
                type=str,
            ))
            if not value:
                continue
            if isinstance(value, str):
                prop_list = value.split(',')
            else:
                prop_list = value
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
