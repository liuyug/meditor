%Module scilexerrest

%Import QtCore/QtCoremod.sip
%Import Qsci/qscimod5.sip

class QsciLexerRest: QsciLexerCustom
{
%TypeHeaderCode
#include "scilexerrest.h"
%End
    public:
        QsciLexerRest(QObject * parent=0);
        virtual ~QsciLexerRest();
        virtual const char * language() const;
        virtual const char * lexer() const;
        virtual QString description(int style) const;
        virtual void styleText(int start, int end);
        virtual QColor defaultColor(int style) const;
        virtual QColor defaultPaper(int style) const;
        virtual QFont defaultFont(int style) const;
        void setDebugLevel(int level);
        void readConfig(QString & prop_file);
};


