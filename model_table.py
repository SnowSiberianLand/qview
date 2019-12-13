from PySide.QtGui import *
from PySide.QtCore import *
from ui_utils import icon_load


class GroupDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(GroupDelegate, self).__init__(parent)
        self._plus_icon = QIcon("rsicon/plus.png")
        self._minus_icon = icon_load("minus")

    def initStyleOption(self, option, index):
        super(GroupDelegate, self).initStyleOption(option, index)
        if not index.parent().isValid():
            is_open = bool(option.state & QStyle.State_Open)
            option.icon = self._minus_icon if is_open else self._plus_icon

class GroupView(QTreeView):
    def __init__(self, model, parent=None):
        super(GroupView, self).__init__(parent)
        self.setIndentation(0)
        self.setExpandsOnDoubleClick(False)
        self.clicked.connect(self.on_clicked)
        delegate = GroupDelegate(self)
        self.setItemDelegateForColumn(0, delegate)
        self.setModel(model)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setStyleSheet("background-color: white;font-family: SanSerif; alignment: center")

    @Slot(QModelIndex)
    def on_clicked(self, index):
        if not index.parent().isValid() and index.column() == 0:
            self.setExpanded(index, not self.isExpanded(index))


class GroupModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(GroupModel, self).__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["", "Data Category"])
        for i in range(self.columnCount()):
            it = self.horizontalHeaderItem(i)
            it.setForeground(QColor("black"))


    def add_group(self, group_name):
        item_root = QStandardItem()
        item_root.setIcon(QIcon('rsicon/plus.png'))
        item_root.setTextAlignment(Qt.AlignCenter)
        item_root.setEditable(False)
        item = QStandardItem(group_name)
        item.setEditable(False)
        ii = self.invisibleRootItem()
        i = ii.rowCount()
        for j, it in enumerate((item_root, item)):
            ii.setChild(i, j, it)
            ii.setEditable(True)
        for j in range(self.columnCount()):
            it = ii.child(i, j)
            if it is None:
                it = QStandardItem()
                ii.setChild(i, j, it)
            it.setBackground(QColor("white"))
            it.setForeground(QColor("black"))
        return item_root

    def append_element_to_group(self, group_item, texts):
        j = group_item.rowCount()
        item_icon = QStandardItem()
        item_icon.setEditable(False)
        item_icon.setBackground(QColor("white"))
        group_item.setChild(j, 0, item_icon)
        for i, text in enumerate(texts):
            item = QStandardItem(text)
            item.setEditable(True)
            item.setBackground(QColor("white"))
            item.setForeground(QColor("black"))
            group_item.setChild(j, i+1, item)
