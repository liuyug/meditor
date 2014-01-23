
#include <Python.h>

#include <QtCore>
#include <QtGui>
#include <QtAlgorithms>

#include <Qsci/qsciscintilla.h>
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
    properties.insert(0,  "fore:#000000");
    properties.insert(1,  "fore:#4e9a06");
    properties.insert(2,  "fore:#204a87,bold");
    properties.insert(3,  "fore:#888a85");
    properties.insert(4,  "fore:#5c3566");
    properties.insert(5,  "fore:#845902");
    properties.insert(6,  "fore:#a40000");
    properties.insert(7,  "fore:#3465a4,back:#eeeeec");
    properties.insert(8,  "fore:#3465a4,back:#eeeeec,$(font.Monospace)");
    properties.insert(9,  "fore:#8f5902");
    properties.insert(10, "fore:#8f5902");
    properties.insert(11, "fore:#3465a4,back:#eeeeec");
    properties.insert(12, "fore:#ce5c00");
    properties.insert(13, "fore:#555753");
    properties.insert(14, "fore:#4e9a06");
    properties.insert(15, "fore:#a40000");
    properties.insert(16, "italic");
    properties.insert(17, "bold");
    properties.insert(18, "fore:#3465a4,back:#eeeeec,$(font.Monospace)");
    properties.insert(19, "fore:#4e9a06,underline");
    properties.insert(20, "fore:#4e9a06,underline");
    properties.insert(21, "fore:#555753");
    properties.insert(22, "fore:#4e9a06");
    properties.insert(23, "fore:#4e9a06");
    properties.insert(24, "fore:#4e9a06");
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
    regex_keys.append("comment");
    regex_keys.append("title");
    regex_keys.append("section");
    regex_keys.append("transition");
    regex_keys.append("bullet");
    regex_keys.append("enumerated");
    regex_keys.append("definition1");
    regex_keys.append("definition2");
    regex_keys.append("field");
    regex_keys.append("option");
    regex_keys.append("literal1");
    regex_keys.append("literal2");
    regex_keys.append("line");
    regex_keys.append("quote");
    regex_keys.append("doctest");
    regex_keys.append("table1");
    regex_keys.append("table2");
    regex_keys.append("footnote");
    regex_keys.append("target1");
    regex_keys.append("target2");
    regex_keys.append("directive");
    regex_keys.append("newline");
    regex_keys.append("space");
    regex_keys.append("string");
    regex_keys.append("colon");
    regex_keys.append("in_emphasis");
    regex_keys.append("in_strong");
    regex_keys.append("in_literal");
    regex_keys.append("in_url1");
    regex_keys.append("in_url2");
    regex_keys.append("in_link1");
    regex_keys.append("in_link2");
    regex_keys.append("in_footnote");
    regex_keys.append("in_substitution");
    regex_keys.append("in_target");
    regex_keys.append("in_reference");
    regex_keys.append("in_directive");
    regex_keys.append("in_field");
    regexs.insert("comment",     QRegExp("^\\.\\. (?!_|\\[)(?![^\\n]+::)[^\\n]+(?:\\n{0,2} {3,}[^\\n]+)*\\n"));
    regexs.insert("title",       QRegExp("^([=`'\"~^_*+#-]{2,})\\n[^\\n]+\\n\\1\\n"));
    regexs.insert("section",     QRegExp("^[^\\n]+\\n[=`'\"~^_*+#-]{2,}\\n"));
    regexs.insert("transition",  QRegExp("^\\n[=`'\"~^_*+#-]{4,}\\n\\n"));
    regexs.insert("bullet",      QRegExp("^ *[\\-+*] +[^\\n]+(?:\\n+ +[^\\n]+)*\\n"));
    regexs.insert("enumerated",  QRegExp("^ *\\(?[0-9a-zA-Z#](?:\\.|\\)) +[^\\n]+(?:\\n+ +[^\\n]+)*\\n"));
    regexs.insert("definition1", QRegExp("^\\w+\\n( +)[^\\n]+(?:\\n+\\1[^\\n]+)*\\n"));
    regexs.insert("definition2", QRegExp("^\\w+ *:[^\\n]*\\n( +)[^\\n]+(?:\\n+\\1[^\\n]+)*\\n"));
    regexs.insert("field",       QRegExp("^:[^:\\n]+:[ \\n]+[^\\n]+(?:\\n+ +[^\\n]+)*\\n"));
    regexs.insert("option",      QRegExp("^(?:-{1,2}|/)\\w[^\\n]+(?:\\n+ +[^\\n]+)*\\n"));
    regexs.insert("literal1",    QRegExp("^::\\n\\n( +|>)[^\\n]+(?:\\n+\\1[^\\n]*)*\\n"));
    regexs.insert("literal2",    QRegExp("^\\.\\. code::(?:[^\\n]*)\\n\\n([ >]+)[^\\n]+(?:\\n+\\1[^\\n]*)*\\n"));
    regexs.insert("line",        QRegExp("^ *\\|(?: +[^\\n]+)?(?:\\n +[^\\n]+)*\\n"));
    regexs.insert("quote",       QRegExp("^\\n( {2,})[^\\n]+(?:\\n\\1[^\\n]+)*\\n"));
    regexs.insert("doctest",     QRegExp("^>>>[^\\n]+\\n"));
    regexs.insert("table1",      QRegExp("^( *)[\\-=+]{2,}(\\n\\1[\\|+][^\\n]+)+\\n"));
    regexs.insert("table2",      QRegExp("^( *)[\\-=]{2,} [\\-= ]+(\\n\\1[^\\n]+)+\\n"));
    regexs.insert("footnote",    QRegExp("^\\.\\. \\[[^\\n\\]]+\\][ \\n]+[^\\n]+(\\n+ +[^\\n]+)*\\n"));
    regexs.insert("target1",     QRegExp("^\\.\\. _[^\\n]+:(\\n +)*[^\\n]*\\n"));
    regexs.insert("target2",     QRegExp("^__(?: [^\\n]+)*\\n"));
    regexs.insert("directive",   QRegExp("^\\.\\. (?!_|\\[)[^\\n]+::[^\\n]*(\\n+ +[^\\n]+)*\\n"));
    regexs.insert("newline",     QRegExp("^\\n"));
    regexs.insert("space",       QRegExp("^ +"));
    regexs.insert("string",      QRegExp("^[^: \\n]+"));
    regexs.insert("colon",       QRegExp("^:"));
    inline_regexs.insert("in_emphasis",     QRegExp("(\\*[^\\n\\*]+\\*)(?!\\*)"));
    inline_regexs.insert("in_strong",       QRegExp("(\\*\\*[^\\n\\*]+\\*\\*)"));
    inline_regexs.insert("in_literal",      QRegExp("(``[^`]+``)"));
    inline_regexs.insert("in_url1",         QRegExp("(\\w+://[\\w\\-\\.:/]+)"));
    inline_regexs.insert("in_url2",         QRegExp("(`[^<]+<[^>]+>`_+)"));
    inline_regexs.insert("in_link1",        QRegExp("([\\w\\-]+_)(?!\\w)"));
    inline_regexs.insert("in_link2",        QRegExp("(`\\w[^\\n]*\\w`_+)(?!\\w)"));
    inline_regexs.insert("in_footnote",     QRegExp("(\\[[\\w\\*#]+\\]_)(?!\\w)"));
    inline_regexs.insert("in_substitution", QRegExp("(\\|\\w[^\\n]+\\w\\|)"));
    inline_regexs.insert("in_target",       QRegExp("(_`[^`]+`)"));
    inline_regexs.insert("in_reference",    QRegExp("(:\\w+:`[^`]+`)"));
    inline_regexs.insert("in_directive",    QRegExp("^(\\.\\. (?:" + keywords.join("|") + ")::)"));
    inline_regexs.insert("in_field",        QRegExp("^:([^:]+):(?!`)"));
    setDefaultColor(QColor("#000000"));
    setDefaultPaper(QColor("#ffffff"));
    setDefaultFont(QFont("Monospace", 12));
    debug = 30;
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
    return QsciLexerCustom::lexer();
}

QString QsciLexerRest::description(int style) const
{
    return descs.key(style, QString());
}

QString QsciLexerRest::rangeText(int start, int end)
{
    QString text;
    if(!editor())
        return text;
    int bs_line, be_line, index;
    editor()->lineIndexFromPosition(start, &bs_line, &index);
    editor()->lineIndexFromPosition(end, &be_line, &index);
    for(int line=bs_line;line<(be_line+1);line++){
        text += editor()->text(line);
    }
    return text;
}

QString QsciLexerRest::stylingText(int * start, int * end)
{
    QList<int> keys = styled_text.keys();
    qSort(keys.begin(), keys.end(), qGreater<int>());
    QList<int>::iterator item;
    for(item=keys.begin(); item!=keys.end(); item++) {
        if(*start > *item && styled_text[*item].style != 0) {
            *start = *item;
            break;
        } else {
            styled_text.remove(*item);
        }
    }
    if(styled_text.empty()){
        *start = 0;
    }
    *end = editor()->length();
    return rangeText(*start, *end);
}

QMap <int, struct STYLEDTEXT> QsciLexerRest::parseText(int * start, int * end)
{
    QString text;
    text = stylingText(start, end);
    int line, index;
    editor()->lineIndexFromPosition(*start, &line, &index);
    int offset = index;
    QList<QString>::iterator item;
    QMap <int, struct STYLEDTEXT> tstyles;
    QRegExp rx;
    QString key, mstring;
    int line_fix, index_end;
    int m_start, m_end;
    struct STYLEDTEXT stext;
    int pos;
    while(1){
        pos = -1;
        for(item=regex_keys.begin();item!=regex_keys.end();item++){
            if((*item).startsWith("in_")) continue;
            key = *item;
            rx = regexs[*item];
            pos = rx.indexIn(text, offset, QRegExp::CaretAtOffset);
            if(pos>=0) break;
        }
        if(pos<0) break;
        mstring = rx.cap(0);
        if(debug<15) qDebug()<<line<<":"<<key<<":"<<rx.matchedLength()<<": "<<mstring;
        line_fix = mstring.count('\n');
        if(line_fix>0) {
            index_end = 0;
        } else {
            index_end = index + mstring.length();
        }
        m_start = editor()->positionFromLineIndex(line, index);
        m_end = editor()->positionFromLineIndex(line + line_fix, index_end);
        stext.length = m_end - m_start;
        stext.style = descs[key];
        tstyles[m_start] = stext;
        line += line_fix;
        index = index_end;
        offset += rx.matchedLength();
    }
    *end = qMax(*end, m_end);
    return tstyles;
}

void QsciLexerRest::styleText(int start, int end)
{
    if(debug<15) qDebug()<<__FUNCTION__<<" start: "<<start<<" end: "<<end;
    if(!editor())
        return;
    QMap <int, struct STYLEDTEXT> tstyles;
    tstyles = parseText(&start, &end);
    QList<int> nkeys = tstyles.keys();
    qSort(nkeys.begin(), nkeys.end(), qGreater<int>());
    QList<int>::iterator nitem;
    for(nitem=nkeys.begin();nitem!=nkeys.end();nitem++){
        startStyling(*nitem);
        setStyling(tstyles[*nitem].length, tstyles[*nitem].style);
    }
    styled_text.unite(tstyles);
    int bs_line, be_line, index;
    editor()->lineIndexFromPosition(start, &bs_line, &index);
    editor()->lineIndexFromPosition(end, &be_line, &index);
    int line, offset, cap_idx = 1;
    int m_start, m_end;
    QString line_text;
    QList<QString>::iterator item;
    QRegExp rx;
    for(line=bs_line;line<(be_line+1);line++){
        line_text = editor()->text(line);
        for(item=regex_keys.begin();item!=regex_keys.end();item++){
            if(!(*item).startsWith("in_")) continue;
            rx = inline_regexs[*item];
            offset = 0;
            while(rx.indexIn(line_text, offset) != -1){
                m_start = editor()->positionFromLineIndex(line, rx.pos(cap_idx));
                m_end = editor()->positionFromLineIndex(line, rx.pos(cap_idx) + rx.cap(cap_idx).length());
                startStyling(m_start);
                setStyling(m_end - m_start, descs[*item]);
                if(debug<15) qDebug()<<line<<":"<<*item<<":"<<rx.matchedLength()<<": "<<rx.cap(cap_idx);
                offset = rx.pos(0) + rx.matchedLength();
            }
        }
    }
    startStyling(end);
    return;
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

void QsciLexerRest::setDebugLevel(int level)
{
    debug = level;
}

void QsciLexerRest::readConfig(QString & prop_file)
{
    QSettings prop_settings(prop_file, QSettings::IniFormat);
    QMap<int, QString>::iterator item;
    QStringList::iterator sitem;
    QStringList prop_list;
    QString prop_key;
    QFont ffont;
    QRegExp rx("\\$\\(font\\.(\\w+)\\)");
    for(item=properties.begin();item!=properties.end();item++){
        prop_key.sprintf("style.%s.%d", language(), item.key());
        prop_list = prop_settings.value(prop_key).toStringList();
        for(sitem=prop_list.begin();sitem!=prop_list.end();sitem++){
            if((*sitem).startsWith("face:")){
                setColor(QColor((*sitem).split(":")[1]), item.key());
            } else if((*sitem).startsWith("back:")){
                setPaper(QColor((*sitem).split(":")[1]), item.key());
            } else if((*sitem).contains(rx)){
                setFont(QFont(rx.cap(1)), item.key()); 
            } else if((*sitem) == "bold"){
                ffont = font(item.key());
                ffont.setBold(1);
                setFont(ffont, item.key());
            } else if((*sitem) == "italic"){
                ffont = font(item.key());
                ffont.setItalic(1);
                setFont(ffont, item.key());
            } else if((*sitem) == "underline"){
                ffont = font(item.key());
                ffont.setUnderline(1);
                setFont(ffont, item.key());
            }
        }
    }
}
