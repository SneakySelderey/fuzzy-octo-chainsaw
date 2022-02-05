import os
import sys
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from settings import *


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('system_files/main.ui', self)
        self.setWindowTitle('Отображение карты')
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon('system_files/icon.png'))
        self.map_file = None
        self.map_size = 650, 450
        self.spn = 0.001
        self.ll = [37.530887, 55.703118]
        self.radio = [self.l_map, self.sat_map, self.hybrid_map]
        [i.clicked.connect(self.changeMap) for i in self.radio]
        self.l_map.setChecked(True)
        self.map_type = 'map'
        self.prev_coords = [self.ll[0], self.ll[1]]
        self.getImage()

    def changeMap(self):
        """Изменение типа карты"""
        parent = self.sender()
        old_map = self.map_type
        self.map_type = 'map' if parent == self.l_map else 'sat' if \
            parent == self.sat_map else 'sat,skl'
        self.getImage() if old_map != self.map_type else None

    def getImage(self):
        """Функция получения изображения по параметрам"""
        parameters = {'ll': ','.join(map(str, self.ll)), 'l': self.map_type,
                      'size': ','.join(map(str, self.map_size)),
                      'spn': f'{self.spn},{self.spn}'}
        response = requests.get(static_api_server, params=parameters)

        if not response:
            if self.ll[0] > 179.9999:
                self.ll[0] = -179.9999 + self.spn * 3.49
                parameters['ll'] = ','.join(map(str, self.ll))
                response = requests.get(static_api_server, params=parameters)
            elif self.ll[0] < -179.9999:
                self.ll[0] = 179.9999 - self.spn * 3.49
                parameters['ll'] = ','.join(map(str, self.ll))
                response = requests.get(static_api_server, params=parameters)
            else:
                self.ll = [self.prev_coords[0], self.prev_coords[1]]
                parameters['ll'] = ','.join(map(str, self.ll))
                response = requests.get(static_api_server, params=parameters)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.picture.setPixmap(QPixmap(self.map_file))

    def closeEvent(self, event):
        """При закрытии формы удаляем файл с изображением"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        """Обрабокта нажатий клавиш клавиатуры"""
        self.prev_coords = [self.ll[0], self.ll[1]]
        if event.key() == Qt.Key_PageUp:
            self.spn = max(self.spn / 2, 0.001)
        if event.key() == Qt.Key_PageDown:
            self.spn = min(self.spn * 2, 32.768)
        if event.key() == Qt.Key_S or event.key() == Qt.Key_Down:
            self.ll[1] -= self.spn * 1.43
        if event.key() == Qt.Key_W or event.key() == Qt.Key_Up:
            self.ll[1] += self.spn * 1.43
        if event.key() == Qt.Key_A or event.key() == Qt.Key_Left:
            self.ll[0] -= self.spn * 3.49
        if event.key() == Qt.Key_D or event.key() == Qt.Key_Right:
            self.ll[0] += self.spn * 3.49
        self.getImage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())