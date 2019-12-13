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

def get_bhstat_data_lists(strg, bhs, mnemos, progress):

    mst = dm.getMetaStorage(strg)
    
    dic = get_bhstat_data(strg, bhs, mnemos, progress)
    names = []
    vals = []
    
    for key in dic:
        val = dic[key]

        name = key
        mnemo = key
        pd = dm.getPropertyByMnemo(mst, mnemo)
        if pd is not None:
            name = pd.getName()
            
        names.append(name)
        vals.append(val)

    zipped = zip(names, vals)
    lst = sorted(zipped, reverse=True)

    n = len(lst)
    for k in range(n):
        itm = lst[k]
        names[k] = itm[0]
        vals[k]  = itm[1]
        
    return names, vals

def get_bhstat_data(strg, bhs, mnemos, progress):
    """
    возвращает dict mnemo-int в соответствии с переданными мнемониками
    кол-во скважин в которых есть данные данного типа
    """
    ret = dict()

    sub = progress.sub_task(30)
    # создаем табличный контроллер
    tbl = tu.makeTableController("WELL_STAT_VIEW", strg, mnemos)
    if tbl is None:
        print("Can't make or refresh table controller")
    sub = cmn.progress_ctx()

    # читаем данные и обновляем таблицу
    sub = progress.sub_task(60)    
    tu.refreshTable(tbl, strg, bhs, sub)
    sub = cmn.progress_ctx()
    
    if len(mnemos)==0:
        vtcd = dm.vec_tcol_desc()
        tbl.getAllProps(vtcd)
       
        for tcd in vtcd:
            mnemo = tcd.prop.getMnemo()
            if mnemo=='BOREHOLE_ID':
                continue
            mnemos.append(mnemo)

    tbl.makeBaseLayers(du.to_str_vec(mnemos))
        
    nrow = tbl.getRowCount()
    ncol = tbl.getColCount()

    ss = ""
    for j in range(ncol):
        mnemo = tbl.header(j)

        tcnt = 0
        
        for i in range(nrow):
            cnt = int(tbl.data(i,j,dmsrv.tdr_raw)) #tdr_raw - так как нужны цыфры а не "плюсики"
            if cnt>0:
                tcnt += 1

        ret[mnemo] = tcnt

    return ret
