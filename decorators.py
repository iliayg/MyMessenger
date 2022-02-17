import sys
import logging

# signal source detection method find()
# returns index of first incoming string, if not exists returns -1
if sys.argv[0].find('client') == -1:
    # if not client
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func_to_log):
    """function-decorator"""
    def log_saver(*args):
        ret = func_to_log(*args)
        LOGGER.debug(f'\nFunction "{func_to_log.__name__}" has been called with parameters {args}. '
                     f'Calling from module {func_to_log.__module__}.')
        return ret
    return log_saver