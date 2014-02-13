import sys
import os.path

__app_name__ = 'RSTEditor'
__app_version__ = '0.1.3'
__default_filename__ = 'unknown.rst'


__data_path__ = os.path.join('%s/share/%s' % (sys.prefix, __app_name__.lower()))
if not os.path.exists(__data_path__):
    __data_path__ = os.path.join('%s/.local/share/%s' % (os.path.expanduser('~'), __app_name__.lower()))
__home_data_path__ = os.path.join(os.path.expanduser('~'), '.config', __app_name__.lower())
