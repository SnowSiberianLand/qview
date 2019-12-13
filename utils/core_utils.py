import mod_dm as dm
import mod_dmsrv as dmsrv
import mod_cmn as cmn
import entity_utils as eu
import data_utils as du
import sys

#typedef strg dm.IDataStorage
#typedef cda dm.ICoreData
#typedef sam dm.ICoreSample
#typedef sams dm.ICoreSamples


def get_core_data(strg, bh):
    """
    returns loaded dm.ICoreData instance for given borehole
    """
    cda = dm.ICoreData.make(dm.db_caching)

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    
    b = cda.load(strg, bh.getID(), True, True, True, tctx, terr)

    return cda

def put_changes(cda):
    """
    put changes to cache
    """
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    return cda.save(tctx, terr)

def make_image_blob(fname):
    with open(fname, mode='rb') as ff: # b is important -> binary
        fdata = ff.read()

    blob = cmn.blob_t()

    blen = len(fdata)
    if blen==0:
        print("can't load image file")
        return blob

    for b in fdata:
        blob.append(b)

    return blob
