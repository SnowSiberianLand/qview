# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv

import data_utils as du
import entity_utils as eu
import table_utils as tu
import range_utils as ru

import math
import operator

#typedef bh dm.IBorehole
#typedef cdata dm.ICompletionData
#typedef citems dm.ICompletionItems
#typedef citem dm.ICompletionItem
#typedef iitems dm.IIsolationItems
#typedef iitem dm.IIsolationItem
#typedef ents dm.entities
#typedef tbl dmsrv.TableControllerBase

def put_changes(cdata):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return cdata.save(tctx, terr)
    
def get_completions(bh):
    """
    returns completion data for given borehole
    """
    if bh is None:
        return None

    strg = bh.getDMO().getDataStorage()
    if strg is None:
        return None
    
    cdata = dm.ICompletionData.make(dm.db_caching, dm.cat_completion_events)
    if cdata is None:
        return None

    bhid = bh.getID()

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    b = cdata.load(strg, bhid, tctx, terr)
    if b==False:
        return None

    return cdata

def del_all_perfs(cdata):
    if cdata is None:
        return False
    
    citms = cdata.completions()
    if citms is None:
        return False

    citms.delAll()
    return True

def perf_count(cdata):
    if cdata is None:
        return 0

    citems = cdata.completions()
    if citems is None:
        return 0
    
    return citems.size()

def del_perf_by_ind(cdata, ind):
    if cdata is None:
        return False

    citems = cdata.completions()
    if citems is None:
        return False
    
    citm = citems.at(ind)
    
    return citems.deleteCompletion(citm)

def append_perf(cdata, top_md, base_md, dt):
    """
    append new perforation interval cdata    
    returns new completion item
    """
   
    if cdata is None:
        return None
    
    citms = cdata.completions()
    if citms is None:
        return None

    citm = citms.appendCompletion(dm.ct_perforation, dt, cmn.get_undefined_i32(), top_md, base_md)
    return citm

def append_isol(cdata, top_md, base_md, dt):
    """
    append new isolation interval cdata    
    returns new isolation item
    """
   
    if cdata is None:
        return None
    
    iitems = cdata.isolations()
    if iitems is None:
        return None

    itm = iitems.appendIsolation(dt, cmn.get_undefined_i32(), top_md, base_md)
    return itm

def del_all_isols(cdata):
    if cdata is None:
        return False
    
    iitems = cdata.isolations()
    if iitems is None:
        return False

    iitems.delAll()
    return True

def isol_count(cdata):
    if cdata is None:
        return 0

    iitems = cdata.isolations()
    if iitems is None:
        return 0
    
    return iitems.size()

def del_isol_by_ind(cdata, ind):
    if cdata is None:
        return False

    iitems = cdata.isolations()
    if iitems is None:
        return False
    
    iitm = iitems.at(ind)
    
    return iitems.deleteIsolation(iitm)

def get_stratums(top_md, base_md, tbl):
    lst = []
    nrow = tbl.getRowCount()
    for i in range(nrow):
        model_id = tu.getInt2("MODEL_ID", i, tbl)
        layer_id = tu.getInt2("GEOLAYER_ID", i, tbl)
        ztop_md = tu.getNum2("LAYER_TOP_MD", i, tbl)
        zbase_md = tu.getNum2("LAYER_BASE_MD", i, tbl)

#        print(layer_id, model_id, top_md, base_md)
    
        #ok = du.intersects(top_md, base_md, ztop_md, zbase_md)
        ll = du.intersection_length(top_md, base_md, ztop_md, zbase_md)
        if ll and ll>=0.1: # 10 cm
            lst.append(layer_id)
            
    return lst


class depth_intvl:
    def __init__(self):    
        self.top_md      = None
        self.base_md     = None

    def __str__(self):
        return '{0:.1f}-{1:.1f}'.format(self.top_md,self.base_md)

class event_item:
    def __init__(self):    
        self.dt4sort     = None      # python's date for sorting    
        self.dt          = None      # date_t
        self.bOpen       = 1
        self.top_md      = None
        self.base_md     = None

    def __str__(self):
        return '{0}, {1:.1f}-{2:.1f}, {3}'.format(self.dt4sort,self.top_md,self.base_md,self.bOpen)

class state_item:
    """
    описывает состояние на дату (после события)
    """
    def __init__(self):    
        self.bh_id       = None
        self.dt4sort     = None      # python's date for sorting
        self.dt          = None      # date_t
        self.lst_intv    = []        # open intervals, MD top/base in tuple
        self.ids         = set()        
        self.strg        = None
    
    def __str__(self):

        sbh = eu.node_names(self.strg, dm.nt_borehole, [self.bh_id])
        
        s = '{0}; {1}'.format(sbh, self.dt4sort)
        s = s + '; '
        
        for i in range(len(self.lst_intv)):
            if (i!=0):
                s = s + ', '
                
            s = s + '{0:.1f}-{1:.1f}'.format(self.lst_intv[i][0],self.lst_intv[i][1])

        lst = []
        for id in self.ids: lst.append(id)

        #ts = str(self.ids)
        ts = eu.node_names(self.strg, dm.nt_stratum, lst)
        if len(ts)!=0:
            s = s + '; '
            s = s + ts
                
        return s

class res_item:
    """
    структура для результата
    """
    def __init__(self):    
        strg     = None
        bh_id    = None    # borehole id
        lay_id   = None   # stratum id
        dt_open  = None   # open date
        dt_close = None   # close date
    
    def __str__(self):

        sbh = eu.node_names(self.strg, dm.nt_borehole, [self.bh_id])
        slay = eu.node_names(self.strg, dm.nt_stratum, [self.lay_id])

        sdt1 = ''
        if self.dt_open is not None:
            sdt1 = '{0}.{1:0>2d}.{2:0>2d}'.format(self.dt_open.year,self.dt_open.month,self.dt_open.day)

        sdt2 = ''
        if self.dt_close is not None:
            sdt2 = '{0}.{1:0>2d}.{2:0>2d}'.format(self.dt_close.year,self.dt_close.month,self.dt_close.day)
        
        return '{0}, {1}, {2}-{3}'.format(sbh, slay, sdt1, sdt2)


def get_completions_intervals(cdata):
    """
    returns list of depth_intvl (completion intervals only)
    """

    out = []

    #perforations
    citems = cdata.completions();
    nitem = citems.size()
    for i in range(nitem):
        citem = citems.at(i)

        itm = depth_intvl()
        itm.top_md  = citem.getTopMD()
        itm.base_md = citem.getBaseMD()
        out.append(itm)

    return out

def make_events(bh_id, cdata):
    """
    makes sorted list of event_item
    """

    out = []

    #perforations
    citems = cdata.completions();
    nitem = citems.size()
    for i in range(nitem):
        citem = citems.at(i)

        itm = event_item()
        itm.dt      = citem.getDate()
        itm.dt4sort = du.from_date_t(itm.dt)
        itm.top_md  = citem.getTopMD()
        itm.base_md = citem.getBaseMD()
        itm.bOpen = 1

        out.append(itm)

    #isolations
    iitems = cdata.isolations();
    nitem = iitems.size()
    for i in range(nitem):
        iitem = iitems.at(i)

        itm = event_item()
        itm.dt      = iitem.getDate()
        itm.dt4sort = du.from_date_t(itm.dt)
        itm.top_md  = iitem.getTopMD()
        itm.base_md = iitem.getBaseMD()
        itm.bOpen = 0

        out.append(itm)

    out = sorted(out, key=operator.attrgetter('dt4sort', 'bOpen'))
    return out

def make_states(bh_id, events, ctx):
    """
    make states from perforation and isolation events
    """

    min_thickness = 0.1 # мин толщина интервалов, интервалы с толщиной<min_thickness не учитываются в результате

    states = []
    intvs = []
    
    n = len(events)
    for i in range(n):
        ev = events[i]

        itm = state_item()
        itm.bh_id = bh_id
        itm.strg = ctx.pStorage
        itm.dt = ev.dt
        itm.dt4sort = ev.dt4sort

        if (ev.bOpen==1):
            itm.lst_intv = ru.interval_or(intvs, ev.top_md, ev.base_md)            
        else:
            itm.lst_intv = ru.interval_subtract(intvs, ev.top_md, ev.base_md, min_thickness)

        intvs = list(itm.lst_intv)
        
        states.append(itm)
        
    return states
    
def bind2stratums(states, tbl):
    """
    формируем для каждого состояния набор пластов в соответствии с вскрытыми интервалами
    """

    n = len(states)
    for i in range(n):
        st = states[i]

        all_ids = set()
        for intv in st.lst_intv:
            ids = get_stratums(intv[0], intv[1], tbl)

            for id in ids:
                all_ids.add(id)
                
        st.ids = all_ids

def make_results(bh_id, states, lay_ids, ctx):
    """
    формируем набор сочетаний скважина/пласт/интервал работы по списку состояний
    """

    out = []

##    for st in states:
##        print(st)
    
    for lay_id in lay_ids:

        dt_open = None
        dt_close = None
        
        for st in states:
            
            if (dt_open is None) and (lay_id in st.ids):
                dt_open = st.dt4sort
                continue

            if (dt_open is None):
                continue

            if (lay_id not in st.ids):
                dt_close = st.dt4sort

                itm = res_item()
                itm.strg = ctx.pStorage
                itm.bh_id = bh_id
                itm.lay_id = lay_id
                itm.dt_open = dt_open
                itm.dt_close = dt_close

                out.append(itm)

                dt_open = None
                dt_close = None


        if (dt_open is not None): # открытый интервал

            itm = res_item()
            itm.strg = ctx.pStorage
            itm.bh_id = bh_id
            itm.lay_id = lay_id
            itm.dt_open = dt_open
            itm.dt_close = dt_close
            
            out.append(itm)
            
            dt_open = None
            dt_close = None
        
    return out
        
    
def get_stratums_from_states(states):
    """
    получим все задействованные в состояниях пласты
    """

    all_ids = set()

    n = len(states)
    for i in range(n):
        st = states[i]

        for id in st.ids:
            all_ids.add(id)

    return all_ids

def get_stratum_ids(items):
    """
    items - list(res_item)
    """

    all_ids = set()

    for itm in items:
        all_ids.add(itm.lay_id)

    return all_ids

##def get_stratum_ids(dd):
##    """
##    dd - dict(bh_id, list(state_item))
##    """
##
##    all_ids = set()
##
##    keys = dd.keys()
##    for key in keys:
##        lst = dd.get(key)
##        ids = get_stratums_from_states(lst)
##
##        for id in ids:
##            all_ids.add(id)
##
##    return all_ids

# ----------------------------------------
# загрузка интервалов, в которых когда-либо делалась перфорация
def load_completion_intervals(ctx, res, bh_id):

    #print("Borehole id:", bh_id)

    sbh = eu.node_names(ctx.pStorage, dm.nt_borehole, [bh_id])

    # loading completion data
    tctx = cmn.progress_ctx()
    dthlp = dm.getDataProcessing().getDataTreatHelper() 
    cdata = dthlp.makeCompletionData(dm.db_caching, dm.cat_completion_events)
    borehole = cdata.load(ctx.pStorage, bh_id, tctx, res.err)

    out = []
    
    citems = cdata.completions()
    nitem = citems.size()
    if nitem == 0:
        s = _("Borehole {0}, No log interpretation data").format(sbh)
        #res.add_warning(s)
        dmsrv.py_log_warn(ctx.opo.logger(), s)
        return out

    out = get_completions_intervals(cdata)
    out = sorted(out, key=operator.attrgetter('top_md', 'base_md'))
    return out

# ----------------------------------------
# обработка скважины
def process_borehole(bh_id, ctx, res):
    #print("Borehole id:", bh_id)

    sbh = eu.node_names(ctx.pStorage, dm.nt_borehole, [bh_id])

    # loading completion data
    tctx = cmn.progress_ctx()
    dthlp = dm.getDataProcessing().getDataTreatHelper()    
    cdata = dthlp.makeCompletionData(dm.db_caching, dm.cat_completion_events)
    b = cdata.load(ctx.pStorage, bh_id, tctx, res.err)

    citems = cdata.completions()
    nitem = citems.size()
    if nitem == 0:
        res.add_warning(_("Borehole {0}, No completion data").format(sbh) )
        return []
        
    #loading zone picks
    wo_stratums = False
    rw = False
    layers = ["MODEL_ID", "GEOLAYER_ID", "LAYER_TOP_MD", "LAYER_BASE_MD"]
    tbl = tu.makeWellpicksTable2("ZONEPICK_TABLE_VIEW", ctx, layers, bh_id, res, rw, wo_stratums)
    
    if tbl is None:
        res.add_error(_("Error getting zonepicks data"))
        return False
        
    events = make_events(bh_id, cdata)

##    for ev in events:
##        print(str(ev))
    
    states = make_states(bh_id, events, ctx)

    bind2stratums(states, tbl)

    lay_ids = get_stratums_from_states(states)
    
    out = make_results(bh_id, states, lay_ids, ctx)
    
    return out

#testing

if __name__ == '__main__':

    import os
    import db_utils

    import builtins
    builtins.__dict__['_'] = lambda s : s

    #cmn.app_init_paths(os.path.abspath('../../../../../build/win64/bin/release/'))
    db.init_loggers()
    dproc.init_lib_dproc()

    ctx = dmsrv.python_ctx()
    res = dmsrv.python_results()

    #ctx.pStorage = db_utils.make_DataStorage(db.db_oracle, "rdm/1@agava64", "meta/1@agava64")
    ctx.pStorage = db_utils.make_DataStorage(db.db_sqlite, "c:/db/demo.rds")
    if ctx.pStorage is None:
        print("DataStorage creation fails")

    #print("Connected to db")

    #raw_input("Press Enter to continue")
        
    ok = True
    ctx.clear()
    res.clear()
    ctx.model_id = 1
    
    ctx.ents.fill_certain_nodes(ctx.pStorage, dm.nt_stratum)
    ctx.ents.append(ctx.pStorage, dm.nt_model, 1)

    all_items = []
    bhids = [14,1,2,3,4,5]

    for bh_id in bhids:
        tmp = process_borehole(bh_id, ctx, res)
        all_items = all_items + tmp
        
    stids = get_stratum_ids(all_items)
    print(stids)

    for itm in all_items:
        print(str(itm))
