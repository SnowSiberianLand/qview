# -*- coding: cp1251 -*-
import mod_dm as dm
import mod_cmn as cmn
import mod_dmsrv as dmsrv

import entity_utils as eu
import table_utils as tu
import table_utils2 as tu2
import mod_ui as ui

import os
import math 
import numpy as np
import subprocess


def get_D_nkt(ctx):
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'TUB_WTHICK', 'TUB_INTD', 'TUB_OUTD']
    table = tu.makeBoreholeTable('TUBING_TABLE', ctx, layer, ctx.borehole_id, py_res, True, True)
    if table is None:
        return None
    if table.getRowCount()==0:
        return None
    else:
        for x in range(table.getRowCount()):
            Dnkt     = tu.getNum2('TUB_INTD', x, table)
            Dnkt_out = tu.getNum2('TUB_OUTD', x, table)
            Tolshina = tu.getNum2('TUB_WTHICK', x, table)
    if cmn.is_undefined(Dnkt) or Dnkt=='':
        if not cmn.is_undefined(Tolshina):
            Dnkt=float(Dnkt_out)-float(Tolshina)*2
        else:
            if cmn.is_undefined(Dnkt_out):
                return Dnkt
            else:
                if Dnkt_out<70:
                    Dnkt=float(Dnkt_out)-2*5.0
                if Dnkt_out<80 and Dnkt_out>69:
                    Dnkt=float(Dnkt_out)-2*6.0
                if Dnkt_out>79:
                    Dnkt=float(Dnkt_out)-2*7.0
    return round(Dnkt,2)

def get_D_nkt2(ctx,bh_id):
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'TUB_WTHICK', 'TUB_INTD', 'TUB_OUTD']
    table = tu.makeBoreholeTable('TUBING_TABLE', ctx, layer, bh_id, py_res, True, True)
    if table is None:
        return None
    if table.getRowCount()==0:
        return None
    else:
        for x in range(table.getRowCount()):
            Dnkt     = tu.getNum2('TUB_INTD', x, table)
            Dnkt_out = tu.getNum2('TUB_OUTD', x, table)
            Tolshina = tu.getNum2('TUB_WTHICK', x, table)
    if cmn.is_undefined(Dnkt) or Dnkt=='':
        if not cmn.is_undefined(Tolshina):
            Dnkt=float(Dnkt_out)-float(Tolshina)*2
        else:
            if cmn.is_undefined(Dnkt_out):
                return Dnkt
            else:
                if Dnkt_out<70:
                    Dnkt=float(Dnkt_out)-2*5.0
                if Dnkt_out<80 and Dnkt_out>69:
                    Dnkt=float(Dnkt_out)-2*6.0
                if Dnkt_out>79:
                    Dnkt=float(Dnkt_out)-2*7.0
    return round(Dnkt,2)


def get_Mgas(ctx,Mgas_default):
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'FPG_CH4', 'FPG_C2H6', 'FPG_C3H8', 'FPG_C4H10', 'FPG_C5H12', 'FPG_N2', 'FPG_CO2', 'FPG_O2']
    table = tu.makeBoreholeTable('FLUP_NGAS_PROPERTIES', ctx, layer, ctx.borehole_id, py_res, True, True)
    if table is None:
        return None
    if table.getRowCount()==0:
        return None
    else:
        for x in range(table.getRowCount()):
            FPG_CH4   = tu.getNum2('FPG_CH4',   x, table)
            FPG_C2H6  = tu.getNum2('FPG_C2H6',  x, table)
            FPG_C3H8  = tu.getNum2('FPG_C3H8',  x, table)
            FPG_C4H10 = tu.getNum2('FPG_C4H10', x, table)
            FPG_C5H12 = tu.getNum2('FPG_C5H12', x, table)
            FPG_N2    = tu.getNum2('FPG_N2',    x, table)
            FPG_CO2   = tu.getNum2('FPG_CO2',   x, table)
            FPG_O2    = tu.getNum2('FPG_O2',    x, table)
        if cmn.is_undefined(FPG_CH4):
            FPG_CH4 = 0
        if cmn.is_undefined(FPG_C2H6):
            FPG_C2H6 = 0
        if cmn.is_undefined(FPG_C3H8):
            FPG_C3H8 = 0
        if cmn.is_undefined(FPG_C4H10):
            FPG_C4H10 = 0
        if cmn.is_undefined(FPG_C5H12):
            FPG_C5H12 = 0
        if cmn.is_undefined(FPG_N2):
            FPG_N2 = 0
        if cmn.is_undefined(FPG_CO2):
            FPG_CO2 = 0
        if cmn.is_undefined(FPG_O2):
            FPG_O2 = 0

## ТАБЛИЦА МОЛЯРНЫХ МАСС
        MCH4   = 16.043
        MC2H6  = 30.07
        MC3H8  = 44.097
        MC4H10 = 58.124
        MC5H12 = 161.0755
        MN2    = 28.013
        MCO2   = 44.01
        MO2    = 15.9994
## находим молярную массу смеси
        Mgas=FPG_CH4*MCH4+FPG_C2H6*MC2H6+FPG_C3H8*MC3H8+FPG_C4H10*MC4H10+FPG_C5H12*MC5H12+FPG_N2*MN2+FPG_CO2*MCO2+FPG_O2*MO2
        if cmn.is_undefined(Mgas) or Mgas==0:
            Mgas=Mgas_default

    return round(Mgas,4)


def get_BHT(ctx,THT,MD_default):
# подсчитываем Тзаб из идеи потери 1 С на 200м.
    bh = eu.find_borehole(ctx.pStorage,ctx.borehole_id)
    L=bh.getDrilledMD() #пробуренный забой
    if cmn.is_undefined(L):
        L=MD_default
    BHT = THT+(L/100)+273
    return round(BHT,2)


def get_Zbhp(ctx,THT,THP,BHP,Mgas_default,MD_default):
    Mgas=get_Mgas(ctx,Mgas_default)
    BHT = get_BHT(ctx,THT,MD_default)
    ##рассчитаем Ркр и Ткр по ф-м Хенкинсона,  Томаса и Филипа
    Pkr = 0.006894*(709.604-(Mgas/28.96)*58.718)
    Tkr = (170.491+(Mgas/28.96)*307.44)/1.8

    Ppr_zab = BHP/(10*Pkr)
    Tpr_zab = BHT/Tkr
    Zbhp = (0.4*math.log10(Tpr_zab)+0.73)**Ppr_zab+0.1*Ppr_zab
    return round(Zbhp,7)

def get_Zbhp2(ctx,BHP,BHT,Mgas_default):
    Mgas=get_Mgas(ctx,Mgas_default)
    ##рассчитаем Ркр и Ткр по ф-м Хенкинсона,  Томаса и Филипа
    Pkr = 0.006894*(709.604-(Mgas/28.96)*58.718)
    Tkr = (170.491+(Mgas/28.96)*307.44)/1.8

    Ppr_zab = BHP/(10*Pkr)
    Tpr_zab = BHT/Tkr
    Zbhp = (0.4*math.log10(Tpr_zab)+0.73)**Ppr_zab+0.1*Ppr_zab
    return round(Zbhp,7)

def get_Zbhp3(bhp,bht,relative_den_gas):
    z = 1-((10.2*bhp*0.101325-6)*(0.00345*relative_den_gas-0.000446)+0.015)*(1.3-0.0144*(bht-283.2))
    return z

def Thydrat_calc(ctx, Potn_default,THP):
    a          = 0.035
    Potn_table = [0.6000,0.6500,0.7000,0.7500,0.8000,0.8500,0.9000,0.9500,1.0000]
    k_table    = [0.0050,0.0060,0.0075,0.0087,0.0100,0.0114,0.0128,0.0144,0.0160]
    B_table    = [1.0000,0.9000,0.8200,0.7600,0.7000,0.6600,0.6100,0.5700,0.5400]
    for i in range(len(Potn_table)):
        if Potn_table[i]>Potn_default:
            if i==0:
                K= k_table[0];B = B_table[0]
            else:
                K = k_table[i-1]+((Potn_table[i]-Potn_default)/(Potn_table[i]-Potn_table[i]-1))*(k_table[i]-k_table[i-1])
                B = B_table[i-1]+((Potn_table[i]-Potn_default)/(Potn_table[i]-Potn_table[i]-1))*(B_table[i]-B_table[i-1])
    LgP = math.log10(THP)
    Discremenant = ((a)**2-4*K*a*(B-LgP))
    if Discremenant<0:
        Thydr=cmn.get_undefined_i32()
    if Discremenant==0:
        Thydr=(-1*a)/(2*K*a)
    if Discremenant>0:
        Thydr=((-1*a)+(Discremenant)**0.5)/(2*K*a)

    return Thydr

def get_a_b_IPR(ctx, well_id):
    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    res = dmsrv.python_results()
    # загрузка
    data = dm.IWellTestsData.makeIpr(dm.db_direct)
    data.load(ctx.pStorage, well_id, pctx, terr)
    #typedef item dm.IWellTest
    if data.size()==0:
        return '',''
    dt = cmn.date_t()
    dt = cmn.date_to_string(data.getDataMaxDate())

    layers = ["BOREHOLE_ID","EVENT_DATE","WT_QUAD_BHP_A"]
    table = tu.makeBoreholeTable("IPR_NAV_TABLE", ctx, layers, well_id, res)
    if table is None:
        return '',''
    rowsCount = table.getRowCount()
    if not rowsCount:
        return '',''
    
    for i in range(rowsCount):
        datet= tu.getStr2("EVENT_DATE",  i, table)
        datet=datet[-7]+datet[-6]+datet[-5]+datet[-4]+datet[-3]+datet[-2]+datet[-1]
        if dt==datet:
            a_coef = tu.getNum2("WT_QUAD_BHP_A",  i, table)
            b_coef = tu.getNum2("WT_QUAD_BHP_B",  i, table)
            ab_date=tu.getStr2("EVENT_DATE",  i, table)
            actual_ab_date=tu.getStr2("EVENT_DATE",  i, table)
    for xxx in range(i+1):
        if cmn.is_undefined(a_coef) or cmn.is_undefined(b_coef):
            a_coef = tu.getNum2("WT_QUAD_BHP_A",  i-xxx, table)
            b_coef = tu.getNum2("WT_QUAD_BHP_B",  i-xxx, table)
            ab_date=tu.getStr2("EVENT_DATE",  i-xxx, table)
            if not cmn.is_undefined(a_coef) and not cmn.is_undefined(b_coef):
                break

    return a_coef,b_coef


def get_initial_IPR_drygas(ctx, well_id):
    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    res = dmsrv.python_results()
    # загрузка
    data = dm.IWellTestsData.makeIpr(dm.db_direct)
    data.load(ctx.pStorage, well_id, pctx, terr)
#typedef item dm.IWellTest
    if data.size()==0:
        return [[],[],[],[],[],[],[],'','','','','']
    dt = cmn.date_t()
    dt = cmn.date_to_string(data.getDataMaxDate())

    for i in range(data.size()):
        item = data.at(i)
        if cmn.date_to_string(item.getDate()) == dt:
            break

    bhp=[];thp=[];qgas=[];ppl=[];dp=[];oil=[];wat=[]
    #typedef stage dm.IWtStage
    for ii in range(item.stagesCount()):
        stage = item.stageAt(ii)
        if cmn.is_undefined(stage.getNGasRateV()) or cmn.is_undefined(stage.getBHPressure()):
            continue
        else:
            if stage.getBHPressure() in bhp:
                continue
            bhp.append(stage.getBHPressure())
            thp.append(stage.getWellheadPressure())
            qgas.append(stage.getNGasRateV())
            if not cmn.is_undefined(stage.getOilRateV()):
                oil.append(stage.getOilRateV())
            else:
                oil.append('')
            if not cmn.is_undefined(stage.getWaterRateV()):
                wat.append(stage.getWaterRateV())
            else:
                wat.append('')
            if not cmn.is_undefined(stage.getSBHPressure()):
                ppl.append(stage.getSBHPressure())
                dp.append(float(stage.getSBHPressure())-float(stage.getBHPressure()))
            else:
                ppl.append('')
                dp.append('')
    sorted_bhp  = []
    sorted_thp  = []
    sorted_qgas = []
    sorted_ppl  = []
    sorted_dp   = []
    sorted_oil  = []
    sorted_wat  = []
    for oo in  range(len(bhp)):
        sorted_bhp.append(bhp[oo])
        sorted_thp.append('')
        sorted_qgas.append('')
        sorted_ppl.append('')
        sorted_dp.append('')
        sorted_oil.append('')
        sorted_wat.append('')
    sorted_bhp.sort()

    for i in range (len(bhp)):
        for ii in range(len(sorted_bhp)):
            if bhp[i]==sorted_bhp[ii]:
                sorted_thp[ii]=thp[i]
                sorted_qgas[ii]=qgas[i]
                sorted_ppl[ii]=ppl[i]
                sorted_dp[ii]=dp[i]
                sorted_oil[ii]  = oil[i]
                sorted_wat[ii]  = wat[i]
                break

    layers = ["BOREHOLE_ID","EVENT_DATE","WT_QUAD_BHP_A"]
    table = tu.makeBoreholeTable("IPR_NAV_TABLE", ctx, layers, well_id, res)
    if table is None:
        print ('False1')
    
    rowsCount = table.getRowCount()
    if not rowsCount:
        print ('False2')
    
    for i in range(rowsCount):
        datet= tu.getStr2("EVENT_DATE",  i, table)
        datet=datet[-7]+datet[-6]+datet[-5]+datet[-4]+datet[-3]+datet[-2]+datet[-1]
        if dt==datet:
            a_coef = tu.getNum2("WT_QUAD_BHP_A",  i, table)
            b_coef = tu.getNum2("WT_QUAD_BHP_B",  i, table)
            ab_date=tu.getStr2("EVENT_DATE",  i, table)
            actual_ab_date=tu.getStr2("EVENT_DATE",  i, table)
    for xxx in range(i+1):
        if cmn.is_undefined(a_coef) or cmn.is_undefined(b_coef):
            a_coef = tu.getNum2("WT_QUAD_BHP_A",  i-xxx, table)
            b_coef = tu.getNum2("WT_QUAD_BHP_B",  i-xxx, table)
            ab_date=tu.getStr2("EVENT_DATE",  i-xxx, table)
            if not cmn.is_undefined(a_coef) and not cmn.is_undefined(b_coef):
                break
##    #блок по проверке качества данных дебита
##    if not cmn.is_undefined(a_coef) and not cmn.is_undefined(b_coef):
##        for i in range(len(sorted_qgas)):
##            if ((a_coef**2)+4*b_coef*((sorted_ppl[i]**2)-(sorted_bhp[i]**2)))>0:
##                yyy=math.sqrt(((a_coef**2)+4*b_coef*((sorted_ppl[i]**2)-(sorted_bhp[i]**2))))
##                if b_coef<0:
##                    sorted_qgas[i]=-a_coef-yyy/(2*b_coef)
##                else:
##                    sorted_qgas[i]=-a_coef+yyy/(2*b_coef)

    return [sorted_bhp,sorted_thp,sorted_qgas,sorted_ppl,sorted_dp,sorted_oil,sorted_wat,dt,a_coef,b_coef,ab_date,actual_ab_date]

def get_last_IPR_drygas(ctx, well_id):
    n_st=[];cho=[];pbuf=[];pdo=[];pposle=[];t_st=[];wat=[];sand=[];pstat=[];uwat=[];usand=[];tim_st=[]
    
    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    res  = dmsrv.python_results()
    # загрузка
    data = dm.IWellTestsData.makeIpr(dm.db_direct)
    data.load(ctx.pStorage, well_id, pctx, terr)
    #typedef item dm.IWellTest
    if data.size()==0:
        return n_st,cho,pbuf,pdo,pposle,t_st,tim_st,wat,sand,pstat,uwat,usand,'01.01.1900'
    dt = cmn.date_t()
    dt = cmn.date_to_string(data.getDataMaxDate())
    dt_d = data.getDataMaxDate()

    layer = ['BOREHOLE_ID', 'EVENT_DATE']
    table = tu.makeBoreholeTable("IPR_NAV_TABLE",ctx,layer,well_id,res)

    for i in range(data.size()):
        item = data.at(i)
        if cmn.date_to_string(item.getDate()) == dt:
            for ii in range(table.getRowCount()):
                ddt = tu.getDate2('EVENT_DATE',  ii, table)
                if ddt.day_number()<1.0001*dt_d.day_number() and ddt.day_number()>0.99999*dt_d.day_number():
                    dt = tu.getStr2('EVENT_DATE',  ii, table)
                    break
            break
    #typedef stage dm.IWtStage
    for ii in range(item.stagesCount()):
        stage = item.stageAt(ii)
        if cmn.is_undefined(stage.getWellheadPressure()):
            continue
        else:
            val = stage.getStageNum()
            if not cmn.is_undefined(val):
                n_st.append(val)
            else:
                n_st.append('')

            val = stage.getDuration()
            if not cmn.is_undefined(val):
                tim_st.append(val)
            else:
                tim_st.append('')

            val = stage.getChokeSize()
            if not cmn.is_undefined(val):
                cho.append(val)
            else:
                val = stage.getOrificeSize()
                if not cmn.is_undefined(val):
                    cho.append(val)
                else:
                    cho.append('')
                
                
            pin = stage.getWellheadPressure()
            if not cmn.is_undefined(pin):
                pbuf.append(float(pin)*1.033227565)
            else:
                pbuf.append('')

            val = stage.getDeviceInputPressure()
            if not cmn.is_undefined(val):
                if float(val)>0:
                    pdo.append(float(val)*1.033227565)
                else:
                    if cmn.is_undefined(pin):
                        pdo.append('')
                    else:
                        pdo.append(float(pin)*1.033227565)
            else:
                if cmn.is_undefined(pin):
                    pdo.append('')
                else:
                    pdo.append(float(pin)*1.033227565)

            val = stage.getDeviceOutputPressure()
            if not cmn.is_undefined(val):
                pposle.append(float(val)*1.033227565)
            else:
                pposle.append('')

            val = stage.getOCFMTemperature()
            if not cmn.is_undefined(val):
                t_st.append(val)
            else:
                t_st.append('')

            val = stage.getWaterV()
            if not cmn.is_undefined(val):
                wat.append(val)
            else:
                wat.append('')

            val = stage.getSandVolume()
            if not cmn.is_undefined(val):
                sand.append(val)
            else:
                sand.append('')

            val = stage.getSWHP()
            if not cmn.is_undefined(val):
                pstat.append(float(val)*1.033227565)
            else:
                pstat.append('')

            val = stage.getWtrf()
            if not cmn.is_undefined(val):
                uwat.append(val)
            else:
                uwat.append('')

            val = stage.getSandSlough()
            if not cmn.is_undefined(val):
                usand.append(val)
            else:
                usand.append('')

    return n_st,cho,pbuf,pdo,pposle,t_st,tim_st,wat,sand,pstat,uwat,usand,dt

def get_all_IPR_drygas(ctx, well_id):
    mas  = [];qual=[]
    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    res  = dmsrv.python_results()

    data = dm.IWellTestsData.makeIpr(dm.db_direct)
    data.load(ctx.pStorage, well_id, pctx, terr)
    #typedef item dm.IWellTest
    if data.size()==0:
        return mas
    dt = cmn.date_t()
    dt = cmn.date_to_string(data.getDataMaxDate())

    for i in range(data.size()):
        item = data.at(i)
        if cmn.date_to_string(item.getDate())==dt:
            continue
        comm = item.getTestResult()
        if comm=='плохое качество':
            qual.append(0)
        else:
            qual.append(1)
        thp=[];gas=[];pstat=[];c_thp_coef='';n_thp_coef='';cn_thp_date=''
        #typedef stage dm.IWtStage
        for ii in range(item.stagesCount()):
            stage = item.stageAt(ii)
            if cmn.is_undefined(stage.getWellheadPressure()) or cmn.is_undefined(stage.getNGasRateV()):
                continue
            else:
                val = stage.getWellheadPressure()
                if not cmn.is_undefined(val):
                    thp.append(float(val)*1.033227565)
                else:
                    thp.append('')

                val = stage.getNGasRateV()
                if not cmn.is_undefined(val):
                    gas.append(val)
                else:
                    gas.append('')
    
                val = stage.getSWHP()
                if not cmn.is_undefined(val):
                    pstat.append(float(val)*1.033227565)
                else:
                    pstat.append('')
    
        layers = ["BOREHOLE_ID","EVENT_DATE","WT_QUAD_BHP_A"]
        table = tu.makeBoreholeTable("IPR_NAV_TABLE", ctx, layers, well_id, res)
        if table is None:
            continue
        
        rowsCount = table.getRowCount()
        if not rowsCount:
            continue
        
        for i in range(rowsCount):
            datet= tu.getStr2("EVENT_DATE",  i, table)
            datet=datet[-7]+datet[-6]+datet[-5]+datet[-4]+datet[-3]+datet[-2]+datet[-1]
            if datet==cmn.date_to_string(item.getDate()):
                c_thp_coef  = tu.getNum2("WT_PWR_WHP_C",  i, table)
                if cmn.is_undefined(c_thp_coef):
                    c_thp_coef=''
                n_thp_coef  = tu.getNum2("WT_PWR_WHP_N",  i, table)
                if cmn.is_undefined(n_thp_coef):
                    n_thp_coef=''
                cn_thp_date = tu.getStr2("EVENT_DATE",    i, table)
                if cmn.is_undefined(cn_thp_date):
                    cn_thp_date=''
                break
        mas.append([thp,gas,pstat,c_thp_coef,n_thp_coef,cn_thp_date])
    return mas,qual

def save_iterp_ik_result(ctx,bh,a,b,A,B,C,N,c,n,ak,bk,Ak,Bk,Ck,Nk,ck,nk,mn_eps,mn_lm,Q,dQ,pbuf,pcas,plin,tlin):
    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    res  = dmsrv.python_results()

    data = dm.IWellTestsData.makeIpr(dm.db_caching)
    data.load(ctx.pStorage, bh.getID(), pctx, terr)
    #typedef item dm.IWellTest
    #typedef params dm.IWtResultParams
    
    if data.size()==0:
        return False
    dt = cmn.date_t()
    dt = data.getDataMaxDate()

    for i in range(data.size()):
        item = data.at(i)
        if (item.getDate()).day_number()==dt.day_number():
##            x = item.resultsCount()
            result = item.resultAt(0)
            params = result.params()
            if not cmn.is_undefined(a):
                params.setQuadEqBhpA(float(a))
            if not cmn.is_undefined(b):
                params.setQuadEqBhpB(float(b))
            if not cmn.is_undefined(A):
                params.setQuadEqWhpA(float(A))
            if not cmn.is_undefined(B):
                params.setQuadEqWhpB(float(B))
            if not cmn.is_undefined(c):
                params.setPwrEqWHP_c(float(c))
            if not cmn.is_undefined(n):
                params.setPwrEqWHP_n(float(n))
            if not cmn.is_undefined(C):
                params.setPwrEqWhpC(float(C))
            if not cmn.is_undefined(N):
                params.setPwrEqWhpN(float(N))
            if not cmn.is_undefined(ak):
                params.setapproxCoeffQuadEqBHP_a(float(ak))
            if not cmn.is_undefined(bk):
                params.setApproxCoeffQuadEqBHP_b(float(bk))
            if not cmn.is_undefined(Ak):
                params.setApproxCoeffQuadEqWHP_A(float(Ak))
            if not cmn.is_undefined(Bk):
                params.setApproxCoeffQuadEqWHP_B(float(Bk))
            if not cmn.is_undefined(ck):
                params.setApproxCoeffPwrEqBHP_C(float(ck))
            if not cmn.is_undefined(nk):
                params.setApproxCoeffPwrEqBHP_N(float(nk))
            if not cmn.is_undefined(Ck):
                params.setApproxCoeffPwrEqWHP_C(float(Ck))
            if not cmn.is_undefined(Nk):
                params.setApproxCoeffPwrEqWHP_N(float(Nk))
            if not cmn.is_undefined(mn_eps):
                params.setAbsMultiplierRough(float(mn_eps))
            if not cmn.is_undefined(mn_lm):
                params.setCoeffMultiplierHydrResistance(float(mn_lm))
            if not cmn.is_undefined(Q):
                params.setRateBHPNull(float(Q))
            if not cmn.is_undefined(dQ):
                params.setScatterRTENG(float(dQ))
            if not cmn.is_undefined(pbuf):
                params.setOperatingBufferPressure(float(pbuf))
            if not cmn.is_undefined(pcas):
                params.setOperatingAnnualPressure(float(pcas))
            if not cmn.is_undefined(plin):
                params.setOperatingLinePressure(float(plin))
            if not cmn.is_undefined(tlin):
                params.setOperatingLineTemperature(float(tlin))

            break
    data.save(pctx, terr)

    ui.refresh_ui_after_regs_changed()    
##    op_opt = dm.op_options()
##    op_ctx = dm.op_context()
##    ch_man = ctx.pStorage.getChangeManager()
##        
##    ress = dm.processed_results()
##    b = ch_man.commit(op_opt,op_ctx,pctx,terr, ress)
    return True

def change_st_ik(ctx,bh,ik,list_exp):
    pctx = cmn.progress_ctx()
    terr = cmn.err_info()
    data = dm.IWellTestsData.makeIpr(dm.db_direct)
    data.load(ctx.pStorage, bh.getID(), pctx, terr)
    #typedef item dm.IWellTest
    if data.size()==0:
        return True
    num = 0
    dt = cmn.date_t()
    dt = cmn.date_to_string(data.getDataMaxDate())
    a=0
    for i in range(data.size()):
        i-=a
        item = data.at(data.size()-i-1)
        if cmn.date_to_string(item.getDate())==dt:
            a=1
            continue
        if i in list_exp:
            num+=1
            if str(num) not in ik:
                item.setTestResult('плохое качество')
        if num==5:
            break
    data.save(pctx, terr)       
    ui.refresh_ui_after_regs_changed() 
    return True

def get_val_fr_opwo(ctx,bh_obj,res):
    marker=0
    qgas=[];bhp=[];thp=[]
    layers = ["BOREHOLE_ID","OP_DATE"]
    table = tu2.makeTableController("OPERATING_PRACTICES_TABLE", ctx.pStorage, layers)
    if table is None:
        return [],[],[]

    tu2.refreshTable(table, ctx.pStorage, [bh_obj])
    rowsCount = table.getRowCount()
    if not rowsCount:
        return [],[],[]

    for i in range(rowsCount):
        if tu.getStr2("BOREHOLE_ID",  i, table) == bh_obj.getName():
            if not cmn.is_undefined(tu.getNum2("OP_RTENGAD",  i, table)) and not cmn.is_undefined(tu.getNum2("OP_BHP_CALC",  i, table)) and not cmn.is_undefined(tu.getNum2("OP_BUFFP",  i, table)):
                qgas.append(tu.getNum2("OP_RTENGAD",  i, table))
                bhp.append(tu.getNum2("OP_BHP_CALC",  i, table))
                thp.append(tu.getNum2("OP_BUFFP",  i, table))
    return qgas,bhp,thp

def get_last_qgas(ctx,bhs,res):
    marker=0
    layers = ["BOREHOLE_ID","PROD_DATE","RESERVOIR_ID","RTENG"]
    table = tu2.makeTableController("MULTIWELL_PROD_TABLE", ctx.pStorage, layers)
    if table is None:
        return []
    tu2.refreshTable(table, ctx.pStorage, bhs)
    rowsCount = table.getRowCount()
    if not rowsCount:
        return []
    well_list=[];rates=[]
    for i in bhs:
        well_list.append(i.getName())
        rates.append(0)
    for i in range(rowsCount):
        if tu.getStr2("BOREHOLE_ID",  i, table) in well_list:
            for ii in range(len(well_list)):
                if well_list[ii]==tu.getStr2("BOREHOLE_ID",  i, table):
                    if not cmn.is_undefined(tu.getNum2("RTENG",  i, table)) and tu.getNum2("RTENG",  i, table)!=0:
                        rates[ii]=tu.getNum2("RTENG",  i, table)
                    break
        else:
            continue
    return rates

def get_exact_qgas(ctx,bh,date,res):
    rate = cmn.get_undefined_r32()

    marker=0
    layers = ["BOREHOLE_ID","PROD_DATE","RESERVOIR_ID","RTENG"]
    table = tu2.makeTableController("MULTIWELL_PROD_TABLE", ctx.pStorage, layers)
    if table is None:
        return rate
    tu2.refreshTable(table, ctx.pStorage, [bh])
    rowsCount = table.getRowCount()
    if not rowsCount:
        return rate
    for i in range(rowsCount):
        bh_n = tu.getStr2("BOREHOLE_ID",  i, table)
        if bh_n==bh.getName():
            if i!=rowsCount-1:
                if (tu.getDate2("PROD_DATE",  i, table)).day_number()<=date.day_number():
                    if (tu.getDate2("PROD_DATE",  i+1, table)).day_number()>date.day_number():
                        if not cmn.is_undefined(tu.getNum2("RTENG",  i, table)):
                            return tu.getNum2("RTENG",  i, table)
                        else:
                            if i!=0:
                                if cmn.is_undefined(tu.getNum2("RTENG",  i+1, table)):
                                    return tu.getNum2("RTENG",  i-1, table)
                                else:
                                    return tu.getNum2("RTENG",  i+1, table)
                        break
        else:
            continue
    return rate

def get_last_pbuf_fr_mer(ctx,bh,res):
    thp = cmn.get_undefined_r32()
    
    layers = ["BOREHOLE_ID","PROD_DATE","RESERVOIR_ID","RTENG"]
    table = tu2.makeTableController("MULTIWELL_PROD_TABLE", ctx.pStorage, layers)
    if table is None:
        return thp

    tu2.refreshTable(table, ctx.pStorage, [bh])
    rowsCount = table.getRowCount()
    if not rowsCount:
        return thp
    for i in range(rowsCount):
        if tu.getStr2("BOREHOLE_ID",  rowsCount-1-i, table) == bh.getName():
            x = tu.getNum2("WHP_MONTHLY",  rowsCount-1-i, table)
            if not cmn.is_undefined(x) and x !=0:
                thp = tu.getNum2("WHP_MONTHLY",  rowsCount-1-i, table)
                break
    return thp

def get_last_pcas_fr_mer(ctx,bh,res):
    thp = cmn.get_undefined_r32()
    
    layers = ["BOREHOLE_ID","PROD_DATE","RESERVOIR_ID","RTENG"]
    table = tu2.makeTableController("MULTIWELL_PROD_TABLE", ctx.pStorage, layers)
    if table is None:
        return thp

    tu2.refreshTable(table, ctx.pStorage, [bh])
    rowsCount = table.getRowCount()
    if not rowsCount:
        return thp
    for i in range(rowsCount):
        if tu.getStr2("BOREHOLE_ID",  rowsCount-1-i, table) == bh.getName():
            x = tu.getNum2("MP_CASING_PRESSURE",  rowsCount-1-i, table)
            if not cmn.is_undefined(x) and x !=0:
                thp = tu.getNum2("MP_CASING_PRESSURE",  rowsCount-1-i, table)
                break
    return thp

def get_last_plin_fr_mer(ctx,bh,res):
    thp = cmn.get_undefined_r32()
    
    layers = ["BOREHOLE_ID","PROD_DATE","RESERVOIR_ID","RTENG"]
    table = tu2.makeTableController("MULTIWELL_PROD_TABLE", ctx.pStorage, layers)
    if table is None:
        return thp

    tu2.refreshTable(table, ctx.pStorage, [bh])
    rowsCount = table.getRowCount()
    if not rowsCount:
        return thp
    for i in range(rowsCount):
        if tu.getStr2("BOREHOLE_ID",  rowsCount-1-i, table) == bh.getName():
            x = tu.getNum2("FLP_MONTHLY",  rowsCount-1-i, table)
            if not cmn.is_undefined(x) and x !=0:
                thp = tu.getNum2("FLP_MONTHLY",  rowsCount-1-i, table)
                break
    return thp

def get_last_tlin_fr_mer(ctx,bh,res):
    thp = cmn.get_undefined_r32()
    
    layers = ["BOREHOLE_ID","PROD_DATE","RESERVOIR_ID","RTENG"]
    table = tu2.makeTableController("MULTIWELL_PROD_TABLE", ctx.pStorage, layers)
    if table is None:
        return thp

    tu2.refreshTable(table, ctx.pStorage, [bh])
    rowsCount = table.getRowCount()
    if not rowsCount:
        return thp
    for i in range(rowsCount):
        if tu.getStr2("BOREHOLE_ID",  rowsCount-1-i, table) == bh.getName():
            x = tu.getNum2("FLP_MONTHLY",  rowsCount-1-i, table)
            if not cmn.is_undefined(x) and x !=0:
                thp = tu.getNum2("FLT_MONTHLY",  rowsCount-1-i, table)
                break
    return thp

def get_last_tbuf_fr_mer(ctx,bh,res):
    thp = cmn.get_undefined_r32()
    
    layers = ["BOREHOLE_ID","PROD_DATE","RESERVOIR_ID","RTENG"]
    table = tu2.makeTableController("MULTIWELL_PROD_TABLE", ctx.pStorage, layers)
    if table is None:
        return thp

    tu2.refreshTable(table, ctx.pStorage, [bh])
    rowsCount = table.getRowCount()
    if not rowsCount:
        return thp
    for i in range(rowsCount):
        if tu.getStr2("BOREHOLE_ID",  rowsCount-1-i, table) == bh.getName():
            x = tu.getNum2("WHT_MONTHLY",  rowsCount-1-i, table)
            if not cmn.is_undefined(x) and x !=0:
                thp = tu.getNum2("WHT_MONTHLY",  rowsCount-1-i, table)
                break
    return thp

def get_last_Ppl_at_perf(ctx,well_id,res):
    # открывает таблицу оценок давлений и ищем последнее Рпл
    layers = ["BOREHOLE_ID","EVENT_DATE","SBHP_COMPL"]
    est_pres = tu.makeBoreholeTable("PRESS_INTERP_TABLE", ctx, layers, well_id, res)
    Ppl  = cmn.get_undefined_r32()
    date = cmn.get_undefined_r32()

    if est_pres is None:
        return Ppl,date
    if est_pres.getRowCount() == 0:
        return Ppl,date
    else:
        tu.sortTable(est_pres, "EVENT_DATE")
        Ppl = tu.getNum2("SBHP_COMPL",  est_pres.getRowCount()-1, est_pres)
        date= tu.getStr2("EVENT_DATE",  est_pres.getRowCount()-1, est_pres)
        if cmn.is_undefined(Ppl):
            if est_pres.getRowCount()>1:
                for i in range(est_pres.getRowCount()-1):
                    Ppl = tu.getNum2("SBHP_COMPL",  est_pres.getRowCount()-2+i, est_pres)
                    date= tu.getStr2("EVENT_DATE",  est_pres.getRowCount()-2+i, est_pres)
                    if not cmn.is_undefined(Ppl):
                        break
    return (Ppl,date)

def get_last_Pbuf_stat(ctx,well_id,res):
    # открывает таблицу оценок давлений и ищем последнее Рпл
    layers = ["BOREHOLE_ID","EVENT_DATE","SBHP_COMPL"]
    est_pres = tu.makeBoreholeTable("PRESS_INTERP_TABLE", ctx, layers, well_id, res)
    Ppl  = cmn.get_undefined_r32()
    date = cmn.get_undefined_r32()

    if est_pres is None:
        return Ppl,date
    if est_pres.getRowCount() == 0:
        return Ppl,date
    else:
        tu.sortTable(est_pres, "EVENT_DATE")
        Ppl = tu.getNum2("EST_SWHP",  est_pres.getRowCount()-1, est_pres)
        date= tu.getStr2("EVENT_DATE",  est_pres.getRowCount()-1, est_pres)
        if cmn.is_undefined(Ppl):
            if est_pres.getRowCount()>1:
                for i in range(est_pres.getRowCount()-1):
                    Ppl = tu.getNum2("EST_SWHP",  est_pres.getRowCount()-2+i, est_pres)
                    date= tu.getStr2("EVENT_DATE",  est_pres.getRowCount()-2+i, est_pres)
                    if not cmn.is_undefined(Ppl):
                        break
    return (Ppl,date)

def get_liambda_fr_pres_meas(ctx,bh,res,d_nkt,plt,leng,z_av,t_aver):
    lmd = cmn.get_undefined_r32()
    date_str = ''

    layers = ["EVENT_DATE", "SBHP"]
    table = tu.makeBoreholeTable("PRESS_MEASURE_TABLE", ctx, layers, bh.getID(), res)
    if table is None:
        return lmd, date_str
    if not tu.hasProps(table, layers, res):
        return lmd, date_str
    if table.getRowCount() == 0:
        res.add_warning( _("No well measurement data (for calculation of liambda)"))
        return lmd, date_str

    tu.sortTable(table, "EVENT_DATE")
    rowCount = table.getRowCount4Sort()

    for i in range(rowCount):
        i=rowCount-i-1
        date_meas = tu.getDate2("EVENT_DATE", i, table)
        date_str  = tu.getStr2("EVENT_DATE", i, table)
        p_zamer   = tu.getNum2("BHP", i, table)
        pbf       = tu.getNum2("BUFP", i, table)
        pust      = tu.getNum2("WHP", i, table)
        if cmn.is_undefined(p_zamer):
            continue
        else:
            if cmn.is_undefined(pbf) and cmn.is_undefined(pust):
                pust = get_last_pbuf_fr_mer(ctx,bh,res)
            else:
                if not cmn.is_undefined(pbf):
                    pust=pbf
            #вычисляем лямбда
            qlast = get_exact_qgas(ctx,bh,date_meas,res)
            if cmn.is_undefined(qlast):
                return lmd, date_str
            s     = 0.03419*plt*leng/(z_av*(t_aver+273.15))
            lmd   = ((p_zamer*0.101325)**2-(pust*0.101325)**2)/(1.377*(10**(-10))*(qlast**2)*(1-math.exp(-2*s))*(z_av**2)*((t_aver+273.15)**2)*(1/d_nkt**5))

    return lmd, date_str

def get_perf_interval(ctx,bh_id,date,process, err):
    dhtp = dm.getDataProcessing().getDataTreatHelper()
    cdata = dhtp.makeCompletionData(dm.db_caching, dm.cat_completion_events)
    loader_data = cdata.load(ctx.pStorage, bh_id, process, err)
    top = cmn.get_undefined_r32()
    bot = cmn.get_undefined_r32()
    if loader_data is False:
        return []
    xxx = cdata.isolations()
    vec_perf_out = dm.vec_perf_interval()
    cdata.getCurrentCompletion(date, vec_perf_out, err)
    nitem = len(vec_perf_out)
    if nitem == 0:
        return top,bot
    bool_x = False
    bool_y = False

    for i in range(nitem):
        if bool_x == False and vec_perf_out[i].code == 11:
            top = vec_perf_out[i].top
            bool_x = True
        else:
            continue

    for i in range(nitem):
        if bool_y == False and vec_perf_out[-1-i].code == 11:
            bot = vec_perf_out[i].bot
            bool_y = True
        else:
            continue
    return top,bot

def get_perf_interval_tvd(ctx,bh_id,date,process, err):
    dhtp = dm.getDataProcessing().getDataTreatHelper()
    cdata = dhtp.makeCompletionData(dm.db_caching, dm.cat_completion_events)
    loader_data = cdata.load(ctx.pStorage, bh_id, process, err)
    top = cmn.get_undefined_r32()
    bot = cmn.get_undefined_r32()
    if loader_data is False:
        return []
    xxx = cdata.isolations()
    vec_perf_out = dm.vec_perf_interval()
    cdata.getCurrentCompletion(date, vec_perf_out, err)
    nitem = len(vec_perf_out)
    if nitem == 0:
        return top,bot
    bool_x = False
    bool_y = False

    for i in range(nitem):
        if bool_x == False and vec_perf_out[i].code == 11:
            top = vec_perf_out[i].top
            bool_x = True
        else:
            continue

    for i in range(nitem):
        if bool_y == False and vec_perf_out[-1-i].code == 11:
            bot = vec_perf_out[i].bot
            bool_y = True
        else:
            continue
        
    res = dmsrv.python_results()
    dsrvData = eu.load_devsurvey(bh_id, cmn.get_undefined_i32(), ctx.pStorage, res) # type: dm.IDsrvData
    if dsrvData:
        top = dsrvData.get_tvd(top)
        bot = dsrvData.get_tvd(bot)

    return top,bot

def get_param_explor_casing(ctx,bh_id):
    res = dmsrv.python_results()
    layers    = ["BOREHOLE_ID","STRING_TYPE","CASING_BASE_MD","CSECT_BASE_MD","CSECT_IDIAM","CSECT_ODIAM","CSECT_WTHICK"]
    casing    = tu.makeBoreholeTable("CASING_STRING_TABLE", ctx, layers, bh_id, res)
    date      = cmn.date_t_from_string('01.01.1900')
    undef_val = cmn.get_undefined_r32()
    bot  = cmn.get_undefined_r32()
    diam = cmn.get_undefined_r32()
    diam_out = cmn.get_undefined_r32()
    
    if casing is None:
        return undef_val,undef_val,undef_val
    if not tu.hasProps(casing, layers, res):
        return undef_val,undef_val,undef_val
    if casing.getRowCount() == 0:
        return undef_val,undef_val,undef_val
    else:
        casingCount = casing.getRowCount()
        for i in range(casingCount):
            prod_dt = tu.getDate2("EVENT_DATE",  i, casing)
            if prod_dt.day_number() > date.day_number():
                typeKON    =   tu.getStr2("STRING_TYPE",  i, casing)
                if typeKON == 'Эксплуатационная':
                    bot  = tu.getNum2("CASING_BASE_MD",   i, casing)
                    if cmn.is_undefined(bot):
                        bot = tu.getNum2("CSECT_BASE_MD",  i, casing)
                    diam     = tu.getNum2("CSTRING_IDIAM", i, casing)
                    diam_out = tu.getNum2("CSTRING_ODIAM", i, casing)  
                    tols = tu.getNum2("CSECT_WTHIC",  i, casing) 
                    if cmn.is_undefined(diam_out) and cmn.is_undefined(diam):
                        diam     = tu.getNum2("CSECT_IDIAM",  i, casing)
                        diam_out = tu.getNum2("CSECT_ODIAM",  i, casing)
                        if cmn.is_undefined(diam_out) and cmn.is_undefined(diam):
                            return bot,undef_val,undef_val
                        else:
                            if cmn.is_undefined(diam_out):
                                if not cmn.is_undefined(tols):
                                    diam_out = diam+2*tols
                                else:
                                    diam_out = diam+2*8
                            else:
                                if not cmn.is_undefined(tols):
                                    diam = diam_out-2*tols
                                else:
                                    diam = diam_out-2*8
                    else:
                        if cmn.is_undefined(diam_out):
                            if not cmn.is_undefined(tols):
                                diam_out = diam+2*tols
                            else:
                                diam_out = diam+2*8
                        else:
                            if not cmn.is_undefined(tols):
                                diam = diam_out-2*tols
                            else:
                                diam = diam_out-2*8
    return bot,diam,diam_out

def get_tubbing_param(ctx,bh_id):
    strg = ctx.pStorage
    md = cmn.get_undefined_r32()
    diam = cmn.get_undefined_r32()

    wmode = dm.db_work_mode()
    tbgs = dm.ITubingEvents.make(wmode)
    
    tctx = cmn.progress_ctx()
    terr = cmn.err_info()
    b = tbgs.load(strg, bh_id, tctx, terr)
    if (False==b):
        return md,diam
    n = tbgs.size()
    if n==0:
        return md,diam
    tbgs.sortByDateAsc()
    
    for i in range(n):
        tbg = tbgs.at(n-(i+1))
        if tbg.optype()==dm.tubop_install:
            md = tbg.baseMd()
            diam = tbg.insDiam()
            if cmn.is_undefined(diam):
                diam = tbg.outDiam()
                if diam<=89:
                    diam -= 13
                else:
                    diam -= 16
            break
    return md,diam

def get_tubbing_param2(ctx,bh_id):
    md   = cmn.get_undefined_r32()
    diam = cmn.get_undefined_r32()
    roug = 0.000006 #mm
    matr = ''

    res = dmsrv.python_results()
    layers = ["BOREHOLE_ID","EVENT_DATE","TUB_OP_TYPE"]
    tbl    = tu.makeBoreholeTable("TUBING_TABLE", ctx, layers, bh_id, res)
    if tbl is None:
        return md,diam,roug
    n = tbl.getRowCount()
    if n==0:
        return md,diam,roug

    dt_prev = ''
    for i in range(n):
        i = n-i-1
        op_type = tu.getStr2("TUB_OP_TYPE",  i, tbl)
        prod_dt = tu.getDate2("EVENT_DATE",  i, tbl)
        if op_type == 'Подъем':
            dt_prev = tu.getDate2("EVENT_DATE",  i, tbl)
            md_prev = tu.getNum2("TUB_BASE_MD",  i, tbl)
            continue
        diam = tu.getNum2("TUB_INTD",     i, tbl)
        md   = tu.getNum2("TUB_BASE_MD",  i, tbl)
        matr = tu.getStr2("TUB_MATERIAL", i, tbl)
        stat = tu.getStr2("TUB_STATE",    i, tbl)
        diout= tu.getNum2("TUB_OUTD",     i, tbl)
        if dt_prev!='':
            if md==md_prev:
                continue
        else:
            break

    tvd = 0
    dsrvData = eu.load_devsurvey(bh_id, cmn.get_undefined_i32(), ctx.pStorage, res) # type: dm.IDsrvData
    if dsrvData:
        if not cmn.is_undefined(md):
            tvd = dsrvData.get_tvd(md)

    if cmn.is_undefined(diam):
        if not cmn.is_undefined(diout):
            diam = diout
            if diam<=89:
                diam -= 13
            else:
                diam -= 16
    if matr == 'Сталь':
        if stat == 'Хорошее':
            roug = 0.000015
        else:
            roug = 0.0002
    else:
        roug = 0.000001
    if matr =='':
        roug = 0.000006
    return md,diam,roug,tvd



def get_last_Tbuf(ctx,bh_id):
    t = cmn.get_undefined_r32()
    
    err  = cmn.err_info()
    tctx = cmn.progress_ctx()
    t    = cmn.get_undefined_r32()
    dpda = dmsrv.IDailyProduction.make(dm.db_caching)
    b    = dpda.load(ctx.pStorage, bh_id, tctx, err)
    if not b:
        return t
    
    dt2 = dpda.getLastDate()
    if not cmn.is_undefined(dt2):
        mas = cmn.to_string_date(dt2).split('.')

        items = dmsrv.vec_dprod_item()
        dpda.getItemsForMonth(int(mas[2]),int(mas[1]),items)
        #typedef itm dmsrv.IDailyItem
        for itm in items:
            rteo = itm.getWellheadTempTELE()
            if not cmn.is_undefined(rteo):
                return rteo
            else:
                rteo = itm.getWellheadTempMSR()
                if not cmn.is_undefined(rteo):
                    return rteo
                else:
                    rteo = itm.getWellheadTempMI()
                    if not cmn.is_undefined(rteo):
                        return rteo
    return t

def get_last_Pbuf(ctx,bh_id):
    p = cmn.get_undefined_r32()
    
    err  = cmn.err_info()
    tctx = cmn.progress_ctx()
    dpda = dmsrv.IDailyProduction.make(dm.db_caching)
    b    = dpda.load(ctx.pStorage, bh_id, tctx, err)
    if not b:
        return p
    
    dt2 = dpda.getLastDate()
    if not cmn.is_undefined(dt2):
        mas = cmn.to_string_date(dt2).split('.')
        
        items = dmsrv.vec_dprod_item()
        dpda.getItemsForMonth(int(mas[2]),int(mas[1]),items)
        #typedef itm dmsrv.IDailyItem
        for itm in items:
            rteo = itm.getWellheadPressureTELE()
            if not cmn.is_undefined(rteo):
                return rteo
            else:
                rteo = itm.getWellheadPressureMSR()
                if not cmn.is_undefined(rteo):
                    return rteo
                else:
                    rteo = itm.getWellheadPressureMI()
                    if not cmn.is_undefined(rteo):
                        return rteo
    return p

def get_last_Pcas(ctx,bh_id):
    p = cmn.get_undefined_r32()
    
    err  = cmn.err_info()
    tctx = cmn.progress_ctx()
    dpda = dmsrv.IDailyProduction.make(dm.db_caching)
    b    = dpda.load(ctx.pStorage, bh_id, tctx, err)
    if not b:
        return p
    
    dt2 = dpda.getLastDate()
    if not cmn.is_undefined(dt2):
        mas = cmn.to_string_date(dt2).split('.')
        
        items = dmsrv.vec_dprod_item()
        dpda.getItemsForMonth(int(mas[2]),int(mas[1]),items)
        #typedef itm dmsrv.IDailyItem
        for itm in items:
            rteo = itm.getCasingPressureTELE()
            if not cmn.is_undefined(rteo):
                return rteo
            else:
                rteo = itm.getCasingPressureMSR()
                if not cmn.is_undefined(rteo):
                    return rteo
                else:
                    rteo = itm.getCasingPressureMI()
                    if not cmn.is_undefined(rteo):
                        return rteo
    return p

def get_last_Plin(ctx,bh_id):
    p = cmn.get_undefined_r32()
    
    err  = cmn.err_info()
    tctx = cmn.progress_ctx()
    dpda = dmsrv.IDailyProduction.make(dm.db_caching)
    b    = dpda.load(ctx.pStorage, bh_id, tctx, err)
    if not b:
        return p
    mh      = ctx.pStorage.getMetaHelper()

    dt2 = dpda.getLastDate()
    if not cmn.is_undefined(dt2):
        mas = cmn.to_string_date(dt2).split('.')
        items = dmsrv.vec_dprod_item()
        dpda.getItemsForMonth(int(mas[2]),int(mas[1]),items)
        for itm in items:
            p = mh.getProperty("DPR_TELE_ORFP_PLUS")
            if cmn.is_undefined(p):
                p = mh.getProperty("DPR_MNL_FLP")
    return p

def get_last_Tlin(ctx,bh_id):
    p = cmn.get_undefined_r32()
    
    err  = cmn.err_info()
    tctx = cmn.progress_ctx()
    dpda = dmsrv.IDailyProduction.make(dm.db_caching)
    b    = dpda.load(ctx.pStorage, bh_id, tctx, err)
    if not b:
        return p
    mh      = ctx.pStorage.getMetaHelper()

    dt2 = dpda.getLastDate()
    if not cmn.is_undefined(dt2):
        mas = cmn.to_string_date(dt2).split('.')
        items = dmsrv.vec_dprod_item()
        dpda.getItemsForMonth(int(mas[2]),int(mas[1]),items)
        for itm in items:
            p = mh.getProperty("DPR_TELE_FLT2")
            if cmn.is_undefined(p):
                p = mh.getProperty("DPR_MNL_FLT")
    return p

def get_last_choke_dp(ctx,bh):
    pplus  = cmn.get_undefined_r64()
    pminus = cmn.get_undefined_r64()

    err  = cmn.err_info()
    tctx = cmn.progress_ctx()
    dpda = dmsrv.IDailyProduction.make(dm.db_caching)
    b    = dpda.load(ctx.pStorage, bh.getID(), tctx, err)
    if not b:
        return cmn.get_undefined_r64()

    mh      = ctx.pStorage.getMetaHelper()

    dt2 = dpda.getLastDate()
    if not cmn.is_undefined(dt2):
        mas = cmn.to_string_date(dt2).split('.')
        items = dmsrv.vec_dprod_item()
        dpda.getItemsForMonth(int(mas[2]),int(mas[1]),items)

        for itm in items:
            pd_plus = mh.getProperty("DPR_TELE_ORFP_PLUS")
            pd_mins = mh.getProperty("DPR_TELE_ORFP_MINUS")
            b,pplus = itm.getValue_r64(pd_plus)
            if not cmn.is_undefined(pplus):
                b,pminus = itm.getValue_r64(pd_mins)
                if not cmn.is_undefined(pminus):
                    return pplus-pminus
            else:
                pd_plus = mh.getProperty("DPR_MSR_WHP_PLUS")
                pd_mins = mh.getProperty("DPR_MSR_WHP_MINUS")
                b,pplus = itm.getValue_r64(pd_plus)
                if not cmn.is_undefined(pplus):
                    b,pminus = itm.getValue_r64(pd_mins)
                    if not cmn.is_undefined(pminus):
                        return pplus-pminus
                else:
                    pd_plus = mh.getProperty("DPR_MNL_FLP")
                    pd_mins = mh.getProperty("DPR_MNL_ORFP")
                    b,pplus = itm.getValue_r64(pd_plus)
                    if not cmn.is_undefined(pplus):
                        b,pminus = itm.getValue_r64(pd_mins)
                        if not cmn.is_undefined(pminus):
                            return pplus-pminus
    return cmn.get_undefined_r64()

def get_last_tres_fr_mer(ctx,bh):
    tres = cmn.get_undefined_r32()

    err  = cmn.err_info()
    tctx = cmn.progress_ctx()
    dpda = dmsrv.IDailyProduction.make(dm.db_caching)
    b    = dpda.load(ctx.pStorage, bh.getID(), tctx, err)
    if not b:
        return tres
    
    mh   = ctx.pStorage.getMetaHelper()
    dt2  = dpda.getLastDate()
    if not cmn.is_undefined(dt2):
        mas = cmn.to_string_date(dt2).split('.')
        items = dmsrv.vec_dprod_item()
        dpda.getItemsForMonth(int(mas[2]),int(mas[1]),items)

        for itm in items:
            tres = mh.getProperty("DPR_TELE_BHP")
            if not cmn.is_undefined(tres):
                return tres
    return tres


def av_temp(ctx,bh_id,res_obj):
    import math
    mh = ctx.pStorage.getMetaHelper()
    t_av = cmn.get_undefined_r32()

    pd_getter = res_obj.getPropertyGetter()
    if pd_getter  is None:
        return t_av
    fluid_t = mh.getProperty("LAYER_TEMPERATURE")
    ok, fluid_t = pd_getter.getProperty_r64(fluid_t)
    if cmn.is_undefined(fluid_t):
        return t_av

    last_Tbuf = get_last_Tbuf(ctx,bh_id)
    if cmn.is_undefined(last_Tbuf):
        return t_av
    
    t_av = (((float(fluid_t)-float(last_Tbuf)))/math.log((273.15+float(fluid_t))/(273.15+float(last_Tbuf))))-273.15
    return t_av

def get_density_wat_phis_chem_test(ctx,bh):
    density = cmn.get_undefined_r32()

    bhlist = dm.vec_borehole_t()
    bh_reg = ctx.pStorage.getRegHelper().getBoreholeRegistry()
    
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'EVENT_DATE', 'FPW_DENSITY']
    table = tu2.makeTableController("FLUP_WATER_PROPERTIES", ctx.pStorage, layer)
    if table is None:
        return density
    
    bhlist.append(bh)
    tu2.refreshTable(table, ctx.pStorage, bhlist, pctx=cmn.progress_ctx())
    
    if table.getRowCount()==0:
        return density
    else:
        density   = tu.getNum2('FPW_DENSITY',   table.getRowCount()-1, table)
        if cmn.is_undefined(density):
            density = cmn.get_undefined_r32()
    return density*1000

def get_wat_type_phis_chem_test(ctx,bh):
    wtype = 0

    bhlist = dm.vec_borehole_t()
    bh_reg = ctx.pStorage.getRegHelper().getBoreholeRegistry()
    
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'EVENT_DATE', 'FPW_DENSITY']
    table = tu2.makeTableController("FLUP_WATER_PROPERTIES", ctx.pStorage, layer)
    if table is None:
        return wtype
    
    bhlist.append(bh)
    tu2.refreshTable(table, ctx.pStorage, bhlist, pctx=cmn.progress_ctx())
    
    if table.getRowCount()==0:
        return wtype
    else:
        wtype   = tu.getNum2('FPW_WTYPE_IPNG',   table.getRowCount()-1, table)
        if cmn.is_undefined(wtype):
            wtype = cmn.get_undefined_r32()
    return wtype


def get_density_phis_chem_test(ctx,bh):
    density = cmn.get_undefined_r32()

    #Ркритическое, Ткрическое, Мол.масса
    CH1_pcr,CH1_tcr,CH1_mw = 4.695,190.6,16.04
    CH2_pcr,CH2_tcr,CH2_mw = 4.976,305.4,30.07
    CH3_pcr,CH3_tcr,CH3_mw = 4.333,369.8,44.09
    CH4_pcr,CH4_tcr,CH4_mw = 3.871,408.1,58.1240
    CH5_pcr,CH5_tcr,CH5_mw = 3.719,425.2,58.1240
    CH6_pcr,CH6_tcr,CH6_mw = 3.435,469.7,72.1510
    CH7_pcr,CH7_tcr,CH7_mw = 3.448,460.4,72.1510
    CH8_pcr,CH8_tcr,CH8_mw = 3.072,507.4,86.1780
    CH9_pcr,CH9_tcr,CH9_mw = 2.79,540.2,100.205
    CH10_pcr,CH10_tcr,CH10_mw = 2.535,568.8,114.232
    N2_pcr,N2_tcr,N2_mw    = 3.465,126.3,28.02
    H2_pcr,H2_tcr,H2_mw    = 1.325,33.3,2.01600
    He_pcr,He_tcr,He_mw    = 0.234,5.2,4.00260
    Ar_pcr,Ar_tcr,Ar_mw    = 4.959,150.4,20
    H2S_pcr,H2S_tcr,H2S_mw = 9.185,373.6,34.08
    CO2_pcr,CO2_tcr,CO2_mw = 7.527,304.2,44.01
    O2_pcr,O2_tcr,O2_mw = 5.08,154.75,16

    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'FPG_CH4', 'FPG_C2H6', 'FPG_C3H8', 'FPG_C4H10', 'FPG_C5H12', 'FPG_N2', 'FPG_CO2', 'FPG_O2']
    table = tu2.makeTableController("FLUP_NGAS_PROPERTIES", ctx.pStorage, layer)
    if table is None:
        return density

    bhlist = dm.vec_borehole_t()
    bh_reg = ctx.pStorage.getRegHelper().getBoreholeRegistry()
    bhlist.append(bh)
    tu2.refreshTable(table, ctx.pStorage, bhlist, pctx=cmn.progress_ctx())

    if table.getRowCount()==0:
        return density
    else:
        for x in range(table.getRowCount()):
            FPG_CH4   = tu.getNum2('FPG_CH4',   x, table)
            FPG_C2H6  = tu.getNum2('FPG_C2H6',  x, table)
            FPG_C3H8  = tu.getNum2('FPG_C3H8',  x, table)
            FPG_C4H10 = tu.getNum2('FPG_C4H10', x, table)
            FPG_C5H12 = tu.getNum2('FPG_C5H12', x, table)
            FPG_N2    = tu.getNum2('FPG_N2',    x, table)
            FPG_CO2   = tu.getNum2('FPG_CO2',   x, table)
            FPG_O2    = tu.getNum2('FPG_О2',    x, table)
        if cmn.is_undefined(FPG_CH4):
            FPG_CH4 = 0
        if cmn.is_undefined(FPG_C2H6):
            FPG_C2H6 = 0
        if cmn.is_undefined(FPG_C3H8):
            FPG_C3H8 = 0
        if cmn.is_undefined(FPG_C4H10):
            FPG_C4H10 = 0
        if cmn.is_undefined(FPG_C5H12):
            FPG_C5H12 = 0
        if cmn.is_undefined(FPG_N2):
            FPG_N2 = 0
        if cmn.is_undefined(FPG_CO2):
            FPG_CO2 = 0
        if cmn.is_undefined(FPG_O2):
            FPG_O2 = 0

    VCH1 = FPG_CH4*0.01*CH1_mw/24.04
    VCH2 = FPG_C2H6*0.01*CH2_mw/24.04
    VCH3 = FPG_C3H8*0.01*CH3_mw/24.04
    VCH4 = FPG_C4H10*0.01*CH4_mw/24.04
    VCH6 = FPG_C5H12*0.01*CH6_mw/24.04
    VN2  = FPG_N2*0.01*N2_mw/24.04
    VCO2 = FPG_CO2*0.01*CO2_mw/24.04
    V02  = FPG_O2*0.01*O2_mw/24.04

    density = VCH1+VCH2+VCH3+VCH4+VCH6+VN2+VCO2+V02
    return density

def get_density_poPT(ctx,thp,tht):
    mgas=get_Mgas(ctx,26.73)
    thp /=10
    ##рассчитаем Ркр и Ткр по ф-м Хенкинсона,  Томаса и Филипа
    pkr = 0.006894*(709.604-(mgas/28.96)*58.718)
    tkr = (170.491+(mgas/28.96)*307.44)/1.8
    ppr = thp/(10*pkr)
    tpr = tht/tkr
    
    z   = (0.4*math.log10(tpr)+0.73)**ppr+0.1*ppr
    den = (0.67*293.15*thp)/(0.1*z*(tht+273.15))
    return den

def get_pkr_tkr(ctx):
    mgas=get_Mgas(ctx,26.73)
    ##рассчитаем Ркр и Ткр по ф-м Хенкинсона,  Томаса и Филипа
    pkr = 0.006894*(709.604-(mgas/28.96)*58.718)
    tkr = (170.491+(mgas/28.96)*307.44)/1.8
    return pkr,tkr

def get_pkr_tkr_phis_chem_test(ctx,bh):
    pkr = cmn.get_undefined_r32()
    tkr = cmn.get_undefined_r32()

    #Ркритическое, Ткрическое, Мол.масса
    CH1_pcr,CH1_tcr,CH1_mw = 4.695,190.6,16.04
    CH2_pcr,CH2_tcr,CH2_mw = 4.976,305.4,30.07
    CH3_pcr,CH3_tcr,CH3_mw = 4.333,369.8,44.09
    CH4_pcr,CH4_tcr,CH4_mw = 3.871,408.1,58.1240
    CH5_pcr,CH5_tcr,CH5_mw = 3.719,425.2,58.1240
    CH6_pcr,CH6_tcr,CH6_mw = 3.435,469.7,72.1510
    CH7_pcr,CH7_tcr,CH7_mw = 3.448,460.4,72.1510
    CH8_pcr,CH8_tcr,CH8_mw = 3.072,507.4,86.1780
    CH9_pcr,CH9_tcr,CH9_mw = 2.79,540.2,100.205
    CH10_pcr,CH10_tcr,CH10_mw = 2.535,568.8,114.232
    N2_pcr,N2_tcr,N2_mw = 3.465,126.3,28.02
    H2_pcr,H2_tcr,H2_mw = 1.325,33.3,2.01600
    He_pcr,He_tcr,He_mw = 0.234,5.2,4.00260
    Ar_pcr,Ar_tcr,Ar_mw = 4.959,150.4,20
    H2S_pcr,H2S_tcr,H2S_mw = 9.185,373.6,34.08
    CO2_pcr,CO2_tcr,CO2_mw = 7.527,304.2,44.01
    O2_pcr,O2_tcr,O2_mw = 5.08,154.75,16

    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'FPG_CH4', 'FPG_C2H6', 'FPG_C3H8', 'FPG_C4H10', 'FPG_C5H12', 'FPG_N2', 'FPG_CO2', 'FPG_O2']
    table = tu2.makeTableController("FLUP_NGAS_PROPERTIES", ctx.pStorage, layer)
    if table is None:
        return pkr,tkr

    bhlist = dm.vec_borehole_t()
    bh_reg = ctx.pStorage.getRegHelper().getBoreholeRegistry()
    bhlist.append(bh)
    tu2.refreshTable(table, ctx.pStorage, bhlist, pctx=cmn.progress_ctx())

    if table.getRowCount()==0:
        return pkr,tkr
    else:
        for x in range(table.getRowCount()):
            FPG_CH4   = tu.getNum2('FPG_CH4',   x, table)
            FPG_C2H6  = tu.getNum2('FPG_C2H6',  x, table)
            FPG_C3H8  = tu.getNum2('FPG_C3H8',  x, table)
            FPG_C4H10 = tu.getNum2('FPG_C4H10', x, table)
            FPG_C5H12 = tu.getNum2('FPG_C5H12', x, table)
            FPG_N2    = tu.getNum2('FPG_N2',    x, table)
            FPG_CO2   = tu.getNum2('FPG_CO2',   x, table)
            FPG_O2    = tu.getNum2('FPG_О2',    x, table)
        if cmn.is_undefined(FPG_CH4):
            FPG_CH4 = 0
        if cmn.is_undefined(FPG_C2H6):
            FPG_C2H6 = 0
        if cmn.is_undefined(FPG_C3H8):
            FPG_C3H8 = 0
        if cmn.is_undefined(FPG_C4H10):
            FPG_C4H10 = 0
        if cmn.is_undefined(FPG_C5H12):
            FPG_C5H12 = 0
        if cmn.is_undefined(FPG_N2):
            FPG_N2 = 0
        if cmn.is_undefined(FPG_CO2):
            FPG_CO2 = 0
        if cmn.is_undefined(FPG_O2):
            FPG_O2 = 0

    VCH1 = FPG_CH4*0.01*CH1_pcr
    VCH2 = FPG_C2H6*0.01*CH2_pcr
    VCH3 = FPG_C3H8*0.01*CH3_pcr
    VCH4 = FPG_C4H10*0.01*CH4_pcr
    VCH6 = FPG_C5H12*0.01*CH6_pcr
    VN2  = FPG_N2*0.01*N2_pcr
    VCO2 = FPG_CO2*0.01*CO2_pcr
    V02  = FPG_O2*0.01*O2_pcr

    pkr = VCH1+VCH2+VCH3+VCH4+VCH6+VN2+VCO2+V02

    VCH1 = FPG_CH4*0.01*CH1_tcr
    VCH2 = FPG_C2H6*0.01*CH2_tcr
    VCH3 = FPG_C3H8*0.01*CH3_tcr
    VCH4 = FPG_C4H10*0.01*CH4_tcr
    VCH6 = FPG_C5H12*0.01*CH6_tcr
    VN2  = FPG_N2*0.01*N2_tcr
    VCO2 = FPG_CO2*0.01*CO2_tcr
    V02  = FPG_O2*0.01*O2_tcr
    
    tkr = VCH1+VCH2+VCH3+VCH4+VCH6+VN2+VCO2+V02
    
    return pkr,tkr

def get_cross_status(i1, i2, error_val):
    """функция возращает положение одного интервала относительно другого (i1 относительно i2):
        если i1 выше i2 - вернется ir_upper
        если i1 ниже i2 - вернется ir_lower
        если i1 больше i2 и включает в себя его - вернется ir_adsorb
        если i1 включен в i2 - вернется ir_contain
        если i1 пересекает i2 - вернется ir_yes

        так же вернет интервал пересечения
    """
    ir_upper   = 1
    ir_lower   = 2
    ir_adsorb  = 3
    ir_contain = 4
    ir_yes     = 5

    if i1[1] <= i2[0]:
        return ir_upper,0

    if i1[0] >= i2[1]:
        return ir_lower,0

    dela_top  = i1[0] - i2[0]
    if math.fabs(dela_top) < error_val: delta_top = 0
    dela_bot  = i1[1] - i2[1]
    if math.fabs(dela_bot) < error_val: delta_bot = 0
        
    top_upper = True if dela_top <= 0 else False
    top_lower = True if dela_top > 0  else False
    bot_upper = True if dela_bot < 0  else False
    bot_lower = True if dela_bot >= 0 else False


    if top_upper and bot_lower:
        return ir_adsorb, i2[1]-i2[0]

    if top_lower and bot_upper:
        return ir_contain, i1[1]-i2[0]

    if top_upper and bot_upper:
        return ir_yes, i2[0]-i1[1]

    if top_lower and bot_lower:
        return ir_yes, i2[1]-i1[0]

    return 1,0


def get_h_heff_fr_perf(ctx,bh_id):
    
    process = cmn.progress_ctx()
    err     = cmn.err_info()
    import datetime
    mas  = str(datetime.date.today()).split('-')
    date = '{0}.{1}.{2}'.format(mas[2],mas[1],mas[0])
    date = cmn.date_t_from_string(date)
    top_perf,bot_perf = get_perf_interval(ctx,bh_id,date,process, err)
    if cmn.is_undefined(top_perf) or cmn.is_undefined(bot_perf):
        return 0,0

##    vtrends = ctx.ents.trends()
##    trend   = vtrends[0]
##    print(trend.getID(), trend.getName())

    pl_list = []; heffcum,hcum = 0,0
    ##top1,bot1 = cmn.get_undefined_r32(),cmn.get_undefined_r32()
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'GEOLAYER_ID', 'LAYER_TOP_MD', 'LAYER_BASE_MD']
    table = tu.makeBoreholeTable('ZONEPICK_TABLE_VIEW', ctx, layer, bh_id, py_res, True, True)
    if table is None:
        return 0, 0
    if table.getRowCount()!=0:
        for x in range(table.getRowCount()):
            top1  = tu.getNum2('LAYER_TOP_MD',   x, table)
            bot1  = tu.getNum2('LAYER_BASE_MD',  x, table)
            if not cmn.is_undefined(top1) and not cmn.is_undefined(bot1):
                kod, heff  = get_cross_status([top_perf,bot_perf], [top1,bot1], 0.001)
                if heff>0:
                    pl_list.append(tu.getInt2('GEOLAYER_ID',   x, table))
                    heffcum+=heff
                    if kod >2:
                        hcum +=(bot1-top1)
    if len(pl_list)==0:
        return 0,0

    heffcum2=0; hcum2=0
    py_res = dmsrv.python_results()
    layer = ['BOREHOLE_ID', 'GEOLAYER_ID', 'LR_THICKNESS', 'LR_NET_THICKNESS']
    table = tu.makeBoreholeTable('ZONEPROP_TABLE_VIEW', ctx, layer, bh_id, py_res, True, True)
    if table is None:
        return 0,0
    if table.getRowCount()!=0:
        for x in range(table.getRowCount()):
            p_id  = tu.getInt2('GEOLAYER_ID',   x, table)
            if p_id in pl_list:
                heff = tu.getNum2('LR_NET_THICKNESS', x, table)
                if cmn.is_undefined(heff):
                    heffcum2+=heff
                h = tu.getNum2('LR_THICKNESS', x, table)
                if cmn.is_undefined(h):
                    hcum2+=h
                else:
                    if cmn.is_undefined(heff):
                        hcum2+=heff
    else:
        return heffcum,hcum
    if cmn.is_undefined(heffcum2) and cmn.is_undefined(hcum2):
        return heffcum2,hcum2
    else:
        return heffcum,hcum

def check_block_line(line):
    a = line.replace('\t',' ',10)
    a = a.replace('  ',' ',30)
    a = a.replace('\'','',4)
    if a == '' or a == ' ':
        return  False
    if len(str(a))==1:
        return  False
    if len(str(a))>1:
        if a[0:2]=='--':
            return  False
        if a[0:2]==' /':
            return  False
        if a[0:1]=='/':
            return  False
    if len(str(a))>2:
        if a[0:3]==' --':
            return  False
        if a[0:2]=='  /':
            return  False
    return True

def find_valid(line,max_num):
    line = line.replace('\t',' ',15)
    m = line.split(' ')
    mas=[]
    num=0
    for ii in range(len(m)):
        if num >= max_num:
            break
        if m[ii]!='':
            num+=1
            if '*' in str(m[ii]):
                mm = str(m[ii]).split('*')
                try: int(mm[0])
                except:
                    mas.append(m[ii])
                else:
                    for i in range(int(mm[0])):
                        if len(mm)==1:
                            mas.append('1*')
                        else:
                            if mm[1]=='':
                                mas.append('1*')
                            else:
                                mas.append(mm[1])
            else:
                if type(m[ii])==str:
                    m[ii]=m[ii].lower()
                mas.append(m[ii])
                if m[ii] =='/':
                    break
        else:
            continue
    return mas

def getS(xm,ym):
    whGdi = np.array(xm)
    whMe = np.array(ym)
    x = np.array(range(len(xm)))
    z = whGdi-whMe
    dx = x[1:] - x[:-1]
    cross_test = np.sign(z[:-1] * z[1:])
    x_intersect = x[:-1] - dx / (z[1:] - z[:-1]) * z[:-1]
    dx_intersect = - dx / (z[1:] - z[:-1]) * z[:-1]
    areas_pos = abs(z[:-1] + z[1:]) * 0.5 * dx
    areas_neg = 0.5 * dx_intersect * abs(z[:-1]) + 0.5 * (dx - dx_intersect) * abs(z[1:])
    areas = np.where(cross_test < 0, areas_neg, areas_pos)
    return np.sum(areas)

def Encode(Year,Month,Day,Hour,Min,Sec):
    M=19245847286399
    P=(Year*12027868624267) % M
    P=(P+Month*2192564880729)% M
    P=(P+Day*18882718092316)% M
    P=(P+Hour*11240937353118)% M
    P=(P+Min*15079220554292)% M
    P=(P+Sec*17560079640875)% M
    return P

def get_max_dp(ctx,obj,z_default):
    #ограничение по депрессии
    heff,h = get_h_heff_fr_perf(ctx,obj.getID())
    res    = dmsrv.python_results()
    ppl,ppl_date    = get_last_Ppl_at_perf(ctx,obj.getID(),res)
    if cmn.is_undefined(ppl):
        return cmn.get_undefined_r32()
    else:
        ppl *=0.1

    otn_den    = get_density_phis_chem_test(ctx,obj)
    if cmn.is_undefined(otn_den):
        otn_den = z_default
        
    wat_den = get_density_wat_phis_chem_test(ctx,obj)
    if cmn.is_undefined(wat_den):
        wat_den=1000

    dp = ((0.1*(h-heff)*(wat_den-otn_den)*9.81*(2*ppl*(10**5)-0.1*(h-heff)*(wat_den-otn_den)*9.81))**0.5)/(10**5)
    if dp==0:
        dp = cmn.get_undefined_r64()
    return dp
