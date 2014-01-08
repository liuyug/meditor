
#include <Python.h>

#include <Qt/QtCore>
#include <Qt/QtGui>

#include <Qsci/qscilexercustom.h>

#include <scilexerrest.h>

QsciLexerRest::QsciLexerRest(QObject * parent): QsciLexerCustom(parent)
{
    setDefaultColor(QColor("#000000"));
    setDefaultPaper(QColor("#ffffff"));
    setDefaultFont(QFont("Monospace", 12));
}

QsciLexerRest::~QsciLexerRest()
{
}

const char * QsciLexerRest::language()
{
    return "rest"
}

const char * QsciLexerRest::lexer()
{
    return "rest"
}

QString QsciLexerRest::description(int style)
{
    return QString("string")
}

void QsciLexerRest::styleText(int start, int end)
{
    return 0
}


