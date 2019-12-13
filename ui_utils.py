from PySide.QtSvg import *
from PySide.QtGui import *


def icon_load(name):
    svg_renderer = QSvgRenderer('rsicon/{0}.svg'.format(name))
    image = QImage(64, 64, QImage.Format_ARGB32)
    image.fill(0x00000000)
    svg_renderer.render(QPainter(image))
    return QPixmap.fromImage(image)