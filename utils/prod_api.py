# -*- coding: cp1251 -*-

###interactive object:
###title: Редактор Python
###mnemo: PYTHON_EDITOR
##
##import ctx_rds
##
###typedef strg mod_dm.IDataStorage
##
##strg = ctx_rds.datastorage

import table_utils2 as tu
import data_utils as du

import mod_dmsrv as dmsrv
import mod_dm as dm
import mod_orm as db
import mod_cmn as cmn

import numpy

#typedef tbl dmsrv.ITableController
#typedef strg dm.IDataStorage
#typedef mst dm.IMetaStorage
#typedef ents dm.entities

def set_none(v):
    n = len(v)
    for k in range(n):
        if cmn.is_undefined(v[k]):
            v[k] = None
##        else:
##            if v[k]==0:
##                v[k] = None

def cvt_vdate(v):
    n = len(v)
    data = numpy.empty(n, dtype='object')
    
    for k in range(n):
        dt = du.from_date_t(v[k])
        data[k] = dt
#        print(dt)
        
#    data = data.astype(DT.datetime)
    return data

def get_prod_data(strg, ents, mnemos):
    """
    возвращает list vec_num_t, vec_date_t, ...
    кол-во элементов list'a равно кол-ву мнемоник
    кол-во элементов массивов определяется данными, длина всех массивов равна
    """

    lst = []
    if strg is None:
        return lst
    
    err = cmn.err_info()
    mst = strg.getMetaStorage()
    tbl = tu.makeTableController("MULTIWELL_PROD_TABLE", strg, mnemos)
    tu.refreshTable2(tbl, ents, strg, err)


    for mnemo in mnemos:
        tcd = dm.tcol_desc(mst, mnemo)
        ftype = tcd.getDataTypeID()
        if ftype==db.ft_num:
            v = cmn.vec_num_t()
            tbl.getDoubles(v, tcd)
            data = numpy.array(v)
            #print(data)
            set_none(data)
            lst.append(data)
        elif ftype==db.ft_date:
            v = cmn.vec_date_t()
            tbl.getDates(v, tcd)
            data = cvt_vdate(v)
            lst.append(data)
        elif ftype==db.ft_string:
            v = cmn.vec_string_t()
            tbl.getStrings(v, tcd)
            data = numpy.array(v, dtype=object)            
            lst.append(data)
        elif ftype==db.ft_int32:
            v = cmn.vec_i32_t()
            tbl.getInts(v, tcd)
            data = numpy.array(v)
            lst.append(data)

    return lst


# --------------------- testing
#if __name__ == '__main__':

    # --------------------------------------
#    bh_id = 23
    
#    ents = dm.entities()
#    ents.append(strg, dm.nt_borehole, bh_id)
    
#    layers = [
#              "PROD_DATE",
#              "OILP", 
#              "WTRP", 
#              "GASP", 
#              "TWRKOIL"]
    
#    lst = get_prod_data(strg, ents, layers)
    
#    nn = len(lst)
    
    ##for kk in range(nn):
    ##    
    ##    v = lst[kk]
    ##    n = len(v)
    ##    print(n)
    ##    for val in v:
    ##        print(val)
    ##
    ##    break
