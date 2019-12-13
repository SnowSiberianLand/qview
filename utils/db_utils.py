
import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db

#typedef strg dm.IDataStorage
#typedef dsrc dm.dsrc_desc


def make_DataStorage(dbtype, connstr, meta = ""):
    """
    """
    strg = dm.makeDataStorageExp("rdm")
    if strg is None:
        print("Can't make new DataStorage instance")
        return None

    progress_ctx = cmn.progress_ctx()
    conn_opts = db.conn_opts()
    err_info = cmn.err_info()

    dd = dm.dsrc_desc()
    dd.init(dm.dsrc_rds, db.glue_datasource_path(dbtype, connstr), meta)

    if False==strg.connect(progress_ctx, dd, conn_opts, False, err_info):
        print(err_info.msg)
        return None

    return strg

def openTargetRDS(dbtype, connstr, meta = ""):
    """
    """
    strg = dm.makeDataStorageExp("rdm")
    if strg is None:
        print("Can't make new DataStorage instance")
        return None

    progress_ctx = cmn.progress_ctx()
    conn_opts = db.conn_opts()
    conn_opts.bCreateNew = True

    err_info = cmn.err_info()

    dd = dm.dsrc_desc()
    dd.init(dm.dsrc_rds, db.glue_datasource_path(dbtype, connstr), meta)

    if False==strg.connect(progress_ctx, dd, conn_opts, False, err_info):
        print(err_info.msg)
        return None

    return strg


def openDB(conn, meta = ""):
    """
    """

    strg = dm.makeDataStorageExp("rdm")
    if strg is None:
        return None

    progress_ctx = cmn.progress_ctx()
    conn_opts = db.conn_opts()
    err_info = cmn.err_info()

    dd = dm.dsrc_desc()
    if False==dd.init(dm.dsrc_rds, conn, meta):
       print("dsrc_desc init error")
       return None

    if False==strg.connect(progress_ctx, dd, conn_opts, False, err_info):
        print(err_info.msg)
        return None

    return strg


def getReflectClass(strg, mnemo):
    scheme = strg.getSchemeName()
    cls = db.find_cls(scheme, mnemo)
    return cls


def getReflectField(cls, mnemo):
    rf = cls.getFieldByColname(mnemo)
    return rf


def getRowcache(strg, rcs, mnemo):
    cls = getReflectClass(strg, mnemo)
    rc = rcs.find(cls)
    return rc
