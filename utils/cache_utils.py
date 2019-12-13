# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db

import data_utils as du
import entity_utils as eu

import sys
import math

#typedef bh dm.IBorehole
#typedef fld dm.IField

#typedef strg dm.IDataStorage
#typedef dman dm.data_manager
#typedef nav dm.NavigatorImpl

def preload_data(strg, fld_id, dcat):
    """
    caches given data category for all boreholes of field "fld_id"
    """
    fld = eu.find_field(strg, fld_id)
    if fld is None:
        return False

    vbh = dm.vec_borehole_t()
    fld.getBoreholes(vbh)
    vids = cmn.vec_i32_t()
##    for bh in vbh:
##        vids.append(bh.getID())

    dm.get_vids(vbh, vids)
    nav = dm.NavigatorImpl()
    nav.append_boreholes(strg, vids, True)

    terr = cmn.err_info()
    b = dm.preload_data_category(strg, nav, dcat, terr)
    return b
