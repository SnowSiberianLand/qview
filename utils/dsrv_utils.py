# -*- coding: cp1251 -*-

import sys
import math
import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv
import data_utils as du
import entity_utils as eu
import table_utils as tu
import wpick_utils as wpu

#typedef surv dm.IDsrvSurvey
#typedef crv_md dm.IDsrvCurve
#typedef crv_incl dm.IDsrvCurve
#typedef dd dm.IDsrvData

class survey:
    """
    wrapper around dm.IDsrvSurvey, for convinience
    """

    def __init__(self, _surv):
        self.surv = _surv

    def npoint(self):
        """
        data point count
        """
        return self.surv.getNpointByData()
        
    def md(self):
        """
        MD channel, list
        """
        return self.get_data(self.surv.getMDVec())

    def tvd(self):
        """
        TVD channel, list
        """        
        return self.get_data(self.surv.getTVDVec())

    def azi_mag(self):
        """
        Magnetic azimuth channel, list
        """
        return self.get_data(self.surv.getAzmtVec())

    def azi_geo(self):
        """
        Geographic azimuth channel, list
        """
        return self.get_data(self.surv.getGeoAzmtVec())

    def azi(self):
        if self.surv.getGeoAzmtVec() is not None:
            return self.azi_geo()
        else:
            return self.azi_mag()
    
    def incl(self):
        """
        Inclination channel, list
        """        
        return self.get_data(self.surv.getInclVec())

    def get_data(self, vec):
        if vec is not None:
            lst = du.from_vec(vec)
            return lst
        else:
            return None
        
def get_dsrv_data(strg, bh):
    mst = strg.getMetaStorage()    
    dd = dm.IDsrvData.make(mst, dm.db_caching)
    if dd is None:
        return None
        
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    
    b = dd.load(strg, bh.getID(), tctx, terr)
    return dd

def append_survey(sda : dm.IDsrvData, bh : dm.IBorehole, arr_md, arr_incl, arr_azi, bCalc):
    """
    appends new deviation survey to "sda"
    arr_md, arr_incl, arr_azi - lists with MD, Inclination, Azimuth
    """
    
    vmd =  du.to_double_vec(arr_md)
    vincl = du.to_double_vec(arr_incl)
    vazi =  du.to_double_vec(arr_azi)

    survs = sda.surveys()
    surv = survs.appendDsrvSurvey(bh.getID())

    terr = cmn.err_info()
    surv.initMdInclAzi(vmd, vincl, vazi, True, terr)

    if bCalc==True:
        copts = dm.incl_calc_opts()
        copts.bUseDeclination = False
        copts.azmt = dm.azmt_geo
        
        surv.recalcTrajectory(copts, terr)
    
    return surv

def put_changes(sda):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return sda.save(tctx, terr)

def dsrv_crv_compare_by_mnemo(c1, c2):
    """    
    returns True is curves have same MNEMO
    c1, c2 - IDsrvCurve
    """
    if (c1.mnemo()!=c2.mnemo()):
        return False

    if (c1.mnemo()=="" and c1.propertyId()!=cmn.get_undefined_i32()):
        return False
            
    return True

def dsrv_crv_compare_by_property(c1, c2):
    """    
    returns True is curves have same PROPERTY_ID
    c1, c2 - IDsrvCurve
    """

    if (c1.propertyId()!=c2.propertyId()):
        return False
    
    return True


def find_dupes(vcrv, comp_func):
    """
        finds dupes in array of IDsrvCurve objects
        using comp_func()
    """
    out = dm.vec_dsrv_curve()
    
    n = len(vcrv)
    for i in range(n):
        c1 = vcrv[i]

        for j in range(i+1, n):
            c2 = vcrv[j]
            b = comp_func(c1, c2)
            if (b==True):
                out.append(c2)
            
    return out

def delete_dsrvcurves_from_db(strg, ids, res):
    crud = strg.getIO()

    fltr = db.filter("rdm", "DSRV_CURVE")
    fltr.setIn("CURVE_ID", ids)

    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    bCommit = True
    stat = db.changes_stat()
    
    bb = crud.del_cascade(fltr, bCommit, stat, pctx, terr)
    if (bb==False):
        res.add_error(terr.msg)

def findBhsInTvdRange(strg, bhs, tvd_min, tvd_max):
    """
    находим скважины, у которых конец траектории (100м) в коридоре [tvd_min, tvd_max]
    """
    """
    находим среди скважин в bhs все горизонтальные
    """
    out = []
    
    nbh = len(bhs)

    for ii in range(nbh):
        bh = bhs[ii]
    
        res = dmsrv.python_results()
        dd = eu.getDevSurveyData(bh.getID(), strg, res.err)
        if dd is None:
            #print('borehole: {0}, no deviation surveys'.format(bh.getName()))                
            continue
    
        #using 1st survey
        surv = dd.firstSurvey()
        if surv is None:
            #print('borehole: {0}, no deviation surveys'.format(bh.getName()))        
            continue

        bIn = is_trajectory_end_in_tvd_range(surv, tvd_min, tvd_max)
        if True==bIn:
            out.append(bh)
            
    return out
    
def findHorizontalBhs(strg, bhs):
    """
    находим среди скважин в bhs все горизонтальные
    """
    out = []
    
    nbh = len(bhs)

    for ii in range(nbh):
        bh = bhs[ii]
    
        res = dmsrv.python_results()
        dd = eu.getDevSurveyData(bh.getID(), strg, res)
        if dd is None:
            #print('borehole: {0}, no deviation surveys'.format(bh.getName()))                
            continue
    
        #using 1st survey
        surv = dd.firstSurvey()
        if surv is None:
            #print('borehole: {0}, no deviation surveys'.format(bh.getName()))        
            continue
        
        bHoriz = is_horizontal(surv)
        if True==bHoriz:
            out.append(bh)
            
    return out

def is_horizontal(surv):
    """
    возвращает True если в траектории есть горизонтальный участок длиной более 100м
    "горизонтальность" определяется как угол > 88 градусов
    """
    if surv is None:
        return False
    
    crv_md = surv.getMDCurve()
    if crv_md is None:
        #print('borehole: {0}, no depth channel'.format(bh.getName()))        
        return False

    vmd = crv_md.data()
    
    crv_incl = surv.getInclCurve()
    if crv_incl is None:
        #print('borehole: {0}, no inclination channel'.format(bh.getName()))        
        return False

    van = crv_incl.data()

    # test survey for horizontal part   
    n = len(vmd)
    #print(n)
    
    tl = 0.0    # накопленная длина горизонтального участка
    for i in reversed(range(n)):
        an = van[i]

        if (cmn.is_undefined(an)): # если угол неопределен, сбрасываем 
            tl = 0.0
            continue 
        
        if an>=88.:
            md = vmd[i]
            if (i<n-1):
                dl = vmd[i+1]-md
                tl = tl + dl
            if tl>100.:
                return True # нашли горизонтальный участок >100м
        else:
            tl=0.0 # reset

    return False

def is_trajectory_end_in_tvd_range(surv, tvd_min, tvd_max):
    """
    возвращает True если конец траектории (100м) в коридоре [tvd_min, tvd_max]
    """
    if surv is None:
        return False
    
    crv_md = surv.getMDCurve()
    if crv_md is None:
        #print('borehole: {0}, no depth channel'.format(bh.getName()))        
        return False

    vmd = crv_md.data()

    crv_tvd = surv.getTVDCurve()
    if crv_tvd is None:
        #print('borehole: {0}, no TVD channel'.format(bh.getName()))        
        return False

    vtvd = crv_tvd.data()
    
    crv_incl = surv.getInclCurve()
    if crv_incl is None:
        #print('borehole: {0}, no inclination channel'.format(bh.getName()))        
        return False

    van = crv_incl.data()

    # test survey for horizontal part   
    n = len(vmd)
    #print(n)
    
    tl = 0.0    # накопленная длина горизонтального участка
    for i in reversed(range(n)):
        an = van[i]
        tvd = vtvd[i]
        
        if (cmn.is_undefined(an)): # если угол неопределен, сбрасываем 
            tl = 0.0
            continue 

        if (cmn.is_undefined(tvd)): # если TVD неопределена, сбрасываем 
            tl = 0.0
            continue 
        
        if (an>=88.) and (tvd>=tvd_min) and (tvd<=tvd_max):
            md = vmd[i]
            
            if (i<n-1):
                dl = vmd[i+1]-md
                tl = tl + dl
            if tl>100.:
                return True # нашли горизонтальный участок >100м в интервале [tvd_min, tvd_max]
        else:
            tl=0.0 # reset

    return False

def findHorizontalBhsForStratum(strg, bhs, gl, mdl, off):
    if gl is None:
        return []
    
    # найдем все горизонтальные скважины
    hbhs = findHorizontalBhs(strg,bhs)
    count = len(hbhs)
    #print("Found: ", count," horizontal boreholes")
       
    # найдем "окно TVD" пласта по маркерам
    mm = wpu.getTvdRange(strg, bhs, gl, mdl)
    if mm[0] is None or mm[0] is None:
        print('TVD range not fount for stratum: {0}'.format(gl.getName()))
        exit(0)
    #print('Stratum TVD range {0:.2f}-{1:.2f}'.format(mm[0],mm[1]))
    
    # расширим диапазон TVD
    tvd_min = mm[0]-off
    tvd_max = mm[1]+off
    
    # найдем горизонтальные у которых конец траектории лежит внутри tvd_min, tvd_max
    bhs1 = findBhsInTvdRange(strg, hbhs, tvd_min, tvd_max)
    count = len(bhs1)
    #print("Found: {0} horizontal boreholes for stratum: {1}".format(count, gl.getName()))

    return bhs1

def check_survey_null_values(strg, ds, nulls, res):
    if ds is None:
        return False

    suspects = set()
    suspects_md = []

    depth = ds.getMD()

    curvesFuncs = []
    curvesFuncs.append((ds.getMD,   "MD"))
    curvesFuncs.append((ds.getTVD,  "TVD"))
    curvesFuncs.append((ds.getCX,   "CX"))
    curvesFuncs.append((ds.getCY,   "CY"))
    curvesFuncs.append((ds.getDN,   "DX"))
    curvesFuncs.append((ds.getDE,   "DY"))
    curvesFuncs.append((ds.getIncl, "Inclination"))
    curvesFuncs.append((ds.getAzmt, "Azimuth"))

    for getData, name in curvesFuncs:

        data = getData()
        for i, v in enumerate(data):
            if v in nulls:
                suspects.add(v)
                suspects_md.append(depth[i])

        if len(suspects_md) > 0:
            msg = _("\"{0}\" channel has suspicious values: {1}").format(name, du.seq2str(suspects))
            res.add_warning(msg, du.make_position(strg, suspects_md, "COMMON_TOP_MD"))

    return True

def check_curves_nulls(strg, ds, crv_mnemos, res):
    if ds is None:
        res.add_error(_("No deviation survey data"))
        return -1 ## worst result

    n = 0

    mst = strg.getMetaStorage()
    for mnemo in crv_mnemos:
        prop = dm.getPropertyByMnemo(mst, mnemo)
        crv = ds.getCurve(prop)
        if crv is None:
            res.add_warning(_("{0} curve is none").format(prop.getName()))
            n += 1

    ## ternary logic
    if n == len(crv_mnemos):
        res.add_error(_("All input curves is none"))
        return -1 ## worst result
    elif n == 0: ## best result
        return 1
    else:
        return 0

def check_curves_emptiness(strg, ds, crv_mnemos, res):
    nulls = check_curves_nulls(strg, ds, crv_mnemos, res)
    if nulls == -1:
        res.add_error(_("Cannot check emptiness of these curves"))
        return False

    mst = strg.getMetaStorage()
    empty = 0
    for mnemo in crv_mnemos:
        prop = dm.getPropertyByMnemo(mst, mnemo)
        crv = ds.getCurve(prop)
        if crv:
            data = crv.data()
        if not (data and len(data) != 0):
            empty += 1
            res.add_warning(_("{0} data is missed").format(prop.getName()))

    ## ternary logic
    if empty == len(crv_mnemos):
        res.add_error(_("All input curves is empty"))
        return -1 ## worst result
    elif empty == 0: ## best result
        return 1
    else:
        return 0

def fill_empty_azimuth(ds, res):
    md_data = ds.getMDCurve().data()
    incl_data = ds.getInclCurve().data()
    azm_data = cmn.vec_num_t()
    count = len(md_data)
    angle_low_cnt = 0
    angle_mid_cnt = 0
    angle_high_cnt = 0
    for i in range(count):
        if (incl_data[i] <= 3.0):
            angle_low_cnt += 1
        elif (incl_data[i] < 10.0):
            angle_mid_cnt += 1
        else:
            angle_high_cnt += 1
    if (angle_high_cnt):
        res.add_warning(_("Borehole is not vertical and hasn't azimut channel"))
##        return None
    azimuth = 0
    ## if angle_high_cnt == 0 and another angles count == 0, we generate azimuth
    for i in range(count):
        azimuth += 90 # we starting from 90 degrees (or 45 in another case)
        if azimuth == 360:
            azimuth = 0
        azm_data.append(azimuth)
    return azm_data

def get_empty_azimuth_intvls(azm_data):
    count = len(azm_data)
    empty_intvls = []
    empty_count = 0
    for i in range(count):
        val = azm_data[i]
        if cmn.is_undefined(val):
            if i == count-1:
                if empty_count > 1:
                    start = i - empty_count
                    empty_intvls.append([start, i]) # last element is analyzing separately
                empty_count = 0
            else:
                empty_count += 1
        else:
            if empty_count > 1:
                start = i - empty_count
                empty_intvls.append([start, i]) # i's item is not undefined and using as end of list, not as item
            empty_count = 0
    return empty_intvls

def get_index_max_elem_list(data):
    maximum = max(data)
    return data.index(maximum) # if all are equal, returns 0 (first index)

def fill_not_empty_azimuth(ds, res):
    md_data = ds.getMDCurve().data()
    incl_data = ds.getInclCurve().data()
    azm = ds.getAzmtCurve()
    azm_data = azm.data()
    count = len(md_data)
    empty_intvls = get_empty_azimuth_intvls(azm_data) # only intvls, not points, without last point

    top_fraction = 0.2 # this and next were got from old version devsurvey_spiral_fill
    mid_fraction = 0.5
    top_bound_mid = math.floor((count - 1) * top_fraction)
    bottom_bound_mid = math.floor((count - 1) * (top_fraction + mid_fraction))
    top = list(range(0, top_bound_mid))
    mid = list(range(top_bound_mid, bottom_bound_mid))
    bottom = list(range(bottom_bound_mid, (count - 1)))

    for intvl_idx in range(len(empty_intvls)):
        first = empty_intvls[intvl_idx][0]
        last = empty_intvls[intvl_idx][1]
        current_intvl = list(range(first, last))
        in_high_level = 0
        in_medium_level = 0
        in_low_level = 0
        for index in range(len(current_intvl)):
            if current_intvl[index] < top_bound_mid:
                in_high_level += 1
            elif current_intvl[index] < bottom_bound_mid:
                in_medium_level += 1
            else:
                in_low_level += 1
        index_prior_level = get_index_max_elem_list([in_high_level, in_medium_level, in_low_level])
        h = md_data[1]-md_data[0]
        prev_points_count_max = math.floor(500 / h) # 500m is value from methodic

        if intvl_idx > 0:
            prev_last = empty_intvls[intvl_idx - 1][1] # prev_first isn't using

        sourcedata = []
        amplitude = 0
        interpolation_h = 0
        
        if index_prior_level == 1 and intvl_idx > 0:
            if first - prev_last <= prev_points_count_max:
                sourcedata=azm_data[prev_last:first]
            else:
                if first-prev_points_count_max < 0:
                    sourcedata=azm_data[0:first]
                else:
                    sourcedata=azm_data[first-prev_points_count_max:first]
        elif index_prior_level == 2:
            if first-prev_points_count_max < 0:
                sourcedata=azm_data[0:first]
            else:
                sourcedata=azm_data[first-prev_points_count_max:first]
        if sourcedata:
            amplitude=(max(sourcedata) - min(sourcedata)) / 2
        if (first != 0 and last != count-1):
            interpolation_h = (azm_data[last] - azm_data[first-1]) / (last - first) # fix #4225: azm_data[last+1] can be undefined

        angle_low_cnt = 0
        angle_mid_cnt = 0
        angle_high_cnt = 0
        for i in range(first, last):
            if (incl_data[i] <= 3.0):
                angle_low_cnt += 1
            elif (incl_data[i] < 10.0):
                angle_mid_cnt += 1
            else:
                angle_high_cnt += 1
        index_prior_angle = get_index_max_elem_list([angle_low_cnt, angle_mid_cnt, angle_high_cnt])

        if first == 0 and last > count-4:
            if angle_high_cnt > 0:
                res.add_warning(_("Borehole is not vertical and hasn't azimut channel"))
##                return None
        calc_azi_empty_interval(ds, first, last, index_prior_level, index_prior_angle, interpolation_h, amplitude)

    calc_azi_empty_points(azm)
    return azm_data

def calc_azi_empty_points(azm):
    azm_data = azm.data()
    count = len(azm_data)
    for i in range(count):
        if cmn.is_undefined(azm_data[i]):
            if i > 0:
                ## interpolation has higher priority than extrapolation
                if i > 1: # we can use extrapolation
                    #azm_data[i] = (azm_data[i-1] - azm_data[i-2]) / 2 + azm_data[i-1] # original strange extrapolation
                    if azm_data[i-1] != 0 or azm_data[i-2] == 0:
                        azm_data[i] = (azm_data[i-1] - azm_data[i-2]) + azm_data[i-1] # extrapolation
                    else:
                        azm_data[i] = (360 - azm_data[i-2]) + azm_data[i-1] # extrapolation
                if i < count - 1: # we can use interpolation:
                    if azm_data[i+1] != 0 or azm_data[i-1] == 0:
                        azm_data[i] = (azm_data[i+1] - azm_data[i-1]) / 2 + azm_data[i-1] # interpolation
                    else:
                        azm_data[i] = (360 - azm_data[i-1]) / 2 + azm_data[i-1] # interpolation
            else:
                azm_data[i] = 0
            azm.setModified(True)

def calc_azi_empty_interval(ds, first, last, index_prior_level, index_prior_angle, interpolation_h, amplitude):
    md_data = ds.getMDCurve().data() ## for first 100 m
    azm = ds.getAzmtCurve()
    azm_data = azm.data()
    count = len(azm_data) ## think that all curves are consistent and have equal length
    azimuth = 0
    process = False
    if first == 0 and last > count-4:
            ## in original method cycle was for full list, not to "last" item, but if we have 1-2 values
            ## of azimuth in end of list, why we should rewrite them?
            for i in range(last):
                if azimuth == 360:
                    ## we wrote 0 degrees twice: for 360 and for 0;
                    ## was got from old version devsurvey_spiral_fill
                    ## but now we write 0 degrees once because it is more right
                    azimuth = 0
                azm_data[i] = azimuth
                azimuth += 90
                    ## setModified in end of function
    
    for i in range(first, last): ## without last item
        if (cmn.is_undefined(azm_data[i])): ## in interval all azimuths should be undefined, took from old script:
            if index_prior_level == 0:
                if i == 0:
                    process = True
                if process:
                    ## in original methodic bound = 100 m, but in old script bound = 10 points.
                    if (md_data[last-1] > 100 and index_prior_angle == 1) or index_prior_angle == 2:
                        ## we don't want double values of zero degrees (or 0 and 360 degrees)
                        if azimuth == 360:
                            azimuth = 0
                        azm_data[i] = azimuth
                        azimuth += 90
                    else:
                        ## we don't want double values of zero degrees (or 0 and 360 degrees)
                        if azimuth == 360:
                            azimuth = 0
                        azm_data[i] = azimuth
                        azimuth += 45
                else:
                    temp_data = azm_data[i-1]
                    if last != count - 1:
                        interpolation_h = (azm_data[last] - azm_data[first-1]) / (last - first + 2) # fix #4225: azm_data[last+1] can be undefined
                    azm_data[i] = temp_data + interpolation_h
                    while azm_data[i] > 360:
                        azm_data[i] -= 360
                    while azm_data[i] < 0:
                        azm_data[i] += 360
            elif index_prior_level == 1:
                temp_data = 0
                if i != 0:
                    temp_data = azm_data[i-1]
                ## we can have interval 0-60% and prior_level will be mid, but first will be 0
                ## and we can have interval 25%-100% and prior level will be mid, but last will be count-1
                if first > 0 and last < count - 1:
                    interpolation_h=(azm_data[last+1] - azm_data[first-1]) / (last - first + 1)
                elif first > 0:
                    interpolation_h=(0 - azm_data[first-1]) / (last - first + 1)
                elif last < count - 1:
                    interpolation_h=(azm_data[last+1] - 0) / (last - first + 1)
                else: # this block shouldn't execute
                    interpolation_h = 0
                
                azm_data[i] = temp_data + interpolation_h
                while azm_data[i] > 360:
                    azm_data[i] -= 360
                while azm_data[i] < 0:
                    azm_data[i] += 360
            else:
                if last == count - 1:
                    if index_prior_angle == 0:
                        if azimuth == 360:
                            azimuth = 0
                        azm_data[i] = azimuth
                        azimuth += 45
                    elif index_prior_angle == 2:
                        azm_data[i] = azm_data[i-1] + amplitude
                        while azm_data[i] > 360:
                            azm_data[i] -= 360
                        while azm_data[i] < 0:
                            azm_data[i] += 360
                    else:
                        azm_data[i] = azm_data[i-1]
                elif last < count - 1:
                    temp_data = azm_data[i - 1]
                    interpolation_h=(azm_data[last+1] - azm_data[first-1]) / (last - first + 1)
                    azm_data[i] = temp_data + interpolation_h
                    while azm_data[i] > 360:
                        azm_data[i] -= 360
                    while azm_data[i] < 0:
                        azm_data[i] += 360
        else:
            azimuth = 0
    azm.setModified(True)

def fill_dsrv_azimuth(ds, pd, ctx, res):
    required_crvs = ["DSRV_MD", "DSRV_INCL"]
    if check_curves_emptiness(ctx.pStorage, ds, required_crvs, res) != 1:
        return None
    
    md_data = ds.getMDCurve().data()
    incl_data = ds.getInclCurve().data()

    azimuth_empty = False
    azm = ds.getCurve(pd)
    if azm is None: # it happens
        np = len(md_data)
        ta = [cmn.get_undefined_r64()]*np
        tv = du.to_double_vec(ta)
        ds.putData(pd, tv)
        azimuth_empty = True

    azm = ds.getCurve(pd)
    azm_data = azm.data()

    count = len(md_data)

    if count != len(incl_data):
        res.add_error(_("Measured depth and inclination angle has different points count"))
        return None

    if azm_data and count != len(azm_data):
        res.add_error(_("Measured depth and azimuth has different points count"))
        return None

    empty_angles = 0
    for i in range(len(incl_data)):
        if incl_data[i] == cmn.get_undefined_r64():
            empty_angles += 1

    if empty_angles > 1:
        res.add_error(_("Deviation survey has not enough inclination angle data"))
        return None

    if not azimuth_empty:
        azm_data = fill_not_empty_azimuth(ds, res)
    else:
        azm_data = fill_empty_azimuth(ds, res)

    return azm_data
