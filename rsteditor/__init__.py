import sys
import os.path
from collections import OrderedDict

__app_name__ = 'RSTEditor'
__app_version__ = '0.2.1.0'
__default_filename__ = 'unknown.rst'

if sys.platform == 'win32':
    if getattr(sys, 'frozen', False):
        prefix = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        prefix = os.path.dirname(os.path.abspath(__file__))
    __icon_path__ = os.path.join(prefix, 'share', 'pixmaps')
    __data_path__ = os.path.join(prefix, 'share', __app_name__.lower())
    __home_data_path__ = os.path.join(
        os.path.expanduser('~'),
        '.%s' % __app_name__.lower()
    )
else:
    __icon_path__ = os.path.join(sys.prefix, 'share', 'pixmaps')
    __data_path__ = os.path.join(sys.prefix, 'share', __app_name__.lower())
    if not os.path.exists(__data_path__):
        # for pip install --local
        __data_path__ = os.path.join(
            os.path.expanduser('~'),
            '.local',
            'share',
            __app_name__.lower()
        )
    __home_data_path__ = os.path.join(
        os.path.expanduser('~'),
        '.config',
        __app_name__.lower()
    )

os.makedirs(__home_data_path__, exist_ok=True)
os.makedirs(os.path.join(__home_data_path__, 'themes'), exist_ok=True)

pygments_styles = {}
try:
    from pygments import styles
    pygments_styles = OrderedDict(sorted(
        styles.STYLE_MAP.items(),
        key=lambda x: x[0]
    ))
    for k, v in pygments_styles.items():
        pygments_styles[k] = v.split('::')[1]
except:
    pass
