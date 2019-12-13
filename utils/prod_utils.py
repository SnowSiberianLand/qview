# -*- coding: cp1251 -*-

import sys

import mod_dmsrv as dmsrv
import mod_dm as dm
import mod_orm as db
import mod_cmn as cmn

import data_utils as du
import entity_utils as eu
import table_utils as tu
import operator
import datetime

#typedef ctx.ents dm.entities
#typedef ents dm.entities
#typedef bh dm.IBorehole
#typedef resv dm.IReservoir

#typedef prod dmsrv.production
#typedef pos dmsrv.prod_position
#typedef pkey dmsrv.prod_key

#typedef dp dm.IDataProcessing
#typedef phlp dm.IProductionHelper

#typedef otot dm.op_total
#typedef pco dm.prod_calc_opts
#typedef opo dm.op_options

def put_changes(prod):
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    return prod.save(tctx, terr)

def get_production_monthly(bh):
    """
    returns monthly production data for given borehole
    """
    if bh is None:
        return None

    strg = bh.getDMO().getDataStorage()
    if strg is None:
        return None
    
    prod = dmsrv.production.make(strg, dm.pit_month, dm.db_caching, dm.pden_bh_resv)

    if prod is None:
        return None

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    bhid = bh.getID()
    
    b = prod.load(bhid, tctx, terr)
    if b==False:
        return None

    return prod

def get_production_total(bh):
    """
    returns total production data for given borehole
    """
    if bh is None:
        return None

    strg = bh.getDMO().getDataStorage()
    if strg is None:
        return None
    
    prod = dmsrv.production.make(strg, dm.pit_total, dm.db_caching, dm.pden_bh_resv)

    if prod is None:
        return None

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()

    bhid = bh.getID()
    
    b = prod.load(bhid, tctx, terr)
    if b==False:
        return None

    return prod

## lift types:
##     1	Flowing
##     11	ESPEn
##     200	Injector

def append_monthly_prod(prod : dmsrv.production, 
                        bh : dm.IBorehole, 
                        resv : dm.IReservoir, 
                        dt,
                        oilp, wtrp, gasp, 
                        twrk,
                        tacc=0):
    """
        oilp - oil monthly production, tonn
        wtrp - water monthly production, tonn
        gasp - solution gas monthly production, m3
        twrk - working time, hours
        tacc - accumulation time, hours
    """                            
    return append_borehole_prod(prod, True, bh, resv, dt,oilp, wtrp, gasp, twrk, tacc)

def append_total_prod(prod : dmsrv.production, 
                        bh : dm.IBorehole, 
                        resv : dm.IReservoir, 
                        dt,
                        oilp, wtrp, gasp, 
                        twrk,
                        tacc=0):
    """
        oilp - oil total production, tonn
        wtrp - water total production, tonn
        gasp - solution gas total production, m3
        twrk - total working time, hours
        tacc - total accumulation time, hours
    """                            
    return append_borehole_prod(prod, False, bh, resv, dt,oilp, wtrp, gasp, twrk, tacc)

def append_borehole_prod(prod : dmsrv.production, 
                        bMonthly,
                        bh : dm.IBorehole, 
                        resv : dm.IReservoir, 
                        dt,                        
                        oilp, wtrp, gasp, 
                        twrk,
                        tacc=0):
    """
        oilp - oil production (for some period), tonn
        wtrp - water production (for some period), tonn
        gasp - solution gas production (for some period), m3
        twrk - working time (for some period), hours
        tacc - accumulation time (for some period), hours
    """
    if bh is None:
        return None
    if resv is None:
        return None
    if cmn.is_undefined(dt):
        return None

    pkey = dmsrv.prod_key()
    pkey.bh_id = bh.getID()
    pkey.resv_id = resv.getID()
    pkey.dt = dt
    #pkey.lift_type = 11    ## ESP
    terr = cmn.err_info()

    if bMonthly:
        pos = prod.insertMonthly(pkey, terr)
        
        nday = days_in_month(dt)
        tall = nday*24
        if twrk>tall:
            twrk=tall
                    
        tidle = tall-twrk
        if tidle<0:
            tidle=0

        pos.setTworkOil(twrk)
        pos.setTaccOil(tacc)
        pos.setTidleOil(tidle)
    else:
        pos = prod.insertTotal(pkey, terr)

        pos.setTworkOil(twrk)

    pos.setOilp(oilp)
    pos.setWtrp(wtrp)
    pos.setGasp(gasp)
    
    return pos

def append_total_winj(prod : dmsrv.production, 
                        bh : dm.IBorehole, 
                        resv : dm.IReservoir, 
                        dt, 
                        wtri,
                        twrk,
                        tacc=0):
    """
        wtri - water total injection, m3
        twrk - total working time, hours
    """                            
    return append_borehole_winj(prod, False, bh, resv, dt, wtri, twrk, tacc)

def append_monthly_winj(prod : dmsrv.production, 
                        bh : dm.IBorehole, 
                        resv : dm.IReservoir, 
                        dt, 
                        wtri,
                        twrk,
                        tacc=0):
    """
        wtri - water monthly injection, m3
        twrk - working time, hours
    """                            
    return append_borehole_winj(prod, True, bh, resv, dt, wtri, twrk, tacc)

def append_borehole_winj(prod : dmsrv.production, 
                        bMonthly,
                        bh : dm.IBorehole, 
                        resv : dm.IReservoir, 
                        dt, 
                        wtri,
                        twrk=744,
                        tacc=0):
    """
        wtri - water injection (for some period), m3
        twrk - working time (for some period), hours
    """
    if bh is None:
        return None
    if resv is None:
        return None
    if cmn.is_undefined(dt):
        return None

    pkey = dmsrv.prod_key()
    pkey.bh_id = bh.getID()
    pkey.resv_id = resv.getID()
    pkey.dt = dt
    terr = cmn.err_info()

    if bMonthly:    
        pos = prod.insertMonthly(pkey, terr)

        nday = days_in_month(dt)
        tall = nday*24
        if twrk>tall:
            twrk=tall
    
        tidle = nday*24-twrk
        if tidle<0:
            tidle=0

        pos.setTworkInjWtr(twrk)
        pos.setTaccInjWtr(tacc)
        pos.setTidleInjWtr(tidle)
    else:
        pos = prod.insertTotal(pkey, terr)

        pos.setTworkInjWtr(twrk)
    
    pos.setWtri(wtri)
    
    
    return pos


def calc_total_production(bh):
    """
    calculate borehole total production
    """
    if bh is None:
        return False

    strg = bh.getDMO().getDataStorage()
    if strg is None:
        return False

    dp = dm.getDataProcessing()
    phlp = dp.getProductionHelper()

    pco = dm.prod_calc_opts()
    pco.m_calc_type = dm.prod_calc_recalculate
    
    opo = dm.op_options()

    opctx = dm.op_context()

    otot = dm.op_total()

    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    b = phlp.make_total_production_bh(strg, bh, pco, opo, opctx, otot, None, tctx, terr)

    return b

## -----------------------------------------------------------------------------------

def days_in_month(dt):
    """
    кол-во дней в месяце
    """
    from calendar import monthrange

    ymd = cmn.to_ymd(dt)    
    qq = monthrange(ymd.year, ymd.month)
    
    return qq[1]

def calc_twrkoila(pos):
    """
    время работы + накопления (по нефти), по мотивам rdm_production.cpp
    результат в часах
    """
    twrk = pos.getTworkOil()
    tacc = pos.getTaccOil()

    #fix: 23_09_2014 время накопления может отсутствовать
    if (cmn.is_undefined(tacc)):
        tacc = 0.0

    if not cmn.is_undefined(twrk):
        ret = twrk+tacc
    else:
        ret = cmn.get_undefined_r64()

    return ret

def calc_tinjwtra(pos):
    """
    время работы + накопления (по нефти), по мотивам rdm_production.cpp
    результат в часах
    """
    twrk = pos.getTworkInjWtr()
    tacc = pos.getTaccInjWtr()

    #fix: 23_09_2014 время накопления может отсутствовать
    if (cmn.is_undefined(tacc)):
        tacc = 0.0

    if not cmn.is_undefined(twrk):
        ret = twrk+tacc
    else:
        ret = cmn.get_undefined_r64()

    return ret

def calc_liqp(pos):
    """
    добыча жидкости, по мотивам rdm_production.cpp
    """
    oilp = pos.getOilp()
    wtrp = pos.getWtrp()

    if (not cmn.is_undefined(oilp)) and (not cmn.is_undefined(wtrp)):
        liqp = oilp+wtrp
    else:
        liqp = cmn.get_undefined_r64()

    return liqp

def calc_rtel(pos):
    """
    дебит жидкости, по мотивам rdm_production.cpp
    """
    liqp = calc_liqp(pos)
    twrkoila = calc_twrkoila(pos)
        
    if (not cmn.is_undefined(liqp)) and (not cmn.is_undefined(twrkoila)) and twrkoila!=0.0:
        ret = liqp/twrkoila*24.
    else:
        ret = cmn.get_undefined_r64()
        
    return ret

def calc_wcut(pos):
    """
    обводненность, по мотивам rdm_production.cpp
    результат в %
    """    
    wtrp = pos.getWtrp()
    liqp = calc_liqp(pos)

    if (not cmn.is_undefined(liqp)) and (not cmn.is_undefined(wtrp)) and liqp!=0.0:
        ret = wtrp/liqp*100.
    else:
        ret = cmn.get_undefined_r64()        

    return ret

def calc_injw(pos):
    """
    преемистость по воде, по мотивам rdm_production.cpp
    """
    wtri = pos.getWtri()
    tinjwtra = calc_tinjwtra(pos)
        
    if (not cmn.is_undefined(wtri)) and (not cmn.is_undefined(tinjwtra)) and tinjwtra!=0.0:
        ret = wtri/tinjwtra*24.
    else:
        ret = cmn.get_undefined_r64()
        
    return ret

def calc_twrk(pos):
    """
    время работы, по мотивам rdm_production.cpp
    результат в часах
    !!! только для нефтяных и нагн по воде    
    """   
#simple_desc(L"TWRK", L"TWRKOILA",L"TINJWTRA",L"TINJGASA",L"TWRKGASA",&first_not_null,false,false,false,false),	 //Время работы
    twrkoila = calc_twrkoila(pos)
    if not cmn.is_undefined(twrkoila):
        return twrkoila

    tinjwtra = calc_tinjwtra(pos)
    if not cmn.is_undefined(tinjwtra):
        return tinjwtra

    return cmn.get_undefined_r64()

def calc_wefa(pos):
    """
    Кэкспл, по мотивам rdm_production.cpp
    !!! только для нефтяных и нагн по воде
    """   
    twrk = calc_twrk(pos)
    ndays = days_in_month(pos.getDate())

    if not cmn.is_undefined(twrk):
        ret = twrk/ndays/24.
    else:
        ret = cmn.get_undefined_r64()
    
    return ret

def is_oil_prod(pos):
    """
    returns true is "pos" is oil production record
    """
    twrk = calc_twrkoila(pos)
    if not cmn.is_undefined(twrk) and (twrk>0):
        return True
    else:
        return False
    
def is_wtr_inj(pos):
    """
    returns true is "pos" is water injection record
    """    
    twrk = calc_tinjwtra(pos)
    if not cmn.is_undefined(twrk) and (twrk>0):
        return True
    else:
        return False
