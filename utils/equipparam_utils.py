# -*- coding: cp1251 -*-
import mod_dm as dm
import mod_cmn as cmn
import mod_dmsrv as dmsrv

import table_utils as tu
import table_utils2 as tu2


def is_paker(ctx,bh,date):
    status = False

    bhlist = dm.vec_borehole_t()
    bh_reg = ctx.pStorage.getRegHelper().getBoreholeRegistry()
    
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'EVENT_DATE']
    table = tu2.makeTableController("PACKER_TABLE", ctx.pStorage, layer)
    if table is None:
        return status
    
    bhlist.append(bh)
    tu2.refreshTable(table, ctx.pStorage, bhlist, pctx=cmn.progress_ctx())
    
    if table.getRowCount()==0:
        return status
    else:
        for i in range(table.getRowCount()):
            dt   = tu.getDate2('EVENT_DATE',   i, table)
            if dt.day_number() >= date.day_number():
                if tu.getNum2('PACKER_OP_TYPE',   i, table)==0:
                    status=True
                    break
    return status

def get_d_diaf(ctx,bh,date):
    d_diaf = cmn.get_undefined_r32()

    bhlist = dm.vec_borehole_t()
    bh_reg = ctx.pStorage.getRegHelper().getBoreholeRegistry()
    
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'EVENT_DATE']
    table = tu2.makeTableController("WELLHEAD_EQUIP_TABLE", ctx.pStorage, layer)
    if table is None:
        return d_diaf
    
    bhlist.append(bh)
    tu2.refreshTable(table, ctx.pStorage, bhlist, pctx=cmn.progress_ctx())
    
    if table.getRowCount()==0:
        return d_diaf
    else:
        for i in range(table.getRowCount()):
            if date.day_number()>= (tu.getDate2('EVENT_DATE', i, table)).day_number():
                if not cmn.is_undefined(tu.getDate2('EQ_DISMANTLING_DATE', i, table)):
                    if date.day_number()< (tu.getDate2('EQ_DISMANTLING_DATE', i, table)).day_number():
                        d_diaf = tu.getNum2('EQ_ORIF_DINNER', i, table)
                    else:
                        d_diaf = cmn.get_undefined_r32()
                else:
                    d_diaf = tu.getNum2('EQ_ORIF_DINNER', i, table)
                break
    return d_diaf

##diam = tu.getNum2('PACKER_OP_TYPE',   i, table)