import sys
import os.path
from collections import OrderedDict

__app_name__ = 'MEditor'
__app_version__ = '0.2.10.11'
__default_basename__ = 'unknown'

prefixs = [
    sys.prefix,
    os.path.join(os.path.expanduser('~'), '.local'),
    os.path.dirname(os.path.abspath(__file__)),
    getattr(sys, '_MEIPASS', ''),
]
for prefix in prefixs:
    __data_path__ = os.path.join(prefix, 'share', __app_name__.lower())
    if os.path.exists(__data_path__):
        __icon_path__ = os.path.join(prefix, 'share', 'pixmaps')
        break
# ~/.config/meditor
__home_data_path__ = os.path.join(
    os.path.expanduser('~'), '.config', __app_name__.lower())

os.makedirs(
    os.path.join(__home_data_path__, 'themes', 'reStructedText'),
    exist_ok=True)
os.makedirs(
    os.path.join(__home_data_path__, 'themes', 'Markdown'),
    exist_ok=True)

pygments_styles = {}
try:
    from pygments import styles
    pygments_styles = OrderedDict(
        [('null', 'null::NullStyle')] + sorted(styles.STYLE_MAP.items(), key=lambda x: x[0])
    )
    for k, v in pygments_styles.items():
        pygments_styles[k] = v.split('::')[1]
except:
    pass

__mathjax_full_path__ = os.path.join(__home_data_path__, 'MathJax-master', 'MathJax.js')
__mathjax_min_path__ = os.path.join(__data_path__, 'math', 'MathJax.min.js')
