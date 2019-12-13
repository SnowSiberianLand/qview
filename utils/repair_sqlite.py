# -*- coding: cp1251 -*-

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv


import os
import sys
from subprocess import call

import shutil

def is_debug_mode():
    return False

class repair_ctx:
    def __init__(self, _fname):
        self.fname = _fname
        app = cmn.getAppOptions()
        self.temp_folder = app.getTempFolder()
        self.app_folder = app.getApplicationPath()
        self.app_path = self.app_folder + "sqlite3.exe"

        self.verify_temp_folder()
        
        self.sql_file = self.temp_folder+"dump.sql"

        if is_debug_mode():
            print("database path",self.fname)
            print("temp folder",self.temp_folder)
            print("app folder",self.app_folder)
            print("sqlite folder",self.app_path)

    def verify_temp_folder(self):
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

    def delete_temp_folder(self):
        shutil.rmtree(self.temp_folder)
    

def export_to_sql(rctx):
    cmd_arg = '\"{0}\"  \"{1}\" ".dump"'.format(rctx.app_path, rctx.fname)

    if is_debug_mode():
        print(cmd_arg)

    with open(rctx.sql_file, "w") as outfile:
        call(cmd_arg, stdout=outfile,shell=True)

def backup_original(rctx, err):
    base=os.path.basename(rctx.fname)
    d = os.path.splitext(base)

    db_fname = d[0]
    db_extention = d[1]

    dirr = os.path.dirname(rctx.fname)

    backup_fname = dirr+"/"+db_fname+"_copy"+db_extention

    b = os.path.isfile(backup_fname)
    bOk = False

    if b==True:
        for i in range(100):
            backup_fname = dirr+"/"+db_fname+"_copy_"+str(i)+db_extention
            b = os.path.isfile(backup_fname)
            if b==False:
                bOk = True
                break
    else:
        bOk = True

    if bOk==False:
        err.msg = "Cant get backup file name"
        return False

    try:
        #print("move file:", rctx.fname, backup_fname)
        shutil.move(rctx.fname, backup_fname)
    except (IOError, os.error) as why:
        err.msg = "Create backup file error: src file {0}, backup file: {1}, Error: {2}".format(rctx.fname, backup_fname,str(why))
        return False

    return True

def restore_db(rctx):
    cmd_arg = '\"{0}\" -init \"{1}\" \"{2}\" ""'.format(rctx.app_path,rctx.sql_file, rctx.fname)
    if is_debug_mode():
        print(cmd_arg)
    call(cmd_arg, shell=True)


def repair_sqlite(ctx, res, progress):

    logger = ctx.opo.lo.logger
    
    with progress.sub_task(5.) as sub1:
        dmsrv.py_log_info(logger, "Prepare ...")
        rctx = repair_ctx(ctx.path)

    bExist = os.path.isfile(rctx.app_path)
    if bExist==False:
        dmsrv.py_log_error(logger, "Cant find sqlite3.exe...")
        return False

    with progress.sub_task(30.) as sub2:
        dmsrv.py_log_info(logger, "Export to sql...")
        export_to_sql(rctx)


    b=True
    dmsrv.py_log_info(logger, "Backup source database...")
    with progress.sub_task(30.) as sub3:
        b = backup_original(rctx, res.err)

    if False==b:
        dmsrv.py_log_error(logger, res.err)
        rctx.delete_temp_folder()
        return False

    with progress.sub_task(30.) as sub4:
        dmsrv.py_log_info(logger, "Restore database...")
        restore_db(rctx)

    with progress.sub_task(5.) as sub5:
        dmsrv.py_log_info(logger, "Delete temporary files...")
        rctx.delete_temp_folder()

    dmsrv.py_log_info(logger, "Repair complete")
    return True


if __name__ == '__main__':

    import os
    import db_utils

    import builtins
    builtins.__dict__['_'] = lambda s : s

    cmn.app_init_paths("../../../../../build/win64/bin/release/")
    db.init_loggers()
    dproc.init_lib_dproc()

    ctx = dmsrv.python_ctx()
    res = dmsrv.python_results()
    ctx.path = "c:/db/Mailformed/agav_vata_03015.rds"

    progress = cmn.progress_ctx()

    repair_sqlite(ctx, res, progress)
