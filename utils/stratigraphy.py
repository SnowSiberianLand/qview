# -*- coding: cp1251 -*-
#interactive object:
#title: Script editor
#mnemo: PYTHON_EDITOR

# скрипт создаёт стратиграфические объекты согласно отечественной или международной классификации
bInternational = False

# fix paths to mods
#import path64_local as mpath

import os
import sys
import shutil


import time
import filecmp
# RV-related

import mod_cmn as cmn
import mod_dm as dm
import mod_orm as db
import mod_gfx as gfx
import mod_dproc as dproc
import mod_dmsrv as dmsrv
import mod_io as io
import mod_ui as ui

#import data_utils as du
import ctx_rds
import db_utils as du
import entity_utils2 as eu
import entity_utils as eu1
#import table_utils2 as tu



class helper:
    grid_id = 1
    strg = 0

    def __init__(self, in_strg):
        #cmn.app_init_paths(str(mpath.binPath())) 
        self.init_failed = True
        try:
            #self.strg = ctx_rds.datastorage
            self.strg = in_strg
        except:
            print("init failed")
            return
        self.init_failed = False

    def getStratObj(self, id):
        f = self.strg.getRegHelper().getStratObjRegistry().find(id)
        return f

    def make_obj(self, ver_id, name, top, base, strat_type, color):
        op = dm.op_result()
        obj_id = -999
        with dm.object_maker4py(self.strg, dm.nt_strat_obj, name) as oo:
            obj = self.getStratObj(oo.m_new_id)
            ed = obj.getEditor()
            ed.setObjTop(top)
            ed.setObjBase(base)
            ed.setObjType(strat_type)
            ed.setObjColor(color, False)
            ed.setStratVerID(ver_id)

    
    def make_internatoinal_stratigICOS(self):
        err = cmn.err_info()
        gid = dm.getNextChangeGroupId()
        bNeedRefreshUI = True
        dm.begin_change_group(self.strg, gid, "making default stratigraphy", False, err)
        name = "DEFAULT_STRATIGRAPHY"
        op = dm.op_result()
        ver_id = -999
        
        with dm.object_maker4py(self.strg, dm.nt_strat_ver, name) as oo:
            #node = oo.getNode()
            ver_id = oo.m_new_id
        #Erathems
        self.make_obj(ver_id, "Paleozoic", 251000, 542000, dm.glt_erathem, "#99b899")
        self.make_obj(ver_id, "Mesozoic", 65500, 251000, dm.glt_erathem, "#4ec7e2")
        self.make_obj(ver_id, "Cenozoic", 0, 65500, dm.glt_erathem, "#f6ee33")
        #Systems
        self.make_obj(ver_id, "Quaternary", 0, 2588, dm.glt_system, "#fff999")
        self.make_obj(ver_id, "Neogene", 2588, 23030, dm.glt_system, "#ffdd2f")
        self.make_obj(ver_id, "Paleogene", 23030, 65500, dm.glt_system, "#f9a870")
        self.make_obj(ver_id, "Cretaceous", 65500, 145500, dm.glt_system, "#88c96f")
        self.make_obj(ver_id, "Jurassic", 145500, 199600, dm.glt_system, "#00b9e8")
        self.make_obj(ver_id, "Triassic", 199600, 251000, dm.glt_system, "#8f52a0")
        self.make_obj(ver_id, "Permian", 251000, 299000, dm.glt_system, "#e86549")
        self.make_obj(ver_id, "Carboiferous", 299000, 359200, dm.glt_system, "#68afb3")
        self.make_obj(ver_id, "Devonian", 359200, 416000, dm.glt_system, "#7c603d")
        self.make_obj(ver_id, "Silurian", 416000, 443700, dm.glt_system, "#b2ddc9")
        self.make_obj(ver_id, "Ordovician", 443700, 488300, dm.glt_system, "#02a68e")
        self.make_obj(ver_id, "Cambrian", 488300, 542000, dm.glt_system, "#8dab79")
        #Series
        self.make_obj(ver_id, "Holocene", 0, 11, dm.glt_series, "#fff2e2f")
        self.make_obj(ver_id, "Pleistocene", 11, 2588, dm.glt_series, "#fef1bd")
        self.make_obj(ver_id, "Pliocene", 2588, 5332, dm.glt_series, "#fff9ad")
        self.make_obj(ver_id, "Miocene", 5332, 23030, dm.glt_series, "#fef200")
        self.make_obj(ver_id, "Oligocene", 23030, 33900, dm.glt_series, "#fbc692")
        self.make_obj(ver_id, "Eocene", 33900, 55800, dm.glt_series, "#fdbc86")
        self.make_obj(ver_id, "Paleocene", 55800, 65500, dm.glt_series, "#fbb27b")
        self.make_obj(ver_id, "Upper C", 65500, 99600, dm.glt_series, "#afd46b")
        self.make_obj(ver_id, "Lower C", 99600, 145500, dm.glt_series, "#95cc79")
        self.make_obj(ver_id, "Upper J", 145500, 161200, dm.glt_series, "#a9dffa")
        self.make_obj(ver_id, "Middle J", 161200, 175600, dm.glt_series, "#71ceef")
        self.make_obj(ver_id, "Lower J", 175600, 199600, dm.glt_series, "#01b5ed")
        
        self.make_obj(ver_id, "Upper T", 199600, 228700, dm.glt_series, "#bb9eca")
        self.make_obj(ver_id, "Middle T", 228700, 245900, dm.glt_series, "#b382ba")
        self.make_obj(ver_id, "Lower T", 245900, 251000, dm.glt_series, "#a65bac")
        
        self.make_obj(ver_id, "Lopingian", 251000, 260400, dm.glt_series, "#f5b3a5")
        self.make_obj(ver_id, "Guadalupian", 260400, 270600, dm.glt_series, "#f58c76")
        self.make_obj(ver_id, "Cisuralian", 270600, 299000, dm.glt_series, "#ea7762")
        
        self.make_obj(ver_id, "Pensylvanian", 299000, 318100, dm.glt_series, "#99c5c8")
        self.make_obj(ver_id, "Mississippian", 318100, 359200, dm.glt_series, "#729d89")
        
        self.make_obj(ver_id, "Upper D", 359200, 385300, dm.glt_series, "#f3e0b0")
        self.make_obj(ver_id, "Middle D", 385300, 397500, dm.glt_series, "#f2cc85")
        self.make_obj(ver_id, "Lower D", 397500, 416000, dm.glt_series, "#e7b26e")
        
        self.make_obj(ver_id, "Pridoli", 416000, 418700, dm.glt_series, "#e2f1e7")
        self.make_obj(ver_id, "Ludlow", 418700, 422900, dm.glt_series, "#bee5de")
        self.make_obj(ver_id, "Wenlock", 422900, 428200, dm.glt_series, "#b1dfd4")
        self.make_obj(ver_id, "Llandovery", 428200, 443700, dm.glt_series, "#97d5ca")
        
        self.make_obj(ver_id, "Upper O", 443700, 460900, dm.glt_series, "#7fcbad")
        self.make_obj(ver_id, "Middle O", 460900, 471800, dm.glt_series, "#31b79e")
        self.make_obj(ver_id, "Lower O", 471800, 488300, dm.glt_series, "#01b18c")
        
        self.make_obj(ver_id, "Furongian", 488300, 499000, dm.glt_series, "#b4dbae")
        self.make_obj(ver_id, "Series 3", 499000, 510000, dm.glt_series, "#accda0")
        self.make_obj(ver_id, "Series 2", 510000, 521000, dm.glt_series, "#9ec294")
        self.make_obj(ver_id, "Terreneuvian", 521000, 542000, dm.glt_series, "#95b58a")
        
        #subseries
        
        self.make_obj(ver_id, "Upper P", 299000, 307200, dm.glt_subseries, "#bdcec6")
        self.make_obj(ver_id, "Middle P", 307200, 311700, dm.glt_subseries, "#acc4c5")
        self.make_obj(ver_id, "Lower P", 311700, 318100, dm.glt_subseries, "#8fbfc5")
        
        self.make_obj(ver_id, "Upper M", 318100, 328300, dm.glt_subseries, "#b8be92")
        self.make_obj(ver_id, "Middle M", 328300, 345300, dm.glt_subseries, "#a7b78f")
        self.make_obj(ver_id, "Lower M", 345300, 359200, dm.glt_subseries, "#85b58c")
        
        #stages
        self.make_obj(ver_id, "Upper S", 11, 126, dm.glt_stage, "#fef2db")
        self.make_obj(ver_id, "Ionian", 126, 781, dm.glt_stage, "#fff0cf")
        self.make_obj(ver_id, "Calabrain", 781, 1806, dm.glt_stage, "#fdf4ce")
        self.make_obj(ver_id, "Gelasian", 1806, 2588, dm.glt_stage, "#fcf0b2")
        
        self.make_obj(ver_id, "Piacenzian", 2588, 3600, dm.glt_stage, "#fffed2")
        self.make_obj(ver_id, "Zanclean", 3600, 5332, dm.glt_stage, "#fffac0")
        
        self.make_obj(ver_id, "Messinian", 5332, 7246, dm.glt_stage, "#fff784")
        self.make_obj(ver_id, "Tortonian", 7246, 11608, dm.glt_stage, "#fff685")
        self.make_obj(ver_id, "Serravallian", 11608, 13820, dm.glt_stage, "#f7ec87")
        self.make_obj(ver_id, "Langhian", 13820, 15970, dm.glt_stage, "#fef667")
        self.make_obj(ver_id, "Burdigalian", 15970, 20430, dm.glt_stage, "#fef26b")
        self.make_obj(ver_id, "Aquitanian", 20430, 23030, dm.glt_stage, "#f7f443")
        
        self.make_obj(ver_id, "Chattian", 23030, 28400, dm.glt_stage, "#ffe5b8")
        self.make_obj(ver_id, "Rupelian", 28400, 33900, dm.glt_stage, "#fedcac")
        self.make_obj(ver_id, "Priabonian", 33900, 37200, dm.glt_stage, "#fad6b5")
        self.make_obj(ver_id, "Bartonian", 37200, 40400, dm.glt_stage, "#fdcaa5")
        self.make_obj(ver_id, "Lutetian", 40400, 48600, dm.glt_stage, "#fbbc90")
        self.make_obj(ver_id, "Ypresian", 48600, 55800, dm.glt_stage, "#f9b48c")
        self.make_obj(ver_id, "Thanetian", 55800, 58700, dm.glt_stage, "#fdc68e")
        self.make_obj(ver_id, "Selandian", 58700, 61100, dm.glt_stage, "#eec38a")
        self.make_obj(ver_id, "Danian", 61100, 65500, dm.glt_stage, "#fbbb84")
        
        self.make_obj(ver_id, "Maastrichtian", 65500, 70600, dm.glt_stage, "#f5f5a3")
        self.make_obj(ver_id, "Campanian", 70600, 83500, dm.glt_stage, "#e7e8a1")
        self.make_obj(ver_id, "Santonian", 83500, 85800, dm.glt_stage, "#dde68d")
        self.make_obj(ver_id, "Coniacian", 85800, 88600, dm.glt_stage, "#d4e38e")
        self.make_obj(ver_id, "Turonian", 88600, 93600, dm.glt_stage, "#c6df7e")
        self.make_obj(ver_id, "Cenomanian", 93600, 99600, dm.glt_stage, "#badc74")
        
        self.make_obj(ver_id, "Albian", 99600, 112000, dm.glt_stage, "#d0e5ad")
        self.make_obj(ver_id, "Aptian", 112000, 125000, dm.glt_stage, "#c1e0a4")
        self.make_obj(ver_id, "Barremain", 125000, 130000, dm.glt_stage, "#bddda0")
        self.make_obj(ver_id, "Hauterivian", 130000, 133900, dm.glt_stage, "#a7d893")
        self.make_obj(ver_id, "Valanginian", 133900, 140200, dm.glt_stage, "#9dd186")
        self.make_obj(ver_id, "Berriasian", 140200, 145500, dm.glt_stage, "#95cf7e")
        
        ############## colors from http://www.worldlibrary.org/
        self.make_obj(ver_id, "Tithonian", 145500, 150800, dm.glt_stage, "#cff0fc")
        self.make_obj(ver_id, "Kimmeridgian", 150800, 155600, dm.glt_stage, "#bdebfb")
        self.make_obj(ver_id, "Oxfordian", 155600, 161200, dm.glt_stage, "#abe7fb")
        self.make_obj(ver_id, "Callovian", 161200, 164700, dm.glt_stage, "#aee6f0")
        self.make_obj(ver_id, "Bathonian", 164700, 167700, dm.glt_stage, "#9ce2ef")
        self.make_obj(ver_id, "Bajocian", 167700, 171600, dm.glt_stage, "#87deee")
        self.make_obj(ver_id, "Aalenian", 171600, 175600, dm.glt_stage, "#6fdaed")
        self.make_obj(ver_id, "Toarcian", 175600, 183000, dm.glt_stage, "#74d1f0")
        self.make_obj(ver_id, "Pliensbachian", 183000, 189600, dm.glt_stage, "#3cc9ef")
        self.make_obj(ver_id, "Sinemurian", 189600, 196500, dm.glt_stage, "#07c1ed")
        self.make_obj(ver_id, "Hettangian", 196500, 199600, dm.glt_stage, "#00bbeb")
        self.make_obj(ver_id, "Rhaetian", 199600, 203600, dm.glt_stage, "#e8c2d8")
        self.make_obj(ver_id, "Norian", 203600, 216500, dm.glt_stage, "#ddb4d1")
        self.make_obj(ver_id, "Carnian", 216500, 228700, dm.glt_stage, "#d1a6c9")
        self.make_obj(ver_id, "Ladinian", 228700, 237000, dm.glt_stage, "#d492bd")
        self.make_obj(ver_id, "Anisian", 237000, 245900, dm.glt_stage, "#c986b6")
        self.make_obj(ver_id, "Olenekian", 245900, 249500, dm.glt_stage, "#c26aa5")
        self.make_obj(ver_id, "Induan", 249500, 251000, dm.glt_stage, "#b861a0")
        self.make_obj(ver_id, "Changhsingian", 251000, 253800, dm.glt_stage, "#fec6b3")
        self.make_obj(ver_id, "Wuchiapingian", 253800, 260400, dm.glt_stage, "#febba5")
        self.make_obj(ver_id, "Capitanian", 260400, 265800, dm.glt_stage, "#fea38a")
        self.make_obj(ver_id, "Wordian", 265800, 268000, dm.glt_stage, "#fe987e")
        self.make_obj(ver_id, "Roadian", 268000, 270600, dm.glt_stage, "#fe8e72")
        self.make_obj(ver_id, "Kungurian", 270600, 275600, dm.glt_stage, "#ef947f")
        self.make_obj(ver_id, "Artinskian", 275600, 284400, dm.glt_stage, "#ef8a74")
        self.make_obj(ver_id, "Sakmarian", 284400, 294600, dm.glt_stage, "#ef806a")
        self.make_obj(ver_id, "Asselian", 294600, 299000, dm.glt_stage, "#f0775f")
        self.make_obj(ver_id, "Gzhelian", 299000, 303400, dm.glt_stage, "#cbd5cd")
        self.make_obj(ver_id, "Kasimovian", 303400, 307200, dm.glt_stage, "#bbd1cd")
        self.make_obj(ver_id, "Moscovian", 307200, 311700, dm.glt_stage, "#aecdc4")
        self.make_obj(ver_id, "Bashkirian", 311700, 318100, dm.glt_stage, "#8ac6c3")
        self.make_obj(ver_id, "Serpukhovian", 318100, 328300, dm.glt_stage, "#c8c281")
        self.make_obj(ver_id, "Visean", 328300, 345300, dm.glt_stage, "#abbc82")
        self.make_obj(ver_id, "Tournaisian", 345300, 359200, dm.glt_stage, "#8ab584")
        
        self.make_obj(ver_id, "Famennian", 359200, 374500, dm.glt_stage, "#f3ebcc")
        self.make_obj(ver_id, "Frasnian", 374500, 385300, dm.glt_stage, "#f4eab9")
        self.make_obj(ver_id, "Givetian", 385300, 391800, dm.glt_stage, "#f5de94")
        self.make_obj(ver_id, "Eifelian", 391800, 397500, dm.glt_stage, "#f5d386")
        self.make_obj(ver_id, "Emsian", 397500, 407000, dm.glt_stage, "#eccf87")
        self.make_obj(ver_id, "Pragian", 407000, 411200, dm.glt_stage, "#eec57b")
        self.make_obj(ver_id, "Lochkovian", 411200, 416000, dm.glt_stage, "#eeba6e")
        self.make_obj(ver_id, " ", 416000, 418700, dm.glt_stage, "#e4f2e6")
        self.make_obj(ver_id, "Ludfordian", 418700, 421300, dm.glt_stage, "#d4eee6")
        self.make_obj(ver_id, "Gorstian", 421300, 422900, dm.glt_stage, "#c3eae6")
        self.make_obj(ver_id, "Homerian", 422900, 426200, dm.glt_stage, "#c5e9db")
        self.make_obj(ver_id, "Sheinwoodian", 426200, 248200, dm.glt_stage, "#b6e4d0")
        self.make_obj(ver_id, "Telychian", 248200, 436000, dm.glt_stage, "#b4e5db")
        self.make_obj(ver_id, "Aeronian", 436000, 439000, dm.glt_stage, "#a4e0d0")
        self.make_obj(ver_id, "Rhuddanian", 439000, 443700, dm.glt_stage, "#93dbc6")
        self.make_obj(ver_id, "Hirnantian", 443700, 445600, dm.glt_stage, "#95dabc")
        self.make_obj(ver_id, "Katian", 445600, 455800, dm.glt_stage, "#81d6bc")
        self.make_obj(ver_id, "Sandbian", 455800, 460900, dm.glt_stage, "#72d0a9")
        self.make_obj(ver_id, "Darriwilian", 460900, 468100, dm.glt_stage, "#35c9b2")
        self.make_obj(ver_id, "Dapingian", 468100, 471800, dm.glt_stage, "#12c5a9")
        self.make_obj(ver_id, "Floian", 471800, 478600, dm.glt_stage, "#00baa0")
        self.make_obj(ver_id, "Tremadocian", 478600, 488300, dm.glt_stage, "#00b698")
        self.make_obj(ver_id, "Stage 10", 488300, 492000, dm.glt_stage, "#e5f1d1")
        self.make_obj(ver_id, "Jiangshanian", 492000, 496000, dm.glt_stage, "#d8ecc6")
        self.make_obj(ver_id, "Paibian", 496000, 499000, dm.glt_stage, "#cae7bc")
        self.make_obj(ver_id, "Guzhangian", 499000, 503000, dm.glt_stage, "#ccddb8")
        self.make_obj(ver_id, "Drumian", 503000, 506500, dm.glt_stage, "#bfd8ad")
        self.make_obj(ver_id, "Stage 5", 506500, 510000, dm.glt_stage, "#b2d4a3")
        self.make_obj(ver_id, "Stage 4", 510000, 515000, dm.glt_stage, "#b4cba0")
        self.make_obj(ver_id, "Stage 3", 515000, 521000, dm.glt_stage, "#a5c697")
        self.make_obj(ver_id, "Stage 2", 521000, 528000, dm.glt_stage, "#a8bd93")
        self.make_obj(ver_id, "Fortunian", 528000, 542000, dm.glt_stage, "#9aba8b")
        
        
        dm.end_change_group(self.strg, gid, err)


    def make_russian_stratig(self):
        err = cmn.err_info()
        #цветовая шкала взятн на сайте ВСЕГЕИ по состоянию на 2014 год
        gid = dm.getNextChangeGroupId()
        bNeedRefreshUI = True
        dm.begin_change_group(self.strg, gid, "making default stratigraphy", False, err)
        name = "DEFAULT_STRATIGRAPHY_RUS"

        op = dm.op_result()
        ver_id = -999
        with dm.object_maker4py(self.strg, dm.nt_strat_ver, name) as oo:
            ver_id = oo.m_new_id

        #Erathems
        self.make_obj(ver_id, "Палеозойская PZ", 251000, 542000, dm.glt_erathem, "#bab284")
        self.make_obj(ver_id, "Мезозойская MZ", 65500, 251000, dm.glt_erathem, "#88c28e")
        self.make_obj(ver_id, "Кайнозойская KZ", 0, 65500, dm.glt_erathem, "#ebc782")
        #Systems
        self.make_obj(ver_id, "Четвертичная", 0, 2588, dm.glt_system, "#fef691")
        self.make_obj(ver_id, "Неогеновая", 2588, 23030, dm.glt_system, "#ece9b6")
        self.make_obj(ver_id, "Палеогеновая", 23030, 65500, dm.glt_system, "#fcc9a0")
        self.make_obj(ver_id, "Меловая", 65500, 145500, dm.glt_system, "#bad89c")
        self.make_obj(ver_id, "Юрская", 145500, 199600, dm.glt_system, "#c2c5df")
        self.make_obj(ver_id, "Триасовая", 199600, 251000, dm.glt_system, "#d0aece")
        self.make_obj(ver_id, "Пермская", 251000, 299000, dm.glt_system, "#fbc296")
        self.make_obj(ver_id, "Каменноугольная", 299000, 359200, dm.glt_system, "#a5a6a6")
        self.make_obj(ver_id, "Девонская", 359200, 416000, dm.glt_system, "#d99f7a")
        self.make_obj(ver_id, "Силурийская", 416000, 443700, dm.glt_system, "#b3c381")
        self.make_obj(ver_id, "Ордовикская", 443700, 488300, dm.glt_system, "#7eb797")
        self.make_obj(ver_id, "Кембрийская", 488300, 542000, dm.glt_system, "#7ca796")
        #Series
        self.make_obj(ver_id, "Голоцен", 0, 11, dm.glt_series, "#fef1e0")
        self.make_obj(ver_id, "Плейстоцен", 11, 2580, dm.glt_series, "#feefb8")
        self.make_obj(ver_id, "Плиоцен", 2580, 5333, dm.glt_series, "#e9e6b4")
        self.make_obj(ver_id, "Миоцен", 5333, 23030, dm.glt_series, "#e9e6b4")
        self.make_obj(ver_id, "Олигоцен", 23030, 33900, dm.glt_series, "#f9f4bd")
        self.make_obj(ver_id, "Эоцен", 33900, 56000, dm.glt_series, "#fff8a8")
        self.make_obj(ver_id, "Палеоцен", 56000, 66000, dm.glt_series, "#fdf273")

        #Cretaceous
        self.make_obj(ver_id, "Верхний K2", 66000, 100500, dm.glt_series, "#e3edc0")
        self.make_obj(ver_id, "Нижний K1", 100500, 145000, dm.glt_series, "#b5d59c")

        #jurassic
        self.make_obj(ver_id, "Верхний J3", 145000, 163500, dm.glt_series, "#bfdfee")
        self.make_obj(ver_id, "Средний J2", 163500, 174100, dm.glt_series, "#9bb0d4")
        self.make_obj(ver_id, "Нижний J1", 174100, 201300, dm.glt_series, "#9ca4cc")

        #triassic
        self.make_obj(ver_id, "Верхний T3", 201300, 237000, dm.glt_series, "#e2bdd7")
        self.make_obj(ver_id, "Средний T2", 237000, 247200, dm.glt_series, "#c997be")
        self.make_obj(ver_id, "Нижний T1", 247200, 252170, dm.glt_series, "#b991bb")
        #Perm
        self.make_obj(ver_id, "Татарский P3", 252170, 265100, dm.glt_series, "#fccd9b")
        self.make_obj(ver_id, "Биармийский P2", 265100, 270600, dm.glt_series, "#fbbe8c")
        self.make_obj(ver_id, "Приуральский P1", 270600, 298900, dm.glt_series, "#fab88a")
        
        self.make_obj(ver_id, "Верхний C3", 298900, 311050, dm.glt_series, "#c6c5b1")
        self.make_obj(ver_id, "Средний C2", 311050, 323200, dm.glt_series, "#a5a6a6")
        self.make_obj(ver_id, "Нижний C1", 323200, 358900, dm.glt_series, "#88989f")

        #devonian
        self.make_obj(ver_id, "Верхний D3", 358900, 382700, dm.glt_series, "#ebb794")
        self.make_obj(ver_id, "Средний D2", 382700, 393300, dm.glt_series, "#c89d7d")
        self.make_obj(ver_id, "Нижний D1", 393300, 419200, dm.glt_series, "#d29981")
        ###
        self.make_obj(ver_id, "Пржидольский S22", 419200, 423000, dm.glt_series, "#cbd89f")
        self.make_obj(ver_id, "Лудловский S21", 423000, 427400, dm.glt_series, "#cbd89f")
        self.make_obj(ver_id, "Венлокский S12", 427400, 433400, dm.glt_series, "#c3bc90")
        self.make_obj(ver_id, "Лландоверийский S11", 433400, 443400, dm.glt_series, "#c3bc90")
        #Ordovician
        self.make_obj(ver_id, "Верхний O3", 443400, 458400, dm.glt_series, "#a7d3b6")
        self.make_obj(ver_id, "Средний O2", 458400, 470000, dm.glt_series, "#9acca6")
        self.make_obj(ver_id, "Нижний O1", 470000, 485400, dm.glt_series, "#7fb691")
        
        self.make_obj(ver_id, "Верхний E3", 485400, 497000, dm.glt_series, "#a7d4ca")
        self.make_obj(ver_id, "Средний E2", 497000, 509000, dm.glt_series, "#97cdbf")
        self.make_obj(ver_id, "Нижний E1", 509000, 535000, dm.glt_series, "#96ccb6")
        
        #stages
        #self.make_obj(ver_id, "Неоплейстоцен", 11, 781, dm.glt_stage, "#fef0cc")
        #self.make_obj(ver_id, "Эоплейстоцен", 781, 1806, dm.glt_stage, "#feefc1")
        
        #на начало 2018 года решение по Гелазскому ещё не принято, так что убираем его
        #self.make_obj(ver_id, "Гелазский", 1806, 2588, dm.glt_stage, "#feeead")
        self.make_obj(ver_id, "Пьяченцский", 2580, 3600, dm.glt_stage, "#f1eebb")
        self.make_obj(ver_id, "Занклский", 3600, 5333, dm.glt_stage, "#f1eebb")
        
        self.make_obj(ver_id, "Мессинский", 5333, 7246, dm.glt_stage, "#e9e6b4")
        self.make_obj(ver_id, "Тортонский", 7246, 11620, dm.glt_stage, "#e9e6b4")
        self.make_obj(ver_id, "Серравальский", 11620, 13820, dm.glt_stage, "#e9e6b4")
        self.make_obj(ver_id, "Лангийский", 13820, 15970, dm.glt_stage, "#e9e6b4")
        self.make_obj(ver_id, "Бурдигальский", 15970, 20440, dm.glt_stage, "#e9e6b4")
        self.make_obj(ver_id, "Аквитанский", 20440, 23030, dm.glt_stage, "#e9e6b4")
        
        self.make_obj(ver_id, "Хаттский", 23030, 28100, dm.glt_stage, "#f9f4bd")
        self.make_obj(ver_id, "Рюпельский", 28100, 33900, dm.glt_stage, "#f9f4bd")
        self.make_obj(ver_id, "Приабонский", 33900, 38000, dm.glt_stage, "#fff8a8")
        self.make_obj(ver_id, "Бартонский", 38000, 41300, dm.glt_stage, "#fff8a8")
        self.make_obj(ver_id, "Лютетский", 41300, 47800, dm.glt_stage, "#fff8a8")
        self.make_obj(ver_id, "Ипрский", 47800, 56000, dm.glt_stage, "#fff8a8")
        self.make_obj(ver_id, "Танетский", 56000, 59200, dm.glt_stage, "#fbf063")
        self.make_obj(ver_id, "Зеландский", 59200, 61600, dm.glt_stage, "#fbf063")
        self.make_obj(ver_id, "Датский", 61600, 66000, dm.glt_stage, "#fbf063")
        
        self.make_obj(ver_id, "Маастрихтский", 66000, 72100, dm.glt_stage, "#dfe7ba")
        self.make_obj(ver_id, "Кампанский", 72100, 83600, dm.glt_stage, "#dfe7ba")
        self.make_obj(ver_id, "Сантонский", 83600, 86300, dm.glt_stage, "#dfe7ba")
        self.make_obj(ver_id, "Коньякский", 86300, 89800, dm.glt_stage, "#dfe7ba")
        self.make_obj(ver_id, "Туронский", 89800, 93900, dm.glt_stage, "#dfe7ba")
        self.make_obj(ver_id, "Сеноманский", 93900, 100500, dm.glt_stage, "#dfe7ba")
        
        self.make_obj(ver_id, "Альбский", 100500, 113000, dm.glt_stage, "#b5d59c")
        self.make_obj(ver_id, "Аптский", 113000, 125000, dm.glt_stage, "#b5d59c")
        self.make_obj(ver_id, "Барремский", 125000, 129400, dm.glt_stage, "#b5d59c")
        self.make_obj(ver_id, "Готтеривский", 129400, 132900, dm.glt_stage, "#b5d59c")
        self.make_obj(ver_id, "Валанжинский", 132900, 139800, dm.glt_stage, "#b5d59c")
        self.make_obj(ver_id, "Берриасский", 139800, 145000, dm.glt_stage, "#b5d59c")
        
        self.make_obj(ver_id, "Титонский", 145000, 152100, dm.glt_stage, "#bedeed")
        self.make_obj(ver_id, "Кимериджский", 152100, 157300, dm.glt_stage, "#bedeed")
        self.make_obj(ver_id, "Оксфордский", 157300, 163500, dm.glt_stage, "#bedeed")
        self.make_obj(ver_id, "Келловейский", 163500, 166100, dm.glt_stage, "#9bb0d4")
        self.make_obj(ver_id, "Батский", 166100, 168300, dm.glt_stage, "#9bb0d4")
        self.make_obj(ver_id, "Байосский", 168300, 170300, dm.glt_stage, "#9bb0d4")
        self.make_obj(ver_id, "Ааленский", 170300, 174100, dm.glt_stage, "#9bb0d4")
        self.make_obj(ver_id, "Тоарский", 174100, 182700, dm.glt_stage, "#9ca4cc")
        self.make_obj(ver_id, "Плинсбахский", 182700, 190800, dm.glt_stage, "#9ca4cc")
        self.make_obj(ver_id, "Синемюрский", 190800, 199300, dm.glt_stage, "#9ca4cc")
        self.make_obj(ver_id, "Геттангский", 199300, 201300, dm.glt_stage, "#9ca4cc")
        self.make_obj(ver_id, "Рэтский", 201300, 208500, dm.glt_stage, "#e2bdd7")
        self.make_obj(ver_id, "Норийский", 208500, 227000, dm.glt_stage, "#e2bdd7")
        self.make_obj(ver_id, "Карнийский", 227000, 237000, dm.glt_stage, "#e2bdd7")
        self.make_obj(ver_id, "Ладинский", 237000, 242000, dm.glt_stage, "#c997be")
        self.make_obj(ver_id, "Анизийский", 242000, 247200, dm.glt_stage, "#c997be")
        self.make_obj(ver_id, "Оленекский", 247200, 251200, dm.glt_stage, "#b991bb")
        self.make_obj(ver_id, "Индский", 251200, 252170, dm.glt_stage, "#b991bb")
        self.make_obj(ver_id, "Вятский", 252170, 258640, dm.glt_stage, "#fccd9b")
        self.make_obj(ver_id, "Северодвинский", 258640, 265100, dm.glt_stage, "#fccd9b")
        self.make_obj(ver_id, "Уржумский", 265100, 267900, dm.glt_stage, "#fbbe8c")
        self.make_obj(ver_id, "Казанский", 267900, 270600, dm.glt_stage, "#fbbe8c")
        self.make_obj(ver_id, "Уфимский", 270600, 277100, dm.glt_stage, "#fab88a")
        self.make_obj(ver_id, "Кунгурский", 277100, 283500, dm.glt_stage, "#fab88a")
        self.make_obj(ver_id, "Артинский", 283500, 290100, dm.glt_stage, "#fab88a")
        self.make_obj(ver_id, "Сакмарский", 290100, 295000, dm.glt_stage, "#fab88a")
        self.make_obj(ver_id, "Ассельский", 295000, 298900, dm.glt_stage, "#fab88a")
        self.make_obj(ver_id, "Гжельский", 298900, 303700, dm.glt_stage, "#c6c5b1")
        self.make_obj(ver_id, "Касимовский", 303700, 310200, dm.glt_stage, "#c6c5b1")
        self.make_obj(ver_id, "Московский", 310200, 316700, dm.glt_stage, "#a5a6a6")
        self.make_obj(ver_id, "Башкирский", 316700, 323200, dm.glt_stage, "#a5a6a6")
        self.make_obj(ver_id, "Серпуховский", 323200, 330900, dm.glt_stage, "#88989f")
        self.make_obj(ver_id, "Визейский", 330900, 346700, dm.glt_stage, "#88989f")
        self.make_obj(ver_id, "Турнейский", 346700, 358900, dm.glt_stage, "#88989f")
        
        self.make_obj(ver_id, "Фаменский", 358900, 372200, dm.glt_stage, "#ebb794")
        self.make_obj(ver_id, "Франский", 372200, 382700, dm.glt_stage, "#ebb794")
        self.make_obj(ver_id, "Живетский", 382700, 387700, dm.glt_stage, "#c89d7d")
        self.make_obj(ver_id, "Эйфельский", 387700, 393300, dm.glt_stage, "#c89d7d")
        self.make_obj(ver_id, "Эмсский", 393300, 407600, dm.glt_stage, "#d29981")
        self.make_obj(ver_id, "Пражский", 407600, 410800, dm.glt_stage, "#d29981")
        self.make_obj(ver_id, "Лохковский", 410800, 419200, dm.glt_stage, "#d29981")
        self.make_obj(ver_id, "_", 419200, 423000, dm.glt_stage, "#cbd89f")
        self.make_obj(ver_id, "Лудфордский", 423000, 425600, dm.glt_stage, "#cbd89f")
        self.make_obj(ver_id, "Горстийский", 425600, 427400, dm.glt_stage, "#cbd89f")
        self.make_obj(ver_id, "Гомерский", 427400, 430500, dm.glt_stage, "#c3bc90")
        self.make_obj(ver_id, "Шейнвудский", 430500, 433400, dm.glt_stage, "#c3bc90")
        self.make_obj(ver_id, "Теличский", 433400, 438500, dm.glt_stage, "#c3bc90")
        self.make_obj(ver_id, "Аэронский", 438500, 440800, dm.glt_stage, "#c3bc90")
        self.make_obj(ver_id, "Рудданский", 440800, 443400, dm.glt_stage, "#a7d3b6")
        self.make_obj(ver_id, "Хирнантский", 443400, 445200, dm.glt_stage, "#a7d3b6")
        self.make_obj(ver_id, "Катийский", 445200, 453000, dm.glt_stage, "#a7d3b6")
        self.make_obj(ver_id, "Сандбийский", 453000, 458400, dm.glt_stage, "#a7d3b6")
        self.make_obj(ver_id, "Дарривильский", 458400, 467300, dm.glt_stage, "#9acca6")
        self.make_obj(ver_id, "Дапинский", 467300, 470000, dm.glt_stage, "#9acca6")
        self.make_obj(ver_id, "Флоский", 470000, 477700, dm.glt_stage, "#7fb691")
        self.make_obj(ver_id, "Тремадокский", 477700, 485400, dm.glt_stage, "#7fb691")
        self.make_obj(ver_id, "Батырбайский", 485400, 489300, dm.glt_stage, "#a7d4ca")
        self.make_obj(ver_id, "Аксайский", 489300, 493100, dm.glt_stage, "#a7d4ca")
        self.make_obj(ver_id, "Сакский", 493100, 497000, dm.glt_stage, "#a7d4ca")
        self.make_obj(ver_id, "Аюсокканский", 497000, 500000, dm.glt_stage, "#a7d4ca")
        self.make_obj(ver_id, "Майский", 500000, 504500, dm.glt_stage, "#97cdbf")
        self.make_obj(ver_id, "Амгинский", 504500, 509000, dm.glt_stage, "#97cdbf")
        self.make_obj(ver_id, "Тойонский", 509000, 515500, dm.glt_stage, "#96ccb6")
        self.make_obj(ver_id, "Ботомский", 515500, 522000, dm.glt_stage, "#96ccb6")
        self.make_obj(ver_id, "Атдабанский", 522000, 528500, dm.glt_stage, "#96ccb6")
        self.make_obj(ver_id, "Томмотский", 528500, 535000, dm.glt_stage, "#96ccb6")
                
        dm.end_change_group(self.strg, gid, err)
        return True
    def make_internatoinal_stratig(self):
        err = cmn.err_info()
        gid = dm.getNextChangeGroupId()
        bNeedRefreshUI = True
        dm.begin_change_group(self.strg, gid, "making default stratigraphy", False, err)
        name = "DEFAULT_STRATIGRAPHY"
        op = dm.op_result()
        ver_id = -999
        
        with dm.object_maker4py(self.strg, dm.nt_strat_ver, name) as oo:
            ver_id = oo.m_new_id
            
        #Erathems
        self.make_obj(ver_id, "Paleozoic", 251000, 542000, dm.glt_erathem, "#92c3a0")
        self.make_obj(ver_id, "Mesozoic", 65500, 251000, dm.glt_erathem, "#07caea")
        self.make_obj(ver_id, "Cenozoic", 0, 65500, dm.glt_erathem, "#f6ec39")
        #Systems
        self.make_obj(ver_id, "Quaternary", 0, 2588, dm.glt_system, "#fef691")
        self.make_obj(ver_id, "Neogene", 2588, 23030, dm.glt_system, "#fedd2d")
        self.make_obj(ver_id, "Paleogene", 23030, 65500, dm.glt_system, "#fea163")
        self.make_obj(ver_id, "Cretaceous", 65500, 145500, dm.glt_system, "#6fc86b")
        self.make_obj(ver_id, "Jurassic", 145500, 199600, dm.glt_system, "#00bbe7")
        self.make_obj(ver_id, "Triassic", 199600, 251000, dm.glt_system, "#994e96")
        self.make_obj(ver_id, "Permian", 251000, 299000, dm.glt_system, "#f7583c")
        self.make_obj(ver_id, "Carboiferous", 299000, 359200, dm.glt_system, "#3faead")
        self.make_obj(ver_id, "Devonian", 359200, 416000, dm.glt_system, "#dd9651")
        self.make_obj(ver_id, "Silurian", 416000, 443700, dm.glt_system, "#a6dfc5")
        self.make_obj(ver_id, "Ordovician", 443700, 488300, dm.glt_system, "#00a98a")
        self.make_obj(ver_id, "Cambrian", 488300, 542000, dm.glt_system, "#81aa72")
        #Series
        self.make_obj(ver_id, "Holocene", 0, 11, dm.glt_series, "#fef1e0")
        self.make_obj(ver_id, "Pleistocene", 11, 2588, dm.glt_series, "#feefb8")
        self.make_obj(ver_id, "Pliocene", 2588, 5332, dm.glt_series, "#fef8a6")
        self.make_obj(ver_id, "Miocene", 5332, 23030, dm.glt_series, "#feef00")
        self.make_obj(ver_id, "Oligocene", 23030, 33900, dm.glt_series, "#fec386")
        self.make_obj(ver_id, "Eocene", 33900, 55800, dm.glt_series, "#feb979")
        self.make_obj(ver_id, "Paleocene", 55800, 65500, dm.glt_series, "#fead6e")

        #Cretaceous
        self.make_obj(ver_id, "Upper C", 65500, 99600, dm.glt_series, "#a6d468")
        self.make_obj(ver_id, "Lower C", 99600, 145500, dm.glt_series, "#7ecd74")

        #jurassic
        self.make_obj(ver_id, "Upper J", 145500, 161200, dm.glt_series, "#97e3fa")
        self.make_obj(ver_id, "Middle J", 161200, 175600, dm.glt_series, "#34d1eb")
        self.make_obj(ver_id, "Lower J", 175600, 199600, dm.glt_series, "#00b7ea")

        #triassic
        self.make_obj(ver_id, "Upper T", 199600, 228700, dm.glt_series, "#c698c2")
        self.make_obj(ver_id, "Middle T", 228700, 245900, dm.glt_series, "#bf7cb1")
        self.make_obj(ver_id, "Lower T", 245900, 251000, dm.glt_series, "#ad579a")
        
        self.make_obj(ver_id, "Lopingian", 251000, 260400, dm.glt_series, "#feaf97")
        self.make_obj(ver_id, "Guadalupian", 260400, 270600, dm.glt_series, "#fe8367")
        self.make_obj(ver_id, "Cisuralian", 270600, 299000, dm.glt_series, "#f76e54")
        
        self.make_obj(ver_id, "Pensylvanian", 299000, 318100, dm.glt_series, "#8ac6c3")
        self.make_obj(ver_id, "Mississippian", 318100, 359200, dm.glt_series, "#619d7e")

        #devonian
        self.make_obj(ver_id, "Upper D", 359200, 385300, dm.glt_series, "#f4e0a9")
        self.make_obj(ver_id, "Middle D", 385300, 397500, dm.glt_series, "#f6c87a")
        self.make_obj(ver_id, "Lower D", 397500, 416000, dm.glt_series, "#efb063")
        ###
        self.make_obj(ver_id, "Pridoli", 416000, 418700, dm.glt_series, "#e4f2e6")
        self.make_obj(ver_id, "Ludlow", 418700, 422900, dm.glt_series, "#b4e5db")
        self.make_obj(ver_id, "Wenlock", 422900, 428200, dm.glt_series, "#a4e0d0")
        self.make_obj(ver_id, "Llandovery", 428200, 443700, dm.glt_series, "#7ed7c6")
        #Ordovician
        self.make_obj(ver_id, "Upper O", 443700, 460900, dm.glt_series, "#5ecca9")
        self.make_obj(ver_id, "Middle O", 460900, 471800, dm.glt_series, "#00bd97")
        self.make_obj(ver_id, "Lower O", 471800, 488300, dm.glt_series, "#00af89")
        
        self.make_obj(ver_id, "Furongian", 488300, 499000, dm.glt_series, "#addda8")
        self.make_obj(ver_id, "Series 3", 499000, 510000, dm.glt_series, "#a1cf9b")
        self.make_obj(ver_id, "Series 2", 510000, 521000, dm.glt_series, "#95c28f")
        self.make_obj(ver_id, "Terreneuvian", 521000, 542000, dm.glt_series, "#8ab584")
        
        #subseries
        #Pensilvanian
        self.make_obj(ver_id, "Upper P", 299000, 307200, dm.glt_subseries, "#bdcec6")
        self.make_obj(ver_id, "Middle P", 307200, 311700, dm.glt_subseries, "#acc4c5")
        self.make_obj(ver_id, "Lower P", 311700, 318100, dm.glt_subseries, "#8fbfc5")
        #Mississippian
        self.make_obj(ver_id, "Upper M", 318100, 328300, dm.glt_subseries, "#b8be92")
        self.make_obj(ver_id, "Middle M", 328300, 345300, dm.glt_subseries, "#a7b78f")
        self.make_obj(ver_id, "Lower M", 345300, 359200, dm.glt_subseries, "#85b58c")
        
        #stages
        self.make_obj(ver_id, "Upper S", 11, 126, dm.glt_stage, "#fef1d6")
        self.make_obj(ver_id, "Ionian", 126, 781, dm.glt_stage, "#fef0cc")
        self.make_obj(ver_id, "Calabrain", 781, 1806, dm.glt_stage, "#feefc1")
        self.make_obj(ver_id, "Gelasian", 1806, 2588, dm.glt_stage, "#feeead")
        
        self.make_obj(ver_id, "Piacenzian", 2588, 3600, dm.glt_stage, "#fefac8")
        self.make_obj(ver_id, "Zanclean", 3600, 5332, dm.glt_stage, "#fef9bd")
        
        self.make_obj(ver_id, "Messinian", 5332, 7246, dm.glt_stage, "#fef587")
        self.make_obj(ver_id, "Tortonian", 7246, 11608, dm.glt_stage, "#fef47d")
        self.make_obj(ver_id, "Serravallian", 11608, 13820, dm.glt_stage, "#fef472")
        self.make_obj(ver_id, "Langhian", 13820, 15970, dm.glt_stage, "#fef366")
        self.make_obj(ver_id, "Burdigalian", 15970, 20430, dm.glt_stage, "#fef259")
        self.make_obj(ver_id, "Aquitanian", 20430, 23030, dm.glt_stage, "#fef14d")
        
        self.make_obj(ver_id, "Chattian", 23030, 28400, dm.glt_stage, "#fee4b2")
        self.make_obj(ver_id, "Rupelian", 28400, 33900, dm.glt_stage, "#fed9a2")
        self.make_obj(ver_id, "Priabonian", 33900, 37200, dm.glt_stage, "#fecfa7")
        self.make_obj(ver_id, "Bartonian", 37200, 40400, dm.glt_stage, "#fec498")
        self.make_obj(ver_id, "Lutetian", 40400, 48600, dm.glt_stage, "#feb98a")
        self.make_obj(ver_id, "Ypresian", 48600, 55800, dm.glt_stage, "#feae7d")
        self.make_obj(ver_id, "Thanetian", 55800, 58700, dm.glt_stage, "#fec37d")
        self.make_obj(ver_id, "Selandian", 58700, 61100, dm.glt_stage, "#fec274")
        self.make_obj(ver_id, "Danian", 61100, 65500, dm.glt_stage, "#feb872")
        
        self.make_obj(ver_id, "Maastrichtian", 65500, 70600, dm.glt_stage, "#f3f29c")
        self.make_obj(ver_id, "Campanian", 70600, 83500, dm.glt_stage, "#eaed93")
        self.make_obj(ver_id, "Santonian", 83500, 85800, dm.glt_stage, "#dee78a")
        self.make_obj(ver_id, "Coniacian", 85800, 88600, dm.glt_stage, "#d1e382")
        self.make_obj(ver_id, "Turonian", 88600, 93600, dm.glt_stage, "#c3df79")
        self.make_obj(ver_id, "Cenomanian", 93600, 99600, dm.glt_stage, "#b5da71")
        
        self.make_obj(ver_id, "Albian", 99600, 112000, dm.glt_stage, "#cde5a8")
        self.make_obj(ver_id, "Aptian", 112000, 125000, dm.glt_stage, "#bfe19f")
        self.make_obj(ver_id, "Barremain", 125000, 130000, dm.glt_stage, "#afdd97")
        self.make_obj(ver_id, "Hauterivian", 130000, 133900, dm.glt_stage, "#9ed78e")
        self.make_obj(ver_id, "Valanginian", 133900, 140200, dm.glt_stage, "#8dd285")
        self.make_obj(ver_id, "Berriasian", 140200, 145500, dm.glt_stage, "#7cce7c")
        
        ############## colors from http://www.worldlibrary.org/
        self.make_obj(ver_id, "Tithonian", 145500, 150800, dm.glt_stage, "#cff0fc")
        self.make_obj(ver_id, "Kimmeridgian", 150800, 155600, dm.glt_stage, "#bdebfb")
        self.make_obj(ver_id, "Oxfordian", 155600, 161200, dm.glt_stage, "#abe7fb")
        self.make_obj(ver_id, "Callovian", 161200, 164700, dm.glt_stage, "#aee6f0")
        self.make_obj(ver_id, "Bathonian", 164700, 167700, dm.glt_stage, "#9ce2ef")
        self.make_obj(ver_id, "Bajocian", 167700, 171600, dm.glt_stage, "#87deee")
        self.make_obj(ver_id, "Aalenian", 171600, 175600, dm.glt_stage, "#6fdaed")
        self.make_obj(ver_id, "Toarcian", 175600, 183000, dm.glt_stage, "#74d1f0")
        self.make_obj(ver_id, "Pliensbachian", 183000, 189600, dm.glt_stage, "#3cc9ef")
        self.make_obj(ver_id, "Sinemurian", 189600, 196500, dm.glt_stage, "#07c1ed")
        self.make_obj(ver_id, "Hettangian", 196500, 199600, dm.glt_stage, "#00bbeb")
        self.make_obj(ver_id, "Rhaetian", 199600, 203600, dm.glt_stage, "#e8c2d8")
        self.make_obj(ver_id, "Norian", 203600, 216500, dm.glt_stage, "#ddb4d1")
        self.make_obj(ver_id, "Carnian", 216500, 228700, dm.glt_stage, "#d1a6c9")
        self.make_obj(ver_id, "Ladinian", 228700, 237000, dm.glt_stage, "#d492bd")
        self.make_obj(ver_id, "Anisian", 237000, 245900, dm.glt_stage, "#c986b6")
        self.make_obj(ver_id, "Olenekian", 245900, 249500, dm.glt_stage, "#c26aa5")
        self.make_obj(ver_id, "Induan", 249500, 251000, dm.glt_stage, "#b861a0")
        self.make_obj(ver_id, "Changhsingian", 251000, 253800, dm.glt_stage, "#fec6b3")
        self.make_obj(ver_id, "Wuchiapingian", 253800, 260400, dm.glt_stage, "#febba5")
        self.make_obj(ver_id, "Capitanian", 260400, 265800, dm.glt_stage, "#fea38a")
        self.make_obj(ver_id, "Wordian", 265800, 268000, dm.glt_stage, "#fe987e")
        self.make_obj(ver_id, "Roadian", 268000, 270600, dm.glt_stage, "#fe8e72")
        self.make_obj(ver_id, "Kungurian", 270600, 275600, dm.glt_stage, "#ef947f")
        self.make_obj(ver_id, "Artinskian", 275600, 284400, dm.glt_stage, "#ef8a74")
        self.make_obj(ver_id, "Sakmarian", 284400, 294600, dm.glt_stage, "#ef806a")
        self.make_obj(ver_id, "Asselian", 294600, 299000, dm.glt_stage, "#f0775f")
        self.make_obj(ver_id, "Gzhelian", 299000, 303400, dm.glt_stage, "#cbd5cd")
        self.make_obj(ver_id, "Kasimovian", 303400, 307200, dm.glt_stage, "#bbd1cd")
        self.make_obj(ver_id, "Moscovian", 307200, 311700, dm.glt_stage, "#aecdc4")
        self.make_obj(ver_id, "Bashkirian", 311700, 318100, dm.glt_stage, "#8ac6c3")
        self.make_obj(ver_id, "Serpukhovian", 318100, 328300, dm.glt_stage, "#c8c281")
        self.make_obj(ver_id, "Visean", 328300, 345300, dm.glt_stage, "#abbc82")
        self.make_obj(ver_id, "Tournaisian", 345300, 359200, dm.glt_stage, "#8ab584")
        
        self.make_obj(ver_id, "Famennian", 359200, 374500, dm.glt_stage, "#f3ebcc")
        self.make_obj(ver_id, "Frasnian", 374500, 385300, dm.glt_stage, "#f4eab9")
        self.make_obj(ver_id, "Givetian", 385300, 391800, dm.glt_stage, "#f5de94")
        self.make_obj(ver_id, "Eifelian", 391800, 397500, dm.glt_stage, "#f5d386")
        self.make_obj(ver_id, "Emsian", 397500, 407000, dm.glt_stage, "#eccf87")
        self.make_obj(ver_id, "Pragian", 407000, 411200, dm.glt_stage, "#eec57b")
        self.make_obj(ver_id, "Lochkovian", 411200, 416000, dm.glt_stage, "#eeba6e")
        self.make_obj(ver_id, " ", 416000, 418700, dm.glt_stage, "#e4f2e6")
        self.make_obj(ver_id, "Ludfordian", 418700, 421300, dm.glt_stage, "#d4eee6")
        self.make_obj(ver_id, "Gorstian", 421300, 422900, dm.glt_stage, "#c3eae6")
        self.make_obj(ver_id, "Homerian", 422900, 426200, dm.glt_stage, "#c5e9db")
        self.make_obj(ver_id, "Sheinwoodian", 426200, 248200, dm.glt_stage, "#b6e4d0")
        self.make_obj(ver_id, "Telychian", 248200, 436000, dm.glt_stage, "#b4e5db")
        self.make_obj(ver_id, "Aeronian", 436000, 439000, dm.glt_stage, "#a4e0d0")
        self.make_obj(ver_id, "Rhuddanian", 439000, 443700, dm.glt_stage, "#93dbc6")
        self.make_obj(ver_id, "Hirnantian", 443700, 445600, dm.glt_stage, "#95dabc")
        self.make_obj(ver_id, "Katian", 445600, 455800, dm.glt_stage, "#81d6bc")
        self.make_obj(ver_id, "Sandbian", 455800, 460900, dm.glt_stage, "#72d0a9")
        self.make_obj(ver_id, "Darriwilian", 460900, 468100, dm.glt_stage, "#35c9b2")
        self.make_obj(ver_id, "Dapingian", 468100, 471800, dm.glt_stage, "#12c5a9")
        self.make_obj(ver_id, "Floian", 471800, 478600, dm.glt_stage, "#00baa0")
        self.make_obj(ver_id, "Tremadocian", 478600, 488300, dm.glt_stage, "#00b698")
        self.make_obj(ver_id, "Stage 10", 488300, 492000, dm.glt_stage, "#e5f1d1")
        self.make_obj(ver_id, "Jiangshanian", 492000, 496000, dm.glt_stage, "#d8ecc6")
        self.make_obj(ver_id, "Paibian", 496000, 499000, dm.glt_stage, "#cae7bc")
        self.make_obj(ver_id, "Guzhangian", 499000, 503000, dm.glt_stage, "#ccddb8")
        self.make_obj(ver_id, "Drumian", 503000, 506500, dm.glt_stage, "#bfd8ad")
        self.make_obj(ver_id, "Stage 5", 506500, 510000, dm.glt_stage, "#b2d4a3")
        self.make_obj(ver_id, "Stage 4", 510000, 515000, dm.glt_stage, "#b4cba0")
        self.make_obj(ver_id, "Stage 3", 515000, 521000, dm.glt_stage, "#a5c697")
        self.make_obj(ver_id, "Stage 2", 521000, 528000, dm.glt_stage, "#a8bd93")
        self.make_obj(ver_id, "Fortunian", 528000, 542000, dm.glt_stage, "#9aba8b")
        
        
        dm.end_change_group(self.strg, gid, err)
        return True

if __name__ == '__main__':

    hh = helper()
    if hh.init_failed:
        print("init failed")
        hh.dump_crashes()
        sys.exit(-1)
    
    #colors by International Commission on Stratigraphy ?
    bICoSColors = True
    #if not then by http://www.worldlibrary.org/article/whebn0000012967/geologic%20time%20scale
    
    if bInternational:
        if bICoSColors:
            hh.make_internatoinal_stratigICOS()
        else:
            hh.make_internatoinal_stratig()
    else:
        hh.make_russian_stratig()
            