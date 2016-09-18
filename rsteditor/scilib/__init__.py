from .input import _SciImSupport

try:
    from .scilexerrest import QsciLexerRest
except Exception:
    print('[WARNING] Do not find c++ lexer, use PYTHON rst lexer')
    from .scilexerrest_py import QsciLexerRest
