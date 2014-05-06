
import logging

try:
    from docutils.core import publish_string
except:
    raise Exception('Please install docutils firstly')


def rst2html(rst_text):
    output = None
    try:
        overrides = {'input_encoding': 'utf-8',
                'output_encoding': 'utf-8'}
        output = publish_string(rst_text,
                writer_name='html',
                settings_overrides=overrides)
    except Exception as err:
        logging.error(unicode(err))
        output = unicode(err)
    return output
