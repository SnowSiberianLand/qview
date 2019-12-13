
import mod_cmn as cmn
import mod_dm as dm


def findBorehole(strg, fld_name, bh_name):
    """
	fld_name is unicode
    bh_name is unicode
    """

    #print(fld_name, bh_name)

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.findByName(fld_name)
    if fld is None:
        return None

    reg_bh = strg.getRegHelper().getBoreholeRegistry()
    bh = reg_bh.findByNameAndField(fld.getID(), bh_name)

    return bh


def getBoreholesByField(strg, fld_name):
    """
    """

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.findByName(fld_name)
    if fld is None:
        return None

    vbh = dm.vec_borehole_t()
    fld.getBoreholes(vbh)

    return vbh


def findBoreholes(strg, fld_name, bhlist):
    """
    find boreholes by comma-delimetered borehole names, e.g. "1,2,5,..."
    """

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.findByName(fld_name)
    if fld is None:
        return None

    vbh = dm.vec_borehole_t()

    reg_bh = strg.getRegHelper().getBoreholeRegistry()

    for bhname in bhlist.split(","):
        bh = reg_bh.findByNameAndField(fld.getID(), bhname)
        if bh is not None:
            vbh.append(bh)

    return vbh

# !!! todo: copy to mainline
def getBoreholesByFieldID(strg, fld_id):
    """
    """

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.find(fld_id)
    if fld is None:
        return None

    vbh = dm.vec_borehole_t()
    fld.getBoreholes(vbh)

    return vbh

# !!! todo: copy to mainline
def getHorizonsByFieldID(strg, fld_id):
    """
    """

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.find(fld_id)
    if fld is None:
        return None

    vhrz = dm.vec_horizon_t()
    fld.getHorizons(vhrz)

    return vhrz

# !!! todo: copy to mainline
def getReservoirsByFieldID(strg, fld_id):
    """
    """

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.find(fld_id)
    if fld is None:
        return None

    vrsv = dm.vec_reservoir_t()
    fld.getReservoirs(vrsv)

    return vrsv

def getStratumsByFieldID(strg, fld_id):
    """
    """
    #print("getStratums STARTED")
    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.find(fld_id)
    if fld is None:
        return None

    vrsv = dm.vec_geolayer_t()
    fld.getGeoLayers(vrsv)

    return vrsv

def findModel(strg, name):
    """
    """
    model = strg.getRegHelper().getModelRegistry().findByName(name)
    return model

def findHorizon(strg, fld_name, horz_name):
    """
	fld_name is unicode
    horz_name is unicode
    """

    #print(fld_name, horz_name)

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.findByName(fld_name)
    if fld is None:
        return None

    reg = strg.getRegHelper().getHorizonRegistry()
    horz = reg.findByNameAndField(fld.getID(), horz_name)

    return horz
