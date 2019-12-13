import pickle
import os
import inspect

# current record list 
lst_rec = []
rec_fname = "calls.bin"
m_ctx_params = dict()
bRecEnabled = True

def set_cur_db(db_id, conns):
    set_context_param('db_id', db_id)
    set_context_param('db_conns', conns)

def set_context_param(key, val):
    """
    sets params that associated with each next call (current db, ...)
    """
    m_ctx_params[key] = val
    
def fn(frame):
    return frame.f_code.co_name    

def callMethod(o, name, args, kwargs):
    global bRecEnabled

    fun = getattr(o, name)

    if bRecEnabled:
        # print('callMethod()')  
        record_method(o, name, args)   

    return fun(*args, **kwargs)

def wrap(lst, *args, **kwargs):
    """
    wraps any function or method with recording
    """
    global bRecEnabled

    anyFunc = lst[0]
    obj = lst[1]

    def wrapper(*args, **kwargs):
        try:
            # do something before            
            if obj is None:                
                if bRecEnabled:
                    record_func(anyFunc, args)                   
                return anyFunc(*args, **kwargs)
            else:
                return callMethod(obj, anyFunc, args, kwargs)
        finally:
            #do something after
            pass
    return wrapper

def enable_recording(b):
    global bRecEnabled

    bRecEnabled = b

def set_fname(fname):
    global rec_fname

    # print('frec.set_fname():', fname)
    rec_fname = fname

def record_func(fn, fn_args:tuple):    
    """
    fn - function
    """
    global lst_rec, rec_fname

    if len(lst_rec)==0:
        load_funcs()

    fn_name = fn.__name__
    rec = (fn_name, fn_args)

    lst_rec.append(rec)

    with open(rec_fname, "wb") as f:
        pickle.dump(lst_rec, f)

def record_method(obj, fn_name, fn_args:tuple):    
    """
    fn - function
    """
    global lst_rec, rec_fname

    # print(obj)
    # print(fn_name)
    #print(fn_args)    

    oname = type(obj).__name__
    rec = (oname, fn_name, fn_args, m_ctx_params)

    if len(lst_rec)==0:
        # print('--- load_funcs()', rec_fname)        
        load_funcs()

    # print('--- record_method()', oname, fn_name)

    lst_rec.append(rec)

    try:
        with open(rec_fname, "wb") as f:
            pickle.dump(lst_rec, f)
    except:
        print("file write error: ", rec_fname)

def load_funcs():
    global rec_fname, lst_rec

    if not os.path.isfile(rec_fname):
        return

    with open(rec_fname, "rb") as f:
        lst_rec = pickle.load(f)

def exec_funcs():
    global lst_rec
    if len(lst_rec)==0:
        load_funcs()

    for rec in lst_rec:
        print(rec)

# def exec_func(fn_name, fn_args:tuple):
#     method_to_call = getattr(fn_name)
#     method_to_call(*fn_args)


# -------------------
# -- debug ----------
# -------------------
def func1(a,b):    
    c = a + b
    print(func1.__name__,c)

# tt = tuple()
# tt += (1,)
# tt += (2,)
# print(tt)

#wrap(func1)(5,6)

#exec_funcs()