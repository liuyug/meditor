#!/bin/sh

rsteditor_version_file='rsteditor/__init__.py'
nsis_file='win32/inst_script.nsi'
desktop_file='rsteditor/share/applications/rsteditor.desktop'

usage()
{
    echo "autoversion.sh [new_version]"
    echo ""
    echo "Current version:" $version
}

check_version()
{
    version=`cat $rsteditor_version_file | grep 'app_version' | cut -d\' -f 2`
}

update_rsteditor_version()
{
    sed  -i -r "s/^(__app_version__).*$/\1 = '$new_version'/" $rsteditor_version_file
}

update_nsis_version()
{
    sed  -i -r "s/^(!define PRODUCT_VER).*$/\1 \"$new_version\"/" $nsis_file
}

update_desktop_version()
{
    sed  -i -r "s/^(Version).*$/\1=$new_version/" $desktop_file
}

update_git_tag()
{
    git tag $new_version
}

update_version()
{
    update_rsteditor_version
    update_nsis_version
    update_desktop_version
    # update_git_tag
}

check_version

if [ "x$1" = "x" ]; then
    usage
    exit 0
fi

new_version=$1

echo "Old version:" $version
echo "New version:" $new_version

update_version

# vim: tabstop=4 shiftwidth=4 expandtab
