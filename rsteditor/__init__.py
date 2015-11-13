import sys
import os.path
from collections import OrderedDict

__app_name__ = 'RSTEditor'
__app_version__ = '0.2.0.2'
__default_filename__ = 'unknown.rst'

if sys.platform == 'linux':
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
elif sys.platform == 'win32':
    __data_path__ = os.path.dirname(os.path.dirname(__file__))
    if os.path.basename(__data_path__) == 'library.zip':
        __data_path__ = os.path.dirname(__data_path__)
    __icon_path__ = os.path.join(__data_path__, 'pixmaps')
    __home_data_path__ = os.path.join(
        os.path.expanduser('~'),
        '.%s' % __app_name__.lower()
    )

os.makedirs(__home_data_path__, exist_ok=True)

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
