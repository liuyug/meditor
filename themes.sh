#!/bin/sh

set -e
set -x


echo "Get reStructuredText themes..."
share_theme="`pwd`/meditor/data/themes"

mkdir -p themes/reStructuredText
mkdir -p themes/Markdown

rst_share_theme="$share_theme/reStructuredText"
md_share_theme="$share_theme/Markdown"
mkdir -p $rst_share_theme
mkdir -p $md_share_theme

# reStructuredText Themes
(
cd themes/reStructuredText

# Rykka/rhythm.css
rm -rf $rst_share_theme/rhythm.css
mkdir -p $rst_share_theme/rhythm.css
if [ -d rhythm.css ]; then
    (cd rhythm.css; git pull)
else
    git clone https://github.com/Rykka/rhythm.css
fi
(
cd rhythm.css
cp -rf dist $rst_share_theme/rhythm.css
cp -rf math $rst_share_theme/rhythm.css
cp -rf syntax $rst_share_theme/rhythm.css
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
rm -rf $rst_share_theme/docutils-solarized
mkdir -p $rst_share_theme/docutils-solarized

if [ -d docutils-solarized ]; then
    (cd docutils-solarized ; git pull)
else
    git clone https://github.com/fladd/docutils-solarized
fi
(
cd docutils-solarized
python2=`which python2`
if [ "x$python2" != "x" ]; then
    $python2 docutils_solarized_invert.py docutils_solarized_light.css docutils_solarized_dark.css
fi
cp -f *.css $rst_share_theme/docutils-solarized
(
cd $rst_share_theme/docutils-solarized
if [ -e docutils_solarized_dark.css ]; then
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
else
cat > theme.json <<EOF
{
    "solarized-light": {
        "stylesheet_path":"docutils_solarized_light.css",
        "syntax-highlight": "short"
    }
}
EOF
fi
)
)

# reStructuredText end
)


echo "Get Markdown themes..."
# Markdown Themes
(
cd themes/Markdown

# https://github.com/raycon/vscode-markdown-css
theme_name="vscode-markdown-css"
rm -rf $md_share_theme/$theme_name
mkdir -p $md_share_theme/$theme_name
if [ -d $theme_name ]; then
    (cd $theme_name; git pull)
else
    git clone http://github.com/raycon/vscode-markdown-css $theme_name
fi
(
cd $theme_name
cp -f *.css $md_share_theme/$theme_name

(
cd $md_share_theme/$theme_name
sed -i -r 's/.vscode-dark //' markdown-dark-material.css
sed -i -r 's/.vscode-dark,//' markdown-dark-material.css
sed -i -r 's/.vscode-light //' markdown-light.css
sed -i -r 's/.vscode-light,//' markdown-light.css
)
)

# https://github.com/wecatch/markdown-css
theme_name="wecatch-markdown-css"
rm -rf $md_share_theme/$theme_name
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
rm -rf $md_share_theme/$theme_name
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
