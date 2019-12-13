import mod_dm as dm
import mod_dmsrv as dmsrv
import mod_cmn as cmn

import entity_utils as eu
import data_utils as du

import sys

#typedef zprops dmsrv.zoneprops
#typedef zpos dmsrv.zoneprop_position
#typedef key dmsrv.zoneprop_key

def calc_zoneprops(bh, mdl_loginterp, mdl_picks):
    """
    recalculates average zone properties for borehole
    """
    if bh is None:
        return False

    if mdl_loginterp is None:
        return False

    if mdl_picks is None:
        return False

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()    
    return dmsrv.calc_avg_zoneprops(bh, mdl_loginterp, mdl_picks, tctx, terr)
    
def get_zprops_by_bh(strg, bh, model_id=cmn.get_undefined_i32(), gl_id=cmn.get_undefined_i32()):
    """
    makes dmsrv.zoneprops and load data by given borehole, model and geolayer
    """
    
    zprops = dmsrv.zoneprops(strg, dm.db_caching)

    bhids = cmn.vec_i32_t()
    bhids.append(bh.getID())

    glids = cmn.vec_i32_t()
    if cmn.get_undefined_i32()!=gl_id:
        glids.append(gl_id)
        
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    b = zprops.load_by_bh(bh.getID(), model_id, glids, tctx, terr)

    return zprops

def get_zprops(strg, bhs, model_id=cmn.get_undefined_i32(), gl_id=cmn.get_undefined_i32()):
    """
    makes dmsrv.zoneprops and load data by given boreholes, model and geolayer
    """
    
    zprops = dmsrv.zoneprops(strg, dm.db_caching)

    if type(bhs) == type(list()):
        vbh = du.to_bh_vec(bhs)
    else:
        vbh = bhs # already dm.vec_borehole_t
        
    bhids = cmn.vec_i32_t()
    dm.get_vids(vbh, bhids)

    glids = cmn.vec_i32_t()
    if cmn.get_undefined_i32()!=gl_id:
        glids.append(gl_id)
        
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    b = zprops.load_multi_bh(bhids, model_id, glids, tctx, terr)

    return zprops

def append(zprops, bh, mdl, gl):
    """
    appends new item into zoneprops, returns dmsrv.zoneprop_position
    """
    key = dmsrv.zoneprop_key()
    key.borehole_id = bh.getID()
    key.model_id = mdl.getID()
    key.layer_id = gl.getID()

    terr = cmn.err_info()
    zpos = zprops.insert(key, terr)
    return zpos

def put_changes(zprops):
    """
    put changes to cache
    """
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    return zprops.save(tctx, terr)