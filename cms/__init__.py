VERSION = (2, 0, 0, 'timetravel', 1, 0, 0)
__version__ = '.'.join(map(str, VERSION))

# patch settings 
try:
    from conf import patch_settings
    from django.conf import settings
    patch_settings()
except ImportError:
    """
    This exception means that either the application is being built, or is
    otherwise installed improperly. Both make running patch_settings
    irrelevant.
    """
    pass

