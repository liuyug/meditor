import os.path
import logging

try:
    from docutils.core import publish_string
    from docutils.core import publish_cmdline
    from docutils.core import publish_cmdline_to_binary
    from docutils.writers.odf_odt import Writer, Reader
except:
    raise Exception('Please install docutils firstly')

from rsteditor import __home_data_path__


def get_rhythm_css():
    stylesheet = {}
    rhythm_css_dir = os.path.join(__home_data_path__,
                                  'template',
                                  'rhythm.css')
    if os.path.exists(rhythm_css_dir):
        stylesheet = {
            'stylesheet_path': '%s,%s' % (os.path.join(rhythm_css_dir,
                                                       'dist',
                                                       'css', 'rhythm.css'),
                                          os.path.join(rhythm_css_dir,
                                                       'syntax',
                                                       'molokai.css')),
            'syntax-highlight': 'short',
        }
    return stylesheet

def rst2htmlcode(rst_text):
    output = None
    try:
        overrides = {
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8'
        }
        overrides.update(get_rhythm_css())
        output = publish_string(
            rst_text,
            writer_name='html',
            settings_overrides=overrides,)
    except Exception as err:
        logging.error(unicode(err))
        output = unicode(err)
    return output

def rst2html(rst_file, filename):
    output = None
    try:
        overrides = {
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8'
        }
        overrides.update(get_rhythm_css())
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

def rst2odt(rst_file, filename):
    output = None
    try:
        writer = Writer()
        reader = Reader()
        styles_odt = os.path.join(__home_data_path__,
                                  'template',
                                  'styles.odt')
        output = publish_cmdline_to_binary(
            reader=reader,
            writer=writer,
            argv=[
                rst_file,
                filename,
                '--stylesheet=%s' % styles_odt,
            ]
        )
    except Exception as err:
        logging.error(unicode(err))
        output = unicode(err)
    return output
