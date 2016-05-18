
#include <QtCore>
#include <QtGui>
#include <QtAlgorithms>

#include <Qsci/qsciscintilla.h>
#include <Qsci/qscilexercustom.h>

#include "scilexerrest.h"

struct REGEX_PATTERN token_patterns[] = {
    // ^\.\. +[\-\w]+::.*\n
    {"directive",   "^\\.\\. +[\\-\\w]+::.*\\n"},
    // ^\.\. +[\-\w].*\n(\n* .*\n)*\n
    {"comment",     "^\\.\\. +[\\-\\w].*\\n(\\n* .*\\n)*\\n"},
    // ^([=`'"~^_*+#-]+)\n.+\n\1\n
    {"title",       "^([=`'\"~^_*+#-]+)\\n.+\\n\\1\\n"},
    // ^\w.*\n[=`'"~^_*+#-]+\n
    {"section",     "^\\w.*\\n[=`'\"~^_*+#-]+\\n"},
    // ^\n[=`'"~^_*+#-]{4,}\n\n
    {"transition",  "^\\n[=`'\"~^_*+#-]{4,}\\n\\n"},
    // ^( *)[\-+*] +.+\n(\n*\1[\-+*] +.+\n)*\n
    {"bullet",      "^( *)[\\-+*] +.+\\n(\\n*\\1[\\-+*] +.+\\n)*\\n"},
    // ^( *)[(]?[0-9a-zA-Z#]+[.)] +.+\n(\1[(]?[0-9a-zA-Z#]+[.)] +.+\n)*\n
    {"enumerated",  "^( *)[(]?[0-9a-zA-Z#]+[.)] +.+\\n(\\1[(]?[0-9a-zA-Z#]+[.)] +.+\\n)*\\n"},
    // ^\w.*\n( +).+\n(\n*\1.+\n)*(\w.*\n( +).+\n(\n*\1.+\n)*)*\n
    {"definition",  "^\\w.*\\n( +).+\\n(\\n*\\1.+\\n)*(\\w.*\\n( +).+\\n(\\n*\\1.+\\n)*)*\\n"},
    // ^:[ \w\-]+:.*\n(\n* .+\n)*(:[ \w\-]+:.*\n(\n* .+\n)*)*\n
    {"field",       "^:[ \\w\\-]+:.*\\n(\\n* .+\\n)*(:[ \\w\\-]+:.*\\n(\\n* .+\\n)*)*\\n"},
    // ^[\-/]+\w.+\n(\n* +.*\n)*([\-/]+\w.+\n(\n* +.*\n)*)*\n
    {"option",      "^[\\-/]+\\w.+\\n(\\n* +.*\\n)*([\\-/]+\\w.+\\n(\\n* +.*\\n)*)*\\n"},
    // ::\n\n( +).+\n(\n*\1.+\n)*\n
    {"literal1",    "::\\n\\n( +).+\\n(\\n*\\1.+\\n)*\\n"},
    // ^>.*\n(>.*\n)*\n
    {"literal2",    "^>.*\\n(>.*\\n)*\\n"},
    // ^.. code::.*\n\n( +).+\n(\1.+\n)*\n
    {"literal3",    "^.. code::.*\\n\\n( +).+\\n(\\1.+\\n)*\\n"},
    // ^( {2,})\w.+\n(\n*\1.+\n)*\n
    {"quote",       "^( {2,})\\w.+\\n(\\n*\\1.+\\n)*\\n"},
    // ^ *\|( +.+)?\n( {2,}.*\n)*( *\|( +.+)?\n( {2,}.*\n)*)*\n
    {"line",        "^ *\\|( +.+)?\\n( {2,}.*\\n)*( *\\|( +.+)?\\n( {2,}.*\\n)*)*\\n"},
    // ^>>> .+\n
    {"doctest",     "^>>> .+\\n"},
    // ^( *)[\-=+]{2,}\n(\1[\|+].+\n)+\n
    {"table1",      "^( *)[\\-=+]{2,}\\n(\\1[\\|+].+\\n)+\\n"},
    // ^( *)[\-=]{2,} [\-= ]+\n(\1.+\n)+\n
    {"table2",      "^( *)[\\-=]{2,} [\\-= ]+\\n(\\1.+\\n)+\\n"},
    // ^\.\. \[[^\]]+\] .+\n(\n* {3,}.+\n)*\n
    {"footnote",    "^\\.\\. \\[[^\\]]+\\] .+\\n(\\n* {3,}.+\\n)*\\n"},
    // ^\.\. _[^:]+:( .+)*\n
    {"target1",     "^\\.\\. _[^:]+:( .+)*\\n"},
    // ^__ .+\n
    {"target2",     "^__ .+\\n"},
    // ^ only match from line beginning
    // \n+
    {"newline",     "\\n+"},
    {"colon",      ":+"},
    {"string",      "[^:\\n]+"},
    // (\*\w[^*\n]*\*)
    {"in_emphasis",     "(\\*\\w[^*\\n]*\\*)"},
    {"in_strong",       "(\\*\\*\\w[^*\\n]*\\*\\*)"},
    {"in_literal",      "(``\\w[^`\\n]*``)"},
    // \W((http|https|ftp)://[\w\-\.:/]+)\W
    {"in_url1",         "\\W((http|https|ftp)://[\\w\\-\\.:/]+)\\W"},
    {"in_url2",         "(`[^<\\n]+<[^>\\n]+>`_)"},
    {"in_link1",        "\\W(\\w+_)\\W"},
    {"in_link2",        "(`\\w[^`\\n]*`_)"},
    {"in_footnote",     "(\\[[\\w*#]+\\]_)"},
    {"in_substitution", "(\\|\\w[^\\|]*\\|)"},
    {"in_target",       "(_`\\w[^`\\n]*`)"},
    {"in_reference",    "(:\\w+:`\\w+`)"},
    {"in_directive",    ""},    // delay added
    {"in_field",        "^:([^:]+):[ \\n]"},
    {"in_unusedspace",  "( +)\\n"},
    {"", ""},
};

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
    styles.insert("newline", 0);
    styles.insert("comment", 1);
    styles.insert("title", 2);
    styles.insert("section", 2);
    styles.insert("transition", 3);
    styles.insert("bullet", 4);
    styles.insert("enumerated", 4);
    styles.insert("definition", 5);
    styles.insert("field", 0);
    styles.insert("in_field", 6);
    styles.insert("option", 7);
    styles.insert("literal1", 8);
    styles.insert("literal2", 8);
    styles.insert("literal3", 8);
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
    setDefaultColor(QColor("#000000"));
    setDefaultPaper(QColor("#ffffff"));
    setDefaultFont(QFont("Monospace", 12));
    debug = 30;
    QString name, pattern;
    struct REGEX_TOKEN token;
    for (int i = 0; ; i++) {
        if (token_patterns[i].name == "") {
            break;
        }
        token.name = token_patterns[i].name;
        pattern  = token_patterns[i].pattern;
        if (token.name.startsWith("in_")) {
            if (token.name == "in_directive") {
                pattern = "^\\.\\. +(" + keyword_list.join("|") + ")::";
            }
            token.regex = QRegularExpression(
                    pattern,
                    QRegularExpression::UseUnicodePropertiesOption |
                    QRegularExpression::CaseInsensitiveOption
                    );
            inline_tokens.append(token);
        } else {
            token.regex = QRegularExpression(pattern,
                    QRegularExpression::UseUnicodePropertiesOption |
                    QRegularExpression::CaseInsensitiveOption |
                    QRegularExpression::MultilineOption
                    );
            block_tokens.append(token);
        }
    }
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

void QsciLexerRest::clear()
{
    styled_text.clear();
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
            y = qMin(y + 3, styled_keys.size() - 1);
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
    // captured text index: 0
    const int cap_idx = 0;
    int m_start = start;
    int offset = 0;
    int m_end;
    QRegularExpressionMatch mo;
    struct TEXTSTYLE text_style;
    struct REGEX_TOKEN token;
    int line_fix, end_line, end_index;
    startStyling(start);
    while (offset < text.size()) {
        foreach(token, block_tokens) {
            mo = token.regex.match(text, offset,
                    QRegularExpression::NormalMatch,
                    QRegularExpression::AnchoredMatchOption);
            if (mo.hasMatch()) {
                break;
            }
        }
        if (! mo.hasMatch()) {
            if (debug < 15) qDebug()<<"Could not match:"<<text.mid(offset);
            break;
        }
        if (debug < 15)
            qDebug() << "[DEBUG]" << token.name
                << "(" << line + 1 << "," << index << ")"
                << ":" << mo.captured(cap_idx);
        line_fix = mo.captured(cap_idx).count('\n');
        end_line = line + line_fix;
        if (line_fix > 0) {
            end_index = 0;
        } else {
            end_index = index + mo.captured(cap_idx).length();
        }
        m_end = editor()->positionFromLineIndex(end_line, end_index);
        if ((m_end - m_start) > 0) {
            setStyling(m_end - m_start, styles[token.name]);
            text_style.length = m_end - m_start;
            text_style.style = token.name;
            styled_text.insert(m_start, text_style);
        } else {
            qDebug()<<"*** !! length < 0 !! ***";
        }
        m_start = m_end;
        line = end_line;
        index = end_index;
        offset = mo.capturedEnd(cap_idx);
    }
    return;
}

void QsciLexerRest::do_InlineStylingText(int start, int end)
{
    // captured text index: 1
    const int cap_idx = 1;
    int bs_line, be_line, index;
    editor()->lineIndexFromPosition(start, &bs_line, &index);
    editor()->lineIndexFromPosition(end, &be_line, &index);
    QRegularExpressionMatch mo;
    QRegularExpressionMatchIterator mi;
    QString line_text;
    int m_start, m_end;
    struct REGEX_TOKEN token;
    for (int line = bs_line; line < be_line; line++) {
        line_text = editor()->text(line);
        foreach (token, inline_tokens) {
            mi = token.regex.globalMatch(line_text);
            while (mi.hasNext()) {
                mo = mi.next();
                m_start = editor()->positionFromLineIndex(line, mo.capturedStart(cap_idx));
                m_end = editor()->positionFromLineIndex(line, mo.capturedEnd(cap_idx));
                startStyling(m_start);
                setStyling(m_end - m_start, styles[token.name]);
                if (debug < 15)
                    qDebug() << "[DEBUG]" << token.name
                        << "(" << line + 1 << "," << mo.capturedStart(cap_idx) << ")"
                        << ":" << mo.captured(cap_idx);
            }
        }
    }
}

void QsciLexerRest::styleText(int start, int end)
{

    if (!editor())
        return;
    if (debug < 15)
        qDebug() << "==================== style begin ====================";
    int s_start = start;
    int s_end = end;
    getStylingPosition(&s_start, &s_end);
    if (debug < 15)
        qDebug() << "** Fix styled range from (" << start << "," << end << ") to ("
            << s_start << "," << s_end << ") **";
    do_StylingText(s_start, s_end);
    do_InlineStylingText(s_start, s_end);
    startStyling(editor()->length());
    if (debug < 15)
        qDebug() << "==================== style end ====================";
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
