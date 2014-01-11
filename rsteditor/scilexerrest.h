#ifndef QSCILEXERREST_H
#define QSCILEXERREST_H
#include <QtGui>
#include <Qsci/qscilexercustom.h>

class QsciLexerRest: public QsciLexerCustom
{
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
    private:
        QStringList keywords;
        QMap <QString, int> descs;
        QMap <QString, QRegExp> regexs;
        QMap <QString, QRegExp> inline_regexs;
        QMap <int, QString> properties;
        QStringList & getProperties(int style);
};

#endif
