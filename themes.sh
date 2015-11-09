#!/bin/sh

mkdir -p themes

cd themes

# timhughes/restructuredtext-theme
if [ -d restructuredtext-theme ]; then
    (cd restructuredtext-theme; git pull)
else
    git clone http://bitbucket.org/timhughes/restructuredtext-theme
fi

(
cd restructuredtext-theme
cat > theme.json <<EOF
{
    "stylesheet_path":"reset.css,goldfish.css,goldfish-pygments-long.css,goldfish-pygments-long-python.css",
    "syntax-highlight": "long"
}
EOF
)

# Rykka/rhythm.css
if [ -d rhythm.css ]; then
    (cd rhythm.css; git pull)
else
    git clone https://github.com/Rykka/rhythm.css
fi

(
cd rhythm.css
cat > theme.json <<EOF
{
    "stylesheet_path":"dist/css/rhythm.css,syntax/molokai.css",
    "syntax-highlight": "short"
}
EOF
)


# vim: tabstop=4 shiftwidth=4 expandtab
