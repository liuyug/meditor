import re
import logging

from PyQt5 import Qsci, QtGui, QtCore

from ..util import toUtf8

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
        'newline': 0,
        'comment': 1,
        'title': 2,
        'section': 2,
        'transition': 3,
        'bullet': 4,
        'enumerated': 4,
        'definition': 5,
        'field': 0,
        'option': 7,
        'literal': 8,
        'literal2': 8,
        'literal3': 8,
        'line': 9,
        'line2': 9,
        'quote': 10,
        'doctest': 11,
        'table': 12,
        'table1': 12,
        'table2': 12,
        'footnote': 13,
        'target': 14,
        'target1': 14,
        'target2': 14,
        'directive': 0,
    }
    inline_styles = {
        'in_field': 6,
        'in_directive': 15,
        'in_emphasis': 16,
        'in_strong': 17,
        'in_literal': 18,
        'in_url': 19,
        'in_url1': 19,
        'in_url2': 19,
        'in_url3': 19,
        'in_link': 20,
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
        ('title',       r'''^([=`'"~^_*+#-]+)\n.+\n\1\n'''),
        ('section',     r'''^\w.*\n[=`'"~^_*+#-]+\n'''),
        ('transition',  r'''^\n[=`'"~^_*+#-]{4,}\n\n'''),
        ('bullet',      r'''^[\-+*] +.+(\n+ {2,}.+)*\n'''),
        ('enumerated',  r'''^(\(?(#|\w+)[.)] +)\S.*(\n+ {2,}.+)*\n'''),
        ('field',       r'''^:[ \w\-]+:.*(\n+ +.*)*\n'''),
        ('option',      r'''^[\-/]+\w[^\n]+(\n+ +.*)*\n'''),
        ('literal2',    r'''^>.*\n(>.*\n)*\n'''),
        ('line',        r'''^\|.*(\n .*)*\n'''),
        ('line2',       r'''^( +\|).*\n'''),
        ('quote',       r'''^( {2,})\w.+(\n+\1.+)*\n\n'''),
        ('definition',  r'''^\w.*\n +.*(\n+ +.*)*\n'''),
        ('doctest',     r'''^>>> .+\n'''),
        ('table1',      r'''^( *)[\-=+]{2,}\n(\1[\|+].+\n)+\n'''),
        ('table2',      r'''^( *)[\-=]{2,} [\-= ]+\n(\1.+\n)+\n'''),

        ('literal3',    r'''^\.\. +code::.*(\n+ {2,}.+)*\n\n'''),
        ('directive',   r'''^\.\. +[\-\w]+::.*(\n+ {2,}.+)*\n'''),
        ('footnote',    r'''^\.\. \[[^\]]+\] .+(\n+ {3,}.+)*\n'''),
        ('target1',     r'''^\.\. _[^:]+: .*\n'''),
        ('comment',     r'''^\.\. +[\-\w].*(\n+ {2,}.+)*\n'''),
        ('target2',     r'''^__ .+\n'''),
        # ^ only match from line beginning
        ('literal',     r'''::\n(\n+ +.*)+\n'''),
        ('newline',     r'''\n+'''),
        ('colon',       r''':+'''),
        ('string',      r'''[^:\n]+'''),

        # inline markup
        ('in_emphasis', r'''(\*\w[^*\n]*\*)'''),
        ('in_strong',   r'''(\*{2}\w[^*\n]*\*{2})'''),
        ('in_literal',  r'''(`{2}\w[^`\n]*`{2})'''),
        ('in_url1',     r'''\W(\w+://[\w\-\.:/]+)\W'''),
        ('in_url2',     r'''(`[^<\n]+<[^>\n]+>`_)'''),
        ('in_url3',     r'''^(\w+://[\w\-\.:/]+)\W'''),
        ('in_link1',    r'''\W(\w+_)\W'''),
        ('in_link2',    r'''(`\w[^`\n]*`_)'''),
        ('in_footnote', r'''(\[[\w*#]+\]_)'''),
        ('in_substitution', r'''(\|\w[^\|]*\|)'''),
        ('in_target',    r'''(_`\w[^`\n]*`)'''),
        ('in_reference', r'''(:\w+:`\w+`)'''),
        ('in_directive', r'''^\.{2} +(%s):{2}''' % '|'.join(keyword_list)),
        ('in_field',     r'''^:([^:]+):[ \n]'''),
        ('in_unusedspace', r'''( +)\n'''),
    ]
    block_tokens = None
    inline_tokens = None

    def __init__(self, parent=0):
        super(QsciLexerRest, self).__init__(parent)
        self.setDefaultColor(QtGui.QColor('#000000'))
        self.setDefaultPaper(QtGui.QColor('#ffffff'))
        self.setDefaultFont(QtGui.QFont('Monospace', 12))
        self.rstyles = dict(zip(*(self.styles.values(), self.styles.keys())))
        self.inline_rstyles = dict(zip(*(self.inline_styles.values(), self.inline_styles.keys())))
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
        return 'reStructedText'

    def description(self, style):
        return self.rstyles.get(style) or self.inline_rstyles.get(style)

    def do_StylingText(self, start, end):
        text = self.parent().text(start, end)
        self.startStyling(start)
        offset = 0
        while offset < len(text):
            mo = None
            for key, tok in self.block_tokens:
                mo = tok.match(text, offset)
                if mo:
                    break
            assert mo, repr(text[offset:])
            # !! must match a style
            m_string = mo.group(0)
            length = len(m_string.encode('utf8'))
            logger.debug('match: %s, %s, %s' % (key, length, repr(m_string)))
            self.setStyling(length, self.styles[key])
            offset = mo.end()
        self.do_InlineStylingText(start, end)

    def do_InlineStylingText(self, start, end):
        start_line, _ = self.editor().lineIndexFromPosition(start)
        end_line, _ = self.editor().lineIndexFromPosition(end)
        for x in range(start_line, end_line + 1):
            pos = self.editor().positionFromLineIndex(x, 0)
            if self.parent().getStyleAt(pos) == self.styles['literal']:
                continue
            text = self.editor().text(x)
            for key, tok in self.inline_tokens:
                mo_list = tok.finditer(text)
                for mo in mo_list:
                    m_string = mo.group(1)
                    length = len(m_string.encode('utf8'))
                    m_start = self.editor().positionFromLineIndex(x, mo.start(1))
                    logger.debug('inline match: %s, %s, %s' % (key, length, repr(m_string)))
                    self.startStyling(m_start)
                    self.setStyling(length, self.inline_styles[key])

    def styleText(self, start, end):
        """start and end is based bytes """
        if not self.editor():
            return
        if self.editor()._pauseLexer:
            self.editor()._lexerStart = min(start, self.editor()._lexerStart)
            self.editor()._lexerEnd = max(end, self.editor()._lexerEnd)
            return
        pos = max(start - 1, 0)
        pre_style = self.parent().getStyleAt(pos)
        while pos > 0:
            style = self.parent().getStyleAt(pos)
            if style not in self.inline_rstyles and style != pre_style:
                pos += 1
                break
            pos -= 1
        fix_start = pos
        pos = min(end + 1, self.parent().length())
        suf_style = self.parent().getStyleAt(pos)
        while pos < self.parent().length():
            style = self.parent().getStyleAt(pos)
            if style not in self.inline_rstyles and style != suf_style:
                pos -= 1
                break
            pos += 1
        fix_end = pos
        logger.debug('styling'.center(40, '-'))
        text = self.parent().text(start, end)
        fix_text = self.parent().text(fix_start, fix_end)
        logger.debug('text: %s %s %s' % (start, end, repr(text)))
        logger.debug('fix range text: %s %s %s' % (fix_start, fix_end, repr(fix_text)))
        self.do_StylingText(fix_start, fix_end)

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
