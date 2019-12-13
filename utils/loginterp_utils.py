# -*- coding: cp1251 -*-

import sys

import mod_dmsrv as dmsrv
import mod_dm as dm
import mod_orm as db
import mod_cmn as cmn
import mod_dproc as dproc

import data_utils as du
import entity_utils as eu
import table_utils2 as tu
import table_utils as tu2
import perf_utils as pu

import math
import operator
import random

from collections import namedtuple

#typedef lda dm.ILogData

#typedef runs dm.ILogRuns
#typedef run dm.ILogRun

#typedef frames dm.ILogFrames
#typedef frame dm.ILogFrame

#typedef crv dm.ILogCurve
#typedef ents dm.entities
#typedef tbl dmsrv.TableControllerBase

class helper:
    """
    helper for getting log interpretation data by <bh, mdl>
    """

    def __init__(self, _bh, _mdl):
        self.bh    = _bh
        self.mdl   = _mdl

        strg = _bh.getDMO().getDataStorage()
        self.lda = get_loginterp_data(strg, _bh, _mdl)

    def get_first_frame(self):
        frames = self.lda.frames()
        n = frames.size()
        if 0==n:
            return None

        return frames.at(0)

    def npoint(self):
        frame = self.get_first_frame()
        if frame is None:
            return 0

        return frame.getNpoint()
    
    def get_curve(self, mnemo):
        """
        mnemo means property mnemo
        """
        frame = self.get_first_frame()
        if frame is None:
            return None

        crv = frame.curveByMnemo(mnemo)
        
        return crv

    def get_curve_data(self, mnemo):
        """
        mnemo means property mnemo
        """
        crv = self.get_curve(mnemo)
        if crv is None:
            return None

        if crv.data_type()==dm.ldt_float:
            vec = crv.fdata()
            return self.get_data_impl(vec)
        elif crv.data_type()==dm.ldt_integer:
            vec = crv.idata()
            return self.get_data_impl(vec)
        elif crv.data_type()==dm.ldt_string:
            vec = crv.sdata()
            return self.get_data_impl(vec)
        return None
    
    def get_data_impl(self, vec):
        if vec is not None:
            lst = du.from_vec(vec)
            return lst
        else:
            return None

    def top_md(self):
        frame = self.get_first_frame()
        if frame is None:
            return None

        vec = frame.topMdVec()
        if vec is None:
            return None
        
        return self.get_data_impl(vec)

    def base_md(self):
        frame = self.get_first_frame()
        if frame is None:
            return None

        vec = frame.baseMdVec()
        if vec is None:
            return None

        return self.get_data_impl(vec)

    def top_tvd(self):
        frame = self.get_first_frame()
        if frame is None:
            return None

        vec = frame.topTvdVec()
        if vec is None:
            return None
        
        return self.get_data_impl(vec)

    def base_tvd(self):
        frame = self.get_first_frame()
        if frame is None:
            return None

        vec = frame.baseTvdVec()
        if vec is None:
            return None
        
        return self.get_data_impl(vec)

    def lito(self):
        return self.get_curve_data('LR_LITO')

    def tsat(self):
        return self.get_curve_data('LR_TSAT')

    def poro(self):
        return self.get_curve_data('LR_PORO')

    def perm(self):
        return self.get_curve_data('LR_PERM')

    def soil(self):
        return self.get_curve_data('LR_OGSAT')


## -----------------------------------------------

def put_changes(lda):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return lda.save(tctx, terr)

def append_lito(frame, arr):
    return append_int_curve(frame, "LR_LITO", arr)

def append_tsat(frame, arr):
    return append_int_curve(frame, "LR_TSAT", arr)

def append_poro(frame, arr):
    return append_num_curve(frame, "LR_PORO", "frac.", arr)

def append_perm(frame, arr):
    return append_num_curve(frame, "LR_PERM", "mD", arr)

def append_soil(frame, arr):
    return append_num_curve(frame, "LR_OGSAT", "frac.", arr)


def clone_loginterp(lda, mdl1, mdl2):
    """
    clones logrun associated with mdl1 to new logrun associated with mdl2
    """
    runs = lda.runs()
    run = runs.findFirstByModel(mdl1.getID())
    if run is None:
        return None
    
    run2 = run.clone()
    run2.setModelID(mdl2.getID())

    return run2

def append_int_curve(frame, mnemo, _arr):
    if type(_arr)==type(list()):
        arr = du.to_int_vec(_arr)
    else:
        arr = _arr

    n = len(arr)
    if n!=frame.getNpoint():
        return None

    lda = frame.logData()
    strg = lda.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    
    crv = frame.appendCurve(pd,None)
    crv.set_data_type(dm.ldt_integer)
    crv.setData(arr)
    return crv

def append_num_curve(frame, mnemo, units, _arr):
    """
    appends numeric (float) curve with given mnemo and units
    """
    if type(_arr)==type(list()):
        arr = du.to_double_vec(_arr)
    else:
        arr = _arr

    n = len(arr)
    if n!=frame.getNpoint():
        return None

    lda = frame.logData()
    strg = lda.getDataStorage()
    mst = strg.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    ud = dm.getUnitByMnemo(mst, units)
    
    crv = frame.appendCurve(pd,ud)
    crv.set_data_type(dm.ldt_float)
    crv.setData(arr)
    return crv

def append_frame(lda, bh, mdl, lst_top, lst_base):
    """
    appends new log interpretation run and frame
    """
    if bh is None:
        return None
    bhid = bh.getID()

    if mdl is None:
        return None
    mdl_id = mdl.getID()

    runs = lda.runs()
    
    run = runs.appendLogRun(bhid, dm.lt_log_interp)
    run.setModelID(mdl_id)
    
    frames = lda.frames()

    if type(lst_top)==type(list()):
        vtop = du.to_double_vec(lst_top)
    else:
        vtop = lst_top

    if type(lst_base)==type(list()):
        vbase = du.to_double_vec(lst_base)
    else:
        vbase = lst_base

    frame = frames.appendIntervalFrame(run.getID(), vtop, vbase)
    return frame

def get_loginterp_data(strg, bh, mdl):
    mst = strg.getMetaStorage()    
    lda = dm.ILogData.make(strg, dm.db_caching, dm.cat_logresults)
    if lda is None:
        return None
        
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    
    b = lda.load(strg, bh.getID(), mdl.getID(), tctx, terr)
    return lda

class loginterp_intvl:
    def __init__(self):    
        self.top_md      = None
        self.base_md     = None
        self.saturation  = None
        self.lithotype   = None
        self.Kporo       = None
        self.Kpr         = None
        self.Ksut        = None
        self.top_tvd     = None
        self.base_tvd    = None
        self.stratum     = None
        self.stratumX    = None
        self.stratumY    = None

    def __str__(self):
        return '{0:.1f}-{1:.1f}, {2}, {3}, {4:.2f}, {5:.2f}, {6:.2f}'.format(self.top_md,self.base_md,self.saturation, self.lithotype, self.Kporo, self.Kpr, self.Ksu)

#typedef model_ids cmn.set_i32_t
def getStratumAndCoord(lda, top_md, bot_md, ctx, res):

    bh_id = lda.boreholeId()
    model_ids = cmn.set_i32_t()
    lda.getModelIds(model_ids)

    if len(model_ids) > 1:
        res.add_error(_("Too much models in logdata"))
        return None, None, None

    if len(model_ids) < 1:
        res.add_error(_("Model of logdata is undefined"))
        return None, None, None

    wo_stratums = False
    rw = False
    layers = ["MODEL_ID", "GEOLAYER_ID", "LAYER_TOP_MD", "LAYER_BASE_MD", "LAYER_TOP_CX", "LAYER_TOP_CY", "GEOLAYER_ID"]
    tbl = tu2.makeWellpicksTable2("ZONEPICK_TABLE_VIEW", ctx, layers, bh_id, res, rw, wo_stratums)

    if tbl is None:
        res.add_error(_("Error getting zonepicks data"))
        return None, None, None, None, None

    for i in range(tbl.getRowCount()):
        model_tbl = tu.getInt2('MODEL_ID', i, tbl)
        if not model_ids.has_key(model_tbl):
            continue
        top_tbl = tu.getNum2("LAYER_TOP_MD", i, tbl)
        bot_tbl = tu.getNum2("LAYER_BASE_MD", i, tbl)
        top_cx = tu.getNum2("LAYER_TOP_CX", i, tbl)
        top_cy = tu.getNum2("LAYER_TOP_CY", i, tbl)
        if du.intersects(top_md, bot_md, top_tbl, bot_tbl):
            stratum_name = tu.getStr2("GEOLAYER_ID", i, tbl)
            return top_tbl, bot_tbl, stratum_name, top_cx, top_cy
        else:
            continue
    return None, None, None, None, None



def get_report_min_thickness(ctx, res):
     ok, minthickness = ctx.get_value("RPT_MIN_THICKNESS")
     return minthickness

def get_loginterp_intervals(lda, ctx, res):
    """
    returns list of loginterp_intvl
    """

    out = []

    #frames
    logframes = lda.frames()
    nframe = logframes.size()
    for i in range(nframe):
        logframe = logframes.at(i)
        if logframe.frame_type() == 0:
            continue
        TopMDData = logframe.topMdVec()
        BaseMDData = logframe.baseMdVec()
        TopTVDData = logframe.topTvdVec()
        if TopTVDData is None:
            TopTVDData = [cmn.get_undefined_r32()]*logframe.getNpoint()
        BaseTVDData = logframe.baseTvdVec()
        if BaseTVDData is None:
            BaseTVDData = [cmn.get_undefined_r32()]*logframe.getNpoint()

        saturationCrv = logframe.saturationCurve()
        saturationData = None
        if saturationCrv:
            saturationData = saturationCrv.idata()
        else:
            saturationData = [cmn.get_undefined_i32()]*logframe.getNpoint()

        lithoCrv = logframe.litoCurve()
        lithotypeData = None
        if lithoCrv:
            lithotypeData = lithoCrv.idata()
        else:
            lithotypeData = [cmn.get_undefined_i32()]*logframe.getNpoint()
            
        permData = get_data_from(logframe, 'LR_PERM')
        poroData = get_data_from(logframe, 'LR_PORO')
        satData = get_data_from(logframe, 'LR_OGSAT')

        for j in range(len(lithotypeData)):
            itm = loginterp_intvl()
            itm.saturation = saturationData[j]
            itm.lithotype = lithotypeData[j]

            itm.top_md = TopMDData[j]
            itm.base_md = BaseMDData[j]
            itm.Kporo = poroData[j]
            itm.Kpr = permData[j]
            itm.Ksut = satData[j]
            itm.top_tvd = TopTVDData[j]
            itm.base_tvd = BaseTVDData[j]
            str_top, str_bot, str_name, str_x, str_y = getStratumAndCoord(lda, TopMDData[j], BaseMDData[j], ctx, res)

            if (str_top is None) and (str_bot is None) and (str_name is None):
                continue
            itm.stratum = str_name
            itm.stratumX = str_x
            itm.stratumY = str_y
            out.append(itm)

    return out

def load_loginterp_intervals(ctx, res, bh_id, model_id):
    #print("Borehole id:", bh_id)

    sbh = eu.node_names(ctx.pStorage, dm.nt_borehole, [bh_id])

    tctx = cmn.progress_ctx()
    dthlp = dm.getDataProcessing().getDataTreatHelper()
    lda = dthlp.makeLogData(ctx.pStorage, dm.db_caching, dm.cat_logresults)
    borehole = lda.load(ctx.pStorage, bh_id, model_id, tctx, res.err)
    out = []

    logframes = lda.frames()
    nframes = logframes.size()
    if nframes == 0:
        s = _("Borehole {0}, No log interpretation data").format(sbh)
        #res.add_warning(s)
        dmsrv.py_log_warn(ctx.opo.logger(), s)
        return out
    out = get_loginterp_intervals(lda, ctx, res)
    out = sorted(out, key=operator.attrgetter('top_md', 'base_md'))
    return out

def ifnonperf_intvl(perf_intvls, log_intvls, intvl_number):
    log_intvl = log_intvls[intvl_number]
    for i in range(len(perf_intvls)):
        if (log_intvl.top_md >= perf_intvls[i].top_md):
            ##log_intvl fully in perforated interval:
            ##return false
            if (log_intvl.base_md <= perf_intvls[i].base_md):
                return False
            ##log_intvl topMD in perf. interval, baseMD after perf. interval:
            ##change topMD to baseMD of perf. interval & new log_intvl after perf. interval
            elif (log_intvl.top_md <= perf_intvls[i].base_md):
                log_intvl.top_md = perf_intvls[i].base_md
                continue
        elif (log_intvl.base_md >= perf_intvls[i].top_md):
            ##log_intvl topMD before perf. interval, baseMD in perf. interval
            ##change baseMD to topMD of perf. interval & new log_intvl before perf. interval
            if (log_intvl.base_md <= perf_intvls[i].base_md):
                log_intvl.base_md = perf_intvls[i].top_md
                continue
            ##perforated interval fully in log_intvl
            ##change baseMD to topMD of perf. interval -> new log_intvl before perf. interval AND
            ##generating additional log_intvl with topMD = baseMD of perf. interval,
            ##baseMD = baseMD of current log_intvl. Generated log_intvl will be after perf. interval
            else:
                end = log_intvl.base_md
                log_intvl.base_md = perf_intvls[i].top_md
                newlog_intvl = loginterp_intvl()
                newlog_intvl.top_md = perf_intvls[i].base_md
                newlog_intvl.base_md = end
                newlog_intvl.saturation = log_intvl.saturation
                newlog_intvl.lithotype = log_intvl.lithotype
                log_intvls.insert(intvl_number + 1, newlog_intvl)
                return True
    return True

def get_data_from(ilogframe, mnemo):
    curve = ilogframe.curveByMnemo(mnemo)
    if curve is None:
        out_undefined = [cmn.get_undefined_r32()]*ilogframe.getNpoint()
        return out_undefined
    
    elif curve.data_type() == dm.ldt_float:
        return curve.fdata()
    elif curve.data_type()== dm.ldt_integer:
        return curve.idata()
    elif curve.data_type()== dm.ldt_string:
        return curve.sdata()


def saturated_intvl(log_intvl, valueclasses):

    """
    valueclass[0] - COLLECTOR
    ##valueclass[1] - OIL_SATURATION
    ##valueclass[2] - GAS_SATURATION
    """

    if dm.evaluate(valueclasses[0], log_intvl.lithotype):
        if dm.evaluate(valueclasses[1], log_intvl.saturation):
            return True
        elif dm.evaluate(valueclasses[2], log_intvl.saturation):
            return True
##    if log_intvl.lithotype == 1:
##        if log_intvl.saturation == 1:
##            return True
    return False

def combining_nonperf_intvls(log_intvls, min_thickness):

    out = []
    uncombined = []
    cur_intvl = pu.depth_intvl()
    if len(log_intvls) == 0:
        return out, uncombined
    cur_intvl.top_md = log_intvls[0].top_md
    cur_intvl.base_md = log_intvls[0].base_md
    strt_intvl = 0
    for i in range(1, len(log_intvls)):
        ##distance = abs(log_intvls[i].top_md - cur_intvl.base_md)
        if abs(log_intvls[i].top_md - cur_intvl.base_md)<1e-2:
            cur_intvl.base_md = log_intvls[i].base_md
            if (i + 1 == len(log_intvls)):
                if (cur_intvl.base_md - cur_intvl.top_md >= min_thickness):
                    out.append(cur_intvl)
                    for j in range(strt_intvl, i+1):
                        uncombined.append(log_intvls[j])
        else:
            if ((cur_intvl.base_md - cur_intvl.top_md) >= min_thickness):
                out.append(cur_intvl)
                for j in range(strt_intvl, i):
                    uncombined.append(log_intvls[j])
                
            cur_intvl = pu.depth_intvl()
            cur_intvl.top_md = log_intvls[i].top_md
            cur_intvl.base_md = log_intvls[i].base_md
            strt_intvl = i

            if (i + 1 == len(log_intvls)):
                if (cur_intvl.base_md - cur_intvl.top_md >= min_thickness):
                    out.append(cur_intvl)
                    uncombined.append(log_intvls[i])

    return out, uncombined

def merge_loginterp_models(bh_id, strg, m1_uuid, m2_uuid, dst_uuid, res):
    """
    merges loginterp
    """
    tctx = cmn.progress_ctx()
    dthlp = dm.getDataProcessing().getDataTreatHelper()
    lda = dthlp.makeLogData(strg, dm.db_caching, dm.cat_logresults)
    
    count = lda.mergeRuns(strg, bh_id, m1_uuid, m2_uuid, dst_uuid, tctx, res.err)
    b = lda.save(tctx, res.err)
    if b:
        return count
    else:
        return 0

def load_nonperf_intervals(ctx, res):

    """
    A list of namedtuple of three items is returned.
    Namedtuple is:
        well_name: name of well
        combined addperf_intvls: intervals-candidates for future perforation (list of intervals)
        (intervals is pu.depth_intvl)
        loginterpret_intvls: log interpretation intervals candidates for future perforation
        (list of loginterp_intvl)
    """

    #typedef bh dm.IBorehole
    strg = ctx.pStorage
    bhs = ctx.ents.boreholes()
    models = ctx.ents.models()
    out = []
    if (models is None) or (len(models) == 0):
        res.err.msg = (_("No output model selected"))
        return out
    nbh = len(bhs)
    if (bhs is None) or (nbh == 0):
        res.err.msg = (_("Boreholes not found"))
        return out

    model_id = models[0].getID()
    
    collector_vc = du.get_value_class("COLLECTOR", "LR_LITO", ctx, res)
    oil_sat_vc = du.get_value_class("OIL_SATURATION", "LR_TSAT", ctx, res)
    gas_sat_vc = du.get_value_class("GAS_SATURATION", "LR_TSAT", ctx, res)
    
    valueclasses = []
    valueclasses.append(collector_vc)
    valueclasses.append(oil_sat_vc)
    valueclasses.append(gas_sat_vc)
    
    minthickness = get_report_min_thickness(ctx, res)
    if cmn.is_undefined(minthickness):
        res.err.msg = (_("No minimal thickness defined"))
        return out
    #minthickness = 1
    WellAddPerfIntvls = namedtuple("WellAddPerfIntvls", "well_name addperf_intvls log_intvls")

#typedef progress cmn.progress_phase
    progress = cmn.progress_phase(ctx.pctx, 0, nbh)
    
    ii = 0
    for bh in bhs:
        print("Processing {0} borehole".format(bh.getName()))
        bhid = bh.getID()
        addperf_intvls = []
        loginterpret_intvls = []
        perf_intvls = pu.load_completion_intervals(ctx, res, bhid)

        log_intvls = load_loginterp_intervals(ctx, res, bhid, model_id)

        for intvl_number in range(len(log_intvls)):
            if (ifnonperf_intvl(perf_intvls, log_intvls, intvl_number)):
                if (saturated_intvl(log_intvls[intvl_number], valueclasses)):
                    addperf_intvls.append(log_intvls[intvl_number])

        combined_intvls, uncombined_intvls = combining_nonperf_intvls(addperf_intvls, minthickness)
        out.append(WellAddPerfIntvls(bh.getName(), combined_intvls, uncombined_intvls))
        ii += 1
        progress.change(ii)

    return out

def gen_int_param(n, imin, imax):
    """
    returns list with random int values [imin, imax]
    """
    ret = [0]*n

    for k in range(n):
        ret[k] = random.randint(imin, imax)
        
    return ret

def gen_int_param(n, codes):
    """
    returns list with random int values inside "codes" list
    """
    ret = [0]*n
    
    ind_max = len(codes)-1
    for k in range(n):
        ind = random.randint(0, ind_max)
        ret[k] = codes[ind]
        
    return ret

def gen_num_param(n, vmin, vmax):
    """
    returns list with random float values [vmin, vmax]
    """    
    ret = [0]*n

    for k in range(n):
        ret[k] = random.uniform(vmin, vmax)
        
    return ret

def gen_tops_and_bots(top, base, n):
    step = (base-top)/n
    tops = []
    bots = []
    for k in range(n):
        md_top = top + k*step
        md_base = md_top + step
        tops.append(md_top)
        bots.append(md_base)
    return (tops, bots)

if __name__ == '__main__':
   
    import os
    import db_utils
    import builtins
    builtins.__dict__['_'] = lambda s : s

    cmn.app_init_paths(os.path.abspath('../../../../../build/win64/bin/debug/'))
    
    db.init_loggers()
    dproc.init_lib_dproc()

    ctx = dmsrv.python_ctx()
    res = dmsrv.python_results()

    ##ctx.pStorage = db_utils.make_DataStorage(db.db_sqlite, "c:/db/q.rds")
    ctx.pStorage = db_utils.make_DataStorage(db.db_sqlite, "c:/db/demo.rds")
    if ctx.pStorage is None:
        print("DataStorage creation fails")

    ctx.clear()
    res.clear()
    #ctx.ents.fill(ctx.pStorage)
    ctx.ents.append(ctx.pStorage, dm.nt_model, 16)
    ctx.ents.append(ctx.pStorage, dm.nt_borehole, 1)
    load_nonperf_intervals(ctx, res)
    
    print("Done!")
