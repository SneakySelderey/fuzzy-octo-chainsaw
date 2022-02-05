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
        self.setWindowIcon(QIcon('system_files/icon.png'))
        self.map_file = None
        self.map_size = 650, 450
        self.spn = 0.002
        self.z = 15
        self.ll = 37.530887, 55.703118
        self.radio = [self.l_map, self.sat_map, self.hybrid_map]
        [i.clicked.connect(self.changeMap) for i in self.radio]
        self.l_map.setChecked(True)
        self.map_type = 'map'
        self.coords = '37.530887,55.703118'
        self.prev_coords = self.coords
        self.spn = '0.002,0.002'
        self.getImage()

    def changeMap(self):
        """Изменение типа карты"""
        parent = self.sender()
        old_map = self.map_type
        self.map_type = 'map' if parent == self.l_map else 'sat' if \
            parent == self.sat_map else 'sat,skl'
        self.getImage() if old_map != self.map_type else None

    def keyPressEvent(self, event):
        """Обрабокта нажатий клавиш клавиатуры"""
        if event.key() == Qt.Key_PageUp:
            self.z = min(19, self.z + 1)
        elif event.key() == Qt.Key_PageDown:
            self.z = max(0, self.z - 1)
        self.getImage()

    def getImage(self):
        """Функция получения изображения по параметрам"""
        parameters = {'ll': ','.join(map(str, self.ll)), 'l': self.map_type,
                      'size': ','.join(map(str, self.map_size)), 'z': self.z}
        response = requests.get(static_api_server, params=parameters)

        if not response:
            if float(self.coords.split(',')[0]) > 179.9999:
                self.coords = f"-179.9999,{self.coords.split(',')[1]}"
                map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.coords}&spn={self.spn}&l=map"
                response = requests.get(map_request)
            elif float(self.coords.split(',')[0]) < -179.9999:
                self.coords = f"179.9999,{self.coords.split(',')[1]}"
                map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.coords}&spn={self.spn}&l=map"
                response = requests.get(map_request)
            else:
                self.coords = self.prev_coords
                map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.coords}&spn={self.spn}&l=map"
                response = requests.get(map_request)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.picture.setPixmap(QPixmap(self.map_file))

    def closeEvent(self, event):
        """При закрытии формы удаляем файл с изображением"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        self.prev_coords = self.coords
        if event.key() == Qt.Key_S or event.key() == Qt.Key_Down:
            coords = list(map(float, self.coords.split(',')))
            coords[1] = coords[1] - (list(map(float, self.spn.split(',')))[1] * 1.4)
            self.coords = ','.join(list(map(str, coords)))

        if event.key() == Qt.Key_W or event.key() == Qt.Key_Up:
            coords = list(map(float, self.coords.split(',')))
            coords[1] = coords[1] + (list(map(float, self.spn.split(',')))[1] * 1.4)
            self.coords = ','.join(list(map(str, coords)))

        if event.key() == Qt.Key_A or event.key() == Qt.Key_Left:
            coords = list(map(float, self.coords.split(',')))
            coords[0] = coords[0] - (list(map(float, self.spn.split(',')))[0] * 3.2)
            self.coords = ','.join(list(map(str, coords)))

        if event.key() == Qt.Key_D or event.key() == Qt.Key_Right:
            coords = list(map(float, self.coords.split(',')))
            coords[0] = coords[0] + (list(map(float, self.spn.split(',')))[0] * 3.2)
            self.coords = ','.join(list(map(str, coords)))
        self.getImage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())