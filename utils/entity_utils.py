# -*- coding: cp1251 -*-


import mod_cmn as cmn
import mod_dm as dm
import mod_dmsrv as dmsrv

#typedef th dm.ITrajectoryHelper
#typedef node dm.INode
#typedef rh dm.IRegistryHelper

def find_borehole(strg, borehole_id):
    """
    """
    bh = strg.getRegHelper().getBoreholeRegistry().find(borehole_id)
    return bh

def findHorizonByName(strg, fld, horz_name):
    if fld is None:
        return None

    reg = strg.getRegHelper().getHorizonRegistry()
    horz = reg.findByNameAndField(fld.getID(), horz_name)

    return horz

def findFieldByName(strg, fld_name):
    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.findByName(fld_name)
    return fld

def getFirstModel(strg):
    reg_mdl = strg.getRegHelper().getModelRegistry()
    n = reg_mdl.getElemCount()
    if 0==n:
        return None

    return reg_mdl.getElem(0)

def getFirstField(strg):
    reg_fld = strg.getRegHelper().getFieldRegistry()
    n = reg_fld.getElemCount()
    if 0==n:
        return None

    return reg_fld.getElem(0)

def getFields(strg):
    reg_fld = strg.getRegHelper().getFieldRegistry()
    vtmp = dm.vec_field_t()
    reg_fld.getElems(vtmp)
    return vtmp

def findBoreholeByName(strg, fld, bh_name):
    if fld is None:
        return None

    reg_bh = strg.getRegHelper().getBoreholeRegistry()
    bh = reg_bh.findByNameAndField(fld.getID(), bh_name)

    return bh

def findPlannedBoreholeByName(strg, mdl, bh_name):
    if mdl is None:
        return None

    reg_bh = strg.getRegHelper().getBoreholeRegistry()
    bh = reg_bh.findByNameAndModel(mdl.getID(), bh_name)

    return bh

def findStratumByName(strg, fld, lay_name):
    if fld is None:
        return None

    reg = strg.getRegHelper().getGeoLayerRegistry()
    lay = reg.findByNameAndField(fld.getID(), lay_name)

    return lay

def findReservoirByName(strg, fld, lay_name):
    if fld is None:
        return None

    reg = strg.getRegHelper().getReservoirRegistry()
    lay = reg.findByNameAndField(fld.getID(), lay_name)

    return lay

def find_cluster(strg, cluster_id):
    """
    """
    cl = strg.getRegHelper().getClusterRegistry().find(cluster_id)
    return cl

def find_stratum(strg, stratum_id):
    """
    """
    lay = strg.getRegHelper().getGeoLayerRegistry().find(stratum_id)
    return lay

def findContourByName(strg, cname):
    """
    returns 1st contour with such name
    """
    vtmp = dm.vec_contourset_t()
    strg.getRegHelper().getContourRegistry().findByName(cname, vtmp)

    if len(vtmp)==0:
        return None
    
    return vtmp[0]

def find_horizon(strg, horizon_id):
    """
    """
    hrz = strg.getRegHelper().getHorizonRegistry().find(horizon_id)
    return hrz

def find_model(strg, model_id):
    """
    """
    mdl = strg.getRegHelper().getModelRegistry().find(model_id)
    return mdl

def find_field(strg, fld_id):
    """
    """
    fld = strg.getRegHelper().getFieldRegistry().find(fld_id)
    return fld

def findNodeName(strg, nt, id):
    node = dm.find_node(strg, nt, id)
    if not node is None:
        return node.getNodeName()
    return ""


def findModel(strg, name):
    """
    """        
    model = strg.getRegHelper().getModelRegistry().findByName(name)
    return model

def findModelByName(strg, name):
    """
    finds model by name
    """
    model = strg.getRegHelper().getModelRegistry().findByName(name)
    return model


def getGrid3D(model, index, data_load = True):
    """
    """
    strg = dm.getDataStorage(model)
    grids = dm.vec_grid3d_t()
    strg.getRegHelper().getGrid3DRegistry().findByModel(model.getID(), grids)
    grid = grids[index]
    if data_load:
        if not loadGridData(grid):
            return None
    return grid


def loadGridData(grid):
    if grid is None:
        return False
    #data = grid.getData()
    ctx = cmn.progress_ctx()
    err = cmn.err_info()
    return grid.loadData(ctx, err)


def loadCubeData(cube):
    if cube is None:
        return False
    #data = cube.getData()
    ctx = cmn.progress_ctx()
    err = cmn.err_info()
    return cube.loadData(ctx, err)


def loadSurfaceData(surf):
    if surf is None:
        return False
    ctx = cmn.progress_ctx()
    err = cmn.err_info()
    return surf.loadData(ctx, err)


def getCubeByName(grid, name, data_load = True):
    """
    """
    strg = dm.getDataStorage(grid)
    cube = strg.getRegHelper().getCubeRegistry().findByNameAndGrid(grid.getID(), name)
    if (data_load):
        loadCubeData(cube)
    return cube


def getCubeByMnemo(grid, mnemo, data_load = True):
    """
    """
    strg = dm.getDataStorage(grid)
    cube = strg.getRegHelper().getCubeRegistry().findByMnemoAndGrid(grid.getID(), mnemo)
    if (data_load):
        loadCubeData(cube)
    return cube


def getDynCubeByName(grid, name):
    """
    """
    strg = dm.getDataStorage(grid)
    dyncube = strg.getRegHelper().getDynCubeRegistry().findByNameAndGrid(grid.getID(), name)
    return dyncube


def getDynCubeByMnemo(grid, mnemo):
    """
    """
    strg = dm.getDataStorage(grid)
    dyncube = strg.getRegHelper().getDynCubeRegistry().findByMnemoAndGrid(grid.getID(), mnemo)
    return dyncube


def getContours(strg, name, model = None):
    """
    """
    reg = strg.getRegHelper().getContourRegistry()
    
    contours = dm.vec_contourset_t()

    if model is None:
        reg.findByName(name, contours)
    else:    
        cset = reg.findByNameAndModel(name, model.getID())        
        if cset is not None:
            contours.append(cset)

    return contours

def getFirstContourByName(strg, name, model = None):
    vctr = getContours(strg, name, model)
    
    n = len(vctr)
    if (0==n):
        return None
        
    # используем первый контур из найденных
    return vctr[0]

def getFirstSurfaceByName(strg, name, model = None):
    vctr = getSurfaces(strg, name, model)
    
    n = len(vctr)
    if (0==n):
        return None
        
    # используем первую поверхность из найденных
    return vctr[0]

def getSurfaces(strg, name, model = None, data_load = True):
    """
    """
    reg = strg.getRegHelper().getSurfaceRegistry()
    
    surfaces = dm.vec_surface_t()
    
    if model is None:
        reg.findByName(name, surfaces)
    else:
        surf = reg.findByNameAndModel(name, model.getID())
        if surf is not None:
            surfaces.append(surf)
            
    if data_load:
        for s in surfaces:
            loadSurfaceData(s)
    return surfaces

def getFirstSurfaceByName(strg, name, model = None, data_load = True):
    vsurf = getSurfaces(strg, name, model, data_load)
    n = len(vsurf)
    if (0==n):
        return None
    
    # используем первую поверхность из найденных
    return vsurf[0]


def getLogFrames(borehole_id, ctx, py_res):
    wlh = dm.getDataProcessing().getWellLogsHelper()
    lo = cmn.logger_opts()
    frames = cmn.set_i32_t()
    res = wlh.getLogFrames(ctx.pStorage, borehole_id, frames, lo, py_res.err)
    return frames


def getLogInterpFrame(bh_id, model_id, strg):
    """
    возвращает первый frame_id для <borehole_id, model_id>
    """
    res = dmsrv.python_results()
    fids = getLogresultFramesByModel(bh_id, model_id, strg, res)

    if fids is None:
        return None

    for fid in fids:
        return fid

    return None

def getLogInterpFrames(borehole_id, strg, py_res):
    """
    get all Log interp frame IDs by borehole
    """
    ents = dm.entities()
    ents.fill_certain_nodes(strg, dm.nt_model)
    models = ents.models()
    
    wlh = dm.getDataProcessing().getWellLogsHelper()
    lo = cmn.logger_opts()

    frames = cmn.set_i32_t()
    
    for model in models:
        tset = cmn.set_i32_t()
        res = wlh.getLogresultFrames(strg, borehole_id, model.getID(), tset, lo, py_res.err)

        for item in tset: 
            frames.add(item)
        
    return frames

def getLogresultFrames(borehole_id, model_id, ctx, py_res):
    return getLogresultFramesByModel(borehole_id, model_id, ctx.pStorage, py_res)

def getLogresultFramesByModel(borehole_id, model_id, strg, py_res):
    wlh = dm.getDataProcessing().getWellLogsHelper()
    lo = cmn.logger_opts()
    frames = cmn.set_i32_t()
    res = wlh.getLogresultFrames(strg, borehole_id, model_id, frames, lo, py_res.err)
    return frames

def load_frame(borehole_id, frame_id, dcat, ctx, py_res):
    ##wlh = dm.getDataProcessing().getWellLogsHelper()
    ##lo = cmn.logger_opts()
    ##wl = wlh.loadWellLogs(ctx.pStorage, borehole_id, welllog_id, lo, py_res.err)

    load_blobs = True
    prg_ctx = cmn.progress_ctx()

    dtreat = dm.getDataProcessing().getDataTreatHelper()
    logdata = dtreat.makeLogData(ctx.pStorage, dm.db_caching, dcat)
    logdata.load_by_frame(ctx.pStorage, borehole_id, frame_id, load_blobs, prg_ctx, py_res.err)

    return logdata

def load_loginterp_by_frame(borehole_id, frame_id, strg, py_res):
    ldata = dm.ILogData.make(strg, dm.db_caching, dm.cat_logresults)
    prg_ctx = cmn.progress_ctx()
    load_blobs = True
    b = ldata.load_by_frame(strg, borehole_id, frame_id, load_blobs, prg_ctx, py_res.err)
    return ldata

def load_loginterp_by_bh_and_model(borehole_id, model_id, strg, err):
    ldata = dm.ILogData.make(strg, dm.db_caching, dm.cat_logresults)
    prg_ctx = cmn.progress_ctx()
    load_blobs = True
    b = ldata.load(strg, borehole_id, model_id, prg_ctx, err)
    return ldata
    
def load_prodloginterp_by_bh_and_model(borehole_id, model_id, strg, err):
    ldata = dm.ILogData.make(strg, dm.db_caching, dm.cat_prod_logs_results)
    prg_ctx = cmn.progress_ctx()
    load_blobs = True
    b = ldata.load(strg, borehole_id, model_id, prg_ctx, err)
    return ldata

def load_loginterp(borehole_id, frame_id, ctx, py_res):
    return load_loginterp_by_frame(borehole_id, frame_id, ctx.pStorage, py_res)

def load_loginterp(borehole_id, strg, py_res):
    """
    load all log interpretation data by borehole
    """
    ldata = dm.ILogData.make(strg, dm.db_caching, dm.cat_logresults)
    prg_ctx = cmn.progress_ctx()
    b = ldata.load(strg, borehole_id, cmn.get_undefined_i32(), prg_ctx, py_res.err)
    return ldata

def load_devsurvey(borehole_id, devsurvey_id, strg, py_res):
    th = dm.getDataProcessing().getTrajectoryHelper()
    lo = cmn.logger_opts()
    model_id = cmn.get_undefined_i32()
    dmode = dm.dsrv_mode_all
    if cmn.is_undefined(devsurvey_id):
        ds = th.loadSurvey(strg, borehole_id, lo, model_id, py_res.err)
    else:
        ds = th.loadSurvey(strg, borehole_id, devsurvey_id, lo, py_res.err)
    return ds

def load_devsurvey_flt(borehole_id, flt, strg, py_res):
    th = dm.getDataProcessing().getTrajectoryHelper()
    lo = cmn.logger_opts()
    rank = flt.rank if flt.use_rank else cmn.get_undefined_i32()
    kind = flt.kind if flt.use_kind else cmn.get_undefined_i32()
    model_id = cmn.get_undefined_i32()
    dmode = dm.dsrv_mode_all
    ds = th.loadSurvey(strg, borehole_id, rank, kind, model_id, dmode, lo, py_res.err)
    return ds

def getDevSurveyData(borehole_id, strg, err):
    dth = dm.getDataProcessing().getDataTreatHelper()
    lo = cmn.logger_opts()
    mst = strg.getMetaStorage()
    dd = dth.makeDsrvData(mst, dm.db_caching) # temporary, todo: replace with getting workmode from strg

    if dd is None:
        return None
        
    prg_ctx = cmn.progress_ctx()
    ds = dd.load(strg, borehole_id, prg_ctx, err)
    return dd

def getDsrvDataWithMdl(borehole_id, model_id, kind, rank, strg, py_res):
    dth = dm.getDataProcessing().getDataTreatHelper()
    lo = cmn.logger_opts()
    mst = strg.getMetaStorage()
    dd = dth.makeDsrvData(mst, dm.db_caching) # temporary, todo: replace with getting workmode from strg

    if dd is None:
        return None
    
    prg_ctx = cmn.progress_ctx()
    
    dsrv_id = cmn.get_undefined_i32()
    filter = dm.curves_filter()
    if(cmn.get_undefined_i32() != kind):
        filter.kind = kind
        filter.use_kind = True
    else:
        filter.use_kind = False
        
    if(cmn.get_undefined_i32() != rank):
        filter.rank = rank
        filter.use_rank = True
    else:
        filter.use_rank = False
        
    if(cmn.get_undefined_i32() != model_id):
        mdl = strg.getRegHelper().getModelRegistry().find(model_id)
        filter.model_guid = mdl.getUUID()
        filter.use_model = True
    else:
        filter.use_model = False
        
    ds = dd.load(strg, borehole_id, filter, prg_ctx, py_res.err)
    return dd
    
def get_log_curve_data(logframe, mnemo, ctx, res):
    mst = ctx.pStorage.getMetaStorage()
    pd = dm.getPropertyByMnemo(mst, mnemo)
    if pd is None:
        res.add_error(_("Incorrect IPropertyDesc \"{0}\"").format(mnemo))
        return None

    vec = dm.vec_log_curve()
    logframe.findCurvesByProperty(pd.getID(),vec)

    if len(vec)==0:
        #res.add_error(_("\"{0}\" property not found").format(mnemo))
        return None
    
    curve = vec[0]
    if curve.data_type() == dm.ldt_float:
        return curve.fdata()
    if curve.data_type() == dm.ldt_integer:
        return curve.idata()
    if curve.data_type() == dm.ldt_string:
        return curve.sdata()

    return None

## make new entities
def makeField(strg, fld_name):
    """
    make new well and borehole
    """    
    fld = dm.make_field(strg, fld_name)
    if fld is not None:
        dm.refresh_ui_after_new_node_created(fld.getTreeNode())
        
    return fld
    
def makeBorehole(strg, fld, bhname):
    """
    make new well and borehole
    """
    bh = dm.make_borehole_and_well(strg,fld, bhname, bhname)
    if bh is not None:
        dm.refresh_ui_after_new_node_created(bh.getTreeNode())
        
    return bh

def makeBorehole2(strg, fld, wname, bhname):
    """
    make new well and borehole
    """
    bh = dm.make_borehole_and_well(strg, fld, bhname, wname)

    if bh is not None:
        dm.refresh_ui_after_new_node_created(bh.getTreeNode())
        
    return bh

def makePlannedBorehole(strg, mdl, bhname):
    """
    make new planned well and borehole
    """
    bh = dm.make_planned_borehole_and_well(strg, mdl, bhname, bhname)
    if bh is not None:
        dm.refresh_ui_after_new_node_created(bh.getTreeNode())
        
    return bh

def verifyWelDynProp(strg, model_id, mnemo):
    reg_wdp = strg.getRegHelper().getWellDynPropRegistry()
    wdp = reg_wdp.findByMnemoAndModel(model_id, mnemo)
    
    if wdp is None:
        nnctx = dm.new_node_context()
        nnctx.model_id = model_id
        reg_ed = reg_wdp.getEditor()
        wdp = reg_ed.addNewElement(nnctx)

        ed = wdp.getEditor()
        ed.setModelID(model_id)
        ed.setMnemo(mnemo)
        ed.setName(mnemo)

        dm.refresh_ui_after_new_node_created(wdp.getTreeNode())
        
    return wdp

def verifyField(strg, fld_name):
    reg = strg.getRegHelper().getFieldRegistry()    
    fld = reg.findByName(fld_name)
    if fld is not None:
        return fld
    
    fld = dm.find_or_make_field(strg, fld_name)
    dm.refresh_ui_after_new_node_created(fld.getTreeNode())
    return fld

def verifyArea(strg, name):
    reg = strg.getRegHelper().getAreaRegistry()    
    obj = reg.findByName(name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyAccobj(strg, name):
    rh = strg.getRegHelper()    
    reg = strg.getRegHelper().getAccobjRegistry()    
    obj = reg.findByName(name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_accobj)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyDepartment(strg, name):
    rh = strg.getRegHelper()
    reg = rh.getDepartmentRegistry()    
    obj = reg.findByName(name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_department)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifySite(strg, name):
    rh = strg.getRegHelper()
    reg = rh.getSiteRegistry()    
    obj = reg.findByName(name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_site)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())        
    return obj

def verifyNetwork(strg, name):
    rh = strg.getRegHelper()
    reg = rh.getNetworkRegistry()
    obj = reg.findByName(name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_network)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyPipeline(strg, net_name, name):
    net = verifyNetwork(strg, net_name)
    
    rh = strg.getRegHelper()
    reg = rh.getPipelineRegistry()
    obj = reg.findByNameAndNetwork(net.getID(), name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.network_id = net.getID()
        obj = reg_ed.addNewElement(nnctx)
        #ed = obj.getEditor()        
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_pipeline)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyBranch(strg, net_name, pipe_name, name):
    net = verifyNetwork(strg, net_name)
    pipe = verifyPipeline(strg, net_name, pipe_name)
    
    rh = strg.getRegHelper()
    reg = rh.getBranchRegistry()
    obj = reg.findByNameAndPipeline(pipe.getID(), name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.pipeline_id = pipe.getID()
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_branch)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyJunction(strg, name):
    rh = strg.getRegHelper()
    reg = rh.getJunctionRegistry()

    vobj = dm.vec_junction_t()
    reg.findByName(name, vobj)
    
    if len(vobj)==0:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_junction)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
        return obj
    
    return vobj[0]

def verifyCluster(strg, fld_name, name):
    fld = verifyField(strg, fld_name)
    reg = strg.getRegHelper().getClusterRegistry()
    obj = reg.findByNameAndField(fld.getID(), name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.field_id = fld.getID()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())        
    return obj

def verifyPlatform(strg, fld_name, name):
    fld = verifyField(strg, fld_name)
    reg = strg.getRegHelper().getPlatformRegistry()
    obj = reg.findByNameAndField(fld.getID(), name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.field_id = fld.getID()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyGtf(strg, fld_name, name):
    fld = verifyField(strg, fld_name)
    reg = strg.getRegHelper().getGtfRegistry()
    obj = reg.findByNameAndField(fld.getID(), name)
    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.field_id = fld.getID()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyReservoir(strg, fld_name, resv_name):
    fld = verifyField(strg, fld_name)    

    reg = strg.getRegHelper().getReservoirRegistry()    
    obj = reg.findByNameAndField(fld.getID(), resv_name)
    if obj is not None:
        return obj
    
    obj = dm.find_or_make_reservoir(strg, fld.getID(), resv_name)
    dm.refresh_ui_after_new_node_created(obj.getTreeNode())

    return obj

def verifyFluidContact(strg, fld_name, gl_name, fct_type):
    """
    fct_type - string like OWC, GOC, GWC
    """
    rh = strg.getRegHelper()
    
    fld = verifyField(strg, fld_name)    
    gl = dm.find_or_make_geolayer(strg, fld.getID(), gl_name)

    name = "{0}_{1}".format(gl_name, fct_type)
    
    reg = rh.getContactRegistry()
    obj = reg.findByNameAndField(fld.getID(), name)

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.field_id = fld.getID()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)

        dm.refresh_ui_after_new_node_created(obj.getTreeNode())

    fct = dm.cnt_owc
    if fct_type=="OWC":
        fct = dm.cnt_owc
    elif fct_type=="GOC":
        fct = dm.cnt_goc
    elif fct_type=="GWC":
        fct = dm.cnt_gwc        

    ed = obj.getEditor()

    ed.setType(fct)
    ed.setLayerID(gl.getID(), False)
        
    return obj
    
def verifyStratum(strg, fld_name, gl_name):
    fld = verifyField(strg, fld_name)

    reg = strg.getRegHelper().getGeoLayerRegistry()    
    obj = reg.findByNameAndField(fld.getID(), gl_name)
    if obj is not None:
        return obj
    
    obj = dm.find_or_make_geolayer(strg, fld.getID(), gl_name)
    dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyHorizon(strg, fld_name, hz_name):
    fld = verifyField(strg, fld_name)

    reg = strg.getRegHelper().getHorizonRegistry()    
    obj = reg.findByNameAndField(fld.getID(), hz_name)
    if obj is not None:
        return obj
    
    obj = dm.find_or_make_horizon(strg, fld.getID(), hz_name)
    dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyPlannedBorehole(strg, mdl_name, bhname):
    mdl = verifyModel(strg, mdl_name)

    bh = findPlannedBoreholeByName(strg, mdl, bhname)
    if (bh is not None):
        return bh
    
    return makePlannedBorehole(strg, mdl, bhname)

def verifyBorehole2(strg, fld, bhname):
    bh = findBoreholeByName(strg, fld, bhname)
    if (bh is not None):
        return bh
    
    return makeBorehole(strg, fld, bhname)

def verifyBorehole(strg, fld_name, bhname):
    fld = verifyField(strg, fld_name)

    bh = findBoreholeByName(strg, fld, bhname)
    if (bh is not None):
        return bh
    
    return makeBorehole(strg, fld, bhname)

def verifyBorehole2(strg, fld_name, wname, bhname):
    fld = verifyField(strg, fld_name)

    bh = findBoreholeByName(strg, fld, bhname)
    if (bh is not None):
        return bh
    
    return makeBorehole2(strg, fld, wname, bhname)

def verifyModel(strg, model_name):
    reg = strg.getRegHelper().getModelRegistry()    
    
    mdl = reg.findByName(model_name)
    if mdl is not None:
        return mdl
    
    obj = dm.find_or_make_model(strg, model_name)
    dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyGrid3D(strg, mdl_name, name):    
    rh = strg.getRegHelper()
    reg = rh.getGrid3DRegistry()    
    
    mdl = verifyModel(strg, mdl_name)
    
    obj = reg.findByNameAndModel(mdl.getID(), name)    

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.model_id = mdl.getID()
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_grid3d)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyGrid2D(strg, mdl_name, name):    
    rh = strg.getRegHelper()
    reg = rh.getGrid2DRegistry()    
    
    mdl = verifyModel(strg, mdl_name)
    
    obj = reg.findByNameAndModel(mdl.getID(), name)    

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.model_id = mdl.getID()
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_grid2d)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyValues2D(strg, g2, mnemo, name, dynprop2d=None, tstep=None):
    rh = strg.getRegHelper()
    if g2 is None:
        return None # grid should exist
    
    reg = rh.getValues2DRegistry()    
    
    obj = reg.findByMnemoAndGrid(g2.getID(), mnemo)

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.mnemo = mnemo
        nnctx.grid_id = g2.getID()

        if None!=dynprop2d:
            nnctx.dynprop_id = dynprop2d.getID()

        if None!=tstep:
            nnctx.tstep_id = tstep.getID()

        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_values2d)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyValues2Da(strg, g2, dynprop2d, tstep):
    """
    for dynamic cubes
    """
    return verifyValues2D(strg, g2, '', '', dynprop2d, tstep)

def verifyDynValues2D(strg, g2, dynprop2d, dt_string):
    """
    for dynamic cubes
    """
    mdl_id = g2.getModelID()
    rh = strg.getRegHelper()
    mdl = rh.getModelRegistry().find(mdl_id)
    tstep = verifyTimestep(strg, mdl.getName(), dt_string)    
    return verifyValues2Da(strg, g2, dynprop2d, tstep)

def verifyTimestep(strg, mdl_name, dt_string):
    rh = strg.getRegHelper()
    reg = rh.getTimeStepRegistry()    

    mdl = verifyModel(strg, mdl_name)
    
    dt = cmn.date_t_from_string(dt_string)
    
    obj = reg.findByNameAndModel(mdl.getID(), dt_string)

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.model_id = mdl.getID()
        nnctx.dt = dt

        obj = reg_ed.addNewElement(nnctx)

        ed = obj.getEditor()
        
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_timestep)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyCube(strg, g3, mnemo, name, dyn_cube=None, tstep=None):
    rh = strg.getRegHelper()
    if g3 is None:
        return None # grid should exist
    
    reg = rh.getCubeRegistry()    
    
    obj = reg.findByMnemoAndGrid(g3.getID(), mnemo)

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.mnemo = mnemo
        nnctx.grid_id = g3.getID()

        if None!=dyn_cube:
            nnctx.dynprop_id = dyn_cube.getID()

        if None!=tstep:
            nnctx.tstep_id = tstep.getID()

        obj = reg_ed.addNewElement(nnctx)

        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_cube)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyCube2(strg, g3, dyn_cube, tstep):
    """
    for dynamic cubes
    """
    return verifyCube(strg, g3, '', '', dyn_cube, tstep)

def verifyCube3(strg, g3, dyn_cube, dt_string):
    """
    for dynamic cubes
    """
    mdl = g3.getModel()
    tstep = verifyTimestep(strg, mdl.getName(), dt_string)    
    return verifyCube2(strg, g3, dyn_cube, tstep)


def verifyDynCube(strg, g3, mnemo, name):
    rh = strg.getRegHelper()
    if g3 is None:
        return None # grid should exist
    
    reg = rh.getDynCubeRegistry()    
    
    obj = reg.findByMnemoAndGrid(g3.getID(), mnemo)

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.mnemo = mnemo
        nnctx.grid_id = g3.getID()
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_dyncube)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyDynParam2D(strg, g2, mnemo, name):
    rh = strg.getRegHelper()
    if g2 is None:
        return None # grid should exist
    
    reg = rh.getDynProp2DRegistry()    
    
    obj = reg.findByMnemoAndGrid(g2.getID(), mnemo)

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.mnemo = mnemo
        nnctx.grid_id = g2.getID()
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_dynprop2d)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    return obj

def verifyProfile(strg, name):
    rh = strg.getRegHelper()
    reg = rh.getProfileRegistry()    

    vtmp = dm.vec_profile_t()
    reg.findByName(name, vtmp)    

    if len(vtmp)==0:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_profile)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    else:
        obj = vtmp[0]
        
    return obj

def verifyPoints(strg, name):
    rh = strg.getRegHelper()
    reg = rh.getPointsRegistry()    

    vtmp = dm.vec_pointsys_t()
    reg.findByName(name, vtmp)    

    if len(vtmp)==0:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_pointsys)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    else:
        obj = vtmp[0]
        
    return obj

def verifySurface(strg, name):
    rh = strg.getRegHelper()  
    reg = rh.getSurfaceRegistry()    

    vtmp = dm.vec_surface_t()
    reg.findByName(name, vtmp)    

    if len(vtmp)==0:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_surface)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    else:
        obj = vtmp[0]
        
    return obj

def verifyContour(strg, name):
    rh = strg.getRegHelper()    
    reg = rh.getContourRegistry()    

    vtmp = dm.vec_contourset_t()
    reg.findByName(name, vtmp)    

    if len(vtmp)==0:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_contour)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
    else:
        obj = vtmp[0]
        
    return obj

def verifyBlock(strg, mdl_name, name):

    mdl = verifyModel(strg, mdl_name)
    
    rh = strg.getRegHelper()    
    reg = rh.getBlockRegistry()    

    obj = reg.findByNameAndModel(name, mdl.getID())    

    if obj is None:
        reg_ed = reg.getEditor()
        nnctx = dm.new_node_context()
        nnctx.name = name
        nnctx.model_id = mdl.getID()
        obj = reg_ed.addNewElement(nnctx)
        rh.refresh_finders_add_obj(obj.getDMO(), dm.nt_block)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())

    return obj

def verifyBhGroup(strg, mdl, name):
    """
    find or make new bhgroup by name
    """
    reg = strg.getRegHelper().getBoreholeGroupRegistry()

    if mdl is not None:
        model_id = mdl.getID()
    else:
        model_id = cmn.get_undefined_i32()

    obj = reg.findByNameAndModel(model_id, name)

    if obj is None:
        nnctx = dm.new_node_context()    
        nnctx.name = name
        nnctx.model_id = model_id    

        reg_ed = reg.getEditor()
        obj = reg_ed.addNewElement(nnctx)
        dm.refresh_ui_after_new_node_created(obj.getTreeNode())
        
    if obj is None:
        return None
    
    if obj is not None:
        ed = obj.getEditor()
        ed.setModelID(model_id)
        ed.setGroupType(2) ## user group
        
    return obj

def node_name(strg, nt, id):
    s = ""
    node = dm.find_node(strg, nt, id)

    if node is None:
        return s
            
    s = node.getNodeName()

    return s

def node_names(strg, nt, ids):
    s = ""
    for i in range(len(ids)):
        id = ids[i]
        node = dm.find_node(strg, nt, id)

        if node is None:
            continue
            
        if 0!=i:
            s = s + ", "
        
        s = s + node.getNodeName()

    return s

def getNamesAsString(obj_list):
    n = len(obj_list)
    s = ""
    for i in range(n):
        obj = obj_list[i]
        
        if (i!=0):
            s = s + ', '

        s = s + obj.getName()

    return s

def getBoreholesByField(strg, fld_id):
    """
    """

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.find(fld_id)
    if fld is None:
        return None

    vbh = dm.vec_borehole_t()
    fld.getBoreholes(vbh)

    return vbh

def getHorizonsByField(strg, fld_id):
    """
    """

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.find(fld_id)
    if fld is None:
        return None

    vhrz = dm.vec_horizon_t()
    fld.getHorizons(vhrz)

    return vhrz

def getReservoirsByField(strg, fld_id):
    """
    """

    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.find(fld_id)
    if fld is None:
        return None

    vrsv = dm.vec_reservoir_t()
    fld.getReservoirs(vrsv)

    return vrsv

def getStratumsByField(strg, fld_id):
    """
    """
    #print("getStratums STARTED")
    reg_fld = strg.getRegHelper().getFieldRegistry()
    fld = reg_fld.find(fld_id)
    if fld is None:
        return None

    vstrat = dm.vec_geolayer_t()
    fld.getGeoLayers(vstrat)

    return vstrat

def getTimestepsByModel(strg, mdl_id):
    """
    returns list of time steps for given model
    """
    out = []

    vtstep = dm.vec_timestep_t()
    strg.getRegHelper().getTimeStepRegistry().findByModel(mdl_id, True, vtstep)

    for tstep in vtstep:
        out.append(tstep)

    return out


def getCubesByModel(strg, mdl_id):
    """
    returns list of cubes for 1st grid in given model
    """

    cubes = []

    vgrid = dm.vec_grid3d_t()
    strg.getRegHelper().getGrid3DRegistry().findByModel(mdl_id, vgrid)

    for grid in vgrid:
        vcube = dm.vec_cube_t()
        grid.getCubes(vcube)    
        for cube in vcube:
            cubes.append(cube)

        break

    return cubes

def getDynCubesByModel(strg, mdl_id):
    """
    returns list of dynamic cubes for 1st grid in given model
    """

    dcubes = []

    vgrid = dm.vec_grid3d_t()
    strg.getRegHelper().getGrid3DRegistry().findByModel(mdl_id, vgrid)

    for grid in vgrid:
        vdyncube = dm.vec_dyncube_t()
        grid.getCubeDynProps(vdyncube)    
        for dcube in vdyncube:
            dcubes.append(dcube)

        break

    return dcubes

def getParams2DByModel(strg, mdl_id):
    """
    returns list of params 2D for 1st grid in given model
    """

    out = []

    vgrid = dm.vec_grid2d_t()
    strg.getRegHelper().getGrid2DRegistry().findByModel(mdl_id, vgrid)

    for grid in vgrid:
        vitm = dm.vec_values2d_t()
        grid.getValues2D(vitm)    
        for itm in vitm:
            out.append(itm)

        break

    return out

def getDynParams2DByModel(strg, mdl_id):
    """
    returns list of dynamic params 2D for 1st grid in given model
    """

    out = []

    vgrid = dm.vec_grid2d_t()
    strg.getRegHelper().getGrid2DRegistry().findByModel(mdl_id, vgrid)

    for grid in vgrid:
        vitm = dm.vec_dynprop2d_t()
        grid.getDynProps2D(vitm)    
        for itm in vitm:
            out.append(itm)

        break

    return out

def getFields(strg, fld_name):
    """
    finds field by name and return it in list, 
    or (if fld_name is empty or None) returns all fields in strg
    """
    fields = []
    
    reg_fld = strg.getRegHelper().getFieldRegistry()

    bHaveName = False
    if fld_name is not None:
        if len(fld_name)>0:
            bHaveName = True

    if bHaveName:
        fld = reg_fld.findByName(fld_name)
        if fld is not None:
            fields.append(fld)
    
    if len(fields)==0 and not bHaveName:
        n = reg_fld.getElemCount()
        for k in range(n):
            fld = reg_fld.getElem(k)
            fields.append(fld)
            
    return fields