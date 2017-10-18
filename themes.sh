#!/bin/sh

set -e
set -x

share_theme="`pwd`/meditor/share/meditor/themes"

mkdir -p themes/reStructedText
mkdir -p themes/Markdown

rst_share_theme="$share_theme/reStructedText"
md_share_theme="$share_theme/Markdown"
mkdir -p $rst_share_theme
mkdir -p $md_share_theme

# reStructedText Themes
(
cd themes/reStructedText

# Rykka/rhythm.css
mkdir -p $rst_share_theme/rhythm.css
if [ -d rhythm.css ]; then
    (cd rhythm.css; git pull)
else
    git clone https://github.com/Rykka/rhythm.css
fi
(
cd rhythm.css
git archive --format tar master | tar xv -C $rst_share_theme/rhythm.css
)

(
cd $rst_share_theme/rhythm.css
cat > theme.json <<EOF
{
    "rhythm.css": {
        "stylesheet_path":"dist/css/rhythm.css,math/math.css,syntax/molokai.css",
        "syntax-highlight": "short"
    }
}
EOF
)


# fladd/docutils-solarized
mkdir -p $rst_share_theme/docutils-solarized

if [ -d docutils-solarized ]; then
    (cd docutils-solarized ; git pull)
else
    git clone https://github.com/fladd/docutils-solarized
fi
(
cd docutils-solarized
git archive --format tar master | tar xv -C $rst_share_theme/docutils-solarized
(
cd $rst_share_theme/docutils-solarized
python docutils_solarized_invert.py docutils_solarized_light.css docutils_solarized_dark.css
cat > theme.json <<EOF
{
    "solarized-light": {
        "stylesheet_path":"docutils_solarized_light.css",
        "syntax-highlight": "short"
    },
    "solarized-dark": {
        "stylesheet_path":"docutils_solarized_dark.css",
        "syntax-highlight": "short"
    }
}
EOF
)
)

# reStructedText end
)


# Markdown Themes
(
cd themes/Markdown

# https://github.com/raycon/vscode-markdown-css
theme_name="vscode-markdown-css"
mkdir -p $md_share_theme/$theme_name
if [ -d $theme_name ]; then
    (cd $theme_name; git pull)
else
    git clone http://github.com/raycon/vscode-markdown-css $theme_name
fi
(
cd $theme_name
cp -f *.css $md_share_theme/$theme_name
)

# https://github.com/wecatch/markdown-css
theme_name="wecatch-markdown-css"
mkdir -p $md_share_theme/$theme_name
if [ -d $theme_name ]; then
    (cd $theme_name; git pull)
else
    git clone http://github.com/wecatch/markdown-css $theme_name
fi
(
cd $theme_name
cp -f themes/*.css $md_share_theme/$theme_name
)

# https://github.com/hzlzh/MarkDown-Theme
theme_name="hzlzh-markdown-theme"
mkdir -p $md_share_theme/$theme_name
if [ -d $theme_name ]; then
    (cd $theme_name; git pull)
else
    git clone http://github.com/hzlzh/MarkDown-Theme $theme_name
fi
(
cd $theme_name
cp -f CSS/*.css $md_share_theme/$theme_name
)



)



# vim: tabstop=4 shiftwidth=4 expandtab
