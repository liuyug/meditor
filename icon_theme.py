#!/usr/bin/python3

import os
import re
import argparse
import os.path
import configparser
import xml.etree.ElementTree as etree


def collect_iconames(source_dir):
    icon_names = []
    regex_iconame = re.compile(r'QIcon\.fromTheme\((\'|\")([\w\-]+)\1')
    for root_dir, dirs, files in os.walk(source_dir):
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext != '.py':
                continue
            with open(os.path.join(root_dir, filename)) as f:
                for mo in regex_iconame.finditer(f.read()):
                    icon_names.append(mo.group(2))
    return icon_names


def create_qrc(theme_dir, qrc_file, added_icons=None):
    tree = etree.Element('RCC', version='1.0')
    element_qresource = etree.SubElement(tree, 'qresource', prefix='icons/embed_qrc')

    theme_dirs = []

    index_theme = os.path.join(theme_dir, 'index.theme')
    theme_cfg = configparser.ConfigParser()
    theme_cfg.read(index_theme)
    theme_name = theme_cfg.get('Icon Theme', 'Name', fallback='')
    theme_comment = theme_cfg.get('Icon Theme', 'Comment', fallback='')
    theme_inherits = theme_cfg.get('Icon Theme', 'Inherits', fallback=None)
    if theme_inherits:
        print('%s [%s]: %s' % (theme_name, theme_inherits, theme_comment))
    else:
        print('%s: %s' % (theme_name, theme_comment))

    theme_dirs.append(theme_dir)
    print('add searching directory: %s' % theme_dir)

    element = etree.SubElement(element_qresource, 'file', alias='index.theme')
    element.text = os.path.relpath(index_theme)

    while theme_inherits:
        inherit_themes = theme_inherits.split(',')
        theme_inherits = None
        for inherit_theme in inherit_themes:
            inherit_dir = os.path.abspath(os.path.join(theme_dir, '..', inherit_theme))
            if not os.path.exists(inherit_dir):
                print('skip directory: %s' % inherit_dir)
                continue
            print('add searching directory: %s' % inherit_dir)
            theme_dirs.append(inherit_dir)

            index_theme = os.path.join(inherit_dir, 'index.theme')
            cfg = configparser.ConfigParser()
            cfg.read(index_theme)
            theme_inherits = cfg.get('Icon Theme', 'Inherits', fallback=None)


    for theme_dir in theme_dirs:
        print('search directory "%s" ...' % theme_dir)
        for root_dir, dirs, files in os.walk(theme_dir):
            root_alias = root_dir[len(theme_dir) + 1:]
            for f in files:
                icon_name, ext = os.path.splitext(f)
                if ext in ['.png', '.svg']:
                    if added_icons and icon_name not in added_icons:
                        continue
                    print('add icon:', icon_name, ext)
                    element = etree.SubElement(
                        element_qresource, 'file', alias=os.path.join(root_alias, f))
                    element.text = os.path.relpath(os.path.join(root_dir, f))

    with open(qrc_file, 'w') as f:
        f.write('<!DOCTYPE RCC>\n')
        f.write(etree.tostring(tree, encoding='unicode'))


def main():
    parser = argparse.ArgumentParser(description='Qt Resource for Tango Theme')
    parser.add_argument(
        '--list', action='store_true', help='Linux system icon Themes')
    qrc = parser.add_argument_group('create theme QT resource')
    qrc.add_argument('--theme', help='use icon theme')
    qrc.add_argument('--collect', help='collect all icon names from source code')
    qrc.add_argument('--qrc', help='output QT qrc file')

    args = parser.parse_args()
    themes = {}
    for prefix in ['/usr/share/icons', '/usr/local/share/icons']:
        if not os.path.exists(prefix):
            continue
        for theme_dir in os.listdir(prefix):
            themes[theme_dir] = os.path.join(prefix, theme_dir)
    if args.list:
        print(list(themes.keys()))
    elif args.qrc:
        icon_names = collect_iconames(args.collect)
        create_qrc(themes[args.theme], args.qrc, icon_names)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
