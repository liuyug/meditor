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

from rsteditor import __data_path__, __home_data_path__


default_overrides = {
    'input_encoding': 'utf-8',
    'output_encoding': 'utf-8',
}


def get_theme_settings(theme, pygments):
    """
    1. pygments.css has been created in app.py so parameter pygments is unused.
    2. load html4css1 css from docutils packages. if not found load from home data path
    """
    html4css1_path = os.path.realpath(os.path.dirname(html4css1.__file__))
    if not os.path.exists(html4css1_path):
        html4css1_path = os.path.join(__data_path__, 'docutils', 'writers', 'html4css1')
    stylesheet = {}
    stylesheet['stylesheet_dirs'] = [html4css1_path]
    stylesheet['template'] = os.path.join(html4css1_path, 'template.txt')
    pygments_path = os.path.join(__home_data_path__, 'themes', 'pygments.css')
    if os.path.exists(pygments_path):
        stylesheet['stylesheet_path'] = pygments_path
        stylesheet['syntax_highlight'] = 'short'
    if theme == 'docutils':
        css_paths = []
        css_paths.append('html4css1.css')
        css_paths.append('math.css')
        if 'stylesheet_path' in stylesheet:
            css_paths += stylesheet['stylesheet_path'].split(',')
        stylesheet['stylesheet_path'] = ','.join(css_paths)
        return stylesheet
    theme_dir = os.path.join(__home_data_path__, 'themes', theme)
    stylesheet['stylesheet_dirs'].append(theme_dir)
    try:
        styles = json.load(open(os.path.join(theme_dir, 'theme.json')))
    except Exception as err:
        logging.error(err)
        styles = {}
    # stylesheet_path : css file path
    # syntax_highlight: short
    # template: template file path
    if 'syntax_highlight' in styles:
        stylesheet['syntax_highlight'] = styles['syntax_highlight']
    if 'stylesheet_path' in styles:
        css_paths = styles['stylesheet_path'].split(',')
        if 'stylesheet_path' in stylesheet:
            css_paths += stylesheet['stylesheet_path'].split(',')
        stylesheet['stylesheet_path'] = ','.join(css_paths)
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
        logging.error(err)
        output = err
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
        logging.error(err)
        output = err
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
        logging.error(err)
        output = err
    return output
