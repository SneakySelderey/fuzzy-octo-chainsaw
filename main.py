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
        self.bbox = '36.6,54.6~38.6,56.6'
        self.getImage()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?&bbox={self.bbox}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.picture.setPixmap(QPixmap(self.map_file))

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        left_down = self.bbox.split('~')[0]
        up_right = self.bbox.split('~')[1]
        if event.key() == Qt.Key_S or event.key() == Qt.Key_Down:
            size_y = float(up_right.split(',')[1]) - float(left_down.split(',')[1])
            new_y = float(left_down.split(',')[1]) - size_y, float(up_right.split(',')[1]) - size_y
            self.bbox = f"{self.bbox.split('~')[0].split(',')[0]},{new_y[0]}~" \
                        f"{self.bbox.split('~')[1].split(',')[0]},{new_y[1]}"

        if event.key() == Qt.Key_W or event.key() == Qt.Key_Up:
            size_y = float(up_right.split(',')[1]) - float(left_down.split(',')[1])
            new_y = float(left_down.split(',')[1]) + size_y, float(up_right.split(',')[1]) + size_y
            self.bbox = f"{self.bbox.split('~')[0].split(',')[0]},{new_y[0]}~" \
                        f"{self.bbox.split('~')[1].split(',')[0]},{new_y[1]}"

        if event.key() == Qt.Key_A or event.key() == Qt.Key_Left:
            size_x = float(up_right.split(',')[0]) - float(left_down.split(',')[0])
            new_x = float(left_down.split(',')[0]) - size_x, float(up_right.split(',')[0]) - size_x
            self.bbox = f"{new_x[0]},{self.bbox.split('~')[0].split(',')[1]}~" \
                        f"{new_x[1]},{self.bbox.split('~')[1].split(',')[1]}"

        if event.key() == Qt.Key_D or event.key() == Qt.Key_Right:
            size_x = float(up_right.split(',')[0]) - float(left_down.split(',')[0])
            new_x = float(left_down.split(',')[0]) + size_x, float(up_right.split(',')[0]) + size_x
            self.bbox = f"{new_x[0]},{self.bbox.split('~')[0].split(',')[1]}~" \
                        f"{new_x[1]},{self.bbox.split('~')[1].split(',')[1]}"
        self.getImage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())