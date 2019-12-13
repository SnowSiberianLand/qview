# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv

import data_utils as du
import entity_utils as eu
import table_utils as tu
import math

#typedef surv dm.IDevSurvey
#typedef ctx.ents dm.entities
#typedef ctx dmsrv.python_ctx
#typedef ctx.opo dm.op_options


def calc_from_vmovt_by_bh(tbl, vftri, surv, ctx, res):
    """  
    calculates TVD and MD from: VMOVT + TVD_INIT and inclinometry
    tctrl - TableControllerBase
    vftri - table row indexes to process (filtering supported)
    """

    logger = ctx.opo.lo.logger
    
    bh = eu.find_borehole(ctx.pStorage, ctx.borehole_id)
    if bh is None:
        msg = _("Internal error, Incorrect BOREHOLE_ID = {0}").format(ctx.borehole_id)
        res.add_error(msg)
        dmsrv.py_log_error(logger, msg)
        return False

    # get elevation (kelly bushing, kb)
    well = bh.getWell()
    if well is None:
        msg = _("Internal error. Can't find well for borehole, BOREHOLE_ID = {0}").format(ctx.borehole_id)
        res.add_error(msg)
        dmsrv.py_log_error(logger, msg)
        return False

    kb = well.getElevation()
    if cmn.is_undefined(kb):
        kb = 0.
    
    ##tu.sortTable(tbl, "PICK_MD") это нельзя делать из-за контекстного вызова из GUI
    rowCount = tbl.getRowCount()
    #print(rowCount)

    mst = ctx.pStorage.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, 'BOREHOLE_ID')

    nrow = len(vftri)
    print(nrow)
    
    for k in range(nrow): # last row is new (for editable table) !!!:
        ind = vftri[k]
        ok, tbhid = tbl.dataAsInt(pd, cmn.get_undefined_i32(), ind)

        if tbhid!=ctx.borehole_id:
            continue # another borehole, skip
        
        fct = tu.getStr2("CONTACT_ID",   ind,   tbl)
        mdl = tu.getStr2("MODEL_ID",   ind,   tbl)
        
        vmovt = tu.getNum2("DPICK_VERT_MOVT",   ind,   tbl)
        tvd_init = tu.getNum2("PICK_TVD_INIT",   ind,   tbl)

        ex_tvd = tu.getNum2("PICK_TVD", ind,   tbl)
        ex_md  = tu.getNum2("PICK_MD", ind,   tbl)
        
        dt = du.fmt_date(du.from_date_t(tu.getDate2("EVENT_DATE", ind, tbl)))

        # если нет vmovt или tvd_init - ничего не можем посчитать
        if vmovt==cmn.get_undefined_r64() or tvd_init==cmn.get_undefined_r64():
            s = _("Dynamic fluid contact pick: {0}, Model: {1}, Date: {2} - VMOVT or TVD_INIT undefined").format(fct, mdl, dt)
            res.add_warning(s)
            dmsrv.py_log_warn(ctx.opo.logger(), s)
            continue

        tvd = tvd_init - vmovt # потому что подъем
        
        tcx = 0.;
        tcy = 0.;
        md = 0.;
        ok, md, tcx, tcy = surv.get_data4tvd(tvd)

        s_ex_md = "NULL"
        if ex_md!=cmn.get_undefined_r64():
            s_ex_md = '{0:.2f}'.format(ex_md)

        s_ex_tvd = "NULL"
        if ex_tvd!=cmn.get_undefined_r64():
            s_ex_tvd = '{0:.2f}'.format(ex_tvd)

        s_md = "NULL"
        if md!=cmn.get_undefined_r64():
            s_md = '{0:.2f}'.format(md)

        s_tvd = "NULL"
        if tvd!=cmn.get_undefined_r64():
            s_tvd = '{0:.2f}'.format(tvd)
            
        if ok==False:
            s = _("Fluid contact: {0}, Model:{1}, Can't get TVD for MD value: {2}").format(fct, mdl, s_md)
            res.add_warning(s)
            dmsrv.py_log_warn(ctx.opo.logger(), s)
            continue

        # значение не изменилось, пропускаем
        if math.fabs(ex_md-md)<1e-3 and math.fabs(ex_tvd-tvd)<1e-3:
            s = _("Dynamic fluid contact pick: {0}, Model: {1}, Date: {2}, VMOVT={3:.2f}, TVD={4}, MD={5} calculated MD and TVD values are equal to the existing ones, skipped").format(fct, mdl, dt, vmovt, s_tvd, s_md)
            res.add_warning(s)
            dmsrv.py_log_info(ctx.opo.logger(), s)
            continue
        
        EPS=0.1
        if math.fabs(md-tvd) < kb-EPS:
            s = _("MD-TVD < Elevation, depth: {0:.2f}").format(md)
            res.add_error(s)
            continue

        tu.setValue(tvd,"PICK_TVD",ind,tbl)
        tu.setValue(md,"PICK_MD",ind,tbl)

        s = _("Dynamic fluid contact pick: {0}, Model: {1}, Date: {2}, VMOVT={3}, TVD={4} -> {5}, MD={6} -> {7}").format(fct, mdl, dt, vmovt, s_ex_tvd, s_tvd, s_ex_md, s_md)
        dmsrv.py_log_info(ctx.opo.logger(), s)
        res.add_comment(dm.operation_result.or_success, s)

    return True
