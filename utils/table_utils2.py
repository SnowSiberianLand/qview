# -*- coding: cp1251 -*-

import sys
import mod_cmn as cmn
import mod_dm as dm
import mod_dmsrv as dmsrv

import data_utils as du
import entity_utils as eu

#typedef layer_holder dmsrv.DataLayerHolder
#typedef layer dmsrv.BaseLayer
#typedef nav dm.NavigatorImpl


# -----------------------------
# make and navigate tables
# -----------------------------

def makeTableController(name, strg, layers = None, rw = False):
    """
    """
    mst = strg.getMetaStorage()

    tdesc = dmsrv.table_description(mst)

    if not dmsrv.findTableDesc(mst, name, tdesc):
        print("table description not found")
        return None

    table = None
    if name == 'COMP_SQUEEZE_TABLE_VIEW':
        table = dmsrv.makeCompletionController(strg, tdesc)
    elif not rw:
        table = dmsrv.makeCommonController(strg, tdesc)
    else:
        table = dmsrv.makeCommonControllerRW(strg, tdesc)

    if table is None:
        print("table controller creation failed")
        return None
        
    if name=="MULTIWELL_PROD_TABLE":
        #сильно ускорит работу по большим месторождениям
        #иначе приводит к тому, что определяется минимальная/максимальная дата по показателям разработки
        #на больших базах это не быстро

        tdesc.m_prod_caps.flt_feature.bShowDateSelector = False 

    baselayers = cmn.vec_wstring_t()
    if layers is None:
        lays = tdesc.def_templates[0].layers
        for lay in lays:
              baselayers.append(lay.lname)
    else:
        for l in layers:
            baselayers.append(l)
    table.makeBaseLayers(baselayers)

    return table

def refreshTable(table, strg, bhlist, pctx=cmn.progress_ctx()):
    """
    """
    ents = dm.entities()    
    vbh = du.to_bh_vec(bhlist)

    ents.append(vbh)
    
    nav = dm.make_navigator(strg, ents)
    terr = cmn.err_info();
    return table.refresh(nav, pctx, terr)

def refreshTable2(table, ents, strg, err):
    """
    """
    strg = table.getDataStorage()
    nav = dmsrv.make_py_navigator_impl()
    nav.assign(strg, ents)
    progress_ctx = cmn.progress_ctx()
    return table.refresh(nav, progress_ctx, err)

def refreshTableWithProgress(table, strg, bhlist, progress_ctx):
    """
    """
    ents = dm.entities()    
    vbh = du.to_bh_vec(bhlist)

    ents.append(vbh)
    
    nav = dm.make_navigator(strg, ents)
    terr = cmn.err_info();
    return table.refresh(nav, progress_ctx, terr)

def refreshTableWithDateRange(tbl, strg, bhlist, dt1, dt2, pctx, err):
    """
    for MSTR_EVENT-based tables
    """
    ents = dm.entities()    
    vbh = du.to_bh_vec(bhlist)
    ents.append(vbh)

    nav = dm.NavigatorImpl();
    safe = dm.safe_entities();
    ents.to_safe(safe);
    nav.append(strg, safe);

    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, "EVENT_DATE")

    var1 = cmn.to_variant(dt1)
    var2 = cmn.to_variant(dt2)

    nav.push_back(pd, var1)
    nav.push_back(pd, var2)
    
    return tbl.refresh(nav, pctx, err)

def refreshTableWithDate(tbl, strg, bhlist, dt,pctx=None):
    """
    for PRODUCTION-based tables
    """
    ents = dm.entities()    
    vbh = du.to_bh_vec(bhlist)
    ents.append(vbh)

    nav = dm.NavigatorImpl();
    safe = dm.safe_entities();
    ents.to_safe(safe);
    nav.append(strg, safe);

    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, "PROD_DATE")

    var = cmn.to_variant(dt)
    
    nav.push_back(pd, var)
    
    if pctx==None:
        pctx = cmn.progress_ctx()
        
    terr = cmn.err_info();
    return tbl.refresh(nav, pctx, terr)

def refreshTableWithDateGtf(tbl, strg, gtf, dt,pctx=None):
    """
    for PRODUCTION-based tables
    """
    ents = dm.entities()    
    #vbh = du.to_bh_vec(bhlist)
    ents.append(gtf)

    nav = dm.NavigatorImpl();
    safe = dm.safe_entities();
    ents.to_safe(safe);
    nav.append(strg, safe);

    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, "PROD_DATE")

    var = cmn.to_variant(dt)
    
    nav.push_back(pd, var)
    
    if pctx==None:
        pctx = cmn.progress_ctx()
        
    terr = cmn.err_info();
    return tbl.refresh(nav, pctx, terr)

def refreshPropTableWithDateRange(tbl, strg, bhlist, dt1, dt2,pctx=None):
    """
    for PRODUCTION-based tables
    """
    ents = dm.entities()    
    vbh = du.to_bh_vec(bhlist)
    ents.append(vbh)

    nav = dm.NavigatorImpl();
    safe = dm.safe_entities();
    ents.to_safe(safe);
    nav.append(strg, safe);

    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, "EXPORT_DATE_RANGE")

    var1 = cmn.to_variant(dt1)
    var2 = cmn.to_variant(dt2)
    
    nav.push_back(pd, var1)
    nav.push_back(pd, var2)

    if pctx==None:
        pctx = cmn.progress_ctx()
    terr = cmn.err_info();
    return tbl.refresh(nav, pctx, terr)

def refreshTableByFilter(table, strg, filter):
    """
    Filter is a dict that contains literals such keys as 'field', 'borehole','reservoir' etc. 
    The values should be used for filtering
    """
    ents = dm.entities()  
    nt_filter = dict()  
    nav = dmsrv.make_py_navigator_impl()
    if 'borehole' in list(filter.keys()):
        nt_filter[dm.nt_borehole] = filter['borehole']

    if 'reservoir' in list(filter.keys()):
        nt_filter[dm.nt_reservoir] = filter['reservoir']

    if 'stratum' in list(filter.keys()):
        nt_filter[dm.nt_stratum] = filter['stratum']

    if 'horizon' in list(filter.keys()):
        nt_filter[dm.nt_horizon] = filter['horizon']

    if 'model' in list(filter.keys()):
        nt_filter[dm.nt_model] = filter['model']

    for key, cond in list(nt_filter.items()):
        # print(key, cond)
        vec = du.to_i32_vec(cond)        
        nav.append(strg, key, vec, False)

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    b = table.refresh(nav, tctx, terr)
    #print b
    return b

def packTable(table):
    res = dict()
    try:
        layer_holder = table.getLayerHolder()
        nrow = table.getRowCount()
        ncol = table.getColCount()

        res['ncol'] = ncol
        res['nrow'] = nrow

        #print("ncol {0}".format(ncol))
        #print("nrow {0}".format(nrow))

        for col in range(ncol):

            pd = table.getPropDesc(0,col)
            if pd is None:
                print("No prop desc bug...")

            res[ "header{0}".format(col) ] = pd.getShortName()
            res[ "unit{0}".format(col) ] = layer_holder.getLayerUnit(col)

            col_list = []
            for row in range(nrow):
                s = table.data(row, col, dmsrv.tdr_display)
                col_list.append(s)

            res[ "cdata{0}".format(col) ] = col_list

        return res
    except:
        print("packTable Failed")
        return res

def getFilteredTable(filter, doc_mnemo, strg):
    res = dict()
    
    try:

        table = makeTableController(doc_mnemo, strg)

        refreshTableByFilter(table, strg, filter)
        res = packTable(table)

        return res
    except:
        print("getFilteredTable Failed")
        return res

def getFilterTemplate(doc_mnemo):
    rules = dmsrv.get_navigate_rules(doc_mnemo)
    res = dict()
    
    if rules is None:
        print("Empty nts for filter template")
        return res
    
    linker = dict()

    linker[dm.nt_borehole] = 'borehole'
    linker[dm.nt_field] = 'field'
    linker[dm.nt_reservoir] = 'reservoir'
    linker[dm.nt_horizon] = 'horizon'
    linker[dm.nt_stratum] = 'stratum'
    linker[dm.nt_model] = 'model'
    
    for rule in rules:
        if rule.nt in list(linker.keys()):
            value = linker[rule.nt]
            res[value] = rule.bMulti


    return res

def getTableTitle(doc_mnemo,strg):
    
    try:
        mst = strg.getMetaStorage()
        tdesc = dmsrv.table_description(mst)

        if not dmsrv.findTableDesc(mst, doc_mnemo, tdesc):
            print(doc_mnemo)
            print("table description not found")
            return ""

        return tdesc.title
    except:
        print("No table data returned")
        return ""

def getTableTitles(strg, mnemos):
    """         
    returns dict <mnemo, title> for table views defined by mnemos
    """

    res = dict()

    for mnemo in mnemos:
        title = getTableTitle(mnemo, strg)
        res[mnemo] = title

    return res

def getTableData(doc_name, strg, bhids):
    """
    returns table data
    used in RV-WEB (updateTableSimple)
    """
    res = dict()
    
    tbl = makeTableController(doc_name, strg)

    bhs = []
    for bhid in bhids:
        bh = eu.find_borehole(strg, bhid)
        if bh is not None:
            bhs.append(bh)

    refreshTable(tbl, strg, bhs)

    return packTable(tbl)

def makeAndRefreshTable(tmnemo, strg, layers, bhlist, rw = False):
    """
    """
    table = makeTableController(tmnemo, strg, layers, rw)
    if table is None:
        return None
    if not refreshTable(table, strg, bhlist):
        return None
    return table


def sortTable(table, *mnemos):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    sort_ctx = table.getSortContext()
    sort_ctx.clear()
    direct = dm.sdir_asc
    for m in mnemos:
        tcd = dm.tcol_desc(dm.getPropertyByMnemo(mst, m))
        sort_ctx.add_col(direct, tcd)
    table.sort_table(True)


# -----------------------------
# access to table data
# -----------------------------

def getInt(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    return table.dataAsInt(pd, cmn.get_undefined_i32(), row)

def getInt2(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    ok, int = table.dataAsInt(pd, cmn.get_undefined_i32(), row)
    if not ok:
        int = cmn.get_undefined_i32()
    return int

def getInts(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    ints = cmn.vec_i32_t()
    ok = table.dataAsInts(pd, cmn.get_undefined_i32(), row, ints)
    return du.from_vec(ints)

def getNum(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    return table.dataAsNum(pd, cmn.get_undefined_i32(), row, None)

def getNum2(mnemo, row, table, unit=None):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    ok, num = table.dataAsNum(pd, cmn.get_undefined_i32(), row, unit)
    if not ok:
        num = cmn.get_undefined_r64()
    return num

def getStr(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    return table.dataAsString(pd, cmn.get_undefined_i32(), row, 2, None)

def getStr2(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    if pd is None:
        print("Can't find property {0}".format(mnemo))
        return ""

    ok, str = table.dataAsString(pd, cmn.get_undefined_i32(), row, 2, None)
    if not ok:
        return ""
    
    return str

def getDate(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    date = cmn.date_t()
    res = table.dataAsDate(pd, cmn.get_undefined_i32(), row, date)
    return res, date

def getDate2(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    date = cmn.date_t()
    ok = table.dataAsDate(pd, cmn.get_undefined_i32(), row, date)
    if not ok:
        date = cmn.get_undefined_date()
    return date


def getXlsDateNum(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
##    print type(pd), pd
##    print type(sys.maxint), sys.maxint
##    print type(row), row
    num = table.dataAsXlsDate(pd, cmn.get_undefined_i32(), row)
    return num

def updateAggregationMode4Col(mnemo, table, mode):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)

    layer_holder = table.getLayerHolder()
    n = layer_holder.getLayerCount()

    for i in range(n):
        layer = layer_holder.getLayer(i)
        if (layer.getColDesc().prop == pd):
            layer.setAggregationMode(mode)
            break
