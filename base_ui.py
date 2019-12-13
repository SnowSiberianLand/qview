# -*- coding: cp1251 -*-
from PySide.QtGui import *
from PySide.QtCore import *
from ui_utils import icon_load
from xml.dom import minidom
from xml.etree.ElementTree import *
import logging
import __main__


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = parent

    def emit(self, record):
        msg = self.format(record)


class BaseDialog(QDialog):

    def __init__(self, parent=None):
        center = __main__.app.desktop().availableGeometry().center() #type: QRect
        self.screen_width = __main__.app.desktop().screenGeometry().width()
        self.screen_height = __main__.app.desktop().screenGeometry().height()
        super(BaseDialog, self).__init__(parent)
        self.setWindowIcon(icon_load('link-72'))
        self.m_mouse_down = False
        self.setWindowTitle('Choose object for analize ...')
        self.setStyleSheet("""color: #333; border: 1px solid black; background-color: white;
        border-style: ridge; font-family: SanSerif; border-radius: 45mm;""")

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(center.x()-200, center.y()-200, 300, 400)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.setStyleSheet("""padding-left: 16px; padding-right: 16px; 
        padding-top: 8px; padding-bottom: 8px; font-family: SanSerif; alignment: left;""")

    def mousePressEvent(self, QMouseEvent):
        self.mouse_old = QMouseEvent.pos()
        self.m_mouse_down = (QMouseEvent.button() == Qt.LeftButton)

    def releaseMouse(self, QMouseEvent):
        self.m_right_button_pressed = (QMouseEvent.button() == Qt.RightButton)

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_mouse_down = False

    def mouseMoveEvent(self, QMouseEvent):
        if self.m_mouse_down:
            x = QMouseEvent.x()
            y = QMouseEvent.y()

            rect = self.geometry()
            left = (abs(x - rect.left()) >= 5)
            right = (abs(x - rect.right()) >= 5)
            bottom = (abs(y - rect.bottom()) >= 5)

            if self.m_mouse_down:
                dx = x - self.mouse_old.x()
                dy = y - self.mouse_old.y()

            if (left or right):
                rect.setLeft(rect.left() + dx)
                rect.setRight(rect.right() + dx)

            if (bottom):
                rect.setBottom(rect.bottom() + dy)
                rect.setTop(rect.top()+dy)

            self.setGeometry(rect)
            self.updateGeometry()


class openFileDialog(QFileDialog):

    def __init__(self):
        super(openFileDialog, self).__init__()
        self.FileName = None
        self.m_mouse_down = False
        self.options = self.Options()
        self.options |= QFileDialog.DontUseNativeDialog
        self.options |= QFileDialog.DontResolveSymlinks
        self.setWindowTitle("Choose file or rds data >>>")
        self.setWindowFlags(Qt.FramelessWindowHint)
        aa = self.findChild(QSplitter, "splitter")
        if aa is not None:
            bb = aa.children()[1]
            if bb is not None:
                bb.hide()
        self.setStyleSheet("QFileDialog {color: black; border: 0.5px groove black; background-color: white; \
                            border-style: groove; font-family: SanSerif; padding: 6px;}"
                           "QWidget {font-family: SanSerif}")
        self.setWindowIcon(icon_load('link-72'))

    def mousePressEvent(self, QMouseEvent):
        self.mouse_old = QMouseEvent.pos()
        self.m_mouse_down = (QMouseEvent.button() == Qt.LeftButton)

    def releaseMouse(self, QMouseEvent):
        self.m_right_button_pressed = (QMouseEvent.button() == Qt.RightButton)

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_mouse_down = False

    def mouseMoveEvent(self, QMouseEvent):
        if self.m_mouse_down:
            x = QMouseEvent.x()
            y = QMouseEvent.y()

            rect = self.geometry()
            left = (abs(x - rect.left()) >= 5)
            right = (abs(x - rect.right()) >= 5)
            bottom = (abs(y - rect.bottom()) >= 5)

            if self.m_mouse_down:
                dx = x - self.mouse_old.x()
                dy = y - self.mouse_old.y()

            if (left or right):
                rect.setLeft(rect.left() + dx)
                rect.setRight(rect.right() + dx)

            if (bottom):
                rect.setBottom(rect.bottom() + dy)
                rect.setTop(rect.top()+dy)

            self.setGeometry(rect)
            self.updateGeometry()

    def save_strings(self):
        fl = QSettings("settings/def_value.conf", QSettings.IniFormat)
        fl.setValue("rds_string/user", self.nameLineEdit.text())
        fl.setValue("rds_string/pass", self.passline.text())
        fl.setValue("rds_string/server", self.server_line.text())
        fl.setValue("meta_string/user", self.nameMeta.text())
        fl.setValue("meta_string/pass", self.passMeta.text())
        fl.setValue("meta_string/server", self.serverMeta.text())


class BaseProgram(QMainWindow):

    def __init__(self):
        super(BaseProgram, self).__init__()
        style_string = "QMainWindow {color: black; border: 0.5px groove black; background-color: white; \
                        border-style: groove; font-family: SanSerif; padding: 5px;} " \
                        "QToolBar {border-style: none}"
                       #"QStatusBar {color: black; background: white; font-family: SanSerif; padding: 6px;}"

        self.setWindowIcon(icon_load('diamond'))
        self.screen_width = __main__.app.desktop().screenGeometry().width()
        self.screen_height = __main__.app.desktop().screenGeometry().height()
        self.setGeometry(self.screen_width/2-300, self.screen_height/2-300, 900, 900)
        self.setStyleSheet(style_string)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        console_log_widget = QWidget()
        self.delimiter_bar = QPlainTextEditLogger(console_log_widget)
        self.delimiter_bar.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.delimiter_bar)
        logging.getLogger().setLevel(logging.DEBUG)

        self.toolbar = QToolBar(self)
        self.toolbar.setAutoFillBackground(True)
        self.addToolBar(self.toolbar)


class FormConnection(QDialog):

    def __init__(self):
        super(FormConnection, self).__init__()
        center = __main__.app.desktop().availableGeometry().center() #type: QRect
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("QWidget {border: 1px groove grey; padding-left: 6px; padding-right: 6px; padding-top: 2px;"
                           "padding-bottom: 2px; margin: 4px; font-family: SanSerif}"
                           "QDialogButton {background: white; padding: 6px; margin: 2px;}"
                           "QDialog {background: white; color: black}"
                           "QLineEdit {font-family: SanSerif}"
                           "QCheckBox {border: none; padding: 6px; margin: 0px}")
        fl = QSettings("settings/def_value.conf", QSettings.IniFormat)
        self.setGeometry(center.x()-100, center.y()-100, 300, 200)
        tmp_layer = QHBoxLayout()
        tmp_layer.setAlignment(Qt.AlignLeft)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.save_connection = QCheckBox(self)
        self.save_connection.setText("Save connection")
        self.save_connection.setCheckState(Qt.Unchecked)
        self.spacer = QSpacerItem(0,self.width()/2, QSizePolicy.Expanding, QSizePolicy.Expanding)

        tmp_layer.addWidget(self.save_connection)
        tmp_layer.addSpacerItem(self.spacer)
        tmp_layer.addWidget(self.buttons)

        self.formLayout = QFormLayout(self)
        self.nameLineEdit = QLineEdit(); self.nameLineEdit.setText(fl.value("rds_string/user"))
        self.passline = QLineEdit(); self.passline.setText(fl.value("rds_string/pass"))
        self.server_line = QLineEdit(); self.server_line.setText(fl.value("rds_string/server"))
        title = QLabel("Enter oracle connection properties ...")
        title.setStyleSheet("""border: none; font-family: SanSerif; font-size: 14px; font-weight: bold;""")

        self.formLayout.addRow(title)
        self.formLayout.addRow("&Name:      ", self.nameLineEdit)
        self.formLayout.addRow("&Password:", self.passline)
        self.formLayout.addRow("&Server:     ", self.server_line)


        self.nameMeta = QLineEdit(); self.nameMeta.setText(fl.value("meta_string/user"))
        self.passMeta = QLineEdit(); self.passMeta.setText(fl.value("meta_string/pass"))
        self.serverMeta = QLineEdit(); self.serverMeta.setText(fl.value("meta_string/server"))
        self.formLayout.addRow("&Name meta:  ", self.nameMeta)
        self.formLayout.addRow("&Password:   ", self.passMeta)
        self.formLayout.addRow("&Server meta:", self.serverMeta)

        self.formLayout.addRow(tmp_layer)
        self.setLayout(self.formLayout)
        self.exec_()

        if self.result() == QDialog.Accepted:
            if self.save_connection.checkState() == Qt.Checked:
                self.save_strings()


    def getString(self):
        if self.nameMeta.text() == "":
            return ('{0}/{1}@{2}'.format(self.nameLineEdit.text(), self.passline.text(), self.server_line.text()), \
                    '{0}/{1}@{2}'.format(self.nameLineEdit.text(), self.passline.text(), self.server_line.text()))
        else:
            return ('{0}/{1}@{2}'.format(self.nameLineEdit.text(), self.passline.text(), self.server_line.text()), \
                    '{0}/{1}@{2}'.format(self.nameMeta.text(), self.passMeta.text(), self.serverMeta.text()))

    def mousePressEvent(self, QMouseEvent):
        self.mouse_old = QMouseEvent.pos()
        self.m_mouse_down = (QMouseEvent.button() == Qt.LeftButton)

    def releaseMouse(self, QMouseEvent):
        self.m_right_button_pressed = (QMouseEvent.button() == Qt.RightButton)

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_mouse_down = False

    def mouseMoveEvent(self, QMouseEvent):
        if self.m_mouse_down:
            x = QMouseEvent.x()
            y = QMouseEvent.y()

            rect = self.geometry()
            left = (abs(x - rect.left()) >= 5)
            right = (abs(x - rect.right()) >= 5)
            bottom = (abs(y - rect.bottom()) >= 5)

            if self.m_mouse_down:
                dx = x - self.mouse_old.x()
                dy = y - self.mouse_old.y()

            if (left or right):
                rect.setLeft(rect.left() + dx)
                rect.setRight(rect.right() + dx)

            if (bottom):
                rect.setBottom(rect.bottom() + dy)
                rect.setTop(rect.top()+dy)

            self.setGeometry(rect)
            self.updateGeometry()

    def save_strings(self):
        fl = QSettings("settings/def_value.conf", QSettings.IniFormat)
        fl.setValue("rds_string/user", self.nameLineEdit.text())
        fl.setValue("rds_string/pass", self.passline.text())
        fl.setValue("rds_string/server", self.server_line.text())
        fl.setValue("meta_string/user", self.nameMeta.text())
        fl.setValue("meta_string/pass", self.passMeta.text())
        fl.setValue("meta_string/server", self.serverMeta.text())


class tagForm(QDialog):

    def __init__(self, mainApp):
        super(tagForm, self).__init__()
        self.parentApp = mainApp
        center = __main__.app.desktop().availableGeometry().center() #type: QRect
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("QWidget {border: 1px groove grey; padding-left: 6px; padding-right: 6px; padding-top: 2px;"
                           "padding-bottom: 2px; margin: 4px; font-family: SanSerif}"
                           "QDialogButton {background: white; padding: 6px; margin: 2px;}"
                           "QDialog {background: white; color: black}"
                           "QLineEdit {font-family: SanSerif}"
                           "QCheckBox {border: none; padding: 6px; margin: 0px}")
        fl = QSettings("settings/def_value.conf", QSettings.IniFormat)
        self.setGeometry(center.x()-75, center.y()-50, 200, 100)
        tmp_layer = QHBoxLayout()
        tmp_layer.setAlignment(Qt.AlignRight)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.spacer = QSpacerItem(0,self.width()/2, QSizePolicy.Expanding, QSizePolicy.Expanding)

        tmp_layer.addSpacerItem(self.spacer)
        tmp_layer.addWidget(self.buttons)

        self.formLayout = QFormLayout(self)
        self.nameLineEdit = QLineEdit(); self.nameLineEdit.setText("Work")
        self.nameLineEdit.setAlignment(Qt.AlignCenter)

        title = QLabel("Enter tag name...")
        title.setStyleSheet("""border: none; font-family: SanSerif; font-size: 14px; font-weight: bold;""")

        self.formLayout.addRow(title)
        self.formLayout.addRow(self.nameLineEdit)

        self.formLayout.addRow(tmp_layer)
        self.setLayout(self.formLayout)
        self.exec_()

        if self.result() == QDialog.Accepted:
            self.save_strings()

    def mousePressEvent(self, QMouseEvent):
        self.mouse_old = QMouseEvent.pos()
        self.m_mouse_down = (QMouseEvent.button() == Qt.LeftButton)
        
    def releaseMouse(self, QMouseEvent):
        self.m_right_button_pressed = (QMouseEvent.button() == Qt.RightButton)

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_mouse_down = False

    def mouseMoveEvent(self, QMouseEvent):
        if self.m_mouse_down:
            x = QMouseEvent.x()
            y = QMouseEvent.y()

            rect = self.geometry()
            left = (abs(x - rect.left()) >= 5)
            right = (abs(x - rect.right()) >= 5)
            bottom = (abs(y - rect.bottom()) >= 5)

            if self.m_mouse_down:
                dx = x - self.mouse_old.x()
                dy = y - self.mouse_old.y()

            if (left or right):
                rect.setLeft(rect.left() + dx)
                rect.setRight(rect.right() + dx)

            if (bottom):
                rect.setBottom(rect.bottom() + dy)
                rect.setTop(rect.top()+dy)

            self.setGeometry(rect)
            self.updateGeometry()

    def save_strings(self):
        self.parentApp.Keeper.tag_name = self.nameLineEdit.text()
        fl = self.parentApp.Keeper.workspace.write_well(self.nameLineEdit.text())
        self.parentApp.Keeper.file_xml = '\n'.join([line for line in minidom.parseString(tostring(self.parentApp.Keeper.workspace.root))\
                                                   .toprettyxml(indent=' ' * 2).split('\n') if line.strip()])
