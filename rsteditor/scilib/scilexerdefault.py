import logging

from PyQt5 import Qsci
from PyQt5.QtGui import QColor, QFont

logger = logging.getLogger(__name__)


class QsciLexerDefault(Qsci.QsciLexerCustom):
    styles = {
        "Default": 0,
        "Comment": 1,
        "Keyword": 2,
        "String": 3,
        "Number": 4,
    }

    def __init__(self, parent=None):
        super(QsciLexerDefault, self).__init__(parent)
        self.setDefaultColor(QColor('#000000'))
        self.setDefaultPaper(QColor('#ffffff'))
        self.setDefaultFont(QFont('Monospace', 12))

        self.setColor(QColor('#000000'), self.styles['Default'])
        self.setColor(QColor('#007f00'), self.styles['Comment'])
        self.setColor(QColor('#00007f'), self.styles['Keyword'])
        self.setColor(QColor('#7f007f'), self.styles['String'])
        self.setColor(QColor('#007f7f'), self.styles['Number'])
        for k, v in self.styles.items():
            self.setPaper(QColor('#ffffff'), v)
            self.setFont(QFont('Monospace', 12), v)

    def language(self):
        return 'Defaut'

    def description(self, style_idx):
        if style_idx < len(self.styles):
            return 'Default Lexer'
        else:
            return ''

    def styleText(self, start, end):
        if not self.editor():
            return
        self.startStyling(start)
        text = self.parent().text()[start:end]
        # example
        # regular expressions
        # splitter = re.compile(
        #     r"(\{\.|\.\}|\#|\'|\"\"\"|\n|\s+|\w+|\W)"
        # )
        # tokens = [
        #     (token, len(bytearray(token, "utf-8")))
        #     for token in splitter.findall(text)
        # ]
        # Multiline styles
        # multiline_comment_flag = False
        # Check previous style for a multiline style
        # if start != 0:
        #     previous_style = self.editor().SendScintilla(
        #         self.editor().SCI_GETSTYLEAT, start - 1)
        #     if previous_style == self.styles["MultilineComment"]:
        #         multiline_comment_flag = True
        # # Style the text in a loop
        # for i, token in enumerate(tokens):
        #     if (multiline_comment_flag == False and
        #             token[0] == "#" and tokens[i+1][0] == "["):
        #         # Start of a multiline comment
        #         self.setStyling(
        #             token[1], self.styles["MultilineComment"]
        #         )
        #         # Set the multiline comment flag
        #         multiline_comment_flag = True
        #     elif multiline_comment_flag == True:
        #         # Multiline comment flag is set
        #         self.setStyling(
        #             token[1], self.styles["MultilineComment"]
        #         )
        #         # Check if a multiline comment ends
        #         if token[0] == "#" and tokens[i-1][0] == "]":
        #             multiline_comment_flag = False
        #     elif token[0] in self.keyword_list:
        #         # Keyword
        #         self.setStyling(
        #             token[1],
        #             self.styles["Keyword"]
        #         )
        #     elif token[0] in self.unsafe_keyword_list:
        #         # Keyword
        #         self.setStyling(
        #             token[1],
        #             self.styles["Unsafe"]
        #         )
        #     else:
        #         # Style with the default style
        #         self.setStyling(
        #             token[1],
        #             self.styles["Default"]
        #         )
        # QScintilla lexer's length is based byte
        self.setStyling(len(bytearray(text, 'utf-8')), self.styles['Default'])
