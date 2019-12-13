import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv

import data_utils as du
import entity_utils as eu
import table_utils as tu
import range_utils as ru

import sys
import math
import operator

#typedef bh dm.IBorehole

#typedef pkrs dm.IPackerEvents
#typedef pkr  dm.IPackerEvent

def print_packer(strg, pkr):   
    dt = pkr.getDate()
    sdt = cmn.to_string_date(dt)
    
    md = pkr.getMD()
    sz = pkr.getSize()
    stype = du.get_dic_string(strg, 'PACKER_TYPE', pkr.getType())
    diam = pkr.getInsDiam()
    smat = du.get_dic_string(strg, 'PACKER_MATERIAL', pkr.getMaterial())
    
    if pkr.getOpType()==dm.packer_op_install:
        print(sdt, 'Install', '{0:.2f}'.format(md), stype, '{0:.2f}'.format(sz), '{0:.2f}'.format(diam), smat)
    else:
        print(sdt, 'Removal')
        
def put_changes(pkrs):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return pkrs.save(tctx, terr)
    
def get_packers(bh):
    """
    returns packers data for given borehole
    """
    if bh is None:
        return None

    strg = bh.getDMO().getDataStorage()
    if strg is None:
        return None
    
    pkrs = dm.IPackerEvents.make(dm.db_caching)

    if pkrs is None:
        return None

    bhid = bh.getID()

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    b = pkrs.load(strg, bhid, tctx, terr)
    if b==False:
        return None

    return pkrs