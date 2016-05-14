
#include <QtCore>
#include <QtGui>
#include <QtAlgorithms>

#include <Qsci/qsciscintilla.h>
#include <Qsci/qscilexercustom.h>

#include "scilexerrest.h"

QsciLexerRest::QsciLexerRest(QObject * parent): QsciLexerCustom(parent)
{
    keyword_list.append("attention");
    keyword_list.append("caution");
    keyword_list.append("danger");
    keyword_list.append("error");
    keyword_list.append("hint");
    keyword_list.append("important");
    keyword_list.append("note");
    keyword_list.append("tip");
    keyword_list.append("warning");
    keyword_list.append("admonition");
    keyword_list.append("image");
    keyword_list.append("figure");
    keyword_list.append("topic");
    keyword_list.append("sidebar");
    keyword_list.append("code");
    keyword_list.append("math");
    keyword_list.append("rubric");
    keyword_list.append("epigraph");
    keyword_list.append("highlights");
    keyword_list.append("compound");
    keyword_list.append("container");
    keyword_list.append("table");
    keyword_list.append("csv-table");
    keyword_list.append("list-table");
    keyword_list.append("contents");
    keyword_list.append("sectnum");
    keyword_list.append("section-autonumbering");
    keyword_list.append("section-numbering");
    keyword_list.append("header");
    keyword_list.append("footer");
    keyword_list.append("target-notes");
    keyword_list.append("meta");
    keyword_list.append("include");
    keyword_list.append("raw");
    keyword_list.append("class");
    keyword_list.append("role");
    keyword_list.append("default-role");
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
    properties.insert(25, "back:#ef2929");
    styles.insert("string", 0);
    styles.insert("colon", 0);
    styles.insert("space", 0);
    styles.insert("newline", 0);
    styles.insert("comment", 1);
    styles.insert("title", 2);
    styles.insert("section", 2);
    styles.insert("transition", 3);
    styles.insert("bullet", 4);
    styles.insert("enumerated", 4);
    styles.insert("definition1", 5);
    styles.insert("definition2", 5);
    styles.insert("field", 0);
    styles.insert("in_field", 6);
    styles.insert("option", 7);
    styles.insert("literal1", 8);
    styles.insert("literal2", 8);
    styles.insert("line", 9);
    styles.insert("quote", 10);
    styles.insert("doctest", 11);
    styles.insert("table1", 12);
    styles.insert("table2", 12);
    styles.insert("footnote", 13);
    styles.insert("target1", 14);
    styles.insert("target2", 14);
    styles.insert("directive", 0);
    styles.insert("in_directive", 15);
    styles.insert("in_emphasis", 16);
    styles.insert("in_strong", 17);
    styles.insert("in_literal", 18);
    styles.insert("in_url1", 19);
    styles.insert("in_url2", 19);
    styles.insert("in_link1", 20);
    styles.insert("in_link2", 20);
    styles.insert("in_footnote", 21);
    styles.insert("in_substitution", 22);
    styles.insert("in_target", 23);
    styles.insert("in_reference", 24);
    styles.insert("in_unusedspace", 25);
    block_tokens.insert("comment",     QRegExp("^\\.\\. (?!_|\\[)(?![^\\n]+::)[^\\n]+(?:\\n{0,2} {3,}[^\\n]+)*\\n"));
    block_tokens.insert("title",       QRegExp("^([=`'\"~^_*+#-]{2,})\\n[^\\n]+\\n\\1\\n"));
    block_tokens.insert("section",     QRegExp("^[^\\n]+\\n[=`'\"~^_*+#-]{2,}\\n"));
    block_tokens.insert("transition",  QRegExp("^\\n[=`'\"~^_*+#-]{4,}\\n\\n"));
    block_tokens.insert("bullet",      QRegExp("^ *[\\-+*] +[^\\n]+(?:\\n+ +[^\\n]+)*\\n"));
    block_tokens.insert("enumerated",  QRegExp("^ *\\(?[0-9a-zA-Z#](?:\\.|\\)) +[^\\n]+(?:\\n+ +[^\\n]+)*\\n"));
    block_tokens.insert("definition1", QRegExp("^\\w+\\n( +)[^\\n]+(?:\\n+\\1[^\\n]+)*\\n"));
    block_tokens.insert("definition2", QRegExp("^\\w+ *:[^\\n]*\\n( +)[^\\n]+(?:\\n+\\1[^\\n]+)*\\n"));
    block_tokens.insert("field",       QRegExp("^:[^:\\n]+:[ \\n]+[^\\n]+(?:\\n+ +[^\\n]+)*\\n"));
    block_tokens.insert("option",      QRegExp("^(?:-{1,2}|/)\\w[^\\n]+(?:\\n+ +[^\\n]+)*\\n"));
    block_tokens.insert("literal1",    QRegExp("^::\\n\\n( +|>)[^\\n]+(?:\\n+\\1[^\\n]*)*\\n"));
    block_tokens.insert("literal2",    QRegExp("^\\.\\. code::(?:[^\\n]*)\\n\\n([ >]+)[^\\n]+(?:\\n+\\1[^\\n]*)*\\n"));
    block_tokens.insert("line",        QRegExp("^ *\\|(?: +[^\\n]+)?(?:\\n +[^\\n]+)*\\n"));
    block_tokens.insert("quote",       QRegExp("^\\n( {2,})[^\\n]+(?:\\n\\1[^\\n]+)*\\n"));
    block_tokens.insert("doctest",     QRegExp("^>>>[^\\n]+\\n"));
    block_tokens.insert("table1",      QRegExp("^( *)[\\-=+]{2,}(\\n\\1[\\|+][^\\n]+)+\\n"));
    block_tokens.insert("table2",      QRegExp("^( *)[\\-=]{2,} [\\-= ]+(\\n\\1[^\\n]+)+\\n"));
    block_tokens.insert("footnote",    QRegExp("^\\.\\. \\[[^\\n\\]]+\\][ \\n]+[^\\n]+(\\n+ +[^\\n]+)*\\n"));
    block_tokens.insert("target1",     QRegExp("^\\.\\. _[^\\n]+:(\\n +)*[^\\n]*\\n"));
    block_tokens.insert("target2",     QRegExp("^__(?: [^\\n]+)*\\n"));
    block_tokens.insert("directive",   QRegExp("^\\.\\. (?!_|\\[)[^\\n]+::[^\\n]*(\\n+ +[^\\n]+)*\\n"));
    block_tokens.insert("newline",     QRegExp("^\\n"));
    block_tokens.insert("space",       QRegExp("^ +"));
    block_tokens.insert("string",      QRegExp("^[^: \\n]+"));
    block_tokens.insert("colon",       QRegExp("^:"));
    inline_tokens.insert("in_emphasis",     QRegExp("(\\*[^\\n\\*]+\\*)(?!\\*)"));
    inline_tokens.insert("in_strong",       QRegExp("(\\*\\*[^\\n\\*]+\\*\\*)"));
    inline_tokens.insert("in_literal",      QRegExp("(``[^`]+``)"));
    inline_tokens.insert("in_url1",         QRegExp("(\\w+://[\\w\\-\\.:/]+)"));
    inline_tokens.insert("in_url2",         QRegExp("(`[^<]+<[^>]+>`_+)"));
    inline_tokens.insert("in_link1",        QRegExp("([\\w\\-]+_)(?!\\w)"));
    inline_tokens.insert("in_link2",        QRegExp("(`\\w[^\\n]*\\w`_+)(?!\\w)"));
    inline_tokens.insert("in_footnote",     QRegExp("(\\[[\\w\\*#]+\\]_)(?!\\w)"));
    inline_tokens.insert("in_substitution", QRegExp("(\\|\\w[^\\n]+\\w\\|)"));
    inline_tokens.insert("in_target",       QRegExp("(_`[^`]+`)"));
    inline_tokens.insert("in_reference",    QRegExp("(:\\w+:`[^`]+`)"));
    inline_tokens.insert("in_directive",    QRegExp("^(\\.\\. (?:" + keyword_list.join("|") + ")::)"));
    inline_tokens.insert("in_field",        QRegExp("^:([^:]+):(?!`)"));
    inline_tokens.insert("in_unusedspace",  QRegExp("( +)\\n"));
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
    return styles.key(style, QString());
}

QString QsciLexerRest::getTextRange(int start, int end)
{
    QString text;
    if (!editor())
        return text;
    int bs_line, be_line, index;
    editor()->lineIndexFromPosition(start, &bs_line, &index);
    editor()->lineIndexFromPosition(end, &be_line, &index);
    for (int line=bs_line; line < (be_line + 1) ; line++){
        text += editor()->text(line);
    }
    return text;
}

void QsciLexerRest::getStylingPosition(int * start, int * end)
{
    QList<int> styled_keys;
    styled_keys = styled_text.keys();
    if (styled_keys.isEmpty())
        return;
    int new_start = 0;
    int new_end = editor()->length();
    int x, y, pos;
    QString key;
    for (x = 0; x < styled_keys.size(); x++) {
        pos = styled_keys[x];
        if (*start < pos) {
            x = qMax(x - 2, 0);
            while (x >= 0) {
                new_start = styled_keys[x];
                key = styled_text[new_start].style;
                if (styles[key] != styles["string"])
                    break;
                x --;
            }
            break;
        }
    }
    for (y = 0; y < styled_keys.size(); y++) {
        pos = styled_keys[y];
        if (*end < pos) {
            y = qMin(y + 1, styled_keys.size() - 1);
            while (y < styled_keys.size()) {
                new_end = styled_keys[y];
                key = styled_text[new_end].style;
                if (styles[key] != styles["string"])
                    break;
                y ++;
            }
            break;
        }
    }
    for (int k = x; k < y; k++) {
        styled_text.remove(k);
    }
    *start = new_start;
    *end = new_end;
    return;
}

void QsciLexerRest::do_StylingText(int start, int end)
{
    QString text = getTextRange(start, end);
    if (debug < 15) qDebug()<<"styling text:"<<text;

    int line, index;
    editor()->lineIndexFromPosition(start, &line, &index);

    int m_start = start;
    int offset = 0;
    int m_end;
    QRegExp rx;
    int pos;
    struct TEXTSTYLE text_style;
    QString key, mstring;
    int line_fix, end_line, end_index;

    startStyling(start);
    while (offset < text.size()) {
        foreach(key, block_tokens.keys()) {
            rx = block_tokens[key];
            pos = rx.indexIn(text, offset, QRegExp::CaretAtOffset);
            if (pos > -1)
                break;
        }
        if (pos < 0) {
            if (debug < 15) qDebug()<<"Could not match:"<<text.mid(offset);
            break;
        }
        mstring = rx.cap(0);
        if (debug < 15)
            qDebug()<<"[DEBUG] "<<line<<":"<<key<<":"<<rx.matchedLength()<<": "<<mstring;
        line_fix = mstring.count('\n');
        end_line = line + line_fix;
        if (line_fix > 0) {
            end_index = 0;
        } else {
            end_index = index + mstring.length();
        }
        m_end = editor()->positionFromLineIndex(end_line, end_index);
        if ((m_end - m_start) > 0) {
            setStyling(m_end - m_start, styles[key]);
            text_style.length = m_end - m_start;
            text_style.style = key;
            styled_text.insert(m_start, text_style);
        } else {
            qDebug()<<"*** !! length < 0 !! ***";
        }
        m_start = m_end;
        line = end_line;
        index = end_index;
        offset += rx.matchedLength();
    }
    return;
}

void QsciLexerRest::do_InlineStylingText(int start, int end)
{
    int bs_line, be_line, index;
    editor()->lineIndexFromPosition(start, &bs_line, &index);
    editor()->lineIndexFromPosition(end, &be_line, &index);
    QRegExp rx;
    QString line_text;
    int offset;
    int m_start, m_end;
    for (int line = bs_line; line < be_line; line++) {
        line_text = editor()->text(line);
        foreach(QString key, inline_tokens.keys()) {
            rx = inline_tokens[key];
            offset = 0;
            while(rx.indexIn(line_text, offset) != -1){
                m_start = editor()->positionFromLineIndex(line, rx.pos(1));
                m_end = editor()->positionFromLineIndex(line, rx.pos(1) + rx.cap(1).length());
                startStyling(m_start);
                setStyling(m_end - m_start, styles[key]);
                if(debug<15) qDebug()<<"[DEBUG] "<<line<<":"<<key<<":"<<rx.matchedLength()<<": "<<rx.cap(1);
                offset = rx.pos(0) + rx.matchedLength();
            }
        }
    }
}

void QsciLexerRest::styleText(int start, int end)
{

    if (!editor())
        return;
    if(debug<15) qDebug()<<"=====";
    int s_start = start;
    int s_end = end;
    getStylingPosition(&s_start, &s_end);
    do_StylingText(s_start, s_end);
    do_InlineStylingText(s_start, s_end);
    startStyling(editor()->length());
    return;
}

int QsciLexerRest::defaultStyle() const
{
    return styles["string"];
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
            font.setBold(true);
        } else if(*item == "italic"){
            font.setItalic(true);
        } else if(*item == "underline"){
            font.setUnderline(true);
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
