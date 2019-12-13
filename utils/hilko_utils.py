# -*- coding: cp1251 -*-


# for command-line call
#import path_release_x64

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_dproc as dproc
import mod_dmsrv as dmsrv

import data_utils as du
import entity_utils as eu
import table_utils as tu
import table_utils2 as tu2

import math

def get_begin_month_date(date):
    ymd = cmn.to_ymd(date)
    ymd.day = 1
    dt = cmn.from_ymd(ymd)
    return dt

def get_press_plast(dateProby, items, ata_unit):
    dn_proby = dateProby.day_number()
    iPpl = cmn.get_undefined_r64()
    resv_id = cmn.get_undefined_i32()
    for item_index in reversed(range(items.size())):
            item = items.at(item_index)
            press_dt = item.getDate()
            dn_press = press_dt.day_number()
            diff = dn_proby-dn_press
            if diff > 0 and diff < 92:
                iPpl = item.getSBHPComplTop(ata_unit)
                resv_id = item.getReservoirID()
                if False == cmn.is_undefined(iPpl) and False == cmn.is_undefined(resv_id):
                    return iPpl, resv_id
    return iPpl, resv_id

def get_resv_temp(resv_reg, resv_id, pd_Tpl):
    resv = resv_reg.find(resv_id)
    pget = resv.getPropertyGetter()
    return pget.getProperty_r64(pd_Tpl)

def get_ipr(well_tests, DateProby, WasherSize, ata_unit):
    iPust = cmn.get_undefined_r64()
    iTust = cmn.get_undefined_r64()
    
    IPR = well_tests.findLast(DateProby)
    
    if None != IPR:
        DateIPR = IPR.getDate()
        
        if DateProby == DateIPR:
            k = IPR.stagesCount()
            
            for j in range(k):
                wStage = IPR.stageAt(j)
                OrifSize = wStage.getOrificeSize()

                if OrifSize == WasherSize:
                    iPust = wStage.getWellheadPressure(ata_unit) 
                    iTust = wStage.getWellheadTemperature()
                    return iPust, iTust
    
    return iPust, iTust

def get_month_prod(writer, bh_id, DateProby, ata_unit, tctx, terr):
    iPust = cmn.get_undefined_r64()
    iTust = cmn.get_undefined_r64()
    
    dt2 = get_begin_month_date(DateProby)
    dnum = dt2.day_number()
    dnum = dnum - 60
    date = cmn.date_from_jdn(dnum)
    dt1 = get_begin_month_date(date)
    
    writer.load(bh_id, dt1, dt2, tctx, terr)
            
    for i in reversed(range(writer.rowCount())):
        monthly = writer.getMonthlyAt(i)
        iPust = monthly.getMonthlyWhp(ata_unit)
        iTust = monthly.getMonthlyWht()
        
        if False == cmn.is_undefined(iPust) and False == cmn.is_undefined(iTust):
            return iPust, iTust
        
    return iPust, iTust

def get_gtf(strg, bh, date, tctx, terr):

    #by month production only
    dcats = dm.vec_data_category()
    dcats.append(dm.cat_monthly_production)


    field = bh.getField()
    vgtf = dm.vec_gtf_t() 
    field.getGtfs(vgtf)
    dt = cmn.begin_of_month(date)
    for gtf in vgtf:
        vbh = dm.vec_borehole_t()
        dmsrv.get_gtf_boreholes(strg, gtf.getID(),dt, dcats, vbh, tctx, terr)
        if bh in vbh:
            return gtf
    return None

def get_tbl_gtf_prod(strg, date, gtf):
    dt = cmn.begin_of_month(date)
    layers = ["FIELD_ID:FIELD_NAME",
              "GTF_ID",
              "PROD_DATE",
              "RESERVOIR_ID",
              "SBHP_MONTHLY", 
              "WHP_MONTHLY", 
              "WHT_MONTHLY"]

    vbh = dm.vec_borehole_t()
    tbl = tu2.makeTableController("GTF_MONTHLY_PROD_TABLE", strg, layers)
    tu2.refreshTableWithDateGtf(tbl, strg, gtf, dt)
    #tu2.sortTable(tbl, "FIELD_NAME", "PROD_DATE")
    if tbl.getRowCount() > 0:
        return tbl
    return None
    

def bukachek(p, t):                                                                                           #*----Функция определения влагосодержания в газе по Бюкачеку----
    W = 4.67 * math.exp(t * (0.0735 - 0.00027 * t)) / p + 0.0418 * math.exp(t * (0.054 - 0.0002 * t))         #*  p - текущее давление, ата; * t - текущая температура, град.С
    return W                                                                                                  #* ----результат - возвращает содержание паров воды в газе, г/м3

def Hilko(iCa, iNaK, iMinT, iMinP, iMinProby, iPpl, iPust, iTust, iTpl): #тип выносимой воды по Хилько (по кальцию)
    
    Wtype = cmn.get_undefined_i32()
    WrelK = cmn.get_undefined_r64()
    WrelT = cmn.get_undefined_r64()
    WrelP = cmn.get_undefined_r64()
    
    if iCa!=0 and iNaK!=0 and iMinT>0 and iPpl>0 and iPust>0 and iTust>0: 
        
        if iMinProby > iMinP and (iCa/iNaK) < 0.1: #если минерализация пробы воды больше минерализации пластовой воды, то принимаем минерализацию пластовой воды по верхнему пределу 22 г/л
            iMinP = 22
            
        Wkond = bukachek(iPpl, iTpl) - bukachek(iPust, iTust) #кол-во выделившейся в стволе скважины конденсационной воды
        
        dt = 0.526 * iCa / iNaK - 0.0526 #доля технической воды в минерализованной воде
        
        if iCa/iNaK < 0.1: #исключение технической воды
            dt = 0
        if iCa/iNaK > 2: #исключение пластовой воды
            dt = 1
            
        Wmin = (Wkond * iMinProby) / ((1 - dt) * iMinP + dt * iMinT - iMinProby) #кол-во минерализованной воды
        Wminp = Wmin * (1 - dt)         #кол-во пластовой воды
        Wmint = dt * Wmin               #кол-во техногенной воды
        Wsum = Wkond + Wminp + Wmint    #общее кол-во вынесенной воды 

        if 0 != Wsum:
            WrelK = Wkond / Wsum * 100      #доля конденсационной воды
            WrelT = Wmint / Wsum * 100      #кол-во техногенной воды
            WrelP = Wminp / Wsum * 100      #кол-во пластовой воды
    
            if WrelT < 10:
                if WrelP > WrelK and WrelK > 10:
                    Wtype = 4 #'Пл+К'
                if WrelP > WrelK and WrelK < 10:
                    Wtype = 1 #'Пл'
                    if Wsum < 0:
                        Wtype = cmn.get_undefined_i32()
                        
                if WrelP < WrelK and WrelP > 10:
                    Wtype = 5 #'К+Пл'
                if WrelP < WrelK and WrelP < 10:
                    Wtype = 2 #'К'
                    
            if WrelT > 10 and Wsum > 0:
                if WrelP > 10 and WrelP > WrelT:
                    Wtype = 6 #'Пл+Т'
                if WrelP > 10 and WrelP < WrelT:
                    Wtype = 7 #'Т+Пл'
                if WrelK > WrelT and WrelP <= 10:
                    Wtype = 8 #'К+Т'
                if WrelK < WrelT and WrelP <= 10:
                    Wtype = 9 #'Т+К'

    return Wtype, WrelK, WrelT, WrelP

def get_type_fluid_hilko(ctx, strg, bh, DateProby, iCa, iNaK, iMinProby, WasherSize, press_data, bWTest, well_tests, tctx, terr, res):

    Wtype = cmn.get_undefined_i32()
    WrelK = cmn.get_undefined_r64()
    WrelT = cmn.get_undefined_r64()
    WrelP = cmn.get_undefined_r64()
    
    iMinT = 150                           #минерализация технической воды, равна 150 г/л
    iMinP = 21                            #минерализация пластовой воды, равна 21 г/л
    iPpl = cmn.get_undefined_r64()        #пластовое давление, ата 
    iTpl = cmn.get_undefined_r64()        #пластовая температура, град.С 
    iPust = cmn.get_undefined_r64()       #устьевое давление, ата
    iTust = cmn.get_undefined_r64()       #устьевая температура, град.С
    
    undef = cmn.get_undefined_r64()

    tbl = None
    
    bh_id = bh.getID()
    bh_name = bh.getName()
    
    mh = strg.getMetaHelper()
    pd_Tpl = mh.getProperty("LAYER_TEMPERATURE")
    pd_Ppl = mh.getProperty("SBHP_MONTHLY")
    pd_Pust = mh.getProperty("WHP_MONTHLY")
    pd_Tust = mh.getProperty("WHT_MONTHLY")
    pd_resv = mh.getProperty("RESERVOIR_ID")

    ata_unit = mh.getUnit("ata")

    resv_reg = strg.getRegHelper().getReservoirRegistry()
    
    writer = dmsrv.production(strg, dm.pit_month, dm.db_caching)
    writer_gtf = dmsrv.production(strg, dm.pit_month, dm.db_caching, dm.pden_gtf)
    gtf_monthly = None

    items = press_data.getPressEstItems()

    if undef==iCa or undef==iNaK or undef==iMinProby:
        ymd = cmn.to_ymd(DateProby)
        s = _("Borehole {0}, Date sample {1}.{2}.{3}: No water probes analysis").format(bh_name, ymd.day, ymd.month, ymd.year)
        res.add_warning(s)
        dmsrv.py_log_warn(ctx.opo.logger(), s)
        return False, Wtype, WrelK, WrelT, WrelP
        
    iPpl, resv_id = get_press_plast(DateProby, items, ata_unit) #Пластовое давление и резервуар из "Оценок давлений"

    if undef==iPpl:
        gtf = get_gtf(strg, bh, DateProby, tctx, terr)
        
        if gtf is not None:
            tbl = get_tbl_gtf_prod(strg,DateProby,gtf)
            
            if tbl is not None:
                b, iPpl = tbl.dataAsNum(pd_Ppl, cmn.get_undefined_i32(), 0, ata_unit)
                b, resv_id = tbl.dataAsInt(pd_resv, cmn.get_undefined_i32(), 0)
                if iPpl != undef:
                    ymd = cmn.to_ymd(DateProby)
                    s = ("Скважина {0}, Дата пробы {1}.{2}.{3}: Pпл взято из показателей разработки по ГП").format(bh_name, ymd.day, ymd.month, ymd.year)
                    #res.add_warning(s)
                    dmsrv.py_log_warn(ctx.opo.logger(), s)
            

    if undef==iPpl or cmn.is_undefined(resv_id):
        ymd = cmn.to_ymd(DateProby)
        s = _("Borehole {0}, Date sample {1}.{2}.{3}: No reservoir pressure or reservoir").format(bh_name, ymd.day, ymd.month, ymd.year)
        res.add_warning(s)
        dmsrv.py_log_warn(ctx.opo.logger(), s)
        return False, Wtype, WrelK, WrelT, WrelP

    resv = resv_reg.find(resv_id)
    pget = resv.getPropertyGetter()
    b, iTpl = pget.getProperty_r64(pd_Tpl) #Пластовая температура из резервуара

    if False == b:
        s = _("Reservoir {0}: No reservoir temperature").format(resv.getName())
        res.add_warning(s)
        dmsrv.py_log_warn(ctx.opo.logger(), s)
        return False, Wtype, WrelK, WrelT, WrelP

    if bWTest: #Если есть ИК на дату замера и с таким же диаметром штуцера, то берем Pуст и Tуст из ИК
        iPust, iTust = get_ipr(well_tests, DateProby, WasherSize, ata_unit)

    if undef==iPust or undef==iTust: #Если Pуст и Tуст не нашли в ИК, то берем их из "Показателей разработки"
        iPust, iTust = get_month_prod(writer, bh_id, DateProby, ata_unit, tctx, terr)

        if undef==iPust or undef==iTust:
            if tbl is not None:
                table = tbl
            else:
                gtf = get_gtf(strg, bh, DateProby, tctx, terr)
                if gtf is not None:
                    tbl = get_tbl_gtf_prod(strg,DateProby,gtf)
                    if tbl is not None:
                        table = tbl
                        
            if table is not None:
                b, iPust = table.dataAsNum(pd_Pust, cmn.get_undefined_i32(), 0, ata_unit)
                b, iTust = table.dataAsNum(pd_Tust, cmn.get_undefined_i32(), 0, ata_unit)
                
                if undef not in [iPust,iTust]:
                    ymd = cmn.to_ymd(DateProby)
                    s = ("Скважина {0}, Дата пробы {1}.{2}.{3}: Pуст, Туст взяты из показателей разработки по ГП").format(bh_name, ymd.day, ymd.month, ymd.year)
                    #res.add_warning(s)
                    dmsrv.py_log_warn(ctx.opo.logger(), s)
            
        if undef==iPust or undef==iTust:
            ymd = cmn.to_ymd(DateProby)
            s = _("Borehole {0}, Date sample {1}.{2}.{3}: No monthly production data").format(bh_name, ymd.day, ymd.month, ymd.year)
            res.add_warning(s)
            dmsrv.py_log_warn(ctx.opo.logger(), s)
            return False, Wtype, WrelK, WrelT, WrelP
    
    Wtype, WrelK, WrelT, WrelP = Hilko(iCa, iNaK, iMinT, iMinP, iMinProby, iPpl, iPust, iTust, iTpl)

    return True, Wtype, WrelK, WrelT, WrelP