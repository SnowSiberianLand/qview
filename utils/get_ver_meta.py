# -*- coding: cp1251 -*-



import path_release_x64 as mpath

import mod_cmn as cmn
import mod_orm as db
import sys

def make_iowrap(conn):
    """
        connection string should be like: oracle://rdm/1@agava, sqlite://c:\test1.rds
    """
    terr = cmn.err_info()
    tctx = cmn.progress_ctx()

    dbd = db.db_desc()
    b = db.string2db_desc(conn, dbd)
    if b==False:
        print("invalid connection string \"{0}\"".format(conn))
        return None

    wrap =  db.iowrap()

    copts = db.conn_opts()
    copts.enc_db = cmn.enc_cp1251
    res = wrap.connect(dbd.type, dbd.conn_str, copts, terr)
    
    if (res == False):
        print(terr.msg)
        return None

    return wrap


def get_meta_version(conn):
    """
        return META version
    """
    wrap = make_iowrap(conn)
    if (wrap is None):
        return None
    
    #print "connected to:{0}".format(conn)

    crud = wrap.getIO()

    sql = "SELECT VNUM1, VNUM2, VNUM3, VDATE from META_VERSION order by VNUM1, VNUM2, VNUM3"

    vtbl = db.vtable_wrap()

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    res = crud.load(sql, vtbl, tctx, terr)
    if (res==False):
        print("table META_VERSION isn't exist")
        return None

    nrow = vtbl.rowCount()
    if (nrow==0):
        print("table META_VERSION is empty")
        return None        

    vnum3 = vtbl.get_i32_t(nrow-1,"VNUM3")

    return vnum3


if __name__ == '__main__':
    
    cmn.app_init_paths(mpath.binPath())

    db.init_loggers()
#    dproc.init_lib_dproc()

    narg = len(sys.argv)
    if (narg<2):
        print('empty connection string')
        exit(1)

    conn = sys.argv[1]
    
    vnum3 = get_meta_version(conn)

    if vnum3 is None:
        exit(1)

    print(vnum3)
    exit(0)