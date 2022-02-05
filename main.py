import os
import sys
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from settings import *

SCREEN_SIZE = [600, 450]


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('system_files/main.ui', self)
        self.setWindowTitle('Отображение карты')
        self.map_file = None
        self.map_size = 650, 450
        self.spn = 0.002
        self.ll = 37.530887, 55.703118
        self.z = 15
        self.map_type = 'map'
        self.getImage()

    def getImage(self):
        parameters = {'spn': f'{self.spn},{self.spn}',
                      'll': ','.join(map(str, self.ll)), 'l': self.map_type,
                      'size': ','.join(map(str, self.map_size)),
                      'z': self.z}
        response = requests.get(static_api_server, params=parameters)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.picture.setPixmap(QPixmap(self.map_file))

    def closeEvent(self, event):
        """При закрытии формы удаляем файл с изображением"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())