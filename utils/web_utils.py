# some funcs that are used in rv-web
#
import entity_utils as eu

import mod_dm as dm
import mod_cmn as cmn

def getFields(strg):
    items = dm.vec_field_t()
    strg.getRegHelper().getFieldRegistry().getElems(items)
    d = dict()
    for fld in items:
        d[fld.getID()] = fld.getName()
    return d

def getModels(strg):
    items = dm.vec_model_t()
    strg.getRegHelper().getModelRegistry().getElems(items)
    d = dict()

    for obj in items:
        d[obj.getID()] = obj.getName()
    return d

def getModels3D(strg):
    """
        returns models with 3D grids inside
    """
    items = dm.vec_model_t()
    strg.getRegHelper().getModelRegistry().getElems(items)
    d = dict()

    for obj in items:
        vg3 = dm.vec_grid3d_t()
        obj.getGrids3D(vg3)
        if len(vg3)>0:
            d[obj.getID()] = obj.getName()
    return d

def getSeismic(strg):
    items = dm.vec_seis_dataset()
    strg.getRegHelper().getSeisRegistry().getElems(items)
    d = dict()
    for obj in items:
        name = obj.getName()
        if obj.getGeomType() == 3:
            name = name + "(3d)"
        else:
            name = name + "(2d)"
        d[obj.getID()] = name
    return d

def getContours(strg):
    items = dm.vec_contourset_t()
    strg.getRegHelper().getContourRegistry().getElems(items)
    d = dict()
    for obj in items:
        d[obj.getID()] = obj.getName()
    return d

def getSurfaces(strg):
    items = dm.vec_surface_t()
    strg.getRegHelper().getSurfaceRegistry().getElems(items)
    d = dict()
    for obj in items:
        d[obj.getID()] = obj.getName()
    return d

def getProfiles(strg):
    items = dm.vec_profile_t()
    strg.getRegHelper().getProfileRegistry().getElems(items)
    d = dict()
    for obj in items:
        d[obj.getID()] = obj.getName()
    return d

def getBoreholes(strg, fld_id):
    d = dict()
    bhlist = eu.getBoreholesByField(strg, fld_id)
    for bh in bhlist:
        d[bh.getID()] = bh.getName()
    return d

def getHorizons(strg, fld_id):
    d = dict()
    hrzlist = eu.getHorizonsByField(strg, fld_id)
    for hrz in hrzlist:
        d[hrz.getID()] = hrz.getName()
    return d

def getStratums(strg, fld_id):
    d = dict()
    rsvlist = eu.getStratumsByField(strg, fld_id)
    for rsv in rsvlist:
        d[rsv.getID()] = rsv.getName()
    return d

def getReservoirs(strg, fld_id):
    d = dict()        
    rsvlist = eu.getReservoirsByField(strg, fld_id)
    for rsv in rsvlist:
        d[rsv.getID()] = rsv.getName()
    return d

#--------------
def getCubes(strg, mdl_id):
    """
    returns static cubes
    """
    d = dict()
    #print('get cubes, model_id:', mdl_id) #debug

    lst_cubes = eu.getCubesByModel(strg, mdl_id)
    for cube in lst_cubes:
        d[cube.getID()] = cube.getMnemo()
    return d

def getDynCubes(strg, mdl_id):
    """
    returns dynamic cubes
    """
    d = dict()
    #print('get dyncubes, model_id:', mdl_id) #debug

    lst_cubes = eu.getDynCubesByModel(strg, mdl_id)
    for cube in lst_cubes:
        d[cube.getID()] = cube.getMnemo()
    return d

def getParams2D(strg, mdl_id):
    """
    returns static cubes
    """
    d = dict()
    #print('get cubes, model_id:', mdl_id) #debug

    lst_cubes = eu.getParams2DByModel(strg, mdl_id)
    for cube in lst_cubes:
        d[cube.getID()] = cube.getMnemo()
    return d

def getDynParams2D(strg, mdl_id):
    """
    returns dynamic cubes
    """
    d = dict()
    #print('get dyncubes, model_id:', mdl_id) #debug

    lst_cubes = eu.getDynParams2DByModel(strg, mdl_id)
    for cube in lst_cubes:
        d[cube.getID()] = cube.getMnemo()
    return d

def getTimesteps(strg, mdl_id):
    """
    returns timesteps
    """
    d = dict()
    #print('get timesteps, model_id:', mdl_id) #debug

    lst_tsteps = eu.getTimestepsByModel(strg, mdl_id)
    for tstep in lst_tsteps:
        d[tstep.getID()] = tstep.getName()
    return d

def get_set_from_list(lst):
    res = cmn.set_i32_t()
    for x in lst:
        res.insert(int(x))
    return res

def calc_strg_key(strg):
    if strg is None:
        return "strg0";

    ts = strg.getPath();
    if len(ts)==0:
        ts = "empty";

    ts = ts.replace('/','_')
    ts = ts.replace('.','_')    
    ts = ts.replace(':','')

    return ts
