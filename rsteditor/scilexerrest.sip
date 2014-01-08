%Module qscilexerrest

%Import QtCore/QtCoremod.sip
%Import Qsci/qscimod4.sip

class QsciLexerRest: QsciLexerCustom
{
%TypeHeaderCode
#include <Qt/QtCore>
#include <Qsci/scilexerrest.h>
%End
    public:
        QsciLexerRest(QObject * parent=0);
        ~QsciLexerRest();
        const char * language() const;
        const char * lexer() const;
        void styleText(int start, int end);
};


