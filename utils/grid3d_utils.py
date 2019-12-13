# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import entity_utils as eu
import data_utils as du

import random

#typedef g3 dm.IGrid3D
#typedef ed dm.IGrid3D.IEditor
#typedef ed2 dm.IGrid3D.IDataEditor

def make_cube_vals(dims, vmin, vmax):
    """
    dims - grid dimensions, array: [ni, nj, nk]
    """
    ni = dims[0]
    nj = dims[1]
    nk = dims[2]
    
    ncell = ni*nj*nk
    vals = [0.]*ncell

    dlt = vmax-vmin

    for k in range(ncell):
        val = vmin + dlt*random.random()
        vals[k] = val

    return du.to_r32_vec(vals)
    
def verify_grid3d(strg, mdl_name, name, dims, org, clen):
    g3 = eu.verifyGrid3D(strg, mdl_name, name)
    init_grid3d(g3, dims, org, clen)
    return g3

def init_grid3d(g3, dims, org, clen):
    """    
    dims - grid dimensions, array: [ni, nj, nk]
    org - grid origin point coords, array: [ox, oy, oz]    
    clen - cell length, array [dx, dy, dz]
    """    
    ed = g3.getEditor()

##             2*----------*3
##             /|         /|
##            / |        / |
##          0*--+-------*1 |
##           |  |       |  |
##           | 6*-------+--*7
##           | /        | /
##           |/         |/
##          4*----------*5
    xc1 = [0,2,4,6]    # x = x
    xc2 = [1,3,5,7]    # x = x + dx
    
    yc1 = [0,1,4,5]    # y = y
    yc2 = [2,3,6,7]    # y = y + dy
    
    zc1 = [0,1,2,3]    # z = z
    zc2 = [4,5,6,7]    # z = z + dz
    
    ni = dims[0]
    nj = dims[1]
    nk = dims[2]
    
    ed.setGridType(dm.gt3d_corner_point)
    ed.setNI(ni)
    ed.setNJ(nj)
    ed.setNK(nk)
    
    ox = org[0]
    oy = org[1]
    oz = org[2]
    
    dx = clen[0]
    dy = clen[1]
    dz = clen[2]
    
    ncell = ni*nj*nk
    vsz = ncell*8
    vx = [0.]*vsz
    vy = [0.]*vsz
    vz = [0.]*vsz
    
    ind = 0
    for k in range(nk):
        tz = oz + k*dz
        for j in range(nj):
            ty = oy + j*dy
            for i in range(ni):
                tx = ox + i*dx
                for c in range(8):
                    if c in xc1:
                        vx[ind] = tx
                    else:
                        vx[ind] = tx + dx
    
                    if c in yc1:
                        vy[ind] = ty
                    else:
                        vy[ind] = ty + dy
    
                    if c in zc1:
                        vz[ind] = tz
                    else:
                        vz[ind] = tz + dz
                        
                    ind += 1
    
    vx = du.to_r32_vec(vx)
    vy = du.to_r32_vec(vy)
    vz = du.to_r32_vec(vz)
    
    ed.setAllCellsCoords(vx, vy, vz)
    
    ed2 = g3.getDataEditor()

    tctx = cmn.progress_ctx()
    ed2.make_default_mask(tctx)

    ed2.setReady4Use(True)