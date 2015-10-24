import sys
import os.path

__app_name__ = 'RSTEditor'
__app_version__ = '0.2.0.0'
__default_filename__ = 'unknown.rst'

__icon_path__ = os.path.join(sys.prefix, 'share', 'pixmaps')
if sys.platform == 'win32':
    __icon_path__ = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'share',
                                 'pixmaps')

__data_path__ = os.path.join(sys.prefix, 'share', __app_name__.lower())
if sys.platform == 'win32':
    __data_path__ = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'share',
                                 __app_name__.lower())
else:
    if not os.path.exists(__data_path__):
        __data_path__ = os.path.join(os.path.expanduser('~'),
                                     '.local',
                                     'share',
                                     __app_name__.lower())
__home_data_path__ = os.path.join(os.path.expanduser('~'),
                                  '.config',
                                  __app_name__.lower())
pygments_styles = {}
try:
    from pygments import styles
    for k, v in styles.STYLE_MAP.items():
        pygments_styles[k] = v.split('::')[1]
except:
    pass
