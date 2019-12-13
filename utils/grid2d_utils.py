# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import entity_utils as eu
import data_utils as du

import random

#typedef g2 dm.IGrid2D
#typedef ed dm.IGrid2D.IEditor

def make_values2d_vals(dims, vmin, vmax):
    """
    dims - grid dimentions (cell count), array: [ni, nj]
    """
    ni = dims[0]
    nj = dims[1]
    
    ncell = ni*nj
    vals = [0.]*ncell

    dlt = vmax-vmin

    for k in range(ncell):
        val = vmin + dlt*random.random()
        vals[k] = val

    return du.to_double_vec(vals)

def verify_grid2d(strg, mdl_name, name, dims, org, clen):
    return verify_grid2d_cornerpoint(strg, mdl_name, name, dims, org, clen)
    #return verify_grid2d_irregular(strg, mdl_name, name, dims, org, clen)

def verify_grid2d_irregular(strg, mdl_name, name, dims, org, clen):
    g2 = eu.verifyGrid2D(strg, mdl_name, name)
    init_grid2d_irregular(g2, dims, org, clen)
    return g2

def verify_grid2d_cornerpoint(strg, mdl_name, name, dims, org, clen):
    g2 = eu.verifyGrid2D(strg, mdl_name, name)
    init_grid2d_cornerpoint(g2, dims, org, clen)
    return g2

def init_grid2d_irregular(g2, dims, org, clen):
    """    
    dims - grid dimensions, array: [ni, nj]
    org - grid origin point coords, array: [ox, oy]    
    clen - cell length, array [dx, dy]
    """    
    ed = g2.getEditor()

    ni = dims[0]
    nj = dims[1]

    
    ed.setCellCountI(ni)
    ed.setCellCountJ(nj)
    
    ox = org[0]
    oy = org[1]
    
    dx = clen[0]
    dy = clen[1]
    
    n = (ni+1)*(nj+1)
    vx = [0.]*n
    vy = [0.]*n

    ind = 0
    for j in range(nj+1):
        ty = oy + j*dy
        for i in range(ni+1):
            tx = ox + i*dx
            
            vx[ind] = tx
            vy[ind] = ty

            ind += 1
    
    vx = du.to_r32_vec(vx)
    vy = du.to_r32_vec(vy)
    
    ed.initIrregular(ni, nj, vx, vy)
    
def init_grid2d_cornerpoint(g2, dims, org, clen):
    """    
    dims - grid dimensions, array: [ni, nj]
    org - grid origin point coords, array: [ox, oy]    
    clen - cell length, array [dx, dy]
    """    
    ed = g2.getEditor()

    #
    # grid2d в формате corner point уложен как values2d<point2d>, размерностью 2*nci x 2*ncj
    # поэтому такая странная укладка узлов по индексам в одномерные массивы
    
    ni = dims[0]
    nj = dims[1]
    
    ed.setCellCountI(ni)
    ed.setCellCountJ(nj)
    
    ox = org[0]
    oy = org[1]
    
    dx = clen[0]
    dy = clen[1]
    
    ncell = ni*nj
    vsz = ncell*4
    vx = [0.]*vsz
    vy = [0.]*vsz

    for j in range(nj):
        ty = oy + j*dy
        for i in range(ni):
            tx = ox + i*dx

            jj = 2*j
            ii = 2*i

            ind0 = jj*2*ni + ii
            ind1 = jj*2*ni + ii+1
            ind2 = (jj+1)*2*ni + ii
            ind3 = (jj+1)*2*ni + ii+1
            
            vx[ind0] = tx
            vy[ind0] = ty

            vx[ind1] = tx + dx
            vy[ind1] = ty

            vx[ind2] = tx
            vy[ind2] = ty + dy

            vx[ind3] = tx + dx
            vy[ind3] = ty + dy

    
    vx = du.to_r32_vec(vx)
    vy = du.to_r32_vec(vy)
    
    ed.initCornerpoint(ni, nj, vx, vy)
    