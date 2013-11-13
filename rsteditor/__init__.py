import sys
import os.path

__app_name__ = 'rsteditor'
__app_version__ = '0.0.1'
__default_filename__ = 'unknown.rst'


__data_path__ = os.path.join('%s/share/%s'% (sys.prefix, __app_name__.lower()))
__home_data_path__ = os.path.join(os.path.expanduser('~'), '.config', __app_name__.lower())

