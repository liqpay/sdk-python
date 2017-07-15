import sys

if sys.version_info >= (3, 0):
    from .liqpay3 import *
else:
    from .liqpay import *
