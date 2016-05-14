#ifndef QSCILEXERREST_H
#define QSCILEXERREST_H

#include <Qsci/qscilexercustom.h>

struct TEXTSTYLE{
    int length;
    QString style;
};

class QsciLexerRest: public QsciLexerCustom
{
    // python setup.py don't support qt moc
    // Q_OBJECT
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
        virtual int defaultStyle() const;
        void setDebugLevel(int level);
        void readConfig(QString & prop_file);
    private:
        int debug;
        QStringList keyword_list;
        QMap <QString, int> styles;
        QMap <QString, QRegExp> block_tokens;
        QMap <QString, QRegExp> inline_tokens;
        QMap <int, QString> properties;
        QMap <int, struct TEXTSTYLE> styled_text;
        QString getTextRange(int start, int end);
        void getStylingPosition(int * start, int * end);
        void do_StylingText(int start, int end);
        void do_InlineStylingText(int start, int end);
};

#endif
