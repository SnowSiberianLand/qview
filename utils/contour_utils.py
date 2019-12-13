# -*- coding: cp1251 -*-

# for command-line call
#import path_release_x64

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv
import mod_math as mm

import data_utils as du
import entity_utils as eu

import math

#typedef ctx.ents dm.entities
#typedef dp_def dproc.dproc_def
#typedef cs_prms dm.recalc_local_cs_opts
#typedef X cmn.vec_num_t
#typedef Y cmn.vec_num_t
#typedef v_cset dm.vec_contourset_t
#typedef cset dm.IContourSet
#typedef cont dm.IContour
#typedef curv dm.ICurve
#typedef curv_ed dm.ICurve.IEditor
#typedef cset_ed dm.IContourSet.IEditor
#typedef dmo dm.IDataObj

# ------------------------------------------------------------------
#

def seis2d_to_contours(strg, dset):
    vitm = dm.vec_seis_item()
    dset.getSeisItems(vitm)

    lst = []
    m = len(vitm)
    print('Seismic dataset: {0}, item count: {1}'.format(dset.getName(), m))

    m = len(vitm)
    for j in range(m):

        itm = vitm[j]
        
        if itm.getGeomType()!=2: # working with 2D only
            continue
        
        print('Seismic item: {0}, type: {1}, trace count: {2}'.format(itm.getName(), itm.getGeomType(), itm.getTraceCount()))

        vx = cmn.vec_num_t()
        vy = cmn.vec_num_t()
        itm.getAllTracesCoords(vx, vy)

        name = "{0}_{1}".format(dset.getName(), j)
        
        cset = make_contour_vxvy(strg, name, vx, vy, False)

        lst.append(dset)

    return lst

def trace_contour_points(cset):
    ni = cset.getElemCount()
    print( "--------- Contour:{0}".format(cset.getName()) )
    print(("Item count = {0}, Xmin = {1}, Xmax = {2} Ymin = {3}, Ymax = {4}".format(ni, cset.getXMin(), cset.getXMax(), cset.getYMin(), cset.getYMax())))
    for i in range(0,ni):
        ctr = cset.getElem(i)

        vx = cmn.vec_num_t()
        vy = cmn.vec_num_t()
        ctr.getData(vx, vy)

        np = len(vx)
        print(("Item {0}, point count: {1}".format(i, np)))
        print("Points:")
        for k in range(0,np):
            print( '\t {0:.2f} {1:.2f}'.format(vx[k], vy[k]) ) # X, Y    
            
def make_contour_vxvy(strg, name, vx, vy, closed=False):
    cset = eu.verifyContour(strg, name)

    vp = mm.vec_point2d()
    n = min(len(vx), len(vy))
    for k in range(n):
        tx = vx[k]
        ty = vy[k]
        if cmn.is_undefined(tx) or cmn.is_undefined(ty):
            continue
        
        vp.append(mm.point2d(tx,ty))
                
    return make_contour(strg, name, vp, closed)

def make_contour(strg, name, vp, closed=False):
    cset = eu.verifyContour(strg, name)

    ed_cset = cset.getEditor()
    ed_cset.clear()

    ctr = ed_cset.addItem(name, vp)
    if closed:
        ctr.makeClosed()
        
    return cset

def make_outline_cset(cset, w):
    """
    создаем новый contourset, содержащий оболочку для каждого из элементов cset
    w - ширина оболочки
    """

    dmo = cset.getDMO()
    strg = dmo.getDataStorage()
    
    cset_dst = None
   
    n = cset.getElemCount()
    for i in range(n):
        ctr = cset.getElem(i)
       
        vp = mm.vec_point2d()
        vp2 = mm.vec_point2d()
        ctr.getPoints(vp)
        mm.make_outline(vp, vp2, w)

        cname = cset.getName() + '_outline'

        if None==cset_dst:
            ex_cset_dst = eu.findContourByName(strg, cname)
        
            if None != ex_cset_dst:
                ed_cset = cset.getEditor()
                ed_cset.clear()

                cset_dst = ex_cset_dst
        
        if None==cset_dst:
            cset_dst = dm.makeContourSetByPoints(strg, vp2, cname, cmn.get_undefined_r64(), None, None)
        else:
            dm.appendContourByPoints(cset_dst, vp2, cname, cmn.get_undefined_r64(), None, None)
        
    return cset_dst
