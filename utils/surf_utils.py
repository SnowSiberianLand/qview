# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import entity_utils as eu
import data_utils as du

import random

#typedef surf dm.ISurface
#typedef ed dm.ISurface.IEditor
#typedef data dm.ISurface.IData

def verify_surface(strg, name, dims, org, clen, rot=0.):
    surf = eu.verifySurface(strg, name)
    init_surface_regular(surf, dims, org, clen, rot)
    return surf

def init_surface_regular(surf, dims, org, clen, rot=0.):
    """    
    dims - surface dimensions, array: [ni, nj]
    org - grid origin point coords, array: [ox, oy]    
    clen - cell length, array [dx, dy]
    rot - rotation angle
    """
    
    ni = dims[0]
    nj = dims[1]
    
    x0 = org[0]
    y0 = org[1]
    stepI = clen[0]
    stepJ = clen[1]

    ed = surf.getEditor()

    ed.setNI(ni)
    ed.setNJ(nj)
    
    ed.setX0(x0)
    ed.setY0(y0)
    
    ed.setStepI(stepI)
    ed.setStepJ(stepJ)
    
    ed.setRotation(rot)

    ed.setGridType(dm.sgt_regular)

    terr = cmn.err_info()
    surf.initData(terr)

def make_subsurface(strg, surf, name, ibeg, iend, jbeg, jend):
    """    
    makes subsurface from regular surface
    subsurface view defined by index ranges: [ibeg, iend), [jbeg, jend)
    assumptions:
        regular grid
        no rotation (ibeg, jbeg) - origin point of new grid
    """    
    
    ni = surf.getNI()
    nj = surf.getNJ()

    if ibeg<0 or ibeg>ni:
        return None

    if iend<0 or iend>ni:
        return None

    if ibeg>=iend:
        return None

    if jbeg<0 or jbeg>=nj:
        return None

    if jend<0 or jend>nj:
        return None

    if jbeg>=jend:
        return None

    sub_ni = iend-ibeg 
    sub_nj = jend-jbeg

    step_i = surf.getStepI()
    step_j = surf.getStepJ()

    ox, oy = surf.getNodeCoords(ibeg, jbeg)
    dims = [sub_ni, sub_nj]
    org  = [ox, oy]
    clen = [step_i, step_j]
    
    rot  = surf.getRotation()
    new_surf = verify_surface(strg, name, dims, org, clen, rot)

    data = surf.getData()
    new_data = new_surf.getData()
    
    for i in range(sub_ni):
        for j in range(sub_nj):
            ok, val = data.getValue(ibeg+i, jbeg+j)
            new_data.setValue(i, j, val)

    return new_surf
