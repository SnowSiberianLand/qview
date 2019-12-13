# -*- coding: cp1251 -*-
from collections import namedtuple, OrderedDict
from xml.dom import minidom
from database_utils_br import *
from xml.etree.ElementTree import *
import mod_dm as dm
import mod_cmn as cmn
import mod_dmsrv as dmsrv
import entity_utils as eu
import table_utils
import table_utils2 as tu


def recursive(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            value = recursive(value)
    elif isinstance(obj, list):
        for item in obj:
            recursive(item)
    else:
        try:
            return str(round(float(obj), 2))
        except:
            return obj


class Well(dict):
    def __init__(self, parent=dict()):
        super(Well, self).__init__(parent)

    def return_xml_element(self, rooting_element: Element):
        #TODO: Не трогай! Не будет работать все!!!
        well = SubElement(rooting_element, 'Well') #type: Element
        well.set('name', self['name'])
        for el, val in self.items():
            if el == 'survey': continue
            elif el == 'name': continue
            elif el == 'ProductionString':
                temporary_element = SubElement(well, el)
                for k, v in val.items():
                    s = SubElement(temporary_element, k)
                    if isinstance(v, (dict, OrderedDict)):
                        s.attrib = v
                    elif isinstance(v, (list)):
                        for i in value:
                            s = SubElement(temporary_element, k)
                            s.set(k[:-1], val)
                continue
            temporary_element = SubElement(well, el) #type: Element
            if isinstance(val, list):
                for i in val:
                    dt_temp = SubElement(temporary_element, el[:-1])
                    for key, value in i.items():
                        dt_temp.set(key, str(value))

            elif isinstance(val, (dict, OrderedDict)):
                for key, value in val.items():
                    if isinstance(value, (dict, OrderedDict)):
                        s = SubElement(temporary_element, key)
                        for k, v in value.items():
                            s.set(k, v)
                    elif isinstance(value, (float, int, str)):
                        temporary_element.attrib = self.format_to_string(val)
                        break
                    elif isinstance(value, (list)):
                        for i in value:
                            s = SubElement(temporary_element, key)
                            s.set(key[:-1], val)
        return (well)

    @staticmethod
    def format_to_string(dic):
        for key, value in dic.items():
            dic[key] = str(value)
        return dic


class WellRDS(Well):
    def __init__(self, rds_well: dm.IBorehole, strg=None, model_c=None, model_g=None):
        super(Well, self).__init__()
        self.load_survey(rds_well, strg)
        self['name'] = rds_well.getName()
        self['WellGuid'] = {'Value': rds_well.getID()}
        self['WellDrilledMd'] = {'Value': self.get_well_drilled_md(rds_well)}
        self['FalseBottom'] = {'Value': self.get_false_bottom(rds_well)}
        self['Status'] = get_status(rds_well, strg)
        self['PerfDataS'] = self.get_perf_data(rds_well, strg)
        self['InflowIntervals'] = self.get_inflow_intervals(rds_well, strg)
        self['CementingQualityIntervals'] = self.get_cementing_ivals(rds_well, strg, model_g)
        self['CurrentBottomholes'] = self.get_current_bottomholes(rds_well, strg)
        self['CementBridges'] = self.get_cementing_bridges(rds_well, strg)
        self['SandyArgillaceousPlugs'] = self.get_sandy_argeloise(rds_well, strg)
        self['Breaks'] = self.get_breaks(rds_well, strg)
        self['ProductionString'] = {
            'Constractions': {},
            'BottomKind': {"type" :"Funnel"},
            'FilterTopDepth': {},
            'InflowFromBehindProductionString': {},
            'IsConcentric': 0,
            'CripplingIntervals': {},
            'PerfWithGas': {}}
        self['Cuts'] = []
        self['CementedDevices'] = {}
        self['YearsWithWater'] = {}
        self['YearsWithOverhaulWaterEntry'] = {}
        self['YearsWithOverhaulWaterEntryPicketUtility'] = {}
        self['YearsWithOverhaulClearEntryPicketUtility'] = {}
        self['YearsWithOverhaulStabilizationOfProducingFormation'] = {}
        self['YearsWithOverhaulWashingAndStabilizationOfProducingFormation'] = {}

    def load_survey(self, rds_well: dm.IBorehole, strg):
        dsrv_data = eu.load_devsurvey(rds_well.getID(), cmn.get_undefined_i32(), strg,
                                      dmsrv.python_results())  # type: dm.IDsrvData
        if dsrv_data is None: dsrv_data = False
        self['survey'] = dsrv_data

    def get_well_drilled_md(self, rds_well: dm.IBorehole):
        tmp = rds_well.getDrilledMD()
        if not cmn.is_undefined(tmp):
            return round(self['survey'].get_tvd(tmp), 2)
        else:
            return ''

    def get_false_bottom(self, rds_well: dm.IBorehole):
        tmp = rds_well.getPlugBackMD()
        if not cmn.is_undefined(tmp) and self['survey']:
            return round(self['survey'].get_tvd(tmp), 2)
        else:
            return ''

    def get_perf_data(self, rds_well: dm.IBorehole, strg: dm.IDataStorage):
        print("Load completions for well: {0} ...".format(rds_well.getName()))
        pgs_ = cmn.progress_ctx()
        err_ = cmn.err_info()
        out = []
        dhtpl = dm.getDataProcessing().getDataTreatHelper()  # type: dm.IDataTreatHelper
        perf_ = dhtpl.makeCompletionData(dm.db_caching, dm.cat_completion_events)  # type: dm.ICompletionData
        perf_.load(strg, rds_well.getID(), pgs_, err_)
        last_date = perf_.getDataMaxDate()
        if perf_.completions().size() != 0:
            last_compl = dm.vec_perf_interval()  # type: dm.vec_perf_interval
            perf_.getCurrentCompletion(last_date, last_compl, err_)
            for ival in last_compl:  # type: dm.perf_interval
                compl = {}
                compl['OnTube'] = False
                if self['survey']:
                    top = self['survey'].get_tvd(ival.top)
                    bot = self['survey'].get_tvd(ival.bot)
                else:
                    top = ival.top
                    bot = ival.bot
                if ival.code == 11:
                    items = ival.items_compl
                    type_of_compl = 'perf'
                    for item in items:  # type: dm.ICompletionItem
                        if item.getCompletionType() != dm.ct_liner:
                            continue
                        else:
                            type_of_compl = 'liner'
                            break
                    compl['Top'] = top
                    compl['Base'] = bot
                    compl['Type'] = type_of_compl
                    compl['Year'] = cmn.date_to_string(last_date)
                    compl['ShowYear'] = 'False'
                else:
                    compl['Top'] = top
                    compl['Base'] = bot
                    compl['Type'] = 'isol'
                    compl['Year'] = cmn.date_to_string(last_date)
                    compl['ShowYear'] = 'False'
                out.append(compl)
        return out

    def get_inflow_intervals(self, rds_well: dm.IBorehole, strg: dm.IDataStorage):
        out = []
        print("Try to load gas river data for well: {0} ...".format(rds_well.getName()))
        ctx_ = cmn.progress_ctx()
        err_ = cmn.err_info()

        wtStData = dm.IWellTestsData.makeRftDst(dm.db_caching)  # type: dm.IWellTestsData
        lRes = wtStData.load(strg, rds_well.getID(), ctx_, err_)
        if not lRes:
            print("Well %s has no well test data" % rds_well.getName())
            print(err_.msg)
            return []

        elif wtStData.size() == 0:
            print("Well %s has no well test data" % rds_well.getName())
            return []
        if wtStData.size() == 1:
            wtst_item = wtStData.at(0)
        else:
            wtst_item = wtStData.findLast(wtStData.getDataMaxDate())

        if wtst_item is None:
            print("Well %s has no well test data" % rds_well.getName())
            return []

        count = wtst_item.stagesCount()
        countSite = wtst_item.siteCount()
        haveGas = False
        for i in range(count):
            stage = wtst_item.stageAt(i)  # type: dm.IWtStage
            if if_valid(stage.getGasV()) or if_valid(stage.getGasRateV()) or if_valid(stage.getNGasRateV()) \
                    or if_valid(stage.getNglRateM()):
                haveGas = True
                break
            else:
                continue

        if haveGas:
            for s in range(countSite):
                ival = {}
                site = wtst_item.siteAt(s)  # type: dm.IWtSite
                if self['survey']:
                    pTop = self['survey'].get_tvd(site.getTopMD())
                    pBase = self['survey'].get_tvd(site.getBaseMD())
                else:
                    pTop = site.getTopMD()
                    pBase = site.getBaseMD()
                ival['Top'] = pTop
                ival['Bottom'] = pBase
                ival['Year'] = ''
                ival['ShowLabelYear'] = 'False'
                out.append(ival)
        return out

    def get_cementing_ivals(self, rds_well: dm.IBorehole, strg: dm.IDataStorage, model):
        print("Load PGI data for well: {0} ...".format(rds_well.getName()))
        out = []
        err_ = cmn.err_info()
        model_id = model.getID()
        pgi_data = eu.load_prodloginterp_by_bh_and_model(rds_well.getID(), model_id, strg, err_)  # type: dm.ILogData
        if not pgi_data:
            return []

        runs = pgi_data.runs()  # type: dm.ILogRuns
        rsize = runs.size();
        position = 0
        if rsize == 0:
            return []

        dt = cmn.get_undefined_date()
        cmn.from_string_date("01.01.1900", dt)

        for rnumber in range(rsize):
            run = runs.at(rnumber)
            ldate = cmn.get_undefined_date()
            run.getLogDate(ldate)
            if dt < ldate:
                dt = ldate
                position = rnumber
        frames = dm.vec_log_frame()
        runs.at(position).frames(frames)
        frame = frames[0]  # type: dm.ILogFrame

        cemWithColumn = frame.curveByMnemo("PLR_CBC")  # type: dm.ILogCurve
        germProp = frame.curveByMnemo("PLR_GERM")  # type: dm.ILogCurve
        rCount = frame.getNpoint()
        if rCount == 0:
            print("Borehole " + rds_well.getName() + " has no prodlog data")
            return out
        mdT = frame.topTvdVec()
        md = frame.baseTvdVec()
        if mdT is None or md is None:
            return []

        if cemWithColumn is not None:
            cemWithColumn = cemWithColumn.idata();
        else:
            cemWithColumn = [''] * rCount

        for x in range(rCount):
            scam = {'Top': '', 'Bottom': '', 'CementingQuality': '', 'Colour': ''}
            if self['survey']:
                md[x] = self['survey'].get_tvd(md[x])
                mdT[x] = self['survey'].get_tvd(mdT[x])
            scam['Top'] = mdT[x] if not cmn.is_undefined(mdT[x]) else ''
            scam['Bottom'] = md[x] if not cmn.is_undefined(md[x]) else ''
            if cemWithColumn[x] in [8, 7]:
                cque = 'Good'; colour = 'fuchsia'
            elif cemWithColumn[x] in [5, 6]:
                cque = 'Bad'; colour = '#999999'
            elif cemWithColumn[x] == 9:
                cque = 'Part'; colour = 'lime'
            elif cemWithColumn[x] in [3,4]:
                cque = 'No'; colour = 'whitesmoke'
            scam['CementingQuality'] = cque
            scam['Colour'] = colour
            out.append(scam)
        return out

    def get_current_bottomholes(self, rds_well: dm.IBorehole, strg: dm.IDataStorage):
        print("Load plugback data: {0} ...".format(rds_well.getName()))
        out = OrderedDict()
        value = ''
        btevs = dm.IBottomholeEvents.make(dm.db_caching)
        btevs.load(strg, rds_well.getID(), cmn.progress_ctx(), cmn.err_info())
        vs = btevs.size()
        if vs == 0:
            print("WL: %s has no boreholes history" % rds_well.getName())
            return out
        else:
            btev = btevs.at(vs - 1)  # type: dm.IBottomholeEvent
            dt = btev.getDate();
            dt_string = cmn.to_string_date(dt)
            tvd = btev.bottomMd()
            if self['survey']:
                return [OrderedDict([('Value', self['survey'].get_tvd(tvd)), ('Year', dt_string[-2:])])]
            else:
                return [OrderedDict([('Value', tvd), ('Year', dt_string[-2:])])]

    def get_cementing_bridges(self, rds_well: dm.IBorehole, strg: dm.IDataStorage):
        out = []
        psevdo_ctx = dmsrv.python_ctx(); psevdo_res = dmsrv.python_results()
        psevdo_ctx.pStorage = strg
        layers = ['BOREHOLE_ID', 'EVENT_DATE', 'PLUG_TOP_MD', 'PLUG_BASE_MD', 'PLUG_OPERATION']
        try:
            tus = table_utils.makeBoreholeTable("PLUG_TABLE", psevdo_ctx, layers, rds_well.getID(), psevdo_res) #type: dmsrv.ITableController
            if tus is None:
                print (psevdo_res.err.msg)
                return out
            table_utils.sortTable(tus, 'EVENT_DATE')
        except NameError:
            print(psevdo_res.err.msg)
            return out
        group_open = []; group_closed = []
        key = OrderedDict()
        for i in range(tus.getRowCount()):
            dt = table_utils.getDate2('EVENT_DATE', i, tus)
            top = table_utils.getNum2('PLUG_TOP_MD', i, tus)
            base = table_utils.getNum2('PLUG_BASE_MD', i, tus)
            code = table_utils.getInt2('PLUG_OPERATION', i, tus)
            if code == 1:
                group_open.append((dt, top, base))
            elif code == 1:
                group_closed.append((dt, top, base))
            else:
                group_open.append((dt, top, base))
        if len(group_closed) == 0:
            for ival in group_open:
                key['Top'] = ival[0]
                key['Bottom'] = ival[1]
                key['Year'] = cmn.to_string_date(ival[2])
                key['ShowLabel'] = 0
                out.append(key)
        for ival in group_open:
            ival, show = self.check_open_or_closed(ival, group_closed)
            key['Top'] = ival[0]
            key['Bottom'] = ival[1]
            key['Year'] = cmn.to_string_date(ival[2])
            key['ShowLabel'] = show
            out.append(key)
        return out

    def get_sandy_argeloise(self, rds_well: dm.IBorehole, strg: dm.IDataStorage):
        out = {}
        if len(self['CurrentBottomholes']) != 0:
            out['Top'] = self['CurrentBottomholes'][-1]['Value'];
            out['Year'] = self['CurrentBottomholes'][-1]['Year']
            out['Bottom'] = self['WellDrilledMd']['Value']
        else:
            out['Top'] = self['FalseBottom']['Value']
            out['Year'] = '007'
            out['Bottom'] = self['WellDrilledMd']['Value']
        return out

    def check_open_or_closed(self, bridge, std_vec):
        bridge, bridge_status = bridge, 0
        for std in std_vec:
            if bridge[2] > std[2]:
                continue
            elif (bridge[0] <= std[0] < bridge[1]) or (bridge[0] < std[1] <= bridge[1]):
                bridge_status = 1
                break
        return bridge, bridge_status

    def get_breaks(self, rds_well: dm.IBorehole, strg: dm.IDataStorage):
        """return packer on well"""
        out =[]
        name_of_table = "PACKER_TABLE"
        table = create_table_dynamic_constraction(strg, rds_well)
        if table is None:
            return out

        for row in range(table.getRowCount()):
            nameBhInTable = tu.getStr2("BOREHOLE_ID", row, table)
            if nameBhInTable != rds_well.getName(): continue
            md = float_(tu.getStr2("PACKER_MD", row, table))
            bot = float_(tu.getStr2("PACKER_LENGTH", row, table)) + md
            if self['survey']:
                tvd = self['survey'].get_tvd(md)
                bot_tvd = self['survey'].get_tvd(bot)
            else:
                tvd = md
                bot_tvd = bot
            lenght = float_(tu.getStr2("PACKER_LENGTH", row, table))
            opType = tu.getInt2('PACKER_OP_TYPE', row, table)
            date = tu.getStr2('EVENT_DATE', row, table)
            if opType != 0:
                for p, v in out.items():
                    if v["Top"] == tvd:
                        del out[p]
                        break
            else:
                out.append({'Top' : tvd, 'Bottom' : bot_tvd,
                                'Year': date[-4:], 'ShowLabel' : 1, 'Kind' : 'ProductionString'})
        return out

    def get_prod_string(self, rds_well: dm.IBorehole, strg: dm.IDataStorage):
        table_nkt = create_table_nkt(strg, rds_well)
        if table_nkt is None:
            return True
        out = []
        num_col = 0; bm_max = 0.0
        for row in range(table_nkt.getRowCount()):
            col_dict = {};
            opType = tu.getInt2('TUB_OP_TYPE', row, table_nkt)
            if cmn.is_undefined(opType) or opType == 1: continue
            nameBhInTable = tu.getStr2("BOREHOLE_ID", row, table_nkt)
            if nameBhInTable != rds_well.getName(): continue

            dateE = tu.getStr2('EVENT_DATE', row, table_nkt)  # type: cmn.date_t
            numSec = tu.getStr2('TUB_NUM', row, table_nkt)  # type: int
            assNum = tu.getStr2('TUB_ASSEMBLY', row, table_nkt)  # type: int
            if numSec == '':
                numSec = 0
            else:
                numSec = int(numSec) - 1
            dia = float_(tu.getStr2('TUB_INTD', row, table_nkt))  # type: float
            bmd = float_(tu.getStr2('TUB_BASE_MD', row, table_nkt))  # type: float
            if self['survey']: bmd = self['survey'].get_tvd(bmd)

            perf = tu.getStr2('TUB_REMARKS', row, table_nkt)  # type: float
            if perf == 'перф': check = check_cross_ival(self['PerfData'], bmd)

            col_dict["Top"] = 0.0
            col_dict["Bottom"] = bmd
            col_dict["Diam"] = dia
            col_dict["assNum"] = assNum
            col_dict["date"] = dateE
            out.append(col_dict)
            num_col += 1
            if bm_max < bmd: bm_max = bmd
        if num_col > 1:
            sorted(out, key=lambda x: x['Diam'])
        self['Constractions'] = out
        self['ProductionString']['InflowFromBehindProductionString'] = check_cross_flow(self['InflowIntervals'], bm_max)
        return True


class WellXML(Well):
    def __init__(self, element: Element):
        self['name'] = element.attrib['name']
        for elem in element.getchildren(): #type: Element
            out = {}; tmp = []
            if len(elem.getchildren()) != 0:
                if elem.tag == "ProductionString":
                    for el in elem.getchildren():
                        out[el.tag] = el.attrib
                else:
                    for el in elem.getchildren():
                        tmp.append(el.attrib);
                    self[elem.tag] = tmp
            elif elem.tag in ['Cuts']:
                self[elem.tag] = tmp
            else:
                self[elem.tag] = elem.attrib


class Settings:
    def __init__(self, profile=None, model_c=None, model_g=None, strg=None, tag='Work'):
        self.profile = profile #type:dm.IProfile
        self.model_c = model_c #type:dm.IModel
        self.model_g = model_g #type:dm.IModel
        self.boreholes = dm.vec_borehole_t()
        if self.profile is not None:
            self.profile.getBoreholes(self.boreholes, True)
        self.bh_read = []
        self.strg = strg


class SettingsFromRds(Settings):
    def __init__(self, profile=None, model_c=None, model_g=None, strg=None, tag='Work'):
        super(SettingsFromRds, self).__init__(profile, model_c, model_g, strg, tag)
        self.header_name = ''
        self.tags = OrderedDict()
        self.settings = dict()

    def read_well(self):
        for bh in self.boreholes: #type: dm.IBorehole
            xw = WellRDS(bh, self.strg, self.model_c, self.model_g)
            self.bh_read.append(xw)

    def write_well(self, tag_name="Work"):
        self.root = Element("root")
        etr = ElementTree(self.root)
        tag = SubElement(self.root, "Tag", name=tag_name)
        header = SubElement(tag, "Title", name=self.header_name)
        well_all = SubElement(header, "Wells")
        for well in self.bh_read: #type: WellRDS
            well.return_xml_element(well_all)
        self.tags[tag_name] = well_all

    def write_settings(self):
        sets = SubElement(self.root, "Settings")
        for key, val in self.settings.items():
            tmp = SubElement(sets, key, Value=val)


class SettingsFromXml:
    def __init__(self, data='', parser=None):
        self.data = data
        self.parser = parser
        self.tags = OrderedDict()
        self.settings = dict()
        self.bh_read = []
        self.header_name = ''
        self.read_tags()

    def read_tags(self):
        self.et = parse(self.data, parser = self.parser)
        self.root = self.et.getroot() #type: Element
        for tag in self.root.getchildren(): #type: Element
            if tag.tag == 'Title':
                self.header_name = tag.attrib['name']
            elif tag.tag == 'Settings':
                for t in tag.getchildren():
                    self.settings[t.tag] = t.attrib['Value']
                continue
            self.tags[tag.attrib['name']] = tag
        if len(self.settings.items()) == 0:
            self.settings = self.load_default()

    def load_default(self):
        c = parse("settings/default_settings.xml", parser=self.parser)
        r = c.getroot()
        for tag in r.getchildren():
            if tag.tag == 'Settings':
                for t in tag.getchildren():
                    self.settings[t.tag] = t.attrib['Value']
                continue

    def read_well(self, tag_name=None):
        if tag_name is None and len(self.tags.keys())>=1:
            tag_name = [key for key in self.tags.keys()][0]
        else:
            tag_name = 'Work'
        magic_el = self.tags[tag_name] #type: SubElement
        els = magic_el.findall('Title/Wells/')
        for wl in els:
            self.bh_read.append(WellXML(wl))

    def write_well(self, tag_name=None):
        if tag_name is None and len(self.tags.keys())>=1:
            tag_name = [key for key in self.tags.keys()][0]
        elt = self.root.findall('Tag')
        elt_names = [el.attrib['name'] for el in elt]
        if tag_name not in elt_names:
            tag = SubElement(self.root, "Tag", name=tag_name)
            header = SubElement(tag, "Title", name=self.header_name)
            well_all = SubElement(header, "Wells")
            for well in self.bh_read: #type: WellRDS
                well.return_xml_element(well_all)
            self.tags[tag_name] = well_all

        else:
            for el in elt:
                if el.attrib['name'] == tag_name:
                    self.root.remove(el)
                    break
            tag = SubElement(self.root, "Tag", name=tag_name)  # type: Element
            header = SubElement(tag, "Title", name=self.header_name)
            well_all = SubElement(header, "Wells")
            for well in self.bh_read: #type: WellRDS
                well.return_xml_element(well_all)
            self.tags[tag_name] = well_all

    def write_settings(self):
        sets = elt = self.root.find('Settings')
        for key, val in self.settings.items():
            tmp = sets.find(key)
            if tmp is None:
                tmp = SubElement(sets, key, Value=val)
            else:
                tmp.set('Value', val)


if __name__ == '__main__':
    f = open(r'C:\Users\ysenich\PycharmProjects\TCHView\well_xml', 'r', encoding='cp1251')
    xml_ = f.read()
    xml_parsing = fromstring(xml_)
    root = xml_parsing
    c = WellXML(root)
    cout =  (c.return_xml_element(root))
    print (minidom.parseString(tostring(cout)).toprettyxml())