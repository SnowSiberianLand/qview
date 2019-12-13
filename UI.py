# -*- coding: cp1251 -*-
import operator
from base_ui import *
from Well_Object import *
import mod_dm as dm
import db_utils as dub
import mod_orm as db
from model_table import *
import logging
from paint_picture import Cartoon, Mscenes, TesTCoordinateSupport


dict_well_cat = {
0   : 'Неизвестно',
11  : 'Нефтяная',
12	: 'Газовая',
13	: 'Водозаб',
15	: 'Газоконден',
20	: 'Нагнет',
41	: 'Поглощ',
50	: 'Пьезометр',
51	: 'Наблюд. скв.',
52	: 'Термометрическая',
101	: 'Нагнет по газу'
}

# noinspection PyTypeChecker
reversed_dict_well_cat = dict(map(reversed, dict_well_cat.items()))


dict_well_state = {
0 : 'Неизвестно',
1 : 'Работе',
2 : 'Ост',
3 : 'Ожид_Осв',
4 : 'Осв',
5 : 'Наблюд',
6 : 'Пьезом',
7 : 'Консерв',
8 : 'Ликвид',
9 : 'Ожид_Ликв',
10 : 'Накоплен',
12 : 'Проект',
20 : 'Бурение',
22 : 'Без_тек',
23 : 'Без_прош',
24 : 'Ожид_Осв_т',
25 : 'Освоен_т',
26 : 'Ожид_Осв_п',
27 : 'Освоен_п',
30 : 'Отработка',
31 : 'Откл_ проект',
32 : 'Неперф',
99 : 'Проек_план_раб',
101 : 'Довывод',
102 : 'Простой',
103 : 'Под станком ПРС',
104 : 'Под станком КРС',
105 : 'В монтаже',
106 : 'Осв выше проектной глубины',
107 : 'Испыт',
108 : 'Углубл',
109 : 'Ожид_Подкл',
110 : 'Ликвид после бурения',
111 : 'Ожид_Обустр'
}

reversed_dict_well_state = dict(map(reversed, dict_well_state.items()))

default_table_geometry = QRect()

dict_event_type = {
    0 : 'YearsWithOverhaulWashingAndStabilizationOfProducingFormation',
    1 : 'YearsWithOverhaulClearEntryPicketUtility',
    2 : 'YearsWithOverhaulStabilizationOfProducingFormation',
    3 : 'YearsWithWater',
    4 : 'YearsWithOverhaulWaterEntry',
    5 : 'YearsWithOverhaulWaterEntryPicketUtility'
}

reversed_dict_event_type = dict(map(reversed, dict_event_type.items()))


class MainPWindows(BaseProgram):
    def __init__(self):
        super(MainPWindows, self).__init__()
        self.Keeper = ConDefault()
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.fl = QSettings("settings/def_value.conf", QSettings.IniFormat)
        if self.fl.value("settings/nodes/app_font") is None: self.makeDefaultSetting()
        self.setWindowTitle("Technical View Data")
        self.setFont(self.fl.value("settings/nodes/app_font"))
        self.create_actions()
        self.toolbar.addAction(self.open_well_view_action)
        self.toolbar.addAction(self.open_file_action)
        self.toolbar.addAction(self.open_conn_action)
        self.toolbar.addAction(self.save_file_action)
        self.toolbar.addAction(self.save_with_tag)
        self.toolbar.addAction(self.settings)
        self.toolbar.addSeparator()
        self.center_widget = QWidget(self)

        self.setCentralWidget(self.center_widget)
        # self.main_scenes = Mscenes(self.Keeper)
        self.graphical_site = TesTCoordinateSupport(self)

        self.dview_vidget = WellDataView(self)
        self.addDockWidget(Qt.LeftDockWidgetArea , self.dview_vidget)

        self.main_l = QHBoxLayout()
        self.main_l.setContentsMargins(0, 0, 0, 0)

        self.center_widget.setLayout(self.main_l)
        self.main_l.addWidget(self.graphical_site)

    def create_actions(self):
        self.open_file_action = QAction(icon_load('wspace_shared'), '&open rds base', self)
        self.open_file_action.setShortcut('Ctrl+O')
        self.open_file_action.setStatusTip('Open datasource ...')
        self.open_file_action.triggered.connect(self.init_keeper)

        self.open_conn_action = QAction(icon_load('cloud'), '&open oracle connection', self)
        self.open_conn_action.setStatusTip('Open oracle datasource ...')
        self.open_conn_action.triggered.connect(self.initKeeper_from_ora)

        self.save_file_action = QAction(icon_load('save_all'), '&Save xml data', self)
        self.save_file_action.setStatusTip('Save xml data ...')
        self.save_file_action.triggered.connect(self.keeper_save)

        self.open_well_view_action = QAction(icon_load('tbl_cmn_well'), '&Well View widget data', self)
        self.open_well_view_action.setStatusTip('Open data editor ...')
        self.open_well_view_action.triggered.connect(self.well_view_change_state)
        self.open_well_view_action_state = True
        self.open_well_view_action.setCheckable(True)
        self.open_well_view_action.setChecked(True)

        self.save_with_tag = QAction(icon_load("save_as"), '@save with tag ...', self)
        self.save_with_tag.setStatusTip('save data with tag...')
        self.save_with_tag.triggered.connect(self.open_and_save_with_tag)

        self.settings = QAction(icon_load('settings'), '@settings...', self)
        self.settings.setStatusTip('Settings ')
        self.settings.triggered.connect(self.open_settings)

    def open_settings(self):
        self.st = SettingWindow(self)
        self.st.show()

    def init_keeper(self):
        if isinstance(self.Keeper, ConDefault):
            tmp = OpenFileDialog()
            a, b = tmp.getOpenFileName()
            if (a, b) != ('none', ' '):
                self.Keeper = ConnectionKeeper(a, b)
                if self.Keeper.profile is None:
                    self.Keeper = ConDefault()
                else:
                    self.dview_vidget.reset()

        else:
            msgBox = QMessageBox.warning(self, "Closed connection", "You realy want to close this connection & ",
                                         QMessageBox.Yes | QMessageBox.No) #type: QMessageBox.warning
            if msgBox == QMessageBox.Yes:
                self.Keeper = ConDefault()
                tmp = OpenFileDialog()
                a, b = tmp.getOpenFileName()
                self.Keeper = ConnectionKeeper(a, b)
                if self.Keeper.profile is not None:
                    self.dview_vidget.reset()

        if isinstance(self.Keeper, ConnectionKeeper):
            if self.Keeper.profile is not None:
                self.dview_vidget.reset()
                global perf_list, perf_tab_model, break_model, break_list, inflow_model, inflow_list, cem_model, \
                    re_cuts_model, events_model, bridge_model

                pf_header = ["Скважина", "АО кровли", "АО подошвы", "Год", "Показывать год", "Тип"]
                perf_list = []; tmp_element = [];
                for well in self.Keeper.workspace.bh_read:
                    for i in range(len(well["PerfDataS"])):
                        tmp_element.append(well["name"])
                        tmp_element.append(well["PerfDataS"][i]["Top"])
                        tmp_element.append(well["PerfDataS"][i]["Base"])
                        tmp_element.append(well["PerfDataS"][i]["Year"])
                        tmp_element.append(well["PerfDataS"][i]["ShowYear"])
                        tmp_element.append(well["PerfDataS"][i]["Type"])
                        perf_list.append(tmp_element);
                        tmp_element = [];
                perf_tab_model = MyTableModel(self, perf_list, pf_header, 'perf')

                break_header = ["Скважина", "АО кровли", "АО подошвы", "Год", "Тип"]
                break_list = [];
                tmp_element = [];
                for well in self.Keeper.workspace.bh_read:
                    for i in range(len(well["Breaks"])):
                        tmp_element.append(well["name"])
                        tmp_element.append(well["Breaks"][i]["Top"])
                        tmp_element.append(well["Breaks"][i]["Bottom"])
                        tmp_element.append(well["Breaks"][i]["Year"])
                        tmp_element.append(well["Breaks"][i]["Kind"])
                        break_list.append(tmp_element);
                        tmp_element = [];
                break_model = MyTableModel(self, break_list, break_header, 'breaks')

                inflow_ival = ["Скважина", "АО кровли", "АО подошвы", "Год", "Показывать год"]
                inflow_list = [];
                tmp_element = [];
                for well in self.Keeper.workspace.bh_read:
                    for i in range(len(well["InflowIntervals"])):
                        tmp_element.append(well["name"])
                        tmp_element.append(well["InflowIntervals"][i]["Top"])
                        tmp_element.append(well["InflowIntervals"][i]["Bottom"])
                        tmp_element.append(well["InflowIntervals"][i]["Year"])
                        tmp_element.append(well["InflowIntervals"][i]["ShowLabelYear"])
                        inflow_list.append(tmp_element);
                        tmp_element = [];

                if len(inflow_list) == 0: inflow_list = ['', '', '', '', '']
                inflow_model = MyTableModel(self, inflow_list, inflow_ival, 'inflow')

                cem_q_header = ["Скважина", "АО кровли", "АО подошвы", "Качество Цементирования"]
                cem_list = []; tmp_element = [];
                for well in self.Keeper.workspace.bh_read:
                    for i in range(len(well["CementingQualityIntervals"])):
                        tmp_element.append(well["name"])
                        tmp_element.append(well["CementingQualityIntervals"][i]["Top"])
                        tmp_element.append(well["CementingQualityIntervals"][i]["Bottom"])
                        tmp_element.append(well["CementingQualityIntervals"][i]["CementingQuality"])
                        cem_list.append(tmp_element);
                        tmp_element = [];
                cem_model = MyTableModel(self, cem_list, cem_q_header, 'cementing')

                cem_bridge = ["Скважина", "АО кровли", "АО подошвы", "Год", "Показывать год"]
                bridge_list = []; tmp_element = [];
                for well in self.Keeper.workspace.bh_read:
                    for i in range(len(well["CementBridges"])):
                        tmp_element.append(well["name"])
                        tmp_element.append(well["CementBridges"][i]["Top"])
                        tmp_element.append(well["CementBridges"][i]["Bottom"])
                        tmp_element.append(well["CementBridges"][i]["Year"])
                        tmp_element.append(well["CementBridges"][i]["ShowLabel"])
                        bridge_list.append(tmp_element);
                        tmp_element = [];
                bridge_model = MyTableModel(self, bridge_list, cem_bridge, 'cem_bridges')

                re_cuts_header = ["Скважина", "АО кровли", "АО подошвы", "Мощность разрыва"]
                cut_list = []; tmp_element = [];
                for well in self.Keeper.workspace.bh_read:
                    for i in range(len(well["Cuts"])):
                        tmp_element.append(well["name"])
                        tmp_element.append(well["Cuts"][i]["Top"])
                        tmp_element.append(well["Cuts"][i]["Bottom"])
                        tmp_element.append(well["Cuts"][i]["thikness"])
                        cut_list.append(tmp_element)
                        tmp_element = []
                re_cuts_model = MyTableModel(self, cut_list, re_cuts_header, 'cuts')

                events_header = ["Скважина", "Дата", "Комментарий", "Тип события"]
                event_list = []; tmp_element = [];
                for well in self.Keeper.workspace.bh_read:
                    for i in range(len(well["Cuts"])):
                        tmp_element.append(well["name"])
                        tmp_element.append(well["Cuts"][i]["Date"])
                        tmp_element.append(well["Cuts"][i]["Comment"])
                        tmp_element.append(well["Cuts"][i]["EventType"])
                        event_list.append(tmp_element);
                        tmp_element = [];
                events_model = MyTableModel(self, event_list, events_header, 'events_ands_names')

    def initKeeper_from_ora(self):
        if isinstance(self.Keeper, ConDefault):
            tmp = FormConnection()
            if tmp.result() == QDialog.Accepted and tmp.getString() != '':
                self.Keeper = ConnectionKeeper('oracle', tmp.getString()[0], tmp.getString()[1])
                if self.Keeper.profile is None:
                    self.Keeper = None
                else:
                    self.dview_vidget.reset()

            else:
                self.Keeper == None
        else:
            msgBox = QMessageBox.warning(self, "Closed connection", "You realy want to close this connection & ",
                                         QMessageBox.Yes | QMessageBox.No) #type: QMessageBox.warning
            if msgBox == QMessageBox.Yes:
                tmp = FormConnection()
                if tmp.result() == QDialog.Accepted and tmp.getString() != '':
                    self.Keeper = ConnectionKeeper('oracle', tmp.getString()[0], tmp.getString()[1])
                    if self.Keeper.profile is None:
                        self.Keeper = None
                    else:
                        self.dview_vidget.reset()
                else:
                    self.Keeper == None

        global perf_list, perf_tab_model, break_model, break_list, inflow_model, inflow_list, cem_model, \
            re_cuts_model, events_model, bridge_model
        pf_header = ["Скважина", "АО кровли", "АО подошвы", "Год", "Показать Год", "Тип"]
        perf_list = []
        tmp_element = []
        for well in self.Keeper.workspace.bh_read:
            for i in range(len(well["PerfDataS"])):
                tmp_element.append(well["name"])
                tmp_element.append(well["PerfDataS"][i]["Top"])
                tmp_element.append(well["PerfDataS"][i]["Base"])
                tmp_element.append(well["PerfDataS"][i]["Year"])
                tmp_element.append(well["PerfDataS"][i]["ShowYear"])
                tmp_element.append(well["PerfDataS"][i]["Type"])
                perf_list.append(tmp_element);
                tmp_element = []
        perf_tab_model = MyTableModel(self, perf_list, pf_header)

        break_header = ["Скважина", "АО кровли", "АО подошвы", "Год", "Тип"]
        break_list = [];
        tmp_element = [];
        for well in self.Keeper.workspace.bh_read:
            for i in range(len(well["Breaks"])):
                tmp_element.append(well["name"])
                tmp_element.append(well["Breaks"][i]["Top"])
                tmp_element.append(well["Breaks"][i]["Bottom"])
                tmp_element.append(well["Breaks"][i]["Year"])
                tmp_element.append(well["Breaks"][i]["Kind"])
                break_list.append(tmp_element);
                tmp_element = [];

        break_model = MyTableModel(self, break_list, break_header)
        inflow_ival = ["Скважина", "АО кровли", "АО подошвы", "Год", "Показывать год"]
        inflow_list = [];
        tmp_element = [];

        for well in self.Keeper.workspace.bh_read:
            for i in range(len(well["InflowIntervals"])):
                tmp_element.append(well["name"])
                tmp_element.append(well["InflowIntervals"][i]["Top"])
                tmp_element.append(well["InflowIntervals"][i]["Bottom"])
                tmp_element.append(well["InflowIntervals"][i]["Year"])
                tmp_element.append(well["InflowIntervals"][i]["ShowLabelYear"])
                inflow_list.append(tmp_element);
                tmp_element = [];
        if len(inflow_list) == 0: inflow_list = ['', '', '', '', '']
        inflow_model = MyTableModel(self, inflow_list, inflow_ival)

        cem_q_header = ["Скважина", "АО кровли", "АО подошвы", "Качество Цементирования"]
        cem_list = []; tmp_element = [];
        for well in self.Keeper.workspace.bh_read:
            for i in range(len(well["CementingQualityIntervals"])):
                tmp_element.append(well["name"])
                tmp_element.append(well["CementingQualityIntervals"][i]["Top"])
                tmp_element.append(well["CementingQualityIntervals"][i]["Bottom"])
                tmp_element.append(well["CementingQualityIntervals"][i]["CementingQuality"])
                cem_list.append(tmp_element);
                tmp_element = [];
        cem_model = MyTableModel(self, cem_list, cem_q_header)

        re_cuts_header = ["Скважина", "АО кровли", "АО подошвы", "Мощность разрыва"]
        cut_list = [];
        tmp_element = [];
        for well in self.Keeper.workspace.bh_read:
            for i in range(len(well["Cuts"])):
                tmp_element.append(well["name"])
                tmp_element.append(well["Cuts"][i]["Top"])
                tmp_element.append(well["Cuts"][i]["Bottom"])
                tmp_element.append(well["Cuts"][i]["thikness"])
                cut_list.append(tmp_element);
                tmp_element = [];
        re_cuts_model = MyTableModel(self, cut_list, re_cuts_header)

        cem_bridge = ["Скважина", "АО кровли", "АО подошвы", "Год", "Показывать год"]
        bridge_list = [];
        tmp_element = [];
        for well in self.Keeper.workspace.bh_read:
            for i in range(len(well["CementBridges"])):
                tmp_element.append(well["name"])
                tmp_element.append(well["CementBridges"][i]["Top"])
                tmp_element.append(well["CementBridges"][i]["Bottom"])
                tmp_element.append(well["CementBridges"][i]["Year"])
                tmp_element.append(well["CementBridges"][i]["ShowLabel"])
                bridge_list.append(tmp_element);
                tmp_element = [];
        bridge_model = MyTableModel(self, bridge_list, cem_bridge, 'cem_bridges')

        events_header = ["Скважина", "Дата", "Комментарий", "Тип события"]
        event_list = [];
        tmp_element = [];
        for well in self.Keeper.workspace.bh_read:
            for i in range(len(well["Cuts"])):
                tmp_element.append(well["name"])
                tmp_element.append(well["Cuts"][i]["Date"])
                tmp_element.append(well["Cuts"][i]["Comment"])
                tmp_element.append(well["Cuts"][i]["EventType"])
                event_list.append(tmp_element);
                tmp_element = [];
        events_model = MyTableModel(self, event_list, events_header)

    def open_and_save_with_tag(self):
        if isinstance(self.Keeper, ConDefault):
            msgBox = QMessageBox.warning(self, "Can't save nothing", "You can't save nothing in file ",
                                         QMessageBox.Ok)
        else:
            tagForm(self)
            self.dview_vidget.reset()

    def keeper_save(self):
        self.Keeper.save()

    def makeDefaultSetting(self):
        self.fl.setValue("settings/nodes/well_well", 60.0)
        self.fl.setValue("settings/nodes/well_nkt", 30.0)
        self.fl.setValue("settings/nodes/scale", 20)
        self.fl.setValue("settings/nodes/window_top", 1600.0)
        self.fl.setValue("settings/nodes/table_top", 1600.0)
        self.fl.setValue("settings/nodes/window_base", 1800.0)
        self.fl.setValue("settings/nodes/table_base", 1800.0)
        self.fl.setValue("settings/nodes/app_font", QFont('SansSerif', 26, QFont.Normal))
        self.fl.setValue("settings/nodes/title_font", QFont('SansSerif', 18, QFont.Bold))

    def well_view_change_state(self):
        if self.open_well_view_action_state:
            self.open_well_view_action_state = False
            self.dview_vidget.hide()
        else:
            self.open_well_view_action_state = True
            self.dview_vidget.show()
            # self.dview_vidget = WellDataView(self)


class DialogChooseModel(BaseDialog):
    def __init__(self, profiles, models):
        super(DialogChooseModel, self).__init__()

        self.profile = None;
        self.model_geo = None;
        self.model_c = None;
        self.none_choosing = False
        group_profiles = QGroupBox(self)
        group_profiles.setTitle('Выберите профиль...')
        group_profiles.setStyleSheet("""QGroupBox {border: 1px solid black; border-radius: 1px; 
        font-family: SansSerif; font-size: 12px; margin-top: 5px; padding: 5px}""")
        glayone = QVBoxLayout(group_profiles)
        items_list = QListWidget(self)
        items_list.setStyleSheet("""QListWidget {border-style: none;}""")
        number = 1
        for profile_ in profiles:
            item = QListWidgetItem(view=items_list)
            item.setText(profile_.getName())
            item.setIcon(QIcon(icon_load('nt_profile')))
            item.setData(4, profile_)
            number += 1

        items_list.setCurrentItem(item);
        glayone.addWidget(items_list)
        group_profiles.setLayout(glayone)

        group_profiles_geo = QGroupBox(self)
        group_profiles_geo.setTitle('Выберите модель геоданных...')
        group_profiles_geo.setStyleSheet("""QGroupBox {border: 1px solid black; border-radius: 1px; 
        font-family: SansSerif; font-size: 12px; margin-top: 5px; padding: 5px}""")
        glaytwo = QVBoxLayout(group_profiles_geo)

        model_box = QComboBox(self)
        number = 0
        for mod in models:
            model_box.addItem(QIcon(icon_load('nt_model')), mod.getName())
            model_box.setItemData(number, mod)
            number += 1
        model_box.setCurrentIndex(0)
        glaytwo.addWidget(model_box)

        group_profiles_cont = QGroupBox(self)
        group_profiles_cont.setTitle('Выберите модель контакта флюидов...')
        group_profiles_cont.setStyleSheet("""QGroupBox {border: 1px solid black; 
        border-radius: 1px; font-family: SansSerif; 
        font-size: 12px; margin-top: 5px; padding: 5px}""")
        glaythree = QVBoxLayout(group_profiles_cont)
        model_box.setCurrentIndex(0)
        model_box_c = QComboBox(self)
        number = 0
        for mod in models:
            model_box_c.addItem(QIcon(icon_load('nt_model')), mod.getName())
            model_box_c.setItemData(number, mod)
            number += 1
        model_box_c.setCurrentIndex(0)
        glaythree.addWidget(model_box_c)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(group_profiles)
        main_layout.addWidget(group_profiles_geo)
        main_layout.addWidget(group_profiles_cont)
        main_layout.addWidget(self.buttons)

        result = self.exec_()
        if result == QDialog.Accepted:
            self.profile = items_list.currentItem().data(4)
            self.model_geo = model_box.itemData(model_box.currentIndex())
            self.model_c = model_box_c.itemData(model_box_c.currentIndex())
            self.destroy()
        else:
            self.none_choosing = True
            self.destroy()


class OpenFileDialog(openFileDialog):
    def __init__(self):
        super(OpenFileDialog, self).__init__()
        self.setFilters(("Sqlite files (*.rds)", "Scheme Files (*.xml)"))

    def getOpenFileName(self, *args, **kwargs):
        self.exec_()
        if self.result() == QDialog.Accepted:
            self.fileName = self.selectedFiles()[0]
            if self.selectedFiles()[0].endswith('xml'):
                return 'file', self.selectedFiles()[0]
            elif self.selectedFiles()[0].endswith('rds'):
                return 'rds', self.selectedFiles()[0]
            else:
                return 'none', self.selectedFiles()[0]
        else:
            return 'none', ' '


class SaveXmlFileDialog(openFileDialog):
    def __init__(self):
        super(SaveXmlFileDialog, self).__init__()
        self.setWindowTitle("Выберите папку для сохранения файла >>>")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setFilters(("Scheme Files (*.xml)",))

    def _end(self):
        self.exec_()
        if self.result() == QFileDialog.Accepted:
            return ('file', self.selectedFiles()[0])
        else:
            return ('none', self.selectedFiles()[0])


class workspace:
    def __init__(self, bh_read = [], tag = {}, settings = {}):
        self.bh_read = bh_read
        self.tag = tag
        self.settings = settings


class ConDefault:
    def __init__(self):
        self.workspace = workspace([], {}, dict())
        self.load_default()

    def load_default(self):
        prs = XMLParser(encoding="cp1251")
        c = parse("settings/default_settings.xml", parser=prs)
        r = c.getroot()
        for tag in r.getchildren():
            if tag.tag == 'Settings':
                for t in tag.getchildren():
                    self.workspace.settings[t.tag] = t.attrib['Value']
                continue

    def save(self):
        tip = SaveXmlFileDialog()
        res, fname = tip._end()
        if res != 'none':
            if fname.endswith('.xml'):
                fileXml = open(fname, 'w')
            else:
                fileXml = open("{0}.xml".format(fname), 'w')
            fileXml.write("")
            fileXml.close()


class ConnectionKeeper:
    def __init__(self, type_conn, conn_string, meta=''):
        global qApp
        self.init_type = type_conn
        self.path_to_ = conn_string
        self.storage = None
        self.profile = None  # type: dm.IProfile
        self.model_geo = None  # type: dm.IModel
        self.model_c = None  # type: dm.IModel
        self.profiles = dm.vec_profile_t()
        self.models = dm.vec_model_t()
        self.tag_name = 'Work'

        if type_conn == 'file':
            self.file_xml = open(conn_string, 'r').read()
            prs = XMLParser(encoding="cp1251")
            self.workspace = SettingsFromXml(data=conn_string, parser=prs)
            self.workspace.read_well()
            # self.workspace.write_well(self.tag_name)
            self.file_xml = '\n'.join([line for line in minidom.parseString(tostring(self.workspace.root))\
                                      .toprettyxml(indent=' '*2).split('\n') if line.strip()])
            self.profile = 'xml'

        elif type_conn == 'rds' or type_conn== 'oracle':
            if type_conn == 'rds':
                self.storage = dub.openTargetRDS(db.db_sqlite, conn_string)
            elif type_conn == 'oracle':
                self.storage = dub.openTargetRDS(db.db_oracle, conn_string, meta)
            if self.storage is None:
                logging.warning('error: "ORA-01017: неверно имя пользователя/пароль; '
                                'вход в систему запрещается')
            else:
                self.storage.getRegHelper().getProfileRegistry().getElems(self.profiles)
                self.storage.getRegHelper().getModelRegistry().getElems(self.models)
                if len(self.profiles)==0:
                    msgBox = QMessageBox.warning(qApp, "Can't open this base ", "Profiles not found", QMessageBox.Ok)
                else:
                    self.open_rds_dialog()
                    if self.profile is not None:
                        self.workspace = SettingsFromRds(self.profile, self.model_c, self.model_geo, self.storage, 'Work')
                        self.workspace.read_well()
                        self.workspace.header_name = self.profile.getName()
                        self.workspace.write_well(self.tag_name)
                        #TODO: normal work
                        self.file_xml = '\n'.join([line for line in minidom.parseString(tostring(self.workspace.root))\
                                                  .toprettyxml(indent=' '*2).split('\n') if line.strip()])

    def open_rds_dialog(self):
        tmp_dialog = DialogChooseModel(self.profiles, self.models)
        if tmp_dialog.none_choosing:
            self.profile = None
        else:
            self.profile = tmp_dialog.profile
            self.model_geo = tmp_dialog.model_geo
            self.model_c = tmp_dialog.model_c

    def save(self):
        tip = SaveXmlFileDialog()
        res, fname = tip._end()
        if res != 'none':
            if fname.endswith('.xml'):
                fileXml = open(fname, 'w')
            else:
                fileXml = open("{0}.xml".format(fname), 'w')
            self.workspace.write_well(self.tag_name)
            self.workspace.write_settings()
            self.file_xml = '\n'.join([line for line in minidom.parseString(tostring(self.workspace.root)) \
                                      .toprettyxml(indent=' ' * 2).split('\n') if line.strip()])
            fileXml.write(self.file_xml)
            fileXml.close()


class GraphView(QGraphicsView):
    def __init__(self):
        super(GraphView, self).__init__()
        self.setStyleSheet("QGraphicsView {padding: 0px; margin: 0px}")


class WellDataView(QDockWidget):
    def __init__(self, parent=None):
        super(WellDataView, self).__init__(parent)
        self.AllWellsMode = False
        self.setStyleSheet("QComboBox {background-color: white; font-family: SansSerif;}"
                           "QPushButton {background-color: white; font-family: SansSerif;}"
                           "QTreeWidget {background-color: white; font-family: SansSerif; margin-right: 10 px;}")
        self.data_widget = QWidget(self)
        self.horizontal_layer = QHBoxLayout()
        self.data_widget.setMinimumWidth(350)
        self.setWidget(self.data_widget)
        self.setAllowedAreas(Qt.RightDockWidgetArea|Qt.LeftDockWidgetArea)
        self.vertical_layout = QVBoxLayout(self.data_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        found_mode = QPushButton()
        found_mode.setIcon(icon_load('filter_bar'))
        found_mode.clicked.connect(self.setmode)
        create_new = QPushButton()
        create_new.setIcon(icon_load("create_well"))
        create_new.setDisabled(True)

        self.tree_data = QTreeWidget()
        self.tree_data.header().hide()
        self.well_items = QTreeWidgetItem()
        self.tree_data.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.tree_data.setContextMenuPolicy(Qt.CustomContextMenu)
        self.well_items.setText(0, "Скважины")
        self.well_items.setIcon(0, QIcon("rsicon/wells.png"))
        self.well_items.setFlags(self.well_items.flags() & ~Qt.ItemIsSelectable)
        self.tree_data.addTopLevelItem(self.well_items)

        for i in parent.Keeper.workspace.bh_read:
            well_item = QTreeWidgetItem()
            well_item.setText(0, i['name'])
            well_item.setIcon(0, QIcon("rsicon/wells.png"))
            self.well_items.addChild(well_item)
        self.vertical_layout.addWidget(self.tree_data)
        self.setLayout(self.vertical_layout)

    def filter_event(self):
        self.tmp.setCurrentIndex(self.tmp.findText(self.tmp_line_edit.text()))
        self.setmode()

    def setmode(self):
        if self.tmp.isEditable():
            self.tmp.setEditable(False)
        else:
            self.tmp.setEditable(True)
            self.tmp_line_edit = QLineEdit(self.tmp)
            self.tmp.setLineEdit(self.tmp_line_edit)
            self.tmp_line_edit.returnPressed.connect(self.filter_event)

    def reset(self):
        self.AllWellsMode = False
        self.horizontal_layer = QHBoxLayout()
        self.data_widget = QWidget(self)
        self.data_widget.setMinimumWidth(350)
        self.setWidget(self.data_widget)
        self.setAllowedAreas(Qt.RightDockWidgetArea|Qt.LeftDockWidgetArea)
        self.vertical_layout = QVBoxLayout(self.data_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        found_mode = QPushButton()
        found_mode.setIcon(icon_load('filter_bar'))
        found_mode.clicked.connect(self.setmode)
        create_new = QPushButton()
        create_new.setIcon(icon_load("create_well"))
        create_new.setDisabled(True)
        self.tree_data = QTreeWidget()
        self.tree_data.header().hide()
        self.well_items = QTreeWidgetItem()
        self.tree_data.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_data.setContextMenuPolicy(Qt.CustomContextMenu)
        self.well_items.setText(0, "Скважины")
        self.well_items.setIcon(0, QIcon("rsicon/wells.png"))
        self.well_items.setFlags(self.well_items.flags() & ~Qt.ItemIsSelectable)
        self.tree_data.addTopLevelItem(self.well_items)

        for i in self.parent().Keeper.workspace.bh_read:
            well_item = QTreeWidgetItem()
            well_item.setText(0, i['name'])
            well_item.setData(1, Qt.UserRole, i)
            well_item.setIcon(0, QIcon("rsicon/wells.png"))
            self.well_items.addChild(well_item)
        self.well_items.child(0).setSelected(True)
        self.tree_data.setCurrentItem(self.well_items.child(0))
        self.well_items.setExpanded(True)
        self.vertical_layout.addWidget(self.tree_data)

        self.common_property = QWidget()
        self.common_property.setFixedHeight(self.height()*0.65)

        # Common Property Vertical
        self.cp_vert_lyout = QFormLayout()
        ct_item = self.well_items.child(0)
        ct_t = ct_item.data(1, Qt.UserRole)
        ct_index_ = self.tree_data.currentIndex().row()
        self.choosing_well = self.parent().Keeper.workspace.bh_read[int(ct_index_)]

        self.name_ = QLineEdit(); self.name_.setText(ct_t['name']);
        self.name_.editingFinished.connect(self.change_sets_common)
        self.wellBottom_ = QLineEdit(); self.wellBottom_.setText(ct_t['WellDrilledMd']['Value'])
        self.wellBottom_.editingFinished.connect(self.change_sets_common)
        self.FalseBottom_ = QLineEdit(); self.FalseBottom_.setText(ct_t['FalseBottom']['Value'])
        self.FalseBottom_.editingFinished.connect(self.change_sets_common)
        self.SandyArgillaceousPlugsTop = QLineEdit();
        self.SandyArgillaceousPlugsTop.setText(ct_t['SandyArgillaceousPlugs']['Top']);
        self.SandyArgillaceousPlugsTop.editingFinished.connect(self.change_sets_common)
        self.SandyArgillaceousPlugsYear = QLineEdit();
        self.SandyArgillaceousPlugsYear.setText(ct_t['SandyArgillaceousPlugs']['Year']);
        self.SandyArgillaceousPlugsYear.editingFinished.connect(self.change_sets_common)

        self.status_ = QComboBox();
        for key, value in dict_well_state.items():
            self.status_.addItem(value, userData = key);
        index = self.status_.findText(ct_t['Status']['status'], Qt.MatchFixedString)
        if index >= 0: self.status_.setCurrentIndex(index)
        self.status_.currentIndexChanged.connect(self.change_sets_common)

        self.well_type = QComboBox();
        for key, value in dict_well_cat.items():
            self.well_type.addItem(value, userData = key);
        index = self.well_type.findText(ct_t['Status']['cat'], Qt.MatchFixedString)
        if index >= 0: self.well_type.setCurrentIndex(index)
        self.well_type.currentIndexChanged.connect(self.change_sets_common)

        self.PerfDataS = QPushButton("&Перфорация")
        self.PerfDataS.clicked.connect(self.open_perf_window)
        self.InflowIntervals = QPushButton("&Интервалы притока")
        self.InflowIntervals.clicked.connect(self.open_inflow_window)
        self.CementingQualityIntervals = QPushButton("&Качество Цементирования")
        self.CementingQualityIntervals.clicked.connect(self.open_cem_window)

        #self.CementedDevices = QPushButton("&Зацементированое оборудование")
        self.CementBridges = QPushButton("&Цементные мосты")
        self.CementBridges.clicked.connect(self.open_bridge_window)
        self.Cuts = QPushButton("&Разрывы")
        self.Cuts.clicked.connect(self.open_cuts)
        self.Breaks = QPushButton("&Утерянное оборудование")
        self.Breaks.clicked.connect(self.open_break_window)
        self.WellEvents = QPushButton("&События на скважинах")
        self.WellEvents.clicked.connect(self.open_events)

        self.cp_vert_lyout.addRow("&Имя скважины:      ", self.name_)
        self.cp_vert_lyout.addRow("&Забой:             ", self.wellBottom_)
        self.cp_vert_lyout.addRow("&Искуственный забой:", self.FalseBottom_)
        self.cp_vert_lyout.addRow("&Текущий статус:    ", self.status_)
        self.cp_vert_lyout.addRow("&Тип скважины:    ", self.well_type)
        self.cp_vert_lyout.addRow("&Высота пробки:   ", self.SandyArgillaceousPlugsTop)
        self.cp_vert_lyout.addRow("&Год замера пробки:   ", self.SandyArgillaceousPlugsYear)
        self.cp_vert_lyout.addRow(self.PerfDataS)
        self.cp_vert_lyout.addRow(self.InflowIntervals)
        self.cp_vert_lyout.addRow(self.CementingQualityIntervals)

        #self.cp_vert_lyout.addRow(self.CementedDevices)
        self.cp_vert_lyout.addRow(self.CementBridges)
        self.cp_vert_lyout.addRow(self.Cuts)
        self.cp_vert_lyout.addRow(self.Breaks)
        self.cp_vert_lyout.addRow(self.WellEvents)
        self.common_property.setLayout(self.cp_vert_lyout)
        self.vertical_layout.addWidget(self.common_property)
        self.tree_data.currentItemChanged.connect(self.setCombined)
        #TODO: front
        # self.parent().graphical_site.show_when_load()

    #TODO: таким образом клеим каждую кнопку.
    def open_events(self):
        arent = TableChartBbox(self.parent(), self.WellEvents.text(), self.choosing_well)
        arent.show()
        arent.exec_()
        if arent.result() == QDialog.accepted:
            pass

    def open_perf_window(self):
        arent = TableChartBbox(self.parent(), self.PerfDataS.text(), self.choosing_well)
        arent.show()
        arent.exec_()
        if arent.result() == QDialog.accepted:
            pass

    def open_bridge_window(self):
        arent = TableChartBbox(self.parent(), self.PerfDataS.text(), self.choosing_well)
        arent.show()
        arent.exec_()
        if arent.result() == QDialog.accepted:
            pass

    def open_inflow_window(self):
        arent = TableChartBbox(self.parent(), self.InflowIntervals.text(), self.choosing_well)
        arent.show()
        arent.exec_()
        if arent.result() == QDialog.accepted:
            pass

    def open_break_window(self):
        arent = TableChartBbox(self.parent(), self.Breaks.text(), self.choosing_well)
        arent.show()
        arent.exec_()
        if arent.result() == QDialog.accepted:
            pass

    def open_cem_window(self):
        arent = TableChartBbox(self.parent(), self.CementingQualityIntervals.text(), self.choosing_well)
        arent.show()
        arent.exec_()
        if arent.result() == QDialog.accepted:
            pass

    def open_cuts(self):
        arent = TableChartBbox(self.parent(), self.Cuts.text(), self.choosing_well)
        arent.show()
        arent.exec_()
        if arent.result() == QDialog.accepted:
            pass

    @Slot()
    def change_sets_common(self):
        ct_item = self.tree_data.currentItem()
        ct_index_ = self.tree_data.currentIndex().row()
        self.choosing_well = self.parent().Keeper.workspace.bh_read[int(ct_index_)]
        if ct_item is not None:
            ct_t = ct_item.data(1, Qt.UserRole)
            ct_t['name'] = self.name_.text()
            ct_t['WellDrilledMd']['Value'] = (self.wellBottom_.text())
            ct_t['FalseBottom']['Value'] = (self.FalseBottom_.text())
            ct_t['Status']['status'] = reversed_dict_well_state[self.status_.currentText()]
            ct_t['Status']['cat'] = reversed_dict_well_cat[self.well_type.currentText()]
            ct_t['SandyArgillaceousPlugs']['Top'] = self.SandyArgillaceousPlugsTop.text()
            ct_t['SandyArgillaceousPlugs']['Year'] = self.SandyArgillaceousPlugsYear.text()
            ct_item.setData(1, Qt.UserRole, ct_t)
            self.parent().Keeper.workspace.bh_read[int(ct_index_)] = Well(ct_t)
            #TODO: передать обьект ct_t вместо bh_read в ConnectionKeeper?
        self.tree_data.update()

    @Slot()
    def setCombined(self):
        ct_item = self.tree_data.currentItem()
        ct_index_ = self.tree_data.currentIndex().row()
        self.choosing_well = self.parent().Keeper.workspace.bh_read[int(ct_index_)]
        if ct_item.childCount() == 0:
            if self.AllWellsMode:
                self.reset()
            ct_t = ct_item.data(1, Qt.UserRole)
            self.name_.setText(ct_t['name']);
            self.wellBottom_.setText(ct_t['WellDrilledMd']['Value']);
            self.FalseBottom_.setText(ct_t['FalseBottom']['Value']);
            self.SandyArgillaceousPlugsTop.setText(ct_t['SandyArgillaceousPlugs']['Top'])
            self.SandyArgillaceousPlugsYear.setText(ct_t['SandyArgillaceousPlugs']['Year'])

            #TODO:   File "D:\ysenich\Documents\Projects\SceneView\UI.py", line 875, in setCombined
            #     index = self.status_.findText(ct_t['Status']['status'], Qt.MatchFixedString)
            # TypeError: 'PySide.QtGui.QComboBox.findText' called with wrong argument types:
            #   PySide.QtGui.QComboBox.findText(int, PySide.QtCore.Qt.MatchFlag)
            # Supported signatures:
            #   PySide.QtGui.QComboBox.findText(unicode, PySide.QtCore.Qt.MatchFlags = static_cast<Qt.MatchFlags>(Qt.MatchExactly|Qt.MatchCaseSensitive))

            index = self.status_.findText(ct_t['Status']['status'], Qt.MatchFixedString)
            if index >= 0:
                self.status_.setCurrentIndex(index)
            else:
                self.status_.setCurrentIndex(0)
            self.status_.update()

            index4 = self.well_type.findText(ct_t['Status']['cat'], Qt.MatchFixedString)
            if index4 >= 0:
                self.well_type.setCurrentIndex(index4)
            else:
                self.well_type.setCurrentIndex(0)
            self.well_type.update()
        else:
            self.reset2Wells()

    def reset2Wells(self):
        self.AllWellsMode = True
        self.horizontal_layer = QHBoxLayout()
        self.data_widget = QWidget(self)
        self.data_widget.setMinimumWidth(350)
        self.setWidget(self.data_widget)
        self.setAllowedAreas(Qt.RightDockWidgetArea|Qt.LeftDockWidgetArea)
        self.vertical_layout = QVBoxLayout(self.data_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        found_mode = QPushButton()
        found_mode.setIcon(icon_load('filter_bar'))
        found_mode.clicked.connect(self.setmode)
        create_new = QPushButton()
        create_new.setIcon(icon_load("create_well"))
        create_new.setDisabled(True)
        self.tree_data = QTreeWidget()
        self.tree_data.header().hide()
        self.well_items = QTreeWidgetItem()
        self.tree_data.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.tree_data.setContextMenuPolicy(Qt.CustomContextMenu)
        self.well_items.setText(0, "Скважины")
        self.well_items.setIcon(0, QIcon("rsicon/wells.png"))
        self.well_items.setFlags(self.well_items.flags() & ~Qt.ItemIsSelectable)
        self.tree_data.addTopLevelItem(self.well_items)

        for i in self.parent().Keeper.workspace.bh_read:
            well_item = QTreeWidgetItem()
            well_item.setText(0, i['name'])
            well_item.setData(1, Qt.UserRole, i)
            well_item.setIcon(0, QIcon("rsicon/wells.png"))
            self.well_items.addChild(well_item)
        self.tree_data.setCurrentItem(self.well_items)
        self.well_items.setExpanded(True)
        self.vertical_layout.addWidget(self.tree_data)
        self.common_property = QWidget()
        self.common_property.setFixedHeight(self.height()*0.65)
        self.cp_vert_lyout = QFormLayout()

        #TODO: перфорация
        self.PerfDataS = QPushButton("&Перфорация")
        self.PerfDataS.connect(self.open_perf_window)
        self.InflowIntervals = QPushButton("&Интервалы притока")
        self.InflowIntervals.connect(self.open_inflow_window)
        self.CementingQualityIntervals = QPushButton("&Качество Цементирования")
        self.CementingQualityIntervals.connect(self.open_cem_window)

        #self.CementedDevices = QPushButton("&Зацементированое оборудование")
        self.CementBridges = QPushButton("&Цементные мосты")
        self.CementBridges.connect(self.open_bridge_window)
        self.Cuts = QPushButton("&Разрывы")
        self.Cuts.connect(self.open_cuts)
        self.Breaks = QPushButton("&Утерянное оборудование")
        self.Breaks.connect(self.open_break_window)
        self.WellEvents = QPushButton("&События на скважинах")
        self.WellEvents.connect(self.open_events)

        self.cp_vert_lyout.addRow(self.PerfDataS)
        self.cp_vert_lyout.addRow(self.InflowIntervals)
        self.cp_vert_lyout.addRow(self.CementingQualityIntervals)

        #self.cp_vert_lyout.addRow(self.CementedDevices)
        self.cp_vert_lyout.addRow(self.CementBridges)
        self.cp_vert_lyout.addRow(self.Cuts)
        self.cp_vert_lyout.addRow(self.Breaks)
        self.cp_vert_lyout.addRow(self.WellEvents)
        self.common_property.setLayout(self.cp_vert_lyout)

        self.vertical_layout.addWidget(self.common_property)
        self.tree_data.currentItemChanged.connect(self.setCombined)


class TimeLapsSlider(QSlider):
    def __init__(self, orientation, tags, lout):
        super(TimeLapsSlider, self).__init__(orientation)
        self.setRange(1, len(tags.keys()));
        self.setMaximumWidth(300)
        self.setFocusPolicy(Qt.StrongFocus);
        self.setTickPosition(QSlider.TicksBothSides);
        self.setSingleStep(1)
        self.setTickInterval(1)
        lout.addWidget(self, 0, 0, 1, len(tags))
        for number, tag in enumerate(tags.keys()):
            tmp = QLabel(tag)
            lout.addWidget(tmp, 1, number, 1, 1, Qt.AlignRight)

        if len(tags) == 0:
            tmp = QLabel("Work")
            lout.addWidget(tmp, 1, 0, 1, 1)

    def resetfunc(self, tags, lout: QGridLayout):
        self.setRange(1, (len(tags)))
        self.setSingleStep(1)
        self.setTickInterval(1)
        lout.addWidget(self, 0, 0, 1, len(tags))
        for number, tag in enumerate(tags.keys()):
            tmp = QLabel(tag)
            lout.addWidget(tmp, 1, number, 1, 1, Qt.AlignRight)
        self.setValue(number+1)
        self.setFocusPolicy(Qt.StrongFocus);
        self.setTickPosition(QSlider.TicksBothSides);


class TreeMain(QTreeView):
    def __init__(self):
        self.dict_header={}
        self.dict_data ={}
        super(TreeMain, self).__init__()
        self._datamodel = QStandardItemModel(0, 1)
        self.setModel(self._datamodel)
        self._add_widget('first', None)
        self._add_widget('first2', None)

    def _add_widget(self, name, data):
        std_item = QStandardItem('{}'.format(name))
        self._datamodel.setItem(self._datamodel.rowCount(), 0, std_item)
        node_widget = QPushButton('{}'.format(name))
        qindex_widget = self._datamodel.index(self._datamodel.rowCount(), 1, QModelIndex())
        self.setIndexWidget(qindex_widget, node_widget)


class GroupBoxAllData(QGroupBox):
    def __init__(self, title, model):
        super(GroupBoxAllData, self).__init__(title)


class TableChartBbox(QDialog):
    def __init__(self, parent=None, text='', well=None):
        import __main__
        super(TableChartBbox, self).__init__(parent)
        self.txt = text; self.well = well
        center = __main__.app.desktop().availableGeometry().center() #type: QRect
        self.screen_width = __main__.app.desktop().screenGeometry().width()
        self.screen_height = __main__.app.desktop().screenGeometry().height()

        self.setWindowFlags(self.windowFlags()| Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self.setGeometry(center.x()-200, center.y()-400, 500, 800)
        self.setStyleSheet("""color: #333; border: 1px black; background-color: white; 
        border-style: ridge; font-family: SanSerif; border-radius: 45mm;""")
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.well_simplified = QComboBox()
        self.well_simplified.setStyleSheet("""padding-left: 16px; padding-right: 16px; 
        padding-top: 2px; padding-bottom: 2px; font-family: SanSerif; alignment: center;""")

        cur_index_ = 0; nump = 0;
        for i in self.parent().Keeper.workspace.bh_read:
            if i['name'] == self.parent().dview_vidget.choosing_well['name']: cur_index_ = nump
            self.well_simplified.addItem(i['name'], userdata=i); nump += 1;

        self.fltsrtMod = Proxy()
        self.well_simplified.setCurrentIndex(cur_index_)
        self.well_simplified.currentIndexChanged.connect(self.combowell_change)
        self.filter_edits = QPushButton()
        self.filter_edits.setStyleSheet("""padding-left: 16px; padding-right: 16px; 
        padding-top: 2px; padding-bottom: 2px; font-family: SanSerif; alignment: center;""")
        self.filter_edits.setIcon(icon_load("filter_bar"))
        self.filter_edits.clicked.connect(self.clicked_on_filter)
        self.top_layout.addWidget(self.well_simplified)
        self.top_layout.addSpacing(5)
        self.top_layout.addWidget(self.filter_edits)
        self.top_layout.addStretch(5)
        self.main_layout.addItem(self.top_layout)
        self.tsswidget = NewTableView(self);
        self.tsswidget.horizontalHeader().setStretchLastSection(True)
        self.tsswidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tsswidget.setItemDelegate(MyFloatTextIntDelegat())
        self.main_layout.addWidget(self.tsswidget)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.setStyleSheet("""padding-left: 16px; padding-right: 16px; 
        padding-top: 8px; padding-bottom: 8px; font-family: SanSerif; alignment: center;""")

        self.main_layout.addWidget(self.buttons)
        self.main_layout.setStretchFactor(self.top_layout, 1)
        self.main_layout.setStretchFactor(self.tsswidget, 8)
        self.main_layout.setStretchFactor(self.buttons, 1)
        self.setLayout(self.main_layout)

        self.filter_proxy_model = QSortFilterProxyModel()
        self.well_simplified.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.fltsrtMod.addFilterFunction('test_name', lambda r, s: (s in r[0]) or (r[0] == ''))
        self.create_abstract_model()
        self.finished.connect(self.set_saves)

    #TODO: another worlds
    def create_abstract_model(self):
        global perf_tab_model, break_model, inflow_model, cem_model, re_cuts_model, events_model, bridge_model
        if self.txt == "&Перфорация":
            self.tsswidget.setItemDelegateForColumn(4, MyComboDelegat(self.tsswidget, [('True','True'),('False','False')]))
            self.fltsrtMod.setFilterString(self.well_simplified.currentText())
            self.tsswidget.setModel(self.fltsrtMod)
            self.fltsrtMod.setSourceModel(perf_tab_model)
            self.tsswidget.setSortingEnabled(True)
            self.tsswidget.resizeColumnsToContents()
            perf_tab_model.dataChanged.connect(self.fltsrtMod.invalidate)


        elif self.txt == "&Утерянное оборудование":
            #self.tsswidget.setItemDelegateForColumn(4, MyComboDelegat(self.tsswidget, [('True','True'),('False','False')]))
            self.fltsrtMod.setSourceModel(break_model)
            self.fltsrtMod.setFilterString(self.well_simplified.currentText())
            self.tsswidget.setModel(self.fltsrtMod)
            self.tsswidget.setSortingEnabled(True)
            self.tsswidget.resizeColumnsToContents()
            break_model.dataChanged.connect(self.fltsrtMod.invalidate)


        elif self.txt == "&Интервалы притока":
            self.tsswidget.setItemDelegateForColumn(4, MyComboDelegat(self.tsswidget, [('True','True'),('False','False')]))
            self.fltsrtMod.setSourceModel(inflow_model)
            self.fltsrtMod.setFilterString(self.well_simplified.currentText())
            self.tsswidget.setModel(self.fltsrtMod)
            self.tsswidget.setSortingEnabled(True)
            self.tsswidget.resizeColumnsToContents()
            inflow_model.dataChanged.connect(self.fltsrtMod.invalidate)

        elif self.txt == "&Качество Цементирования":
            self.fltsrtMod.setSourceModel(cem_model)
            self.fltsrtMod.setFilterString(self.well_simplified.currentText())
            self.tsswidget.setModel(self.fltsrtMod)
            self.tsswidget.setSortingEnabled(True)
            self.tsswidget.resizeColumnsToContents()
            cem_model.dataChanged.connect(self.fltsrtMod.invalidate)

        elif self.txt == "&Цементные мосты":
            self.fltsrtMod.setSourceModel(bridge_model)
            self.fltsrtMod.setFilterString(self.well_simplified.currentText())
            self.tsswidget.setModel(self.fltsrtMod)
            self.tsswidget.setSortingEnabled(True)
            self.tsswidget.resizeColumnsToContents()
            re_cuts_model.dataChanged.connect(self.fltsrtMod.invalidate)

        elif self.txt == "&Разрывы":
            self.fltsrtMod.setSourceModel(re_cuts_model)
            self.fltsrtMod.setFilterString(self.well_simplified.currentText())
            self.tsswidget.setModel(self.fltsrtMod)
            self.tsswidget.setSortingEnabled(True)
            self.tsswidget.resizeColumnsToContents()
            re_cuts_model.dataChanged.connect(self.fltsrtMod.invalidate)

        elif self.txt == "&События на скважинах":
            self.tsswidget.setItemDelegateForColumn(3, MyComboDelegat(self.tsswidget, dict_event_type.items()))
            self.fltsrtMod.setSourceModel(events_model)
            self.fltsrtMod.setFilterString(self.well_simplified.currentText())
            self.tsswidget.setModel(self.fltsrtMod)
            self.tsswidget.setSortingEnabled(True)
            self.tsswidget.resizeColumnsToContents()
            events_model.dataChanged.connect(self.fltsrtMod.invalidate)

    def clicked_on_filter(self):
        if self.well_simplified.isEnabled():
            self.well_simplified.setDisabled(True)
            self.fltsrtMod.removeFilterFunction('test_name')
        else:
            self.well_simplified.setEnabled(True)
            self.fltsrtMod.addFilterFunction('test_name', lambda r, s: s in r[0] or r[0]=='')
            self.fltsrtMod.setFilterString(self.well_simplified.currentText())

    def combowell_change(self):
        self.fltsrtMod.setFilterString(self.well_simplified.currentText())

    def keyPressEvent(self, event: QKeyEvent):
        if (event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier):
            self.copys()

        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.paste()

        elif event.key() == Qt.Key_Delete:
            self.clear_tab()

    def copys(self):
        clip = QApplication.clipboard()  # type: QClipboard
        clip.clear()
        selection = self.tsswidget.selectionModel().selection()  # type: QItemSelection
        if selection.size() == 0: return True
        range_ = selection[0]  # type: QItemSelectionRange
        top_left = range_.topLeft();
        start_col = top_left.column();
        start_row = top_left.row()
        bot_right = range_.bottomRight();
        end_col = bot_right.column();
        end_row = bot_right.row()

        prModel = range_.model()  # type: QProxyModel
        val = []
        end_text = '';
        for row in range(start_row, end_row + 1):  # type: QModelIndex
            for column in range(start_col, end_col + 1):
                index = prModel.index(row, column)
                end_text += str(index.data())
                if column < (end_col):
                    end_text += '\t'
                else:
                    end_text += '\n'
        clip.setText(end_text)

    def paste(self):
        clip = QApplication.clipboard()  # type: QClipboard
        txt = clip.text()
        selection = self.tsswidget.selectionModel().selection()  # type: QItemSelectionRange
        if selection.size() == 0: return True

        range_ = selection[0]  # type: QModelIndex
        top_left = range_.topLeft();
        start_col = top_left.column();
        start_row = top_left.row()
        prModel = range_.model()  # type: QProxyModel

        rows = txt.split('\n')[:-1]
        for row in range(len(rows)):  # type: QModelIndex
            cl = rows[row].split('\t')
            index = prModel.index(row + start_row, start_col)  # type: QModelIndex
            prModel.setData(index, cl)
        prModel.invalidate()

    def clear_tab(self):
        selection = self.tsswidget.selectionModel().selection()  # type: QItemSelectionRange
        if selection.size() == 0: return True
        range_ = selection[0]  # type: QModelIndex
        top_left = range_.topLeft();
        start_col = top_left.column();
        start_row = top_left.row()
        bot_right = range_.bottomRight();
        end_col = bot_right.column();
        end_row = bot_right.row()
        prModel = range_.model()  # type: QSortFilterProxyModel
        for row in range(start_row, end_row + 1):  # type: QModelIndex
            for column in range(start_col, end_col + 1):
                index = prModel.index(row, column)
                prModel.setData(index, str())
        prModel.invalidate()

    def delete_row(self):
        selection = self.tsswidget.selectionModel().selection()  # type: QItemSelectionRange
        if selection.size() == 0: return True
        range_ = selection[0]  # type: QModelIndex
        top_left = range_.topLeft()
        start_row = top_left.row()
        bot_right = range_.bottomRight()
        end_row = bot_right.row()
        prModel = range_.model()  # type: QProxyModel
        prModel.removeRows(start_row, end_row-start_row+1, QModelIndex())

    def rpres_(self):
        self.tmp_dataWi=self.tmpwidget.text()
        if len(self.tmp_dataWi) >0:
            self.frame.close()
            selection = self.tsswidget.selectionModel().selection()  # type: QItemSelectionRange
            if selection.size() == 0: return True
            range_ = selection[0]  # type: QModelIndex
            top_left = range_.topLeft();
            start_col = top_left.column();
            start_row = top_left.row()
            bot_right = range_.bottomRight();
            end_col = bot_right.column();
            end_row = bot_right.row()
            prModel = range_.model()
            for row in range(start_row, end_row + 1):  # type: QModelIndex
                for column in range(start_col, end_col + 1):
                    index = prModel.index(row, column)
                    prModel.setData(index, self.tmp_dataWi)
        else:
            self.frame.close()

    def inpaste(self):
        PixelWidthDimension = self.parent().logicalDpiX();
        PixelHeightDimesion = self.parent().logicalDpiY();
        self.rpres_true = False
        self.tmp_dataWi = str()
        self.frame = QWidget(None, Qt.FramelessWindowHint)
        self.frame.setFixedWidth(40*PixelWidthDimension/25.4);
        self.frame.setFixedHeight(14*PixelHeightDimesion/25.4);
        l = QHBoxLayout()
        ydi = QGroupBox("Enter data here...")
        self.tmpwidget = QLineEdit()
        l.addSpacing(3)
        l.addWidget(self.tmpwidget)
        l.addSpacing(3)
        ydi.setLayout(l)
        ydi.setParent(self.frame)
        #Блокируем до завершения ввода
        self.frame.setWindowModality(Qt.ApplicationModal)
        self.frame.show()
        #Если делать MapToGlobal то открывается совсем не так
        self.frame.move(self.cursor().pos())
        self.tmpwidget.returnPressed.connect(self.rpres_)

    def contextMenuEvent(self, event):
        menu = QMenu(self.tsswidget)
        cp = QAction("&Copy...", self, triggered=self.copys)
        menu.addAction(cp)

        paste_in_t = QAction("&Paste...", self, triggered=self.paste)
        menu.addAction(paste_in_t)

        cleat_cells = QAction("&Clear...", self, triggered=self.clear_tab)
        menu.addAction(cleat_cells)

        inpaste_cells = QAction("&Set data...", self, triggered=self.inpaste)
        menu.addAction(inpaste_cells)

        delete_rows = QAction("&Delete row...", self, triggered=self.delete_row)
        menu.addAction(delete_rows)
        menu.exec_(event.globalPos())

    def set_saves(self):
        type_of_ = self.fltsrtMod.sourceModel().name_type
        data = self.fltsrtMod.sourceModel().mylist
        data = sorted(data, key=lambda data: data[0])
        if len(data) == 0:
            return self.result()

        l_prev = data[0][0]
        well = None
        for well in self.parent().Keeper.workspace.bh_read:
            if str(data[0][0].strip()) == well['name']:
                well['PerfDataS'] = []
        if type_of_ == 'perf':
            for l in data:
                if l[0] != l_prev:
                    for well in self.parent().Keeper.workspace.bh_read:
                        if str(l[0].strip()) == well['name']:
                            well['PerfDataS'] = []
                            l_prev = l[0]
                            break
                    well['PerfDataS'].append({'Base': str(l[2]), 'Top': str(l[1]), 'Year': str(l[3]), \
                                              'ShowYear': str(l[4]), 'Type': str(l[5])})
                else:
                    well['PerfDataS'].append({'Base': str(l[2]), 'Top': str(l[1]), 'Year': str(l[3]), \
                                              'ShowYear': str(l[4]), 'Type': str(l[5])})

        elif type_of_ == 'breaks':
            for l in data:
                if l[0] != l_prev:
                    for well in self.parent().Keeper.workspace.bh_read:
                        if str(l[0].strip()) == well['name']:
                            well['Breaks'] = []
                            l_prev = l[0]
                            break
                    well['Breaks'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                        'Year': str(l[3]), 'Kind': str(l[4])})
                else:
                    well['Breaks'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                        'Year': str(l[3]), 'Kind': str(l[4])})

        elif type_of_ == 'inflow':
            for l in data:
                if l[0] != l_prev:
                    for well in self.parent().Keeper.workspace.bh_read:
                        if str(l[0].strip()) == well['name']:
                            well['InflowIntervals'] = []
                            l_prev = l[0]
                            break
                    well['InflowIntervals'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                                           'Year': str(l[3]), 'ShowLabelYear': str(l[4])})
                else:
                    well['InflowIntervals'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                                           'Year': str(l[3]), 'ShowLabelYear': str(l[4])})

        elif type_of_ == 'cementing':
            for l in data:
                if l[0] != l_prev:
                    for well in self.parent().Keeper.workspace.bh_read:
                        if str(l[0].strip()) == well['name']:
                            well['CementingQualityIntervals'] = []
                            l_prev = l[0]
                            break
                    well['CementingQualityIntervals'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                                                    'CementingQuality': str(l[3]), })
                else:
                    well['CementingQualityIntervals'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                                                    'CementingQuality': str(l[3]), })

        elif type_of_ == 'cuts':
            for l in data:
                if l[0] != l_prev:
                    for well in self.parent().Keeper.workspace.bh_read:
                        if str(l[0].strip()) == well['name']:
                            well['Cuts'] = []
                            l_prev = l[0]
                            break
                    well['Cuts'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                                                              'thikness': str(l[3]), })
                else:
                    well['Cuts'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                                                              'thikness': str(l[3]), })
        elif type_of_ == 'cem_bridges':
            for l in data:
                if l[0] != l_prev:
                    for well in self.parent().Keeper.workspace.bh_read:
                        if str(l[0].strip()) == well['name']:
                            well['CementBridges'] = []
                            l_prev = l[0]
                            break
                    well['CementBridges'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                                         'thikness': str(l[3]), })
                else:
                    well['CementBridges'].append({'Bottom': str(l[2]), 'Top': str(l[1]), \
                                         'thikness': str(l[3]), })

        elif type_of_ == 'events_ands_names':
            pass
        return self.result()

class MyTableModel(QAbstractTableModel):
    def __init__(self, parent, mylist, header, name, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.name_type = name
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)+1

    def columnCount(self, parent):
        if len(self.header) > 0:
            return len(self.header)
        else:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        elif index.row() >= len(self.mylist):
            return ''
        return self.mylist[index.row()][index.column()]

    def row(self, index):
        if index >= len(self.mylist):
            return ['' for i in range(self.columnCount(None))]
        else:
            return self.mylist[index]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        elif orientation == Qt.Horizontal and role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def addData(self, data):
        self.mylist.append(data)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def insertRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        num_columns = self.columnCount(index)
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self.endInsertRows()
        return True

    def insertRow(self, row, index):
        if index.isValid():
            return False
        num_columns = self.columnCount(index)
        self.beginInsertRows(QModelIndex(), row, row)
        self.endInsertRows()

    def removeRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        self.beginRemoveRows(QModelIndex(), row, row+count-1)
        self.endRemoveRows()
        num_rows = self.rowCount(QModelIndex())
        for i in range(count, 0, -1):
            self.mylist.pop(i+row-1)
        return True

    def setData(self, index, value, role=Qt.EditRole):
        #TODO: сперва добавляем данные, потом иницируем begininsertRows(один раз)
        if not index.isValid():
            return False
        elif role == Qt.EditRole:
            row = index.row()
            column = index.column()
            if row >= len(self.mylist):
                if column >= len(self.header):
                    return False
                if type(value) == str:
                    self.beginInsertRows(QModelIndex(), index.row(), index.row())
                    self.endInsertRows()
                    self.mylist.append(['']*self.columnCount(QModelIndex()))
                    self.mylist[row][column] = value
                    self.dataChanged.emit(index, index)
                    return True
                else:
                    self.beginInsertRows(QModelIndex(), index.row(), index.row())
                    self.endInsertRows()
                    if len(self.mylist) <= row:
                        self.mylist.append(['']*self.columnCount(QModelIndex()))
                    for v in value:
                        self.mylist[row][column] = v
                        column += 1
                    self.dataChanged.emit(index, index)
            else:
                if column >= len(self.header):
                    return False
                if type(value) == str:
                    self.mylist[row][column] = value
                    self.dataChanged.emit(index, index)
                    return True
                else:
                    for v in value:
                        column = index.column()
                        if len(self.mylist) <= row:
                            self.beginInsertRows(QModelIndex(), index.row(), index.row())
                            self.endInsertRows()
                            self.mylist.append([''] * self.columnCount(QModelIndex()))
                        for v in value:
                            if len(self.mylist[row]) < column:
                                break
                            self.mylist[row][column] = v
                            column += 1
                        self.dataChanged.emit(index, index)
                        column += 1
            column = index.column()
            return True
        return False


class Proxy(QSortFilterProxyModel):
    """
    Implements a QSortFilterProxyModel that allows for custom
    filtering. Add new filter functions using addFilterFunction().
    New functions should accept two arguments, the column to be
    filtered and the currently set filter string, and should
    return True to accept the row, False otherwise.
    Filter functions are stored in a dictionary for easy
    removal by key. Use the addFilterFunction() and
    removeFilterFunction() methods for access.
    The filterString is used as the main pattern matching
    string for filter functions. This could easily be expanded
    to handle regular expressions if needed.
    """

    def __init__(self, parent=None):
        super(Proxy, self).__init__(parent)
        self.filterString = ''
        self.filterFunctions = {}

    def setFilterString(self, text):
        """
        text : string
            The string to be used for pattern matching.
        """
        self.filterString = text.lower()
        self.invalidateFilter()

    def addFilterFunction(self, name, new_func):
        """
        name : hashable object
            The object to be used as the key for
            this filter function. Use this object
            to remove the filter function in the future.
            Typically this is a self descriptive string.
        new_func : function
            A new function which must take two argument s,
            the row to be tested and the ProxyModel's current
            filterString. The function should return True if
            the filter accepts the row, False otherwise.
            ex:
            model.addFilterFunction(
                'test_columns_1_and_2',
                lambda r,s: (s in r[1] and s in r[2]))
        """
        self.filterFunctions[name] = new_func
        self.invalidateFilter()


    def removeFilterFunction(self, name):
        """
        name : hashable object

        Removes the filter function associated with name,
        if it exists.
        """
        if name in self.filterFunctions.keys():
            del self.filterFunctions[name]
            self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        """
        Reimplemented from base class to allow the use
        of custom filtering.
        """
        model = self.sourceModel()
        # The source model should have a method called row()
        # which returns the table row as a python list.
        tests = [func(model.row(row), self.filterString)
                 for func in self.filterFunctions.values()]
        return not False in tests


class MyFloatTextIntDelegat(QItemDelegate):

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        self.lite = False
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        if (value != ''):
            editor.setText(value)
        editor.returnPressed.connect(self.setDataAnyWay)

    def setModelData(self, editor, model, index):
        value = editor.text()
        if (value != '' or self.lite):
            model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def setDataAnyWay(self):
        self.lite = True


class MyComboDelegat(QItemDelegate):

    def __init__(self, parent, value_data):
        "Value_data is a list of tuples: (item, label)"
        QItemDelegate.__init__(self, parent)
        self.value_data = value_data

    @property
    def items(self):
        "The list of items for display"
        return [item[0] for item in self.value_data]

    @property
    def labels(self):
        "The list of labels for display"
        return [item[1] for item in self.value_data]

    def item(self, label):
        "Get the item from a label"
        try:
            index = self.labels.index(label)
        except ValueError:
            return ''
        return self.items[index]

    def createEditor(self, parent, option, index):
        "Create the editor (called each time)"

        combo = QComboBox(parent)
        for duplet in self.value_data:
            item, label = duplet
            combo.addItem(label)
        return combo

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        editor.setCurrentIndex(index.row())
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        "This is the data stored into the field"
        model.setData(index, self.item(editor.currentText()))


class NewTableView(QTableView):
    def __init__(self, parent=None):
        super(NewTableView, self).__init__(parent)

    def resizeRowToContents(self, *args, **kwargs):
        smodel = self.selectionModel() #type: QItemSelectionModel
        sed = smodel.selectedRows()
        for i in range(sed.size()):
            super().resizeRowToContents(sed[i].row())
        #короче это не та функция, она за размер ячеек отвечает


class SettingWindow(QDialog):
    def __init__(self, parent=None):
        import __main__
        super(SettingWindow, self).__init__(parent)
        center = __main__.app.desktop().availableGeometry().center()
        self.screen_width = __main__.app.desktop().screenGeometry().width()
        self.screen_height = __main__.app.desktop().screenGeometry().height()
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setGeometry(center.x() - 200, center.y() - 400, 500, 800)
        self.setStyleSheet("""color: #333; border: 1px black; background-color: white; 
        border-style: ridge; font-family: SanSerif; border-radius: 45mm;""")
        self.main_layout = QVBoxLayout(self)
        self.top_layout = QHBoxLayout()
        self.setWindowTitle("Настройки")
        self.sets = self.parent().Keeper.workspace.settings
        self.mainTabWidget = QTabWidget()
        self.firstTab = QWidget()
        self.firstTab.setStyleSheet("QLabel {border: 0px}")
        self.mainTabWidget.addTab(self.firstTab, "Основные настройки")

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.setStyleSheet("""padding-left: 16px; padding-right: 16px; 
        padding-top: 8px; padding-bottom: 8px; font-family: SanSerif; alignment: center;""")
        self.main_layout.addWidget(self.mainTabWidget)
        self.main_layout.addWidget(self.buttons)
        self.create_first_tab()

    def create_first_tab(self):
        cl = QFormLayout()
        self.title = QLineEdit()
        self.title.setObjectName('Title')
        self.title.setText(self.sets['Title'])
        self.title.editingFinished.connect(self.change_sets_common)
        self.wl_distance = QLineEdit()
        self.wl_distance.setText(self.sets['BetweenWellDistance'])
        self.wl_distance.setObjectName('BetweenWellDistance')
        self.wl_distance.editingFinished.connect(self.change_sets_common)
        self.scale = QLineEdit()
        self.scale.setText(self.sets['VerticalScale'])
        self.scale.setObjectName('VerticalScale')
        self.scale.editingFinished.connect(self.change_sets_common)

        cl.addRow("Имя разреза                ", self.title)
        cl.addRow("Дистанция между скважинами ", self.wl_distance)
        cl.addRow("Вертикальный масштаб       ", self.scale)
        self.firstTab.setLayout(cl)
        # self.name_ = QLineEdit(); self.name_.setText(ct_t['name']);
        # self.name_.editingFinished.connect(self.change_sets_common)

    def data_changes(self):
        pass

    def change_sets_common(self):
        self.sets[self.sender().objectName()] = self.sender().text()