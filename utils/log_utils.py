# -*- coding: cp1251 -*-


import mod_cmn as cmn
import mod_dm as dm
import mod_dmsrv as dmsrv
import mod_orm as db
import data_utils as du
import table_utils as tu
import entity_utils as eu

import random
import math

#typedef c1 dm.ILogCurve
#typedef c2 dm.ILogCurve
#typedef f1 dm.ILogFrame
#typedef f2 dm.ILogFrame
#typedef res dmsrv.python_results
#typedef frame dm.ILogFrame
#typedef ldata dm.ILogData
#typedef crvs dm.ILogCurves
#typedef crv dm.ILogCurve
#typedef ctx dmsrv.python_ctx

def put_changes(lda):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return lda.save(tctx, terr)

def get_log_data(strg, bh):
    mst = strg.getMetaStorage()    
    lda = dm.ILogData.make(strg, dm.db_caching, dm.cat_logs)
    if lda is None:
        return None
        
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    
    b = lda.load(strg, bh.getID(), cmn.get_undefined_i32(), tctx, terr)
    return lda

def append_run_and_frame(lda, bh, lst_md):
    """
    appends new log run and frame
    """
    if bh is None:
        return None
    bhid = bh.getID()

    runs = lda.runs()
    
    run = runs.appendLogRun(bhid, dm.lt_well_logs)
    
    frames = lda.frames()

    if type(lst_md)==type(list()):
        vmd = du.to_double_vec(lst_md)
    else:
        vmd = lst_md

    frame = frames.appendPointFrame(run.getID(), vmd)
    return frame

def append_curve(frame, mnemo, units, lst_vals):
    """
    appends numeric (float) curve with given mnemo and units
    """    
    if mnemo is None:
        return None
    if len(mnemo)==0:
        return None
    
    lda = frame.logData()
    strg = lda.getDataStorage()
    mst = strg.getMetaStorage()
    
    pd = dm.getPropertyByMnemo(mst, mnemo)
    prop_id = cmn.get_undefined_i32()
    if pd is not None:
        prop_id = pd.getID()

    unit_id = dm.getUidByMnemo(mst, units)

    if type(lst_vals)==type(list()):
        vals = du.to_double_vec(lst_vals)
    else:
        vals = lst_vals
        
    crv = frame.appendCurve(prop_id, unit_id, mnemo, units)
    crv.setData(vals)
    return crv

    
def getFirstCurveByProp(frame, prop_id):
    """
    возвращает первую кривую со свойством prop_id
    """
    vcrv = dm.vec_log_curve()
    frame.findCurvesByProperty(prop_id, vcrv)

    if len(vcrv)==0:
        return None
    
    return vcrv[0]

def frame_comp_cc(f1, f2):
    return f2.curveCount() - f1.curveCount()
    
def sort_frames_by_curve_count(frames):  
    """
    sort log frames by curve count DESCending
    frames is list of ILogFrame
    """
    return sorted(frames, frame_comp_cc)


def delete_logframe_from_db(strg, frame_id, res):
    crud = strg.getIO()

    fids = cmn.set_i32_t()
    fids.add(frame_id)
    fltr = db.filter("rdm", "LOGS_FRAME")
    fltr.setIn("FRAME_ID", fids)

    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    bCommit = True
    stat = db.changes_stat()
    
    bb = crud.del_cascade(fltr, bCommit, stat, pctx, terr)
    if (bb==False):
        res.add_error(terr.msg)

def delete_logcurves_from_db(strg, curves, res):
    crud = strg.getIO()

    fltr = db.filter("rdm", "LOGS_CURVE")
    fltr.setIn("CURVE_ID", curves)

    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    bCommit = True
    stat = db.changes_stat()
    
    bb = crud.del_cascade(fltr, bCommit, stat, pctx, terr)
    if (bb==False):
        res.add_error(terr.msg)
    

def remove_loginterp_dupe_frames(borehole_id, strg, res):
    """
    removes dupe frames 
    remain the only one frame on <model,borehole> key
    """

    ldata = eu.load_loginterp(borehole_id, strg, res)
    frames = ldata.frames();
    
    ents = dm.entities()
    ents.fill_certain_nodes(strg, dm.nt_model)
    models = ents.models()

    for model in models:  
        fids = eu.getLogresultFramesByModel(borehole_id,  model.getID(), strg, res)
        nframe = len(fids)

        if (nframe<=1):
            continue

        lst = []
        for fid in fids:
            frame = frames.findById(fid)
            lst.append(frame)
            
        lst = sort_frames_by_curve_count(lst)
        for frame in lst:
            print("borehole_id={0}, frame_id={1}, curve count {2}".format(borehole_id, frame.getID(), frame.curveCount()))

        # remove starting second item (index=1)
        for k in range(1,len(lst)):
            frame = lst[k]
            fid = frame.getID()
            delete_logframe_from_db(strg, fid, res)

        
    return True

def remove_loginterp_dupe_curves_from_frame(borehole_id, frame_id, strg, comp_func, res):  
    """
    removes dupes in log interpretation frame
    curves compared by comp_func
    """
    
    ##print "processing frame_id: {0}".format(frame_id)
    
    ldata = eu.load_loginterp_by_frame(borehole_id, frame_id, strg, res)
    if ldata is None:
        print("Can't get log interpretation data for frame_id={0}".format(frame_id))
        return 0
    
    frames = ldata.frames()
    if frames is None:
        print("Frames data is NULL")
        return 0
        
    frame = frames.findById(frame_id)
    if frame is None:
        print("frame_id={0} not found in loaded data".format(frame_id))
        return 0

##    lr = frame.getFrameData()
##    if lr is None:
##        print("Frame data is NULL")
##        return 0

    vcrv = dm.vec_log_curve()
    frame.curves(vcrv)
    dupes = find_dupes(vcrv, comp_func)

    n = len(vcrv)
    print("-- all ({0}):".format(n))
    for k in range(n):
        crv = vcrv[k]
        print("{0}, {1}, {2}, {3}".format(frame.getID(), crv.getID(), crv.mnemo(), crv.data_size()))

    tset = cmn.set_i32_t()
    n = len(dupes)
    if n>0:
        print("-- duplicates ({0}):".format(n))
    else:
        print("-- duplicates: none")    
    for k in range(n):
        crv = dupes[k]
        tset.add(crv.getID())
        print("{0}, {1}, {2}, {3}".format(frame.getID(), crv.getID(), crv.mnemo(), crv.data_size()))

    ndupe = len(dupes)
    if ndupe==0: # !!! it's important, otherwise deletes all curves
        return 0
    
    delete_logcurves_from_db(strg, tset, res)
    
    return len(tset)


def remove_loginterp_dupe_curves(borehole_id, strg, comp_func, res):
    """
    removes dupes
    """
    
    frames = eu.getLogInterpFrames(borehole_id, strg, res)
    print("borehole_id={0}, frame count {1}".format(borehole_id, len(frames)))

    count = 0
    for frame_id in frames:
        tc = remove_loginterp_dupe_curves_from_frame(borehole_id, frame_id, strg, comp_func, res)
        count += tc

    return count


def find_dupes(vcrv, comp_func):
    """
        finds dupes in array of ILogCurve objects
        using comp_func()
    """
    out = dm.vec_log_curve()
    
    n = len(vcrv)
    for i in range(n):
        c1 = vcrv[i]
        for j in range(i+1, n):
            c2 = vcrv[j]
            b = comp_func(c1, c2)
            if (b==True):
                out.append(c2)
            
    return out

def crv_compare_by_mnemo(c1, c2):
    """    
    returns True is curves have same MNEMO
    c1, c2 - ILogCurve
    """
    if (c1.mnemo()!=c2.mnemo()):
        return False

    if (c1.mnemo()=="" and c1.propertyId()!=cmn.get_undefined_i32()):
        return False
        
    return True

def crv_compare_by_property(c1, c2):
    """    
    returns True is curves have same PROPERTY_ID
    c1, c2 - ILogCurve
    """

    if (c1.propertyId()!=c2.propertyId()):
        return False
    
    return True

def crv_compare_by_ak(c1, c2):
    """    
    returns True is curves have same AK (MNEMO,UNIT,PROPERTY_ID,UNIT_ID,MIN,MAX)
    c1, c2 - ILogCurve
    """
    if (c1.mnemo()!=c2.mnemo()):
        return False

    if (c1.propertyId()!=c2.propertyId()):
        return False

    if (c1.unit()!=c2.unit()):
        return False
    
    if (c1.unitId()!=c2.unitId()):
        return False

    if (c1.getMin()!=c2.getMin()):
        return False

    if (c1.getMax()!=c2.getMax()):
        return False
    
    return True

def check_log_properties(table, prop_pd, unit_pd, prop_str, unit_str, curve_pd, ctx, py_res):
    """
    """
    if table is None:
        return False

    if not tu.hasProps(table, [prop_pd, unit_pd, prop_str, unit_str, curve_pd], py_res):
        return False

    mnemos_wo_props = set()
    props_wo_quants = set()
    props_wo_units = set()
    incorrect_units = set()
    curves1 = set()
    curves2 = set()
    curves3 = set()
    curves4 = set()

    mst = ctx.pStorage.getMetaStorage()
    rowCount = table.getRowCount()
    for i in range(rowCount):
        curve_id = tu.getInt2(curve_pd, i, table)
        prop_id  = tu.getInt2(prop_pd,  i, table)
        unit_id  = tu.getInt2(unit_pd,  i, table)
        prop_s   = tu.getStr2(prop_str, i, table)
        unit_s   = tu.getStr2(unit_str, i, table)

        pd = dm.getPropertyById(mst, prop_id)
        if pd is None:
            mnemos_wo_props.add(prop_s)
            curves1.add(curve_id)
            continue

        if not pd.getDataTypeID() in [db.ft_num, db.ft_num]:
            continue

        qd = pd.getQuantity()
        if qd is None:
            props_wo_quants.add(pd.getMnemo())
            curves2.add(curve_id)
            continue

        if cmn.is_undefined(unit_id):
            props_wo_units.add(pd.getMnemo())
            curves3.add(curve_id)
            continue

        ud = qd.find(unit_id)
        if ud is None:
            unit = dm.getUnitById(mst, unit_id)
            if unit:
                unit_s = unit.getShortName()
            incorrect_units.add(unit_s)
            curves4.add(curve_id)

    position_func = lambda s: du.make_position(ctx.pStorage, list(s), curve_pd)

    if len(mnemos_wo_props) > 0:
        msg = _("Properties not found for mnemos [{0}]").format(du.compact_format(list(mnemos_wo_props)))
        py_res.add_warning(msg, position_func(curves1))
    if len(props_wo_quants) > 0:
        msg = _("Quantity descriptions not found for properties [{0}]").format(du.compact_format(list(props_wo_quants)))
        py_res.add_error(msg, position_func(curves2))
    if len(props_wo_units) > 0:
        msg = _("Unit descriptions not found for properties [{0}]").format(du.compact_format(list(props_wo_units)))
        py_res.add_warning(msg, position_func(curves3))
    if len(incorrect_units) > 0:
        msg = _("Incorrect units [{0}]").format(du.compact_format(list(incorrect_units)))
        py_res.add_error(msg, position_func(curves4))

    return True


def check_necessary_properties(table, prop_pd, necessary_mnemo, ctx, py_res):
    """
    """
    if table is None:
        return False

    if not tu.hasProps(table, [prop_pd], py_res):
        return False

    ok, props = ctx.get_value(necessary_mnemo)
    if not ok:
        py_res.add_error(_("Wrong option keyword: {0}").format(necessary_mnemo))
        return False

    mst = ctx.pStorage.getMetaStorage()
    all_props = set()
    rowCount = table.getRowCount()
    for i in range(rowCount):
        prop_id = tu.getInt2(prop_pd, i, table)
        pd = dm.getPropertyById(mst, prop_id)
        if pd is None:
            continue
        all_props.add(pd.getMnemo())

    missed = [x for x in props if x not in all_props]
    missed = [du.property2str(ctx.pStorage, x) for x in missed]
    if len(missed) > 0:
        py_res.add_error(_("Necessary properties [{0}] are absent").format(du.seq2str(missed)))

    return True


def make_key(model_id, top_md, base_md, prop):
    return "{0}_{1}_{2}_{3}".format(model_id, top_md, base_md, prop)

def from_key(key):
    items = key.split("_")
    return int(items[0]), float(items[1]), float(items[2]), items[3]


def check_duplicate_properties(table, prop_pd, mnemo_pd, curve_pd, model_pd, top_pd, base_pd, ctx, py_res):
    """
    """
    if table is None:
        return False

    props = [prop_pd, mnemo_pd, curve_pd, top_pd, base_pd]
    if model_pd:
        props.append(model_pd)
    if not tu.hasProps(table, props, py_res):
        return False

    curve_prop_map = {}
    all_props = []

    model_id = cmn.get_undefined_i32()

    rowCount = table.getRowCount()
    for i in range(rowCount):
        top_md       = tu.getNum2(top_pd,   i, table)
        base_md      = tu.getNum2(base_pd,  i, table)
        curve_id     = tu.getInt2(curve_pd, i, table)
        prop_id      = tu.getInt2(prop_pd,  i, table)
        prop_text    = tu.getStr2(prop_pd,  i, table)
        mnemo        = tu.getStr2(mnemo_pd, i, table)
        if model_pd:
            model_id = tu.getInt2(model_pd, i, table)

        prop = prop_text if prop_text else mnemo

        all_props.append([model_id, top_md, base_md, prop])
        key = make_key(model_id, top_md, base_md, prop)
        if key not in curve_prop_map:
            curve_prop_map[key] = list()
        curve_prop_map[key].append(curve_id)

    dupes = set()
    curves = set()
    for prop in all_props:
        if all_props.count(prop) > 1:
            dupes.add(prop[3])
            key = make_key(*prop)
            for c in curve_prop_map[key]:
                curves.add(c)

    if len(dupes) > 0:
        if prop == prop_text:
            msg = _("Duplicate properties [{0}] found").format(du.seq2str(dupes))
        else:
            msg = _("Duplicate mnemos [{0}] found").format(du.seq2str(dupes))
        py_res.add_warning(msg, du.make_position(ctx.pStorage, list(curves), curve_pd))

    return True


def check_log_null_values(strg, log, nulls, res):
    """
    """

    if log is None:
        return False

    ##depth = log.getDepth()
    depth = log.depthVec()

    ##curveCount = log.getCurvesCount()
    ##curveCount = log.curveCount()

    curves = dm.vec_log_curve()
    log.data_curves(curves)
    curveCount = len(curves)

    for i in range(curveCount):

       ## if log.isDepth(i) or log.isTopMD(i) or log.isBotMD(i) or log.isTopTVD(i) or log.isBotTVD(i):
       ##     continue

        suspects = set()
        suspects_md = []

        curve = curves[i]
        curve_data_type = curve.data_type()

        data = None
        if curve_data_type == dm.ldt_float:
            data = curve.fdata()
        if curve_data_type == dm.ldt_integer:
            data = curve.idata()
        if curve_data_type == dm.ldt_string:
            data = curve.sdata()

        if data is None:
            continue

        ##data = log.getCurveData(i)
        for j, v in enumerate(data):
            if v in nulls:
                suspects.add(v)
                suspects_md.append(depth[j])

        if len(suspects_md) > 0:

            ##name = log.getMnemo(i)
            name = curve.mnemo()
            ##prop_id = log.getPropertyID(i)
            prop_id = curve.propertyId()
            if not cmn.is_undefined(prop_id):
                name = du.property_id2str(strg, prop_id)

            msg = _("\"{0}\" channel has suspicious values: {1}").format(name, du.seq2str(suspects))
            res.add_warning(msg, du.make_position(strg, suspects_md, "COMMON_TOP_MD"))

    return True


def check_logres_null_values(strg, lrun, nulls, res):
    """
    """

    if lrun is None:
        return False

    top = lrun.topMdVec()
    bot = lrun.baseMdVec()
    curves = dm.vec_log_curve()
    lrun.data_curves(curves)
    curveCount = len(curves)

    ##curveCount = lrun.getNpoint()
    for i in range(curveCount):

        ##if lrun.isDepth(i) or lrun.isTopMD(i) or lrun.isBotMD(i) or lrun.isTopTVD(i) or lrun.isBotTVD(i):
            ##continue

        suspects = set()
        suspect_invs = []

        ##data = lrun.getCurveData(i)
        curve = curves[i]
        curve_data_type = curve.data_type()

        data = None
        if curve_data_type == dm.ldt_float:
            data = curve.fdata()
        if curve_data_type == dm.ldt_integer:
            data = curve.idata()
        if curve_data_type == dm.ldt_string:
            data = curve.sdata()

        if data is None:
            continue

        for j, v in enumerate(data):
            if v in nulls:
                suspects.add(v)
                du.add_interval(suspect_invs, top[j], bot[j])

        if len(suspect_invs) > 0:

            name = curve.mnemo()
            prop_id = curve.propertyId()
            if not cmn.is_undefined(prop_id):
                name = du.property_id2str(strg, prop_id)

            msg = _("\"{0}\" channel has suspicious values: {1}").format(name, du.seq2str(suspects))
            res.add_warning(msg, du.make_position(strg, suspect_invs, "COMMON_TOP_MD", "COMMON_BASE_MD"))

    return True

def gen_num_param(n, vmin, vmax):
    """
    returns list with random float values [vmin, vmax]
    """    
    ret = [0]*n

    decay = -random.uniform(1, 10)/10000
    nwave = random.randint(10,50)
    ttt = 2*math.pi*nwave
    step = ttt/n

    dlt = vmax-vmin
    
    t = 0.
    for k in range(n):
        c = math.exp(k*decay)
        t = t+step
        val = vmin+0.5*dlt*math.sin(t)*c
        ret[k] = 0.5*random.uniform(vmin, vmax) + val
        
    return ret

def make_list(_tmin, _tmax, tstep):
    tmin = min(_tmin, _tmax)
    tmax = max(_tmin, _tmax)
    
    dlt = tmax-tmin
    np = int(dlt/tstep+1)

    lst = [0]*np

    val = tmin
    for k in range(np):
        if val>tmax:
            val = tmax
            
        lst[k] = val

        if val==tmax:
            break
        
        val += tstep

    return lst
