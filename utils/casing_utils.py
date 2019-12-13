# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dmsrv as dmsrv

import data_utils as du
import entity_utils as eu
import table_utils as tu
import range_utils as ru

import sys
import math
import operator

#typedef bh dm.IBorehole

#typedef cdata dm.IWellConstruction
#typedef cstr dm.ICasingString
#typedef cstrs dm.ICasingStrings

#typedef csec dm.ICasingSection

def put_changes(cdata):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return cdata.save(tctx, terr)
    
def get_casing(bh):
    """
    returns casing data (IWellConstruction) for given borehole
    """
    if bh is None:
        return None

    strg = bh.getDMO().getDataStorage()
    if strg is None:
        return None
    
    cdata = dm.IWellConstruction.make(dm.db_caching)

    if cdata is None:
        return None

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    bhid = bh.getID()
    
    b = cdata.load(strg, bhid, tctx, terr)
    if b==False:
        return None

    return cdata

def append_casing(cdata, ctype, md_top, md_base, dt):
    """
    append new casing string
    returns new item
    """
   
    if cdata is None:
        return None

    cstrs = cdata.getCasingStrings()
    
    cstr = cstrs.appendCasingString(ctype, md_top, md_base)
    cstr.setDate(dt)
    
    return cstr
