# -*- coding: cp1251 -*-
import pickle
import io
import mod_cmn as cmn
import mod_dm as dm
import mod_dmsrv as dmsrv

import matplotlib
import matplotlib.pyplot as plt

#typedef rec dmsrv.navigate_record

def make_nts(lst):
    vnt = dm.vec_node_type()
    for nt in lst:
        vnt.append(nt)
    return dm.node_types(vnt)

def append_nav_rec(dd, nt, tbl, fld, kind, bSingle):
    """
    добавляем navigate_record к doc_desc
    """
    rec = make_nav_rec(nt, tbl, fld, kind, bSingle)
    dd.navigate_rules.append(rec)
    
def make_nav_rec(nt, tbl, fld, kind, bSingle):
    """
    возврящает navigate_record
    """
    rec = dmsrv.navigate_record()
    rec.nt = nt
    rec.table_name = tbl
    rec.field_name = fld
    rec.m_kind = kind
    rec.bSingle = bSingle
    rec.bMulti = not bSingle
    
    return rec
    
    
def store_data(d):
    """
    d - some "data" view data object
    """
    blob = cmn.blob_t()

    bin = pickle.dumps(d)
    for b in bin:
        blob.append(b)

    return blob

def load_data(blob):
    """
    blob - blob_t
    returns some "data" view data object
    """    
    obj = None

    if len(blob)>0:
        lst = []
        for b in blob:
            if b<0:
                b = 256+b
            lst.append(b)
            
        bin = bytes(lst)
        
        obj = pickle.loads(bin)       
        
    return obj


def take_png(py_ctx):

    py_ctx.pvctx.m_rdr_result = cmn.blob_t()
    
    imgdata = io.BytesIO()
    plt.savefig(imgdata, format='png')
    bin = imgdata.getvalue()

    for b in bin:
        py_ctx.pvctx.m_rdr_result.append(b)

    return True

