import sys
import os.path
import logging
import json

try:
    from docutils.core import publish_string
    from docutils.core import publish_cmdline
    from docutils.core import publish_cmdline_to_binary
    from docutils.writers.odf_odt import Writer, Reader
    from docutils.writers import html4css1
except:
    raise Exception('Please install docutils firstly')

from rsteditor import __home_data_path__


default_overrides = {
    'input_encoding': 'utf-8',
    'output_encoding': 'utf-8',
}

def get_theme_settings(theme, pygments):
    html4css1_path = os.path.realpath(os.path.dirname(html4css1.__file__))
    stylesheet = {}
    stylesheet['stylesheet_dirs'] = [html4css1_path]
    stylesheet['template'] = os.path.join(html4css1_path, 'template.txt')
    pygments_path = os.path.join(__home_data_path__, 'themes', 'pygments.css')
    if os.path.exists(pygments_path):
        stylesheet['stylesheet_path'] = pygments_path
        stylesheet['syntax_highlight'] = 'short'
    if theme == 'docutils':
        css_paths = []
        css_paths.append(os.path.join(html4css1_path, 'html4css1.css'))
        css_paths += stylesheet['stylesheet_path'].split(',')
        stylesheet['stylesheet_path']=','.join(css_paths)
        return stylesheet
    theme_cfg = os.path.join(__home_data_path__, 'themes', theme, 'theme.json')
    try:
        styles = json.load(open(theme_cfg))
    except Exception as err:
        logging.error(unicode(err))
        styles = {}
    # stylesheet_path : css file path
    # syntax_highlight: short
    # template: template file path
    if 'syntax_highlight' in styles:
        stylesheet['syntax_highlight'] = styles['syntax_highlight']
    if 'stylesheet_path' in styles:
        css_paths = styles['stylesheet_path'].split(',')
        new_css_paths = []
        for css_path in css_paths:
            new_css_path = os.path.realpath(
                os.path.join(__home_data_path__,
                             'themes',
                             theme,
                             css_path))
            new_css_paths.append(new_css_path)
            logging.debug('css path: %s' % new_css_path)
        if 'stylesheet_path' in stylesheet:
            new_css_paths += stylesheet['stylesheet_path'].split(',')
        stylesheet['stylesheet_dirs'].insert(0, os.path.dirname(new_css_paths[0]))
        stylesheet['stylesheet_path']=','.join(new_css_paths)
    if 'template' in styles:
        old_path = styles['template']
        new_path = os.path.realpath(
            os.path.join(__home_data_path__,
                         'themes',
                         theme,
                         old_path))
        stylesheet['template'] = new_path
    return stylesheet

def rst2htmlcode(rst_text, theme='docutils', pygments='docutils', settings={}):
    output = None
    try:
        overrides = {}
        overrides.update(default_overrides)
        overrides.update(settings)
        overrides.update(get_theme_settings(theme, pygments))
        logging.debug(overrides)
        output = publish_string(
            rst_text,
            writer_name='html',
            settings_overrides=overrides,)
    except Exception as err:
        logging.error(unicode(err))
        output = unicode(err)
    return output

def rst2html(rst_file, filename, theme='docutils', pygments='docutils', settings={}):
    output = None
    try:
        overrides = {}
        overrides.update(default_overrides)
        overrides.update(settings)
        overrides.update(get_theme_settings(theme, pygments))
        logging.debug(overrides)
        output = publish_cmdline(
            writer_name='html',
            settings_overrides=overrides,
            argv=[
                rst_file,
                filename,
            ]
        )
    except Exception as err:
        logging.error(unicode(err))
        output = unicode(err)
    return output

def rst2odt(rst_file, filename, theme='docutils', pygments='docutils', settings={}):
    output = None
    try:
        overrides = {}
        overrides.update(default_overrides)
        overrides.update(settings)
        overrides.update(get_theme_settings(theme, pygments))
        logging.debug(overrides)
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
        logging.error(unicode(err))
        output = unicode(err)
    return output
