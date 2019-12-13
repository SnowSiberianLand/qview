# -*- coding: cp1251 -*-

import mod_dm as dm
import mod_dmsrv as dmsrv
import mod_cmn as cmn
import entity_utils as eu
import data_utils as du
import sys

#typedef strg dm.IDataStorage
#typedef gl dm.IGeoLayer
#typedef picks dm.IWellPicks
#typedef wp dm.wellpick

def put_changes(picks):
    """
    put changes to cache
    """
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()    
    return picks.save_simple(tctx, terr)
    
def append_pick(picks, bh, hrz, mdl, md, tvd=None, cx=None, cy=None):
    """
    appends new horizon pick with given MD
    """
    if bh is None or hrz is None or mdl is None:
        return False
    
    wp = dm.wellpick()
    wp.bh_id = bh.getID()
    wp.surfent_id = hrz.getID()
    wp.model_id = mdl.getID()
    wp.md = md
    wp.kind = dm.pick_manual    
    wp.type = dm.pick_horizon

    if tvd is not None:
        wp.tvd = tvd

    if cx is not None:
        wp.cx = cx

    if cy is not None:
        wp.cy = cy

    picks.add_well_pick(wp, dm.pick_horizon, None)
    return True

def get_picks_by_bh(strg, bh, model_id=cmn.get_undefined_i32(), hrz_id=cmn.get_undefined_i32()):
    """
    загружает и возвращает dm.IWellPicks по скважине, варианту данных и горизонтам
    """
    
    picks = dm.IWellPicks.make(strg, dm.db_caching)

    bhids = cmn.vec_i32_t()
    bhids.append(bh.getID())

    hrzids = cmn.vec_i32_t()
    if cmn.get_undefined_i32()!=hrz_id:
        hrzids.append(hrz_id)
        
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    b = picks.load_by_bh(bh.getID(), model_id, hrzids, tctx, terr)

    return picks

def get_picks(strg, bhs, model_id=cmn.get_undefined_i32(), hrz_id=cmn.get_undefined_i32()):
    """
    загружает и возвращает dm.IWellPicks по выбранным скважинам, варианту данных и горизонтам
    """
    
    picks = dm.IWellPicks.make(strg, dm.db_caching)

    if type(bhs) == type(list()):
        vbh = du.to_bh_vec(bhs)
    else:
        vbh = bhs # already dm.vec_borehole_t
        
    bhids = cmn.vec_i32_t()
    dm.get_vids(vbh, bhids)

    hrzids = cmn.vec_i32_t()
    if cmn.get_undefined_i32()!=hrz_id:
        hrzids.append(hrz_id)
        
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    b = picks.load_multi_bh(bhids, model_id, hrzids, tctx, terr)

    return picks

def getPicks(strg, bhs, model_id=cmn.get_undefined_i32(), hrz_id=cmn.get_undefined_i32()):
    """
    загружает и возвращает маркеры горизонтов по выбранным скважинам, варианту данных и горизонту
    """
    
    picks = dm.IWellPicks.make(strg, dm.db_caching)

    vbh = du.to_bh_vec(bhs)
    bhids = cmn.vec_i32_t()
    dm.get_vids(vbh, bhids)

    hrzids = cmn.vec_i32_t()
    if cmn.get_undefined_i32()!=hrz_id:
        hrzids.append(hrz_id)
        
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    b = picks.load_multi_bh(bhids, model_id, hrzids, tctx, terr)

    vwp = dm.vec_wellpick_t()
    picks.get(vwp)
    
    return vwp

def getTvdLimits(vwp):
    """
    возвращает min/max TVD
    """
    n = len(vwp)

    tvd_min = None
    tvd_max = None
    
    for i in range(n):
        wp = vwp[i]
        if cmn.is_undefined(wp.tvd):
            continue
        if (tvd_min==None) or (wp.tvd<tvd_min):
            tvd_min = wp.tvd

        if (tvd_max==None) or (wp.tvd>tvd_max):
            tvd_max = wp.tvd            

    return (tvd_min, tvd_max)

    
def getTvdRange(strg, bhs, gl, mdl):
    """
    возвращает min/max TVD по маркерам горизонтов для скважин bhs, модели mdl и пласта gl
    """
    model_id = mdl.getID()
    
    top_id = gl.getTopHorizonID()
    base_id = gl.getBaseHorizonID()
    
    vwp_top = getPicks(strg, bhs, model_id, top_id)
    mm_top = getTvdLimits(vwp_top)

    vwp_base = getPicks(strg, bhs, model_id, base_id)
    mm_base = getTvdLimits(vwp_base)

    if mm_top[0] is None or mm_base[0] is None:
        return (None, None)
    
    tvd_top = min(mm_top[0],mm_base[0])
    tvd_base= max(mm_top[1],mm_base[1])
    
    return (tvd_top, tvd_base)

def getZone(strg, bh_id, model_id, stratum_id):
    """
    returns zonepick for given <bhid, model_id, stratum_id>
    """
    # make wellpicks instance
    wp = dm.IWellPicks.make(strg)

    gl = eu.find_stratum(strg, stratum_id)
    if gl is None:
        return None

    lst_ids = []
    lst_ids.append(gl.getTopHorizonID())
    lst_ids.append(gl.getBaseHorizonID())
    hrz_ids = du.to_i32_vec( lst_ids )

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    
    # load wellpicks data by <bh_id, model_id, hrz_ids>
    b = wp.load_by_bh(bh_id, model_id, hrz_ids, tctx, terr)
    if b==False:
        sys.exit()
    
    #n = wp.size()
    #s = 'Markers count: {0}'.format(n)
    #print(s)

    vzp = dm.vec_zonepick_t()
    wp.get_zonation(vzp)

    nzp = len(vzp)
    if 0==nzp:
        return None
    
    #s = 'Zones count: {0}'.format(nzp)
    #print(s)

    return vzp[0]