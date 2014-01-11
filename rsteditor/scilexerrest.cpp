
#include <Python.h>

#include <QtCore>
#include <QtGui>

#include <Qsci/qscilexercustom.h>

#include "scilexerrest.h"

QsciLexerRest::QsciLexerRest(QObject * parent): QsciLexerCustom(parent)
{
    keywords.append("attention");
    keywords.append("caution");
    keywords.append("danger");
    keywords.append("error");
    keywords.append("hint");
    keywords.append("important");
    keywords.append("note");
    keywords.append("tip");
    keywords.append("warning");
    keywords.append("admonition");
    keywords.append("image");
    keywords.append("figure");
    keywords.append("topic");
    keywords.append("sidebar");
    keywords.append("code");
    keywords.append("math");
    keywords.append("rubric");
    keywords.append("epigraph");
    keywords.append("highlights");
    keywords.append("compound");
    keywords.append("container");
    keywords.append("table");
    keywords.append("csv-table");
    keywords.append("list-table");
    keywords.append("contents");
    keywords.append("sectnum");
    keywords.append("section-autonumbering");
    keywords.append("section-numbering");
    keywords.append("header");
    keywords.append("footer");
    keywords.append("target-notes");
    keywords.append("meta");
    keywords.append("include");
    keywords.append("raw");
    keywords.append("class");
    keywords.append("role");
    keywords.append("default-role");
    properties.insert(0,  "fore,#000000");
    properties.insert(1,  "fore,#4e9a06");
    properties.insert(2,  "fore,#204a87,bold");
    properties.insert(3,  "fore,#888a85");
    properties.insert(4,  "fore,#5c3566");
    properties.insert(5,  "fore,#845902");
    properties.insert(6,  "fore,#a40000");
    properties.insert(7,  "fore,#3465a4,back,#eeeeec");
    properties.insert(8,  "fore,#3465a4,back,#eeeeec,$(font.Monospace)");
    properties.insert(9,  "fore,#8f5902");
    properties.insert(10, "fore,#8f5902");
    properties.insert(11, "fore,#3465a4,back,#eeeeec");
    properties.insert(12, "fore,#ce5c00");
    properties.insert(13, "fore,#555753");
    properties.insert(14, "fore,#4e9a06");
    properties.insert(15, "fore,#a40000");
    properties.insert(16, "italic");
    properties.insert(17, "bold");
    properties.insert(18, "fore,#3465a4,back,#eeeeec,$(font.Monospace)");
    properties.insert(19, "fore,#4e9a06,underline");
    properties.insert(20, "fore,#4e9a06,underline");
    properties.insert(21, "fore,#555753");
    properties.insert(22, "fore,#4e9a06");
    properties.insert(23, "fore,#4e9a06");
    properties.insert(24, "fore,#4e9a06");
    descs.insert("string", 0);
    descs.insert("colon", 0);
    descs.insert("space", 0);
    descs.insert("newline", 0);
    descs.insert("comment", 1);
    descs.insert("title", 2);
    descs.insert("section", 2);
    descs.insert("transition", 3);
    descs.insert("bullet", 4);
    descs.insert("enumerated", 4);
    descs.insert("definition1", 5);
    descs.insert("definition2", 5);
    descs.insert("field", 0);
    descs.insert("in_field", 6);
    descs.insert("option", 7);
    descs.insert("literal1", 8);
    descs.insert("literal2", 8);
    descs.insert("line", 9);
    descs.insert("quote", 10);
    descs.insert("doctest", 11);
    descs.insert("table1", 12);
    descs.insert("table2", 12);
    descs.insert("footnote", 13);
    descs.insert("target1", 14);
    descs.insert("target2", 14);
    descs.insert("directive", 0);
    descs.insert("in_directive", 15);
    descs.insert("in_emphasis", 16);
    descs.insert("in_strong", 17);
    descs.insert("in_literal", 18);
    descs.insert("in_url1", 19);
    descs.insert("in_url2", 19);
    descs.insert("in_link1", 20);
    descs.insert("in_link2", 20);
    descs.insert("in_footnote", 21);
    descs.insert("in_substitution", 22);
    descs.insert("in_target", 23);
    descs.insert("in_reference", 24);
    regexs.insert("comment",     QRegExp("^\\.\\. (?!_|\\[)(?!.+::).+(?:\\n{0,2} {3,}.+)*\\n"));
    regexs.insert("title",       QRegExp("^([=`'\"~^_*+#-]{2,})\\n.+\\n\\1\\n"));
    regexs.insert("section",     QRegExp("^.+\\n[=`'\"~^_*+#-]{2,}\\n"));
    regexs.insert("transition",  QRegExp("^\\n[=`'\"~^_*+#-]{4,}\\n\\n"));
    regexs.insert("bullet",      QRegExp("^ *[\\-+*] +.+(?:\\n+ +.+)*\\n"));
    regexs.insert("enumerated",  QRegExp("^ *\\(?[0-9a-zA-Z#](?:\\.|\\)) +.+(?:\\n+ +.+)*\\n"));
    regexs.insert("definition1", QRegExp("^\\w+\\n( +).+(?:\\n+\\1.+)*\\n"));
    regexs.insert("definition2", QRegExp("^\\w+ *:.*\\n( +).+(?:\\n+\\1.+)*\\n"));
    regexs.insert("field",       QRegExp("^:[^:]+:[ \\n]+.+(?:\\n+ +.+)*\\n"));
    regexs.insert("option",      QRegExp("^[\\-/]+.+(?:  .+)?(?:\\n+ +.+)*\\n"));
    regexs.insert("literal1",    QRegExp("::\\n\\n([ >]+).+(?:\\n+\\1.*)*\\n\\n"));
    regexs.insert("literal2",    QRegExp(".. code::(?:.*)\\n\\n([ >]+).+(?:\\n+\\1.*)*\\n\\n"));
    regexs.insert("line",        QRegExp("^ *\\|(?: +.+)?(?:\\n +.+)*\\n"));
    regexs.insert("quote",       QRegExp("^( {2,}).+(?:\\n\\1.+)*\\n\\n"));
    regexs.insert("doctest",     QRegExp("^>>>.+\\n"));
    regexs.insert("table1",      QRegExp("^( *)[\\-=+]{2,}(\\n\\1[\\|+].+)+\\n\\n"));
    regexs.insert("table2",      QRegExp("^( *)[\\-=]{2,} [\\-= ]+(\\n\\1.+)+\\n\\n"));
    regexs.insert("footnote",    QRegExp("^\\.\\. \\[[^\\n\\]]+\\][ \\n]+.+(\\n+ +.+)*\\n\\n"));
    regexs.insert("target1",     QRegExp("^\\.\\. _.+:(\\n +)*.*\\n"));
    regexs.insert("target2",     QRegExp("^__(?: .+)*\\n"));
    regexs.insert("directive",   QRegExp("^\\.\\. (?!_|\\[).+::.*(\\n+ +.+)*\\n"));
    regexs.insert("newline",     QRegExp("\\n"));
    regexs.insert("space",       QRegExp(" +"));
    regexs.insert("string",      QRegExp("[^: \\n]+"));
    regexs.insert("colon",       QRegExp(":"));
    inline_regexs.insert("in_emphasis",     QRegExp("(?<!\\*)(\\*\\w.*?\\w\\*)(?!\\*)"));
    inline_regexs.insert("in_strong",       QRegExp("(\\*\\*\\w.*?\\w\\*\\*)"));
    inline_regexs.insert("in_literal",      QRegExp("(``\\w.*?\\w``)"));
    inline_regexs.insert("in_url1",         QRegExp("\\W((?:http://|https://|ftp://)[\\w\\-\\.:/]+)\\W"));
    inline_regexs.insert("in_url2",         QRegExp("(`[^<]+<[^>]+>`_)"));
    inline_regexs.insert("in_link1",        QRegExp("([\\w\\-]+_)\\W"));
    inline_regexs.insert("in_link2",        QRegExp("(`\\w.*?\\w`_)"));
    inline_regexs.insert("in_footnote",     QRegExp("(\\[[\\w\\*#]+\\]_)"));
    inline_regexs.insert("in_substitution", QRegExp("(\\|\\w.*?\\w\\|)"));
    inline_regexs.insert("in_target",       QRegExp("(_`\\w.*?\\w`)"));
    inline_regexs.insert("in_reference",    QRegExp("(:\\w+:`\\w+`)"));
    //inline_regexs.insert("in_directive",    QRegExp("^\\.\\. (%s)::" % '|'.join(keywords)));
    inline_regexs.insert("in_field",        QRegExp("^:([^:]+?):(?!`)"));
    setDefaultColor(QColor("#000000"));
    setDefaultPaper(QColor("#ffffff"));
    setDefaultFont(QFont("Monospace", 12));
    /*
    QMap <int, QString>::iterator item;
    for(item=properties.begin(); item!=properties.end(); item++){
        prop = item.value();
        fgcolor = defaultColor(item.key());
        bgcolor = defaultPaper(item.key());
        font = defaultFont(item.key());
        if(prop.startsWith("face:")){
            //fgcolor = QColor(prop.
        }
    }
    */
}

QsciLexerRest::~QsciLexerRest()
{
}

const char * QsciLexerRest::language() const
{
    return "rst";
}

const char * QsciLexerRest::lexer() const
{
    return "rest";
}

QString QsciLexerRest::description(int style) const
{
    return descs.key(style, QString("unknown"));
}

void QsciLexerRest::styleText(int start, int end)
{
    if(!editor())
        return;
    QString soruce;
    char *chars = (char *) malloc ((end - start) * sizeof(char) + 1);
    editor()->SendScintilla(QsciScintilla::SCI_GETTEXTRANGE, start, end, chars);
    source = QString(chars);
    /*
    startStyling(start, 0x1f);
    75 
        76  vector <text_partition> parts = makePartitions (chars, 0, source.length());
    77  sort(parts.begin(), parts.end(), text_partition_cmp);
    78  int lastIndex = 0;
    79  for (unsigned int i = 0; i < parts.size(); i++) {
        80  qDebug() << "partition id=" << parts[i].id << " begin=" << parts[i].begin << " end=" << parts[i].end;
        81  setStyling(parts[i].begin-lastIndex, getStyle(Default));
        82  setStyling(parts[i].end-parts[i].begin, partition_style[parts[i].id]);
        83  lastIndex = parts[i].end;
        84 
            85  }
        86  if (source.length()-lastIndex > 0) {
            87  setStyling(source.length()-lastIndex, getStyle(Default));
            88  }
            89  free(chars);
            */
}

QColor QsciLexerRest::defaultColor(int style) const
{
    QStringList props = properties.value(style).split(",");
    QStringList::iterator item;
    for(item=props.begin(); item!=props.end(); item++){
        if((*item).startsWith("fore:")){
            return QColor((*item).split(":")[1]);
        }
    }
    return QsciLexerCustom::defaultColor();
}
QColor QsciLexerRest::defaultPaper(int style) const
{
    QStringList props = properties.value(style).split(",");
    QStringList::iterator item;
    for(item=props.begin(); item!=props.end(); item++){
        if((*item).startsWith("back:")){
            return QColor((*item).split(":")[1]);
        }
    }
    return QsciLexerCustom::defaultPaper();
}
QFont QsciLexerRest::defaultFont(int style) const
{
    QStringList props = properties.value(style).split(",");
    QFont font = QsciLexerCustom::defaultFont();
    QStringList::iterator item;
    QRegExp regex("\\$\\(font\\.(.*)\\)");
    for(item=props.begin(); item!=props.end(); item++){
        if(regex.indexIn(*item) != -1){
            font = QFont(regex.cap(1));
        } else if(*item == "bold"){
            font.setBold(TRUE);
        } else if(*item == "italic"){
            font.setItalic(TRUE);
        } else if(*item == "underline"){
            font.setUnderline(TRUE);
        }
    }
    return font;
}
