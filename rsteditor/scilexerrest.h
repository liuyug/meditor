#ifndef QSCILEXERREST_H
#define QSCILEXERREST_H
#include <QtGui>
#include <Qsci/qscilexercustom.h>

struct STYLEDTEXT{
    int length;
    int style;
};

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
        void setDebugLevel(int level);
        void readConfig(QString & prop_file);
    private:
        int debug;
        QStringList keywords;
        QMap <QString, int> descs;
        QList<QString> regex_keys;
        QMap <QString, QRegExp> regexs;
        QMap <QString, QRegExp> inline_regexs;
        QMap <int, QString> properties;
        QMap <int, struct STYLEDTEXT> styled_text;
        QString rangeText(int start, int end);
        QString stylingText(int * start, int * end);
        QMap <int, struct STYLEDTEXT> parseText(int * start, int * end);
};

#endif
