#!/bin/sh

set -e
set -x

share_theme=`pwd`/rsteditor/share/rsteditor/themes

mkdir -p themes
mkdir -p $share_theme

(
cd themes

# timhughes/restructuredtext-theme
mkdir -p $share_theme/restructuredtext-theme
if [ -d restructuredtext-theme ]; then
    (cd restructuredtext-theme; git pull)
else
    git clone http://bitbucket.org/timhughes/restructuredtext-theme
fi
(
cd restructuredtext-theme
git archive --format tar master | tar xv -C $share_theme/restructuredtext-theme
)

# Rykka/rhythm.css
mkdir -p $share_theme/rhythm.css
if [ -d rhythm.css ]; then
    (cd rhythm.css; git pull)
else
    git clone https://github.com/Rykka/rhythm.css
fi
(
cd rhythm.css
git archive --format tar master | tar xv -C $share_theme/rhythm.css
)

# fladd/docutils-solarized
mkdir -p $share_theme/docutils-solarized

if [ -d docutils-solarized ]; then
    (cd docutils-solarized ; git pull)
else
    git clone https://github.com/fladd/docutils-solarized
fi
(
cd docutils-solarized
git archive --format tar master | tar xv -C $share_theme/docutils-solarized
(
cd $share_theme/docutils-solarized
python docutils_solarized_invert.py docutils_solarized_light.css docutils_solarized_dark.css
)
)
)

(
cd $share_theme
(
cd restructuredtext-theme
cat > theme.json <<EOF
{
    "restructuredtext-theme": {
    "stylesheet_path": "goldfish-pygments-long-python.css, goldfish-pygments-long.css, goldfish-pygments.css, goldfish.css, html4css1.css, pygments-default.css, readme.rst, reset.css, transition-stars.css, voidspace.css",
        "syntax-highlight": "long"
    }
}
EOF
)

(
cd rhythm.css
cat > theme.json <<EOF
{
    "rhythm.css": {
        "stylesheet_path":"dist/css/rhythm.css,math/math.css,syntax/molokai.css",
        "syntax-highlight": "short"
    }
}
EOF
)

(
cd docutils-solarized
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

# vim: tabstop=4 shiftwidth=4 expandtab
