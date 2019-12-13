# -*- coding: cp1251 -*-


import sys
import math
import operator
import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv
import data_utils as du
import entity_utils as eu
import table_utils as tu
import range_utils as ru

#typedef bh dm.IBorehole
#typedef tbgs dm.ITubingEvents
#typedef tbg  dm.ITubingEvent

def put_changes(tbgs):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return tbgs.save(tctx, terr)
    
def get_tubings(bh):
    """
    returns tubings data for given borehole
    """
    if bh is None:
        return None

    strg = bh.getDMO().getDataStorage()
    if strg is None:
        return None
    
    tbgs = dm.ITubingEvents.make(dm.db_caching)

    if tbgs is None:
        return None

    bhid = bh.getID()

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    b = tbgs.load(strg, bhid, tctx, terr)
    if b==False:
        return None

    return tbgs

def append_tubing(tbgs, md, dt):
    """
    append new tubings installation event
    returns new item
    """
   
    if tbgs is None:
        return None
    
    itm = tbgs.appendInstallEv(dt, md)
    return itm
