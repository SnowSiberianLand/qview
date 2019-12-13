import mod_cmn as cmn
import mod_dmsrv as dmsrv

import inspect

#typedef appo cmn.IAppOptions

def debug_func(frame):
    """
    for dump func called
    """
    args, _, _, values = inspect.getargvalues(frame)
    debug( 'method called: \"{0}()\"'.format(inspect.getframeinfo(frame)[2]) )

def debug_args(frame):
    """
    for dump method args
    """
    args, _, _, values = inspect.getargvalues(frame)
    debug( 'method called: \"{0}()\"'.format(inspect.getframeinfo(frame)[2]) )
    for i in args:
        if str(i)=='self':
            continue
        debug( "    {0} = {1}".format(i, values[i]) )

    
def verify_logger(logger, bRewrite):
    dmsrv.py_log_verify(logger, bRewrite)
    
def log_error(logger, msg):
    dmsrv.py_log_error(logger, msg)

def log_info(logger, msg):
    dmsrv.py_log_info(logger, msg)

def log_debug(logger, msg):
    dmsrv.py_log_debug(logger, msg)

def log_clear(logger):
    dmsrv.py_log_clear(logger)

def log_set_level(logger, level):
    dmsrv.py_log_set_level(logger, level)


def log_all_set_level(lev):
    appo = cmn.getAppOptions()
    appo.setLogLevel('',lev) # 1st arg doesn't matter

## ---------------------------
## !!! use set_logger() before calling
##     error(), info(), debug()
##

m_logger = ''

def set_logger(logger):
    global m_logger
    m_logger = logger

def verify(bRewrite):
    verify_logger(m_logger, bRewrite)
    
def error(msg):
    log_error(m_logger, msg)

def info(msg):
    log_info(m_logger, msg)

def debug(msg):
    log_debug(m_logger, msg)

def clear():
    dmsrv.py_log_clear(m_logger)

def set_level(level):
    log_set_level(m_logger, level)

if __name__ == '__main__':

    set_logger('mylog')
    
    verify('mylog', True)

    error('test_error1')
    info('test_info1')
    debug('test_debug1')

    clear()
    set_level('INFO')

    error('test_error2')
    info('test_info2')
    debug('test_debug2')

    print('Done')