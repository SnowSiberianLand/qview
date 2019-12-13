# -*- coding: cp1251 -*-

import entity_utils as eu
import table_utils as tu
import mod_cmn as cmn
import mod_orm as db
import mod_dm as dm
import mod_dmsrv as dmsrv

import struct
import time
import datetime
import numpy
import base64
import random
import calendar

def rand_date(ymin, ymax):
    yy = random.randint(ymin,ymax)
    mm = random.randint(1,12)
    dd = random.randint(1,28)
        
    dt = mk_date(yy,mm,dd)
    return dt

def rand_date_monthly(ymin, ymax):
    yy = random.randint(ymin,ymax)
    mm = random.randint(1,12)
    dd = 1
        
    dt = mk_date(yy,mm,dd)
    return dt

class depth_intvl:
    
    def __init__(self):
        self.top_md      = None
        self.base_md     = None

def get_max_pos_non_undef(seq):
    max = 0
    for val in seq:
        if not cmn.is_undefined(val) and val > max:
            max = val

    return max
        

def to_str_vec(seq):
    vec = cmn.vec_wstring_t()
    for s in seq:
        vec.append(s)
    return vec


def to_i32_vec(seq):
    vec = cmn.vec_i32_t()
    for v in seq:
        if (not cmn.is_undef(v)) and (not cmn.is_undefined(v)):
            vec.append(int(v))
        else:
            vec.append(cmn.get_undefined_i32())
            
    return vec

def to_r32_vec(seq):
    vec = cmn.vec_r32_t()
    for v in seq:
        vec.append(v)
            
    return vec

def to_int_vec(seq):
    return to_i32_vec(seq)


def to_float_vec(seq):
    """
    converts list to vec_num_t
    """
    vec = cmn.vec_r32_t()
    for v in seq:
        if (not cmn.is_undef(v)) and (not cmn.is_undefined(v)):
            vec.append(v)
        else:
            vec.append(cmn.get_undefined_r32())
    return vec

def to_double_vec(seq):
    """
    converts list to vec_num_t
    """
    vec = cmn.vec_num_t()
    for v in seq:
        if (not cmn.is_undef(v)) and (not cmn.is_undefined(v)):
            vec.append(v)
        else:
            vec.append(cmn.get_undefined_r32())
    return vec


def to_bh_vec(seq):
    vec = dm.vec_borehole_t()
    for v in seq:
        vec.append(v)
    return vec

def to_uniq_ids(vbh):
    ret = set()
    for bh in vbh:
        ret.add(bh.getID())
    return ret

def to_reservoir_vec(seq):
    vec = dm.vec_reservoir_t()
    for v in seq:
        vec.append(v)
    return vec

def to_stratum_vec(seq):
    vec = dm.vec_geolayer_t()
    for v in seq:
        vec.append(v)
    return vec

def to_model_vec(seq):
    vec = dm.vec_model_t()
    for v in seq:
        vec.append(v)
    return vec

def to_horizon_vec(seq):
    vec = dm.vec_horizon_t()
    for v in seq:
        vec.append(v)
    return vec

def from_vec(vec):
    seq = []
    for v in vec:
        seq.append(v)
    return seq

def blob2string(blob):
    fmt = '{0}b'.format(len(blob))
    return struct.pack(fmt, *blob)

def blob2float_array(blob):
    a = []

    if 0==len(blob):
        return a

    bytes = blob2string(blob)

    alen = len(bytes)
    count = int(alen/4)

    fmt = '<{0}f'.format(count)
    a = struct.unpack(fmt, bytes)
    return a

def blob2int_array(blob):
    a = []

    if 0==len(blob):
        return a

    bytes = blob2string(blob)

    alen = len(bytes)
    count = int(alen/4)

    fmt = '<{0}i'.format(count)
    a = struct.unpack(fmt, bytes)
    return a

def blob2vec_num_t(blob):
    fa = blob2float_array(blob)
    return to_double_vec(fa)

def blob2vec_i32_t(blob):
    fa = blob2int_array(blob)
    return to_i32_vec(fa)

def replace_nulls(vec, null_val):
    """
        replaces given null-value with r32-t_undefined
        
    """
    n = len(vec)
    for k in range(n):
        if null_val==vec[k]:
            vec[k] = cmn.get_undefined_r64()


def from_str_to_int_vec(vec):
    newvec = cmn.vec_i32_t()
    for v in vec:
        ok, i = cmn.from_string_i32(v)
        newvec.append(i)
    return newvec


def property_id2str(strg, id):
    mst = strg.getMetaStorage()
    pd = dm.getPropertyById(mst, id)
    if not pd is None:
        return pd.getShortName()
    return ""


def property2str(strg, mnemo):
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    if not pd is None:
        return pd.getShortName()
    return ""


def get_property_desc(strg, mnemo):
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    return pd

def get_dict_name(strg, mnemo, code):
    pd = get_property_desc(strg, mnemo)
    dic = pd.getDictionary()
    if dic:
        item = dic.find(code)
        if item:
            return item.getShortName()
    return ""


def get_value_class(mnemo, pd_mnemo, ctx, res, silent = False):
    mst = ctx.pStorage.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, pd_mnemo)
    if pd is None:
        res.add_error(_("Invalid IPropertyDesc\"{0}\"").format(pd_mnemo))
        return None
    vc_reg = mst.getMetaHelper().getVClassRegistry()
    vc = vc_reg.findByPropertyAndName(pd.getID(), mnemo)
    if vc is None and not silent:
        res.add_error("Incorrect IValueClass mnemo \"{0}\"".format(mnemo))
    return vc


def check_monotonity(seq):
    count = len(seq)
    for i in range(0, count-1):
        if seq[i] >= seq[i+1]:
            return False
    return True


def check_positive_values(seq):
    for val in seq:
        if not is_positive_value(val):
            return False
    return True


def check_not_negative_values(seq):
    for val in seq:
        if not is_not_negative_value(val):
            return False
    return True


def is_positive_value(val):
    return val > 0.0 and not cmn.is_undefined(val)


def is_not_negative_value(val):
    return val >= 0.0 and not cmn.is_undefined(val)


def is_negative_value(val):
    return val < 0.0


def is_undefined_value(val):
    return cmn.is_undefined(val)


def is_undef_or_zero_value(val):
    return cmn.is_undefined(val) or val == 0.0


def contains(mark, depth):
    #TODO: optimize
    count = len(depth)
    for i in range(0, count-1):
        if depth[i] <= mark <= depth[i+1]:
            return True
    return False


def in_range(x, xmin, xmax, e = 0.0):
    if cmn.is_undefined(e):
        e = 0.0
    return (xmin - e) <= x <= (xmax + e)


def intersects(a1, b1, a2, b2, e = 0.0):
    """
    проверяет пересечение 2-х интервалов [a1,b1] и [a2,b2]
    с заданной точностью для границ
    """
    if cmn.is_undefined(e):
        e = 0.0
    ok = in_range(a1, a2, b2, e) or in_range(a2, a1, b1, e) or \
         in_range(b1, a2, b2, e) or in_range(b2, a1, b1, e)
    return ok

def in_range2(x, xmin, xmax, e = 0.0):
    if cmn.is_undefined(e):
        e = 0.0
    if cmn.is_undefined(x):
        return True
    else:
        return (xmin - e) <= x <= (xmax + e)
def intersection_length(a1, b1, a2, b2):
    """
    возвращает размер зоны пересечения 2-х интервалов [a1,b1] и [a2,b2]
    возвращает None если интервалы не пересекаются или касаются
    возвращаяет 0 если один из интервалов вырожденный и лежит внутри другого
    значения a1,b1  и a2,b2 могут быть не упорядочены по возрастанию
    """
    span = intersection(a1, b1, a2, b2)
    if (span is None):
        return None

    ll = span[1]-span[0]
    return ll

def subtract(a1, b1, a2, b2):
    """
    вычитает из первого [a1,b1] интервала второй [a2,b2]
    возвращает список полученных интервалов list(tuple)
    возвращает первый интервал если интервалы не пересекаются
    значения a1,b1  и a2,b2 могут быть не упорядочены по возрастанию
    """
    out = []
    ll = intersection_length(a1, b1, a2, b2)
    if ll is None:
        return [ (a1,b1) ]

    lst = [(a1,1),(b1,1),(a2,2),(b2,2)]
    lst = sorted(lst)
    #print lst

    f1 = False
    f2 = False
    xbeg = None
    xend = None
    n = len(lst)
    for i in range(n):
        if lst[i][1]==1:
            f1 = f1 ^ True
        if lst[i][1]==2:
            f2 = f2 ^ True

        #print i, 'f1=',f1, 'f2=',f2

        if (xbeg is None) and f1==True and (not f2):
            xbeg = lst[i][0]

        if xbeg is not None:
            if f2==True or i==n-1:
                xend = lst[i][0]
        
        if (xbeg is not None) and (xend is not None):
            out.append( (xbeg, xend) )
            xbeg = None
            xend = None
    
    return out
    

def union(a1, b1, a2, b2):
    """
    возвращает зону объединения (tuple) 2-х интервалов [a1,b1] и [a2,b2]
    возвращает None если интервалы не пересекаются
    значения a1,b1  и a2,b2 могут быть не упорядочены по возрастанию
    """

    ll = intersection_length(a1, b1, a2, b2)
    if ll is None:
        return None

    lst = [a1,b1,a2,b2]
    lst = sorted(lst)
    
    return (lst[0], lst[3])

def intersection(a1, b1, a2, b2):
    """
    возвращает зону пересечения (tuple) 2-х интервалов [a1,b1] и [a2,b2]
    возвращает None если интервалы не пересекаются
    значения a1,b1  и a2,b2 могут быть не упорядочены по возрастанию
    """

    lst = [(a1,1),(b1,1),(a2,2),(b2,2)]
    lst = sorted(lst)
    #print lst

    f1 = False
    f2 = False
    xbeg = None
    xend = None
    n = len(lst)
    for i in range(n):
        if lst[i][1]==1:
            f1 = f1 ^ True
        if lst[i][1]==2:
            f2 = f2 ^ True

        #print f1, f2
        
        if f1 and f2:
            xbeg = lst[i][0]

        if xbeg is not None:
            if (not f1) or (not f2):
                xend = lst[i][0]
                break

    if (xbeg is not None) and (xend is not None):
        #print xbeg, '-', xend
        return (xbeg, xend)
    
    return None


def is_equal(x, y, e = 0.0):
    if cmn.is_undefined(e):
        e = 0.0
    return abs(x - y) < e


def has_significant_values(seq):
    significant = [x for x in seq if not cmn.is_undefined(x)]
    return len(significant) > 0


def find_sequence_nulls(seq, nullstr):
    """
    """
    values = nullstr.split(";")
    nulls = []
    for val in values:
        ok, tmp = cmn.from_string_r32(val)
        if ok:
            nulls.append(tmp)
    suspects = [x for x in seq if x in nulls]
    #distinct
    suspects = list(set(suspects))
    return suspects


def is_equal_sequences(seq1, seq2):
    count1 = len(seq1)
    count2 = len(seq2)
    if count1 != count2:
        return False
    for i in range(count1):
        if seq1[i] != seq2[i]:
            return False
    return True


def item2str(item):
    """
    Converts item to string, using lib_cmn conversions
    If item is list or tuple, conversion will be applied to all subitems
    and result will be surrounded by []
    """
    if isinstance(item, (list, tuple)):
        s = ", ".join([item2str(n) for n in item])
        return "[{0}]".format(s)
    else:
        func = to_str_func(item)
        return func(item)


def seq2str(_seq, sep = ", "):
    seq = list(map(item2str, _seq))
    if len(seq) == 0:
        return ""
    return sep.join(seq)


def compact_format(seq, max = 4):
    if len(seq) > max:
        short_max = max
        if short_max > 8:
            short_max = 8
        short_seq = seq[0:short_max]
        return _("{0}.... total {1} pcs.").format(seq2str(short_seq), len(seq))
    else:
        return "{0}".format(seq2str(seq))


def float2str(val):
    str = "{0:.2f}".format(val) if not cmn.is_undefined(val) else ""
    return str

def mk_date(y,m,d):
    ymd = cmn.ymd_lite()    
    ymd.day = d
    ymd.month = m
    ymd.year = y
    dt =  cmn.from_ymd(ymd)
    return dt

def to_date_t(dt):
    """
    converts Python's datetime.date to cmn.date_t
    """
    s = '{0}.{1}.{2}'.format(dt.day, dt.month, dt.year)
    return str2date(s)

def days_in_month(dt):
    """
    dt - date_t
    """
    ymd = cmn.to_ymd(dt)    
    return calendar.monthrange(ymd.year,ymd.month)[1]
    
def year_from_date_t(dt):
    ymd = cmn.to_ymd(dt)
    return ymd.year

def next_month(dt):
    """
    advances dt to next month
    """
    ymd = cmn.to_ymd(dt)

    if ymd.month<12:
        ymd.month += 1
    else:
        ymd.year += 1
        ymd.month = 1

    dt = cmn.from_ymd(ymd)
    return dt

def from_date_t(dt):
    """
    converts cmn.date_t to Python's datetime.date
    """
    try:
        s = cmn.to_string_date(dt)
        tmp = time.strptime(s, '%d.%m.%Y')
    
        y = tmp[0]
        m = tmp[1]
        d = tmp[2]
        
        return datetime.date(y,m,d)
    except:
        return None

def to_datetime64(dt):
    """
    converts cmn.date_t to numpy.datetime64
    """
    if cmn.is_undefined(dt):
        return None
    
    try:
        ymd = cmn.to_ymd(dt)
        s = '{0}-{1:0>2d}-{2:0>2d}'.format(ymd.year, ymd.month, ymd.day)
        print(s)
        return numpy.datetime64(s)
    except:
        return None

def str2date(s):
    dt = cmn.date_t()
    cmn.from_string_date(s, dt)
    return dt

def from_datetime_t(dt):
    """
    converts cmn.datetime_t to Python's datetime.datetime
    """
    try:
        s = cmn.to_string_datetime(dt)
        tmp = time.strptime(s, '%d.%m.%Y %H:%M:%S')
        y = tmp[0]
        m = tmp[1]
        d = tmp[2]
        H = tmp[3]
        M = tmp[4]
        S = tmp[5]
            
        return datetime.datetime(y,m,d,H,M,S)
    except:
        return None


def get_distance(x1, y1, x2, y2):
    if is_undefined_value(x1) or is_undefined_value(y1) or is_undefined_value(x2) or is_undefined_value(y2):
        return cmn.get_undefined_r64()
    dx = x2 - x1
    dy = y2 - y1
    dist = dmsrv.py_sqrt(dx * dx + dy * dy)
    return dist


def add_interval(list, top, bot):
    data = (top, bot)
    if list.count(data) == 0:
        list.append(data)
        return True
    return False


def add_interval2(list, top_list, bot_list, i):
    top = top_list[i]
    bot = bot_list[i]
    return add_interval(list, top, bot)


def compact_intervals(intervals):
    count = len(intervals)
    if count == 0:
        return intervals
    tmp = intervals;
    tmp.sort()
    res = []
    res.append(tmp[0])
    for i in range(1, count):
        if tmp[i] == tmp[i-1]:
            continue
        if res[-1][1] != tmp[i][0]:
            res.append(tmp[i])
    return res;


def get_bottom_md(borehole_id, ctx):
    bh = eu.find_borehole(ctx.pStorage, borehole_id)
    if bh is None:
        return cmn.get_undefined_r64()
    return bh.getDrilledMD()


def test_monotonity(seq):
    count = len(seq)
    if 0 == count:
        return True

    for i in range(1, count):
        curr = seq[i]
        prev = seq[i-1]
        if cmn.is_undefined(curr):
            if not cmn.is_undefined(prev):
                return False
        if not cmn.is_undefined(prev):
            if curr < prev:
                return False
    return True


def find_non_monotone_indices(seq):
    count = len(seq)
    if 0 == count:
        return None

    res = None
    for i in range(1, count):
        curr = seq[i]
        prev = seq[i-1]
        if cmn.is_undefined(curr):
            if not cmn.is_undefined(prev):
                if res == None:
                    res = []
                res.append(i)
        if not cmn.is_undefined(prev):
            if curr < prev:
                if res == None:
                    res = []
                res.append(i)

    return res


def test_unique(seq):
    not_unique = set()
    count = len(seq)
    for i in range(0, count-1):
        step = seq[i+1].day_number() - seq[i].day_number()
        if step == 0:
            not_unique.add(seq[i])
    return not_unique


def test_period(seq):
    errors = []
    count = len(seq)
    for i in range(0, count-1):
        step = seq[i+1].day_number() - seq[i].day_number()
        period_errors = (step < 28) or (step > 31)
        if period_errors and (step != 0):
            errors.append(i)
            errors.append(i+1)
    return errors


def test_prod_dates(seq):
    errors = []
    count = len(seq)
    for date in seq:
        correct = dmsrv.py_begin_of_month(date)
        if date.day_number() != correct.day_number():
            errors.append(date)
    return errors


def unwrap_seq(seq):
    if len(seq) == 0:
        return []

    ref_item = seq[0]
    if isinstance(ref_item, list):  #list, but not tuple
        _seq = set()
        for s1 in seq:
            for s2 in s1:
                _seq.add(s2)
        return list(_seq)
    else:
        return seq


def to_str_func(item):
    func = lambda s: s
    if isinstance(item, int):
        func = cmn.to_string_i32
    elif isinstance(item, float):
        func = cmn.to_string_r32
    elif isinstance(item, cmn.date_t):
        func = cmn.to_string_date
    return func


def from_str_func(item, datatype):
    if isinstance(item, str):
        if datatype == db.ft_int32:
            return lambda s: cmn.from_string_i32(s)[1]
        elif datatype == db.ft_num:
            return lambda s: cmn.from_string_r32(s)[1]
        elif datatype == db.ft_date:
            return str2date
    return lambda s: s


def make_position(strg, _seq, *mnemos):
    seq = unwrap_seq(_seq)
    if len(seq) == 0:
        return None

    pds = [get_property_desc(strg, n) for n in mnemos]
    if len(pds) == 0 or pds.count(None) > 0:
        return None

    one_item = len(pds) == 1

    nav = dmsrv.make_py_navigator_impl()

    funcs = []
    if one_item:
        funcs = [from_str_func(seq[0], pds[0].getDataTypeID())]
    else:
        funcs = [from_str_func(s, p.getDataTypeID()) for s, p in zip(seq[0], pds)]

    for s in seq:
        vv = []
        if one_item:
            vv = [funcs[0](s)]
        else:
            vv = [func(n) for n, func in zip(s, funcs)]

        nav.add_empty()
        index = nav.size()-1
        for pd, v in zip(pds, vv):
            nav.set_property(pd, dmsrv.make_variant(v), index);

    return nav

def fmt_date(dt):
    """
    dt - python's date
    """
    sdt = ''
    if dt is not None:
        sdt = '{0:0>2d}.{1:0>2d}.{2}'.format(dt.day, dt.month, dt.year)

    return sdt

def fmt_date_inv(dt):
    """
    dt - python's date
    """
    sdt = ''
    if dt is not None:
        sdt = '{0}.{1:0>2d}.{2:0>2d}'.format(dt.year,dt.month,dt.day)

    return sdt

def is_same_year(dt1, dt2):
    """
    возвращает True если даты относятся к одному году (cmn.date_t)
    в остальных случаях - False
    """
    if (dt1 is None or dt2 is None):
        return False
    
    if (cmn.is_undefined(dt1) or cmn.is_undefined(dt2)):
        return False

    ymd1 = cmn.to_ymd(dt1)    
    ymd2 = cmn.to_ymd(dt2)    

    if ymd1.year == ymd2.year:
        return True

    return False


def date_distance(dt1, dt2):
    """
    возвращает расстояние в днях между двумя датами (cmn.date_t)
    """
    if (dt1 is None or dt2 is None):
        return cmn.get_undefined_r64()
    
    if (cmn.is_undefined(dt1) or cmn.is_undefined(dt2)):
        return cmn.get_undefined_r64()
    
    pydt1 = from_date_t(dt1)
    pydt2 = from_date_t(dt2)    
    dd = (pydt2-pydt1).days

    return numpy.abs(dd)
    
def days_in_month(dt):
    """
    кол-во дней в месяце
    dt - date_t
    """
    from calendar import monthrange

    ymd = cmn.to_ymd(dt)
    qq = monthrange(ymd.year, ymd.month)
    
    return qq[1]

#typedef dicmap dm.dic_mapping
#typedef pd dm.IPropertyDesc
#typedef synctx dm.sync_ctx

def recode_dic_item(mnemo, strg, dicmap, code):
    mst = dm.getMetaStorage(strg)
    pd = dm.getPropertyByMnemo(mst, mnemo)
    return recode_dic_item_impl(pd, dicmap, code)    

def recode_dic_item_impl(pd, dicmap, code):
    new_code = dicmap.find_new_id(pd, code)
    return new_code

def ext_code2string(dic, code):
    return dic.get(code, '')


def get_dates(indices, dates):
    res = []
    if indices:
        for i in indices:
            res.append(dates[i])
    return res

def make_pos(pool, lift, category, dates):
    res = []
    for d in dates:
        res.append((pool, lift, category, d))
    return res

def file_to_base64(fname):
    with open(fname, "rb") as image_file:
        s = base64.b64encode(image_file.read())
    return s

def blob_from_base64(s):
    
    data = base64.b64decode(s)

    blob = cmn.blob_t()

    for b in data:
        blob.append(b)

    return blob

def get_dic_string(strg, pd_mnemo, code):
    """
    get dictionary value for given <property, code>
    """
    mst = strg.getMetaStorage()
    mh = mst.getMetaHelper()
    reg = mh.getDicRegistry()

    # получим свойство 
    pd = dm.getPropertyByMnemo(mst, pd_mnemo)

    dic = reg.find(pd.getID())

    if dic.find(code) is None:
        sn = None
    else:
        dic_item = dic.find(code)
        sn = dic_item.getShortName()
    return sn

def verify_dic_elem(strg, pd_mnemo, name):
    """
    verifies that dictionary for property "pd_mnemo" has elem with name "name"
    """
    mst = strg.getMetaStorage()
    mh = mst.getMetaHelper()
    reg = mh.getDicRegistry()

    #получим свойство
    pd = dm.getPropertyByMnemo(mst, pd_mnemo)
    dic = reg.find(pd.getID())
    dic_ed = dic.getEditor()

    key = dmsrv.prod_key()
    dic_items = dm.vec_dic_item_t()
    
    if len(name) > 40: #условие для short_name
        sname = name[0:40]
    else: 
        sname = name

    if dic.find_like(name,dic_items):
        key.name = dic_items[0].getID()
        item_id = key.name
    else:
        dic_item = dic_ed.addNewItemSmart(sname, name)
        dic.refresh_finders_add_obj(dic_item)
        item_id = dic_item.getID()
        
    return item_id

# test

##dt1 = numpy.datetime64('1990-01-01')
##print(dt1)

##dt1 = mk_date(1980,3,1)
##dt2 = mk_date(1980,1,1)
##d = date_distance(dt1,dt2)
##print(d)