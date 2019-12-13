# -*- coding: cp1251 -*-
import mod_dm as dm
import mod_cmn as cmn
import mod_dmsrv as dmsrv
import table_utils2 as tu


def get_dictionary(strg: dm.IDataStorage, prop_mnemo: str):
    import data_utils as du
    meta = dm.getMetaHelper(strg)
    if meta is None:
        return None
    dic_reg = meta.getDicRegistry()
    if dic_reg is None:
        return None
    pd = du.get_property_desc(strg, prop_mnemo)
    dic = None
    if not (pd is None):
        dic = dic_reg.find(pd.getID())
    return dic


def if_valid(value):
    if cmn.is_undefined(value):
        return False
    else:
        return True


def get_status(iwell: dm.IBorehole, strg: dm.IDataStorage):
    global status, cat
    dthlp = dm.getDataProcessing().getDataTreatHelper()
    wellstates = dthlp.makeWellStateEvents(dm.db_caching)
    drct_dict = get_dictionary(strg, 'BH_CATEGORY')  # type: dm.IDictionary
    drctstate_dict = get_dictionary(strg, 'BH_STATUS')

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    cat = ''
    status = ''
    b = wellstates.load(strg, iwell.getID(), tctx, terr)
    if b:
        if wellstates.size() > 0:
            wellstate = wellstates.at(wellstates.size())
            if wellstate is not None:
                cat = wellstate.getCategory()
                if not cmn.is_undefined(cat) and drct_dict is not None:
                    itm = drct_dict.find(cat)  # type: dm.IDicItem
                    cat = itm.getShortName()
                else:
                    cat = str(cat)
                status = wellstate.getStatus()
                if not cmn.is_undefined(status) and drctstate_dict is not None:
                    itm = drct_dict.find(drctstate_dict)  # type: dm.IDicItem
                    status = itm.getShortName()
                else:
                    status = str(status)
    return {'cat': cat, 'status': status}


def check_open_or_closed(bridge, std_vec):
    bridge, bridge_status = bridge, 0
    for std in std_vec:
        pass
    return bridge, bridge_status


def float_(value: object) -> float:
    if value == '':
        return 0.0
    else:
        return float(value)


def create_table_nkt(red, bh):
    print("Read construction data well {0}...".format(bh.getName()))
    layers = ['BOREHOLE_ID', 'EVENT_DATE', 'TUB_OP_TYPE', 'TUB_ASSAMBLY', 'TUB_NUM', 'TUB_BASE_MD', 'TUB_INTD', 'TUB_OUTD', 'TUB_REMARKS']
    table_nodinamyc_constraction = tu.makeTableController('TUBING_TABLE', red, layers)  # type:dmsrv.CommonController
    tu.refreshTable(table_nodinamyc_constraction, red, [bh], cmn.progress_ctx())
    tu.sortTable(table_nodinamyc_constraction, 'EVENT_DATE', 'BOREHOLE_ID', 'TUB_ASSEMBLY', 'TUB_NUM')
    table_count = table_nodinamyc_constraction.getRowCount()
    if table_nodinamyc_constraction is None:
        print("Nkt table wasn't found.")
        return table_nodinamyc_constraction
    if table_count == 0:
        print("No nkt constraction data for select well: {0}".format(bh.getName()))
        return table_nodinamyc_constraction
    return table_nodinamyc_constraction


def create_table_dynamic_constraction(red, bh):
    print ("Create table with packer data...")
    name_of_table = "PACKER_TABLE"
    layers = ["BOREHOLE_ID", "EVENT_DATE", "PACKER_OP_TYPE", "PACKER_MD", "PACKER_LENGTH"]
    table_packers = tu.makeTableController(name_of_table, red, layers)
    tu.refreshTable(table_packers, red, [bh], cmn.progress_ctx())
    tu.sortTable(table_packers, 'BOREHOLE_ID', 'EVENT_DATE', 'PACKER_OP_TYPE')
    if table_packers is None:
        print("Nkt table wasn't found.")
        return table_packers
    if table_packers.getRowCount() == 0:
        print("No packer data for this borehole: {0}".format(bh.getName()))
        return table_packers
    return table_packers


def check_cross_ival(ivals, tube, top=0):
    for iva in ivals:
        if top <= iva['Top'] <= tube:
            iva['OnTube'] = True
            continue
    return True


def check_cross_flow(iflows, tube, top=0):
    out = []
    for flow in iflows:
        if flow['Bottom'] <= tube or flow['Top'] <= tube:
            out.append(flow)
        else:
            continue
    return out


def check_value(value):
    undef_value = None  # type: None
    try:
        value = int(value)
        undef_value = int()
    except ValueError:
        try:
            value = float(value)
            undef_value = float()
        except ValueError:
            value = str(value)
            undef_value = str()
    if cmn.is_undefined(value):
        return undef_value
    else:
        return value


def uncheck_value(value):
    if value == str():
        return cmn.get_undefined_string()
    elif value == float():
        return cmn.get_undefined_r32()
    elif value == int():
        return cmn.get_undefined_i32()
    else:
        return value