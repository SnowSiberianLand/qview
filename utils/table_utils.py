# -*- coding: cp1251 -*-

import sys
import mod_cmn as cmn
import mod_dm as dm
import mod_dmsrv as dmsrv
import mod_orm as db
import data_utils as du


def makeCommonTable(name, ctx, layers, py_res, rw = False, refresh = False):
    """
    """
    mst = ctx.pStorage.getMetaStorage()
    tdesc = dmsrv.table_description(mst)
    if not dmsrv.findTableDesc(mst, name, tdesc):
        py_res.err = cmn.err_info.interr(_("\"{0}\" table description not found").format(name))
        return None

    table = None
    if name == 'COMP_SQUEEZE_TABLE_VIEW':
        table = dmsrv.makeCompletionController(ctx.pStorage, tdesc)
    elif not rw:
        table = dmsrv.makeCommonController(ctx.pStorage, tdesc)
    else:
        table = dmsrv.makeCommonControllerRW(ctx.pStorage, tdesc)

    if table is None:
        py_res.err = cmn.err_info.interr(_("\"{0}\" common controller creation fails").format(name))
        return None

    baselayers = cmn.vec_wstring_t()
    if layers is None:
        lays = tdesc.def_templates[0].layers
        for lay in lays:
              baselayers.append(lay.lname)
    else:
        for l in layers:
            baselayers.append(l)
    table.makeBaseLayers(baselayers)

    if refresh:
        nav = dmsrv.make_py_navigator(ctx, ctx.ents)
        progress_ctx = cmn.progress_ctx()
        b = table.refresh(nav, progress_ctx, py_res.err)
        if not b:
            return None

    return table


def refreshBoreholeTable(table, borehole_id, py_ctx, py_res):
    """
    """
    local_ents = dm.entities(py_ctx.ents)
    local_ents.exclude(dm.nt_borehole)
    local_ents.exclude(dm.nt_well)
    local_ents.append(py_ctx.pStorage, dm.nt_borehole, borehole_id)
    nav = dmsrv.make_py_navigator(py_ctx, local_ents)
    progress_ctx = cmn.progress_ctx()
    return table.refresh(nav, progress_ctx, py_res.err)

def refreshBoreholeTable2(table, borehole_id, py_ctx, rcs, py_res):
    """
    """
    local_ents = dm.entities(py_ctx.ents)
    local_ents.exclude(dm.nt_borehole)
    local_ents.exclude(dm.nt_well)
    local_ents.append(py_ctx.pStorage, dm.nt_borehole, borehole_id)
    nav = dmsrv.make_py_navigator(py_ctx, local_ents)
    progress_ctx = cmn.progress_ctx()
    return table.refresh(nav, rcs, progress_ctx, py_res.err)


def refreshWellpicksTable(table, borehole_id, py_ctx, py_res, wo_stratums):
    """
    формирование таблицы zonepicks/wellpicks
    без фильтра по моделям
    наличие фильтра по пластам - опция
    """
    local_ents = dm.entities(py_ctx.ents)
    local_ents.exclude(dm.nt_borehole)
    local_ents.exclude(dm.nt_well)
    local_ents.exclude(dm.nt_model)
    local_ents.exclude(dm.nt_stratum)
    local_ents.append(py_ctx.pStorage, dm.nt_borehole, borehole_id)

    nodes = dm.vec_node_t()
    dm.from_safe_nodes(py_ctx.pStorage, py_ctx.wellpicks, nodes);
    local_ents.append_vec_node(py_ctx.pStorage, nodes)

    if wo_stratums:
        local_ents.exclude(dm.nt_stratum)

    if len(local_ents.horizons())==0:
        local_ents.complete(py_ctx.pStorage, dm.nt_stratum, dm.nt_horizon)
       
    nav = dmsrv.make_py_navigator(py_ctx, local_ents)
    progress_ctx = cmn.progress_ctx()
    return table.refresh(nav, progress_ctx, py_res.err)

def refreshWellpicksTable2(table, borehole_id, py_ctx, py_res, wo_stratums):
    """
    то же самое но с фильтром по моделям
    """
    local_ents = dm.entities(py_ctx.ents)
    local_ents.exclude(dm.nt_borehole)
    local_ents.exclude(dm.nt_well)
    local_ents.append(py_ctx.pStorage, dm.nt_borehole, borehole_id)

    nodes = dm.vec_node_t()
    dm.from_safe_nodes(py_ctx.pStorage, py_ctx.wellpicks, nodes);
    local_ents.append_vec_node(py_ctx.pStorage, nodes)

    if wo_stratums:
        local_ents.exclude(dm.nt_stratum)

    if len(local_ents.horizons())==0:
        local_ents.complete(py_ctx.pStorage, dm.nt_stratum, dm.nt_horizon)

    #print len(py_ctx.wellpicks)
    
    nav = dmsrv.make_py_navigator(py_ctx, local_ents)
    progress_ctx = cmn.progress_ctx()
    return table.refresh(nav, progress_ctx, py_res.err)

def makeBoreholeTable(name, py_ctx, layers, borehole_id, py_res, rw = False, bRefresh = True):
    """
    """
    table = makeCommonTable(name, py_ctx, layers, py_res, rw)
    if table is None:
        return None

    if bRefresh:
        b = refreshBoreholeTable(table, borehole_id, py_ctx, py_res)
        if False==b:
            return None
        
    return table


def makeBoreholeTable2(name, py_ctx, rcs, layers, borehole_id, py_res, rw = False):
    """
    """
    table = makeCommonTable(name, py_ctx, layers, py_res, rw)
    if table is None:
        return None
    if not refreshBoreholeTable2(table, borehole_id, py_ctx, rcs, py_res):
        return None
    return table


def makeWellpicksTable(name, py_ctx, layers, borehole_id, py_res, rw = False, wo_stratums = False):
    """
    """
    table = makeCommonTable(name, py_ctx, layers, py_res, rw)
    if table is None:
        return None
    if not refreshWellpicksTable(table, borehole_id, py_ctx, py_res, wo_stratums):
        return None
    return table

def makeWellpicksTable2(name, py_ctx, layers, borehole_id, py_res, rw = False, wo_stratums = False):
    """
    то же самое но с фильтром по моделям
    """
    table = makeCommonTable(name, py_ctx, layers, py_res, rw)
    if table is None:
        return None
    if not refreshWellpicksTable2(table, borehole_id, py_ctx, py_res, wo_stratums):
        return None
    return table

def hasProps(table, props, res = None):
    """
    """
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    
    pdescs = dm.vec_property_desc()
    for p in props:
        pdescs.append(dm.getPropertyByMnemo(mst, p))
    ok = table.has_properties(pdescs)
    if not ok and res:
        res.add_error(_("TableController {0} doesn't contain requested properties {1}").format(table.getTableMnemo(), props))
    return ok


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

def getNum2(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    ok, num = table.dataAsNum(pd, cmn.get_undefined_i32(), row, None)
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
    ok, str = table.dataAsString(pd, cmn.get_undefined_i32(), row, 2, None)
    if not ok:
        str = "err"
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

def getBlobAsFloats(mnemo, row, table):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    tcol = dm.tcol_desc(pd, cmn.get_undefined_i32())
    data = cmn.vec_num_t()
    ok = table.blobDataAsFloats(tcol, row, data)
    return ok, data


def setValue(val, mnemo, row, table, bUserChanges = True):
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    tcd = dm.tcol_desc(pd)
    v = dmsrv.make_variant(val)
    ed = table.getTableEditor()
    bEmit = False
    ed.putValue(row, tcd, v, bEmit, bUserChanges)


def addNewRow(table):
    te = table.getTableEditor()
    idx = te.addNewLine(True)
    return idx


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


def sortTable2(table, *tuples):
    """
    Sort table by list of tuples (mnemo, direction)
    """
    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    sort_ctx = table.getSortContext()
    sort_ctx.clear()
    for t in tuples:
        tcd = dm.tcol_desc(dm.getPropertyByMnemo(mst, t[0]))
        sort_ctx.add_col(t[1], tcd)
    table.sort_table(True)


def getFilteredRows(table, filters):
    strg = table.getDataStorage()

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    mst = strg.getMetaStorage()
    cond_group = dm.prop_cond_group(strg,mst)
    i = 0
    for f in filters:
        mnemo = f[0]
        cond_type = f[1]
        expr = f[2]
        pd = du.get_property_desc(strg, mnemo)
        cond_group.add_filter(pd, cond_type, expr, i)
        i = i + 1
    cond_group.parse()

    find_ctx = dmsrv.find_context()
    find_ctx.rtype = dmsrv.find_context.rt_valid
    find_ctx.ctrl = table
    find_ctx.flts = cond_group
    find_ctx.startFrom = 0
    rowcount = table.getRowCount()
    for i in range(rowcount):
        find_ctx.active.append(i)

    row_indices = cmn.vec_i32_t()
    dmsrv.find_all(find_ctx, row_indices, tctx, terr)

    return row_indices


def getDistinctColumn(mnemo, table):
    """
    returns cmn.set<T> for given column
    """
    data = None

    strg = table.getDataStorage()
    mst = strg.getMetaStorage()
    
    pd = dm.getPropertyByMnemo(mst, mnemo)
    if pd is None:
        return False, data

    #integer, numeric, date types allowed
    if pd.getDataTypeID() == db.ft_int32:
        data = cmn.set_i32_t()
    elif pd.getDataTypeID() == db.ft_num or pd.getDataTypeID() == db.ft_num:
        data = cmn.set_num_t()
    elif pd.getDataTypeID() == db.ft_date:
        data = cmn.set_date_t()

    if data is None:
        return False, data

    index = table.getColNum(pd, "")
    ok = table.get_distinct_column(index, data)
    return ok, data
    
def getLayers(strg, mnemos, tctrl, ctx, res):
    layers = ''
    
    mh = strg.getMetaHelper()
    prop_reg = mh.getPropRegistry()

    vpd = dm.vec_property_desc()
    tctrl.getLayerProps(vpd)

    for mnemo in mnemos:
        pd = prop_reg.findByMnemo(mnemo)

        if pd not in vpd:
            layers+=mnemo
            layers+=','
            
            s = 'Добавлен слой информации "{0}".'.format(pd.getShortName(1))
            res.add_warning(s)
            dmsrv.py_log_warn(ctx.opo.logger(), s)

    return layers
    
    
def createControllerByMnemo(strg, mnemo, baselayers):
    mst = strg.getMetaStorage()
    tdesc = dmsrv.table_description(mst)
    
    if not dmsrv.findTableDesc(mst, mnemo, tdesc):
        print("Table {0} description not found").format(mnemo)
        return None
    
    table = None
    if mnemo == 'COMP_SQUEEZE_TABLE_VIEW':
        table = dmsrv.makeCompletionController(strg, tdesc)
    else:
        table = dmsrv.makeCommonControllerRW(strg, tdesc)
    
    if table is None:
        print("Table controller creation failed")
        return None
        
    if mnemo == "MULTIWELL_PROD_TABLE":
        tdesc.m_prod_caps.flt_feature.bShowDateSelector = False
     
    vtcd = dm.vec_tcol_desc()
    table.getAllProps(vtcd)

    vtcd2 = dm.vec_tcol_desc()
    dlh = table.getLayerHolder()
    dlh.getAllLayers(vtcd2)

    for tcd in vtcd2:
        if not tcd in vtcd:
            vtcd.append(tcd)

    stcd = dm.set_tcol_desc()
    table.tableDesc().getProperties(stcd)
    for tcd in stcd:
        if not tcd in vtcd:
            vtcd.append(tcd)

    lays = vtcd
    for lay in lays:
        if (not lay.prop.getMnemo() in baselayers):
            baselayers.append(lay.prop.getMnemo())
    table.makeBaseLayers(baselayers)
    
    return table
    
def tableNullValuesCheck(ctx, table, baselayers, nulls, res):
    # nulls - возможные нулевые значения
    if not table is None:
        nrow = table.getRowCount() - 1
        for l in baselayers: # пробегаем по всем столбцам
            print (l)
            x = dm.getPropertyByMnemo(ctx.pStorage.getMetaStorage(), l) # берем property столбца
            warnings = []
            if x.getDataTypeID() in [2, 6]: # проверяем тип данных int32 or int64
                for i in range(nrow):
                    t = getInt(l, i, table)
                    if t in nulls:
                        warnings.append(du.property2str(ctx.pStorage, l))
            elif x.getDataTypeID() == 0: # float
                for i in range(nrow):
                    t = getNum2(l, i, table)
                    if t in nulls:
                        warnings.append(du.property2str(ctx.pStorage, l))

            if len(warnings) > 0:
                print (("{0} - {1}").format(l, len(warnings))) 
                res.add_warning(_("Column \"{0}\" has null value").format(du.seq2str(warnings)))
    return True        



class TableFilter:
    def  __init__(self, py_ctx):
        self.visible_rows = set()
        self.bUseFilter = False
        
        for irow in py_ctx.vftri:
            self.visible_rows.add(irow)

        if len(self.visible_rows)>0:
            self.bUseFilter = True

    def rowVisible(self, row):
        if self.bUseFilter == False:
            return True

        if row in self.visible_rows:
            return True

        return False
            
