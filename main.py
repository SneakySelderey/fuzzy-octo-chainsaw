import os
import sys
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from system_files.geocoder import *
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
        self.ll = [9.794475, 50.972254]
        self.radio = [self.l_map, self.sat_map, self.hybrid_map]
        [i.clicked.connect(self.changeMap) for i in self.radio]
        self.l_map.setChecked(True)
        self.address.editingFinished.connect(self.getAddress)
        self.delete_req.clicked.connect(self.deletePt)
        self.find_btn.clicked.connect(self.getAddress)
        self.map_type = 'map'
        self.prev_coords = [self.ll[0], self.ll[1]]
        self.moving = False
        self.x = self.width() // 2
        self.y = self.height() // 2
        self.dif_x = self.dif_y = 0
        self.pt = None
        self.getImage()

    def deletePt(self):
        self.pt = None
        self.getImage()

    def setDefault(self):
        """Функция, устанавливающая некоторые значения по умолчанию"""
        self.x = self.width() // 2
        self.y = self.height() // 2
        self.dif_x = self.dif_y = 0
        self.moving = False

    def getAddress(self):
        """Функция обработки введенного адрсеа"""
        if self.address.text():
            value = get_address_pos(self.address.text())
            if value is not None:
                self.setDefault()
                self.ll = get_address_pos(self.address.text())
                self.pt = [self.ll[0], self.ll[1]]
                self.getImage()
            else:
                QMessageBox.critical(self, 'Ошибка запроса',
                                     'Адрес введен неверно')

    def wheelEvent(self, event):
        """Масштабирование"""
        if event.angleDelta().y() > 0:
            self.spn = max(self.spn / 2, 0.001)
        else:
            self.spn = min(self.spn * 2, 32.768)
        self.getImage()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.dif_x = self.x - event.x()
            self.dif_y = self.y - event.y()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setDefault()

    def mouseMoveEvent(self, event):
        """Обработка перемещения карыт с зажатой кнопкой мыши"""
        if self.moving:
            self.prev_coords = [self.ll[0], self.ll[1]]
            x1, y1 = event.x(), event.y()
            self.x = x1 + self.dif_x
            self.y = y1 + self.dif_y
            self.ll[0] -= (self.x - self.width() // 2) * self.spn / 1150
            self.ll[1] += (self.y - self.height() // 2) * self.spn / 1150
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
        if self.pt is not None:
            parameters['pt'] = ','.join(map(str, self.pt)) + ',ya_ru'
        response = requests.get(static_api_server, params=parameters)

        if not response:
            if self.ll[0] > 179.9999:
                self.ll[0] = -179.9999
                if not self.moving:
                    self.ll[0] += self.spn * 3.49
                parameters['ll'] = ','.join(map(str, self.ll))
                response = requests.get(static_api_server, params=parameters)
            elif self.ll[0] < -179.9999:
                self.ll[0] = 179.9999
                if not self.moving:
                    self.ll[0] -= self.spn * 3.49
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