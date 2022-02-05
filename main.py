import os
import sys
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('system_files/main.ui', self)
        self.setWindowTitle('Отображение карты')
        self.map_file = None
        self.spn = self.z = self.ll = 0
        self.map_type = 'map'
        self.coords = '37.530887,55.703118'
        self.prev_coords = self.coords
        self.spn = '0.002,0.002'
        self.getImage()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.coords}&spn={self.spn}&l=map"
        response = requests.get(map_request)

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

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.picture.setPixmap(QPixmap(self.map_file))

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
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