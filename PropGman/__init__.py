__version__ = "0.0.dev1"
__all__ = ['method', 'model']

import sys

if sys.version_info < (3, 7):
    raise RuntimeError('DSRP supports Python 3.7 or higher.')