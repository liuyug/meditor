import os.path
import logging
import json
from collections import OrderedDict

import markdown
import mdx_mathjax

try:
    from docutils.core import publish_string
    from docutils.core import publish_cmdline
    from docutils.core import publish_cmdline_to_binary
    from docutils.writers.odf_odt import Writer, Reader
    from docutils.writers import html5_polyglot
except:
    raise Exception('Please install docutils firstly')

from . import __data_path__, __home_data_path__, \
    __mathjax_full_path__, __mathjax_min_path__

logger = logging.getLogger(__name__)

default_overrides = {
    'input_encoding': 'utf-8',
    'output_encoding': 'utf-8',
}


def get_rst_themes():
    """
    result: { 'theme': theme_dict, ... }
    """
    themes_dirs = [
        os.path.join(__home_data_path__, 'themes', 'reSturctedText'),
        os.path.join(__data_path__, 'themes', 'reStructuredText'),
    ]
    themes = OrderedDict()
    for themes_dir in themes_dirs:
        if os.path.exists(themes_dir):
            for theme in os.listdir(themes_dir):
                theme_json = os.path.join(themes_dir, theme, 'theme.json')
                if os.path.exists(theme_json):
                    try:
                        styles = json.load(open(theme_json))
                        for name, style in styles.items():
                            style['stylesheet_dirs'] = [os.path.dirname(theme_json)]
                            themes[name] = style
                    except Exception as err:
                        logger.error(err)
                        continue
    return themes


def get_theme_settings(theme):
    """
    docutils writer will load css file.
    """
    stylesheet = {}
    search_paths = [
        '/usr/share/docutils/writers',
        os.path.abspath(os.path.dirname(os.path.dirname(html5_polyglot.__file__))),
        os.path.abspath(os.path.join(__data_path__, 'docutils', 'writers')),
    ]
    docutils_theme_path = ''
    for path in search_paths:
        if os.path.exists(os.path.join(path, 'html5_polyglot', 'template.txt')):
            docutils_theme_path = path
            break
    stylesheet['stylesheet_dirs'] = [
        os.path.join(docutils_theme_path, 'html4css1'),
        os.path.join(docutils_theme_path, 'html5_polyglot'),
    ]

    pygments_path = os.path.join(__home_data_path__, 'themes', 'reStructuredText', 'pygments.css')
    if os.path.exists(pygments_path):
        stylesheet['stylesheet_path'] = pygments_path
        stylesheet['syntax_highlight'] = 'short'
    # docutils default theme
    if theme == 'default':
        return stylesheet

    # third part theme
    themes = get_rst_themes()
    styles = themes.get(theme)

    # stylesheet_path : css file path
    # syntax_highlight: short
    # template: template file path
    stylesheet['stylesheet_dirs'].extend(styles['stylesheet_dirs'])
    if 'syntax_highlight' in styles:
        stylesheet['syntax_highlight'] = styles['syntax_highlight']
    if 'stylesheet_path' in styles:
        css_paths = styles['stylesheet_path'].split(',')
        if 'stylesheet_path' in stylesheet:
            css_paths += stylesheet['stylesheet_path'].split(',')
        stylesheet['stylesheet_path'] = ','.join(css_paths)
    if 'template' in styles:
        old_path = styles['template']
        new_path = os.path.abspath(
            os.path.join(__home_data_path__,
                         'themes', 'reStructuredText',
                         theme,
                         old_path))
        stylesheet['template'] = new_path
    return stylesheet


def rst2htmlcode(rst_text, theme='restructedtext', settings={}):
    output = None
    try:
        overrides = {}
        overrides.update(default_overrides)
        overrides.update(settings)
        overrides.update(get_theme_settings(theme))
        logger.debug(overrides)
        output = publish_string(
            rst_text,
            writer_name='html5',
            settings_overrides=overrides,
        )
    except Exception as err:
        logger.error(err)
        output = str(err)
    return output


def rst2html(rst_file, filename, theme='restructedtext', settings={}):
    output = None
    try:
        overrides = {}
        overrides.update(default_overrides)
        overrides.update(settings)
        overrides.update(get_theme_settings(theme))
        logger.debug(overrides)
        output = publish_cmdline(
            writer_name='html5',
            settings_overrides=overrides,
            argv=[
                rst_file,
                filename,
            ]
        )
    except Exception as err:
        logger.error(err)
        output = err
    return output


def rst2odt(rst_file, filename, theme='restructedtext', settings={}):
    output = None
    try:
        overrides = {}
        overrides.update(default_overrides)
        overrides.update(settings)
        overrides.update(get_theme_settings(theme))
        logger.debug(overrides)
        writer = Writer()
        reader = Reader()
        output = publish_cmdline_to_binary(
            reader=reader,
            writer=writer,
            settings_overrides=overrides,
            argv=[
                rst_file,
                filename,
            ]
        )
    except Exception as err:
        logger.error(err)
        output = err
    return output


def get_md_themes():
    """
    result: { 'theme': theme_dict, ... }
    """
    themes_dirs = [
        os.path.join(__home_data_path__, 'themes', 'Markdown'),
        os.path.join(__data_path__, 'themes', 'Markdown'),
    ]
    themes = OrderedDict()
    for themes_dir in themes_dirs:
        if os.path.isdir(themes_dir):
            for theme_dir in os.listdir(themes_dir):
                theme_dir = os.path.join(themes_dir, theme_dir)
                if os.path.isdir(theme_dir):
                    for theme in os.listdir(theme_dir):
                        name, ext = os.path.splitext(theme)
                        if ext.lower() == '.css':
                            themes[name] = os.path.join(theme_dir, theme)
    return themes


def md2htmlcode(markup_file, theme=None, settings={}):
    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.abbr',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.tables',
        'markdown.extensions.smart_strong',
        'markdown.extensions.admonition',
        'markdown.extensions.codehilite',
        'markdown.extensions.headerid',
        'markdown.extensions.meta',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
        'markdown.extensions.toc',
        'markdown.extensions.wikilinks',
        mdx_mathjax.MathJaxExtension(),
    ]
    try:
        overrides = {}
        logger.debug(overrides)
        body = markdown.markdown(
            markup_file, output_format='html5', extensions=extensions)
    except Exception as err:
        logger.error(err)
        body = err

    themes = get_md_themes()
    theme_path = themes.get(theme, 'default')
    theme_css = ''
    if os.path.exists(theme_path):
        with open(theme_path) as f:
            theme_css = f.read()

    pygments_path = os.path.join(
        __home_data_path__, 'themes', 'Markdown', 'pygments.css')
    pygment_css = ''
    if os.path.exists(pygments_path):
        with open(pygments_path) as f:
            pygment_css = f.read()

    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html>')
    html.append('<head>')
    head = []
    head.append('<meta charset="UTF-8" />')
    mathjax = settings.get('mathjax')
    if not mathjax:
        if os.path.exists(__mathjax_full_path__):
            mathjax_path = __mathjax_full_path__ + '?config=TeX-MML-AM_CHTML'
        else:
            mathjax_path = __mathjax_min_path__
        mathjax = """<script type="text/javascript" src="file:///%s"></script>""" % mathjax_path
    if mathjax:
        head.append(mathjax)
    head.append('<style type="text/css">')
    if theme_css:
        head.append(theme_css)
    if pygment_css:
        head.append(pygment_css)
    head.append('</style>')
    html.extend(head)

    html.append('</head>')
    html.append('<body>')
    html.append(body)
    html.append('</body>')
    html.append('</html>')

    return '\n'.join(html)


def md2html(md_file, filename, theme):
    with open(md_file, encoding='UTF-8') as f:
        md_text = f.read()
    settings = {}
    settings['mathjax'] = """<script type="text/javascript" async
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-MML-AM_CHTML">
</script>"""
    html = md2htmlcode(md_text, theme=theme, settings=settings)
    with open(filename, 'wt') as f:
        f.write(html)
