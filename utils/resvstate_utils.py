# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv

import data_utils as du
import entity_utils as eu
import table_utils as tu
import range_utils as ru
import prod_utils as pu

import math
import operator

#typedef bh dm.IBorehole
#typedef evs dm.IResvstateEvents

#typedef prod dmsrv.production

def put_changes(evs):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return evs.save(tctx, terr)

def get_resvstate_data(bh):
    """
    returns resvstate events
    """
    if bh is None:
        return None

    strg = bh.getDMO().getDataStorage()
    if strg is None:
        return None
    
    bhid = bh.getID()
    
    evs = dm.IResvstateEvents.make(dm.db_caching)

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    
    evs.load(strg, bhid, tctx, terr)

    return evs

def calculate_resvstate_data(bh, prod=None):
    """
    calculates resvstate data by monthly production
    """
    
    if prod is None:
        prod = pu.get_production_monthly(bh)

    if prod is None:
        return False
    
    if prod.rowCount()==0:
        return True
    
    evs = get_resvstate_data(bh)

    evs.delAll()

    terr = cmn.err_info()
    
    b = dmsrv.calc_resvstate(prod, evs, terr)

    put_changes(evs)
    
    return b