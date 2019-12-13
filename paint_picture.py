from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtSvg import *
import math

class PenFor(QPen):
    def __init__(self):
        super(PenFor, self).__init__()
        self.setStyle(Qt.SolidLine)
        self.setColor(QColor("Blue"))
        self.setWidth(4)


class WellSvg(QSvgGenerator):
    def __init__(self):
        super(WellSvg, self).__init__()


class Mscenes(QGraphicsScene):
    def __init__(self, ConKeeper, parent=None):
        super(Mscenes, self).__init__(parent)
        settings = ConKeeper.workspace.settings
        self.count_well = len(ConKeeper.workspace.bh_read)
        self.rightSpace = int(settings['FirstAndEndWellDistance'])
        self.betweenwell = int(settings['BetweenWellDistance'])
        self.count_scene = self.betweenwell*self.count_well
        self.minimalMD = float(settings["Minimal_width"])
        self.maximalMD = float(settings["Maximal_width"])
        self.addItem(Line())
        self.setSceneRect(QRectF(-700, -100, self.count_scene, 80 + self.maximalMD-self.minimalMD))

    def reinit(self, ConKeeper):
        settings = ConKeeper.workspace.settings
        self.count_well = len(ConKeeper.workspace.bh_read)
        self.rightSpace = int(settings['FirstAndEndWellDistance'])
        self.betweenwell = int(settings['BetweenWellDistance'])
        self.count_scene = self.betweenwell*self.count_well
        self.minimalMD = float(settings["Minimal_width"])
        self.maximalMD = float(settings["Maximal_width"])
        self.setSceneRect(QRectF(0, self.minimalMD-40, self.count_scene, 80 + self.maximalMD-self.minimalMD))
        index = 0
        # for well in ConKeeper.workspace.bh_read:
        #     gr_item = SimpleWell(settings, well, index)
        #     self.addItem(gr_item)
        #     index += 1
        self.sceneRectChanged().connect(self.change_scene_rect)

    def change_scene_rect(self):
        self.update()
        self.setSceneRect(QRectF(0, -100, self.count_scene, 80 + self.maximalMD - self.minimalMD))


class Cartoon(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super(Cartoon, self).__init__()
        self.setScene(scene)
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        item = Line()
        self.scene().addItem(item)
        self.fitInView(item)
        self.invalidateScene()

    def show_when_load(self):
        self.show()

    def flsScrenReload(self):
        for item in self.scene().items():
            self.fitInView(item)


class SimpleWell(QGraphicsItem):
    def __init__(self, settings, WellObject, index):
        super(SimpleWell, self).__init__()
        settings = ConKeeper.workspace.settings
        self.count_well = len(ConKeeper.workspace.bh_read)
        self.rightSpace = int(settings['FirstAndEndWellDistance'])
        self.betweenwell = int(settings['BetweenWellDistance'])
        self.count_scene = self.betweenwell*self.count_well
        self.minimalMD = float(settings["Minimal_width"])
        self.maximalMD = float(settings["Maximal_width"])

        if index==0:
            self.setX(self.rightSpace)
            self.setY(self.minimalMd)
        else:
            self.setX(self.betweenwell*index)
            self.setY(self.minimalMd)

    def boundingRect(self, *args, **kwargs):
        return QRectF(self.rightSpace, -100, self.betweenwell*2, 1600)

    def paint(self, painter, option, widget=None):
        painter.drawLine(0, 0, self.minimalMd, self.maximalMd)


class Line(QGraphicsItem):
    def __init__(self, parent=None):
        super(Line, self).__init__(parent)

    def boundingRect(self, *args, **kwargs):
        return QRectF(50, 50, 400, 600)

    def paint(self,  painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        painter.setPen(PenFor())
        polygon_line = QPolygonF()
        for point in (QPointF(10, 10), QPointF(300, 300), QPointF(0, 600)):
            polygon_line.append(point)
        painter.drawPolygon(polygon_line)


class TesTCoordinateSupport(QGraphicsView):
    def __init__(self, parent=None):
        super(TesTCoordinateSupport, self).__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.settings = self.parent().Keeper.workspace.settings
        par = int(self.settings['FirstAndEndWellDistance'])
        scene_count = float(self.settings["WellCount"])*int(self.settings["BetweenWellDistance"])+par*2
        self.scene.setSceneRect(QRect(0, int(self.settings["Minimal_width"]), scene_count, \
                                      int(self.settings["Maximal_width"])-int(self.settings["Minimal_width"])))
        self.scene.setObjectName("GraphicalScene")
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setInteractive(True)
        self.scene.addItem(QGraphicsSvgItem("rsicon/well.svg"))
        self.central_point = self.scene.sceneRect().center()

    def wheelEvent(self, event):
        zoomInFactor = 1.12
        zoomOutFactor = 1 / zoomInFactor
        oldPos = self.mapToScene(event.pos())
        if event.delta() > 0:
            zoomFactor = zoomInFactor;
        else:
            zoomFactor = zoomOutFactor;
        self.scale(zoomFactor, zoomFactor)
        dn = self.mapFromScene(oldPos)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.translate(dn.x(), dn.y())

    def dragMoveEvent(self, event):
        oldPos = self.mapToScene(event.pos)
        self.centerOn(oldPos.x(), oldPos.y())

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        else:
            QGraphicsView.keyPressEvent(self, event)

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))

    def drawBackground(self, painter, rect):
        textRect = QRect(0, self.scene.sceneRect().top(), self.scene.sceneRect().right(), 50)
        message = self.tr(self.settings['Title'])
        font = painter.font()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(Qt.black)
        painter.drawRect(textRect)
        painter.drawText(textRect, Qt.AlignCenter, message)


class Well(QGraphicsSvgItem):
    def __init__(self, svg_file):
        super(Well, self).__init__(svg_file)

    def setPosition(self, x_position, y_position):
        self.setX(x_position)
        self.setY(y_position)