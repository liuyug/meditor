from .scilexerdefault import QsciLexerDefault
from .scilexerrest_py import QsciLexerRest
from .scilexerart import QsciLexerArt

from ..util import singleton

from PyQt5 import Qsci


LEXER_EXTENSION = {
    'QsciLexerAVS': ['.avs'],
    'QsciLexerBash': ['.sh', '.bash'],
    'QsciLexerBatch': ['.bat', '.cmd'],
    'QsciLexerCMake': ['.cmake'],
    'QsciLexerCPP': ['.cpp', '.cxx', '.cc', '.c', '.hpp', '.hxx', '.hh', '.h'],
    'QsciLexerCSS': ['.css'],
    'QsciLexerCSharp': ['.cs'],
    'QsciLexerCoffeeScript': ['.coffee'],
    'QsciLexerD': ['.d'],
    'QsciLexerDiff': ['.diff'],
    'QsciLexerFortran': ['.f'],
    'QsciLexerFortran77': ['.f77'],
    'QsciLexerHTML': ['.html', '.htm', '.asp', '.php'],
    'QsciLexerIDL': ['.idl'],
    'QsciLexerJSON': ['.json'],
    'QsciLexerJava': ['.java'],
    'QsciLexerJavaScript': ['.js'],
    'QsciLexerLua': ['.lua'],
    'QsciLexerMakefile': ['.makefile'],
    'QsciLexerMarkdown': ['.markdown', '.md'],
    'QsciLexerMatlab': ['.matlab'],
    'QsciLexerOctave': ['.octave'],
    'QsciLexerPO': ['.po', '.pot'],
    'QsciLexerPOV': ['.pov', '.inc'],
    'QsciLexerPascal': ['.pas'],
    'QsciLexerPerl': ['.pl', '.pm'],
    'QsciLexerPostScript': ['.ps'],
    'QsciLexerProperties': ['.ini', '.conf', 'properties'],
    'QsciLexerPython': ['.py'],
    'QsciLexerRuby': ['.rb'],
    'QsciLexerSQL': ['.sql'],
    'QsciLexerSpice': ['.spice'],
    'QsciLexerTCL': ['.tcl'],
    'QsciLexerTeX': ['.tex'],
    'QsciLexerVHDL': ['.vhdl'],
    'QsciLexerVerilog': ['.verilog'],
    'QsciLexerXML': ['.xml'],
    'QsciLexerYAML': ['.yaml', '.yml'],
}


@singleton
class ExtensionLexer:
    _extension_lexer = {
        '.rst': QsciLexerRest,
        '.rest': QsciLexerRest,
        '.txt': QsciLexerDefault,
        '.log': QsciLexerDefault,
        '.csv': QsciLexerDefault,
        '.desktop': QsciLexerDefault,
        '.spec': QsciLexerDefault,
        '.nfo': QsciLexerArt,
        '.art': QsciLexerArt,
    }

    def __init__(self):
        for lexer in dir(Qsci):
            if not lexer.startswith('QsciLexer'):
                continue
            if lexer in ['QsciLexer', 'QsciLexerCustom']:
                continue
            if lexer in LEXER_EXTENSION:
                lexer_class = getattr(Qsci, lexer)
                for ext in LEXER_EXTENSION[lexer]:
                    self._extension_lexer[ext] = lexer_class
            else:
                print('missing lexer: %s' % lexer)

    def __contains__(self, ext):
        return ext.lower() in self._extension_lexer

    def __getitem__(self, ext):
        return self._extension_lexer.get(ext.lower())

    def get(self, ext):
        return self._extension_lexer.get(ext.lower())


EXTENSION_LEXER = ExtensionLexer()
