#ifdef QSCILEXERREST_H
#define QSCILEXERREST_H

class QsciLexerCustom;

class QsciLexerRest: public QsciLexerCustom
{
    Q_OBJECT
    public:
        QsciLexerRest(QObject * parent=0);
        ~QsciLexerRest();
        const char * language() const;
        const char * lexer() const;
        void styleText(int start, int end);
};

#endif
