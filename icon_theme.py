#!/usr/bin/python3

import os
import re
import argparse
import os.path
import configparser
import xml.etree.ElementTree as etree

standard_icons_dir = [
    '/usr/share/icons',
    '/usr/local/share/icons',
    '%s/.icons' % os.path.expanduser('~'),
    '%s/.local/share/icons' % os.path.expanduser('~'),
]


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


def create_qrc(themes, cur_theme, qrc_file, added_icons=None):
    if cur_theme not in themes:
        print('Do not find theme: %s', cur_theme)
        return
    tree = etree.Element('RCC', version='1.0')
    element_qresource = etree.SubElement(tree, 'qresource', prefix='icons/embed_qrc')
    element = etree.SubElement(element_qresource, 'file', alias='index.theme')
    element.text = 'index.theme'

    theme_inherits = [cur_theme]
    theme_icon_directories = set()

    theme_cfg = configparser.ConfigParser()
    theme_cfg.optionxform = str
    theme_cfg.add_section('Icon Theme')

    index = 0
    while index < len(theme_inherits):
        theme_name = theme_inherits[index]
        print('add searching directory: %s' % themes[theme_name])

        index_theme = os.path.join(themes[theme_name], 'index.theme')
        cfg = configparser.ConfigParser()
        cfg.optionxform = str
        cfg.read(index_theme)
        if index == 0:
            # theme_cfg.set('Icon Theme', 'Name', 'embed_qrc')
            # theme_cfg.set('Icon Theme', 'Comment', 'embed qt resource')
            name = cfg.get('Icon Theme', 'Name', fallback='')
            comment = cfg.get('Icon Theme', 'Comment', fallback='')
            theme_cfg.set('Icon Theme', 'Name', name)
            theme_cfg.set('Icon Theme', 'Comment', comment)

        icon_directories = set(cfg.get('Icon Theme', 'Directories').strip(',').split(','))
        theme_icon_directories |= icon_directories

        # add all sections except "Icon Theme"
        items_dict = dict(cfg.items())
        del items_dict['Icon Theme']
        theme_cfg.read_dict(items_dict)

        inherits = cfg.get('Icon Theme', 'Inherits', fallback=None)
        if inherits:
            for inherit in inherits.strip(',').split(','):
                if inherit not in theme_inherits:
                    theme_inherits.append(inherit)
        index += 1

    if added_icons:
        require_icons = set(added_icons)
    else:
        require_icons = None
    for theme_name in theme_inherits:
        if not require_icons:
            break
        theme_dir = themes[theme_name]
        print('search directory "%s" ...' % theme_dir)
        current_icons = set()
        for root_dir, dirs, files in os.walk(theme_dir):
            root_alias = root_dir[len(theme_dir) + 1:]
            for f in files:
                icon_name, ext = os.path.splitext(f)
                if ext in ['.png', '.svg']:
                    if icon_name not in require_icons:
                        continue
                    print('add icon:', icon_name, ext, root_alias)
                    current_icons.add(icon_name)
                    element = etree.SubElement(
                        element_qresource, 'file', alias=os.path.join(root_alias, f))
                    element.text = os.path.relpath(os.path.join(root_dir, f))
        require_icons -= current_icons
    print('missing icon:', require_icons)

    theme_cfg.set('Icon Theme', 'Directories', ','.join(theme_icon_directories))
    with open('index.theme', 'w') as f:
        theme_cfg.write(f)
    with open(qrc_file, 'w') as f:
        f.write('<!DOCTYPE RCC>\n')
        f.write(etree.tostring(tree, encoding='unicode'))


def main():
    parser = argparse.ArgumentParser(description='Qt Resource for Tango Theme')
    parser.add_argument('-L', '--list', action='store_true', help='Linux system icon Themes')
    qrc = parser.add_argument_group('create theme QT resource')
    qrc.add_argument('--theme', help='use icon theme')
    qrc.add_argument('--source', help='python source code directory.')
    qrc.add_argument('--qrc', help='output QT qrc file')

    args = parser.parse_args()

    # all themes
    # themes = {[theme name] = theme_dir, ...}
    themes = {}
    for prefix in standard_icons_dir:
        if not os.path.exists(prefix):
            continue
        for theme in os.listdir(prefix):
            themes[theme] = os.path.join(prefix, theme)

    if args.list:
        for t in sorted(list(themes.keys())):
            print('%s : %s' % (t, themes[t]))
    elif args.qrc and args.theme and args.source:
        icon_names = collect_iconames(args.source)
        create_qrc(themes, args.theme, args.qrc, icon_names)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
