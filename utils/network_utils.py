# -*- coding: cp1251 -*-
import mod_dm as dm
import mod_cmn as cmn
import mod_dmsrv as dmsrv
import mod_ui as ui

import table_utils as tu
import entity_utils as eu
import table_utils2 as tu2
import estimations_utils as esu

import os
import datetime
import subprocess


class deft_nb:
    def __init__(self,dirr,versia):
        self.dirr = dirr
        self.wells      = []
        self.pipelines  = []
        self.w_list = []
        self.p_list = []
        if versia==3:
            self.read_procedure_03()
        else:
            self.read_procedure()


    def read_procedure(self):
        f          = open(self.dirr,'r')
        count      = 0
        num_str    = 0
        well_found = 0
        poriadok   = []
        num_poriadok=-1

        ##чтение заголовка
        first_date_yyyy=''
        date_found     =0
        num  =0
        for line in f:
            num+=1
            line = line.rstrip('\n') 
            line = line.replace('  ',' ',100)
            mas=line.split(' ')
    
            if mas[0]=='HEADER_END':
                count=0
            if count==1:
                i=0
                well_name   = str(mas[2+6*i])
                well_name = well_name.replace('\"','',2)
                vec_name    = str(mas[3+6*i])
                vec_name = vec_name.replace('\"','',2)
                ed_izm_name = str(mas[4+6*i])
                ed_izm_name = ed_izm_name.replace('\"','',2)
                well_found = 0
                if mas[1+6*i]=="\"WELL\"":
                    if well_name not in self.w_list:
                        self.w_list.append(well_name)
                    for ii in range(len(self.wells)):
                        if str(self.wells[ii][0])==str(well_name):
                            self.wells[ii][1].append([vec_name,ed_izm_name,[]])
                            ##              [0-self.wells(1-pipelines), порядковый номер скв в массиве, порядковый номер ветора в массиве]
                            poriadok.append([0,ii,len(self.wells[ii][1])-1])
                            well_found=1
                            break
                    if well_found==0:
                        self.wells.append([well_name,[[vec_name,ed_izm_name,[]]]])
                        poriadok.append([0,len(self.wells)-1,0])
                        continue
                    else:
                        continue
                well_found=0
                if mas[1+6*i]=="\"GROUP\"":
                    if well_name not in self.p_list:
                        self.p_list.append(well_name)
                    if mas[2+6*i]=="\"TIME\"":
                        continue
                    for ii in range(len(self.pipelines)):
                        if self.pipelines[ii][0]==well_name:
                            self.pipelines[ii][1].append([vec_name,ed_izm_name,[]])
                            ##              [0-self.wells(1-self.pipelines), порядковый номер скв в массиве, порядковый номер ветора в массиве]
                            poriadok.append([1,ii,len(self.pipelines[ii][1])-1])
                            well_found=1
                            break
                    if well_found==0:
                        self.pipelines.append([well_name,[[vec_name,ed_izm_name,[]]]])
                        poriadok.append([1,len(self.pipelines)-1,0])
                well_found=0
            if mas[0]=='HEADER_START':
                count=1
                total_count=0
            if mas[0]=='DATA_END':
                continue
        ##заполнение массивов данными расчета
            if count==2:
                delta=0
                if num_poriadok==-1 and date_found==0:
                    date=mas[0]
                    date_found=1
                    if first_date_yyyy=='':
                        first_date_yyyy=date
                    delta=1
                    if len(mas)==1:
                        continue
                
                for iii in range(len(mas)-delta):
                    iii+=delta
                    if mas[iii]=='' or cmn.is_undefined(mas[iii]):
                        continue
                    if num_poriadok+1>len(poriadok):
                        num_poriadok=-1
                        date_found=0
                        break
                    num_poriadok+=1
                    if int(poriadok[num_poriadok][0])==0:
                        self.wells[poriadok[num_poriadok][1]][1][poriadok[num_poriadok][2]][2].append([date,mas[iii]])
                    if int(poriadok[num_poriadok][0])==1:
                        self.pipelines[poriadok[num_poriadok][1]][1][poriadok[num_poriadok][2]][2].append([date,mas[iii]])
                if num_poriadok+1>=len(poriadok):
                    num_poriadok=-1
                    date_found=0
            if mas[0]=='DATA_START':
                count=2
        f.close()

    def read_procedure_03(self):
        f          = open(self.dirr,'r')
        count      = 0
        num_str    = 0
        well_found = 0
        poriadok   = []
        num_poriadok=-1

        ##чтение заголовка
        date=''
        self.first_date_yyyy=''
        date_found     =0
        num  =0
        for line in f:
            line = line.rstrip('\n') 
            mas=line.split(' ')
            num_str+=1
            if count==1:
                if mas[0]=='HEADER_END':
                    count=3
                else:
                    x=4
                    if len(mas)<=19:
                        x=3
                    if len(mas)<=13:
                        x=2
                    if len(mas)<=7:
                        x=1
                    for i in range(x):
                        well_name   = str(mas[2+6*i])
                        well_name   = well_name.replace("\"","",2)
                        vec_name    = str(mas[3+6*i])
                        vec_name    = vec_name.replace("\"", "",2)
                        if vec_name=='PINFORM':
                            sdfjsfjfl=1
                        ed_izm_name = str(mas[4+6*i])
                        ed_izm_name = ed_izm_name.replace("\"", "",2)
        
                        if mas[1+6*i]=="\"WELL\"":
                            if well_name not in self.w_list:
                                self.w_list.append(well_name)
                            well_found=0
                            for ii in range(len(self.wells)):
                                if self.wells[ii][0]==well_name:
                                    self.wells[ii][1].append([vec_name,ed_izm_name,[]])
                                    ##              [0-wells(1-pipelines), порядковый номер скв в массиве, порядковый номер ветора в массиве]
                                    poriadok.append([0,ii,len(self.wells[ii][1])-1])
                                    well_found=1
                                    break
                            if well_found==0:
                                self.wells.append([well_name,[[vec_name,ed_izm_name,[]]]])
                                ##              [0-wells(1-pipelines), порядковый номер скв в массиве, порядковый номер ветора в массиве]
                                poriadok.append([0,len(self.wells)-1,0])
    ##                        well_found=0
                        else:
                            if well_name not in self.p_list:
                                self.p_list.append(well_name)
                            well_found=0
                            for ii in range(len(self.pipelines)):
                                if self.pipelines[ii][0]==well_name:
                                    self.pipelines[ii][1].append([vec_name,ed_izm_name,[]])
                                    ##              [0-wells(1-pipelines), порядковый номер скв в массиве, порядковый номер ветора в массиве]
                                    poriadok.append([1,ii,len(self.pipelines[ii][1])-1])
                                    well_found=1
                                    break
                            if well_found==0:
                                self.pipelines.append([well_name,[[vec_name,ed_izm_name,[]]]])
                                ##              [0-wells(1-pipelines), порядковый номер скв в массиве, порядковый номер ветора в массиве]
                                poriadok.append([1,len(self.pipelines)-1,0])
    ##                    well_found=0
        
            if mas[0]=='HEADER_START':
                count+=1
                continue   
        
        ##---------------------------------------
        ##заполнение массивов данными расчета
        ##---------------------------------------
            if count==4:
                delta=0
                if num_poriadok+1>=len(poriadok):
                    num_poriadok=0
                if num_poriadok==0:
                    date=mas[0]
                    if self.first_date_yyyy=='':
                        self.first_date_yyyy=date
                    delta=1;
                    num_poriadok+=1
                for iii in range(len(mas)-delta):
                    iii+=delta
                    if mas[iii]=='':
                        continue
                    if int(poriadok[num_poriadok][0])==0:
                        self.wells[poriadok[num_poriadok][1]][1][poriadok[num_poriadok][2]][2].append([date,mas[iii]])
                    if int(poriadok[num_poriadok][0])==1:
                        self.pipelines[poriadok[num_poriadok][1]][1][poriadok[num_poriadok][2]][2].append([date,mas[iii]])
                    num_poriadok+=1
        
            if mas[0]=='DATA_START' and count == 3:
                count=4
        f.close()

    def find_val_in_deftlist(self,name,mnemo,kod_list):
        value=cmn.get_undefined_r32()
        if kod_list==1:
            for i in range(len(self.wells)):
                if str(self.wells[i][0]).lower()==name.lower():
                    for ii in range(len(self.wells[i][1])):
                        if self.wells[i][1][ii][0].lower()==mnemo.lower():
                            value=float(self.wells[i][1][ii][2][1][1])
                            return value
        else:
            for i in range(len(self.pipelines)):
                if str(self.pipelines[i][0]).lower()==name.lower():
                    for ii in range(len(self.pipelines[i][1])):
                        if str(self.pipelines[i][1][ii][0]).lower()==mnemo.lower():
                            value=float(self.pipelines[i][1][ii][2][1][1])
                            return value
                    break
        return value
