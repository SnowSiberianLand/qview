# -*- coding: cp1251 -*-

import mod_dm as dm
import mod_orm as db
import mod_cmn as cmn

import table_utils2 as tu

import xlwt


    
#typedef table dmsrv.TableControllerBase
#typedef wbook xlwt.Workbook
#typedef wsheet xlwt.Worksheet
#typedef col xlwt.Column
#typedef row xlwt.Row
#typedef ctx dmsrv.python_ctx
#typedef pp cmn.progress_phase
#typedef pd dm.IPropertyDesc

def getFileName(ctx, res):

    fname = ctx.path
    if len(fname)==0:
        rpt_fname = ctx.get_string_value("RPT_FILE_NAME")
        if rpt_fname[0] == True:
            fname = rpt_fname[1]

    if len(fname)==0:
        res.add_error("Report filename is not found or empty")

    return fname

def get_col_width(num_characters):
    return int((1+num_characters) * 256)

def get_font_height(szpt):
    return int(szpt*20)


def write_num(sheet, row, col, val, style = None):
    """
    не выводит в отчет num_t_undefined и None
    """
    if val is None:
        return
    
    if cmn.is_undefined(val):
        return

    if style is not None:
        sheet.write(row, col, val, style)
    else:
        sheet.write(row, col, val)

## style cache, due to Excel style limit 4K
class XLStyleCache(object):
    kwd_mark = object()

    def cached_easyxf(self, string='', **kwargs):
         return self.cached_easyxf2(None, string, **kwargs)
     
    def cached_easyxf2(self, fmt, string='', **kwargs):
        if not hasattr(self, '_cached_easyxf'):
            self._cached_easyxf = {}
        key = (fmt), (string,) + (self.kwd_mark,) + tuple(sorted(kwargs.items()))
        stl = xlwt.easyxf(string, **kwargs)

        if fmt is not None:
            stl.num_format_str = fmt
            
        return self._cached_easyxf.setdefault(key, stl)

## column definition
class col_def:
    mnemo = ''
    title = ''
    index = None
    fmt_str = ''
    stl = xlwt.XFStyle()
    stl_last = xlwt.XFStyle()
    width = None
    ftype = None
    
    data_stl_str = 'border: right thin, left thin; align: wrap on, vert centre, horiz right; font: height {0};'.format(get_font_height(10))
    last_row_stl_str = 'border: right thin, bottom thin, left thin; align: wrap on, vert centre, horiz right; font: height {0};'.format(get_font_height(10))

    def __init__(self, ctx=None, stls=None, _index=-1, _mnemo="", _title="", wrap=False):
        self.mnemo = _mnemo
        self.title = _title
        self.index = _index
        if (ctx is not None):
            self.fmt_str = self.getFmtStr(ctx,_mnemo)
            self.ftype = self.getPropType(ctx,_mnemo)
        if (stls is not None):
            self.stl = stls.cached_easyxf2(self.fmt_str, self.data_stl_str)
            self.last_stl = stls.cached_easyxf2(self.fmt_str, self.last_row_stl_str)   
            self.width = get_col_width(len(self.title)+6)

            # ограничим максимальную ширину колонки
            # если заголовок влазить не будет, нужно добавить в стиль alignment: wrap true;
            if (self.width>4200):
                self.width = 4200
            
        if (wrap==False):
            data_stl_str = 'border: right thin, left thin; vert centre, horiz right; font: height {0};'.format(get_font_height(10))
        
        

    def  getFmtStr(self, ctx, mnemo):
        mst = ctx.pStorage.getMetaStorage()
        pd = dm.getPropertyByMnemo(mst, mnemo)
        if pd is None:
            print("Wrong property mnemo:",mnemo)
            return None
            
        ft = pd.getDataTypeID()
        if (ft==db.ft_date):
            return 'DD.MM.YYYY'
        elif (ft==db.ft_num) or (ft==db.ft_num):
            return '#0.0'
        
        return None
    
    def getPropType(self, ctx, mnemo):
        ft = None
        mst = ctx.pStorage.getMetaStorage()
        pd = dm.getPropertyByMnemo(mst, mnemo)

        if pd is not None:
            ft = pd.getDataTypeID()
        return ft

    def getValue(self, tbl, row, unit=None):
        if self.ftype==db.ft_num or self.ftype==db.ft_num:
            num = tu.getNum2(self.mnemo, row, tbl, unit)       
            if (num is None) or (num==cmn.get_undefined_r64()):
                num = ''
            return num
        elif self.ftype==db.ft_date:
            num = tu.getXlsDateNum(self.mnemo, row, tbl)
            if (num is None) or (num==cmn.get_undefined_r64()):
                num = ''
            return num
        else:
            return tu.getStr2(self.mnemo, row, tbl)


## для pd получить список словарных значений, похожих на массив flags
def extract_dictionary_codes(pd, flags):
    codes = set([0, 1])
    codes.clear()

    if pd is None:
        print("dic is None")
        return codes

    dic = pd.getDictionary()
    if dic is None:
        print("dic is None")
        return codes

    n = len(flags)
    for i in range(n):
        str = flags[i]
        str_upper = str.upper()

        n1 = dic.getItemCount()
        for i1 in range(n1):
            elem = dic.getItem(i1)
            sname = elem.getShortName()
            if sname==str:
                id = elem.getID()
                codes.add(id)
            else:
                sname1 = sname.upper()
                if str_upper==sname1:
                    id = elem.getID()
                    codes.add(id)
    return codes
