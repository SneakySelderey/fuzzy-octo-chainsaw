import os
import sys
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from system_files.geocoder import *
from settings import *


USEFUL_KEYS = [Qt.Key_Down, Qt.Key_Up, Qt.Key_Left, Qt.Key_Right, Qt.Key_W,
               Qt.Key_S, Qt.Key_A, Qt.Key_D, Qt.Key_PageDown, Qt.Key_PageUp]


def except_hook(cls, exception, traceback):
    """Вывод ошибок"""
    sys.__excepthook__(cls, exception, traceback)


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('system_files/main.ui', self)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon('system_files/icon.png'))

        QMessageBox.information(self, 'Важно',
                                'Вы можете управлять картой с помощью зажатия '
                                'левой кнопки мыши и ее перемещения. '
                                'Масштаб карты изменяется колесиком мыши')

        self.map_size = 650, 450
        self.spn = 0.002
        self.ll = [9.794475, 50.972254]
        self.z = 17
        self.prev_coords = [self.ll[0], self.ll[1]]
        self.x = self.width() // 2
        self.y = self.picture.y() + self.picture.height() // 2
        self.dif_x = self.dif_y = 0

        self.map_type = 'map'
        self.moving = False
        self.pt = None
        self.map_file = None
        self.new_req = True
        self.LMB_hold_and_mouse_move = False
        self.click = False

        self.radio = [self.l_map, self.sat_map, self.hybrid_map]
        [i.clicked.connect(self.changeMap) for i in self.radio]
        self.l_map.setChecked(True)
        self.delete_req.clicked.connect(self.deletePt)
        self.delete_req.clicked.connect(self.clear_address_line)
        self.find_btn.clicked.connect(self.getAddress)
        self.show_post_index.stateChanged.connect(self.addressShow)
        self.address_line.setReadOnly(True)
        self.statusbar.messageChanged.connect(self.changeStatusColor)

        self.getImage()

    def getPt(self):
        return f'{self.pt[0]},{self.pt[1]}'

    def deletePt(self):
        """Удаление метки"""
        self.pt = None
        self.new_req = False
        self.getImage()

    def clear_address_line(self):
        """Удаление адреса"""
        self.address_line.setPlainText('')

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
                self.new_req = True
                self.click = False
                self.ll = get_address_pos(self.address.text())
                self.pt = [self.ll[0], self.ll[1]]
                try:
                    result = get_full_address(
                        f'{self.pt[0]},{self.pt[1]}',
                        postal_code=self.show_post_index.isChecked())
                    self.address_line.setPlainText(result)
                except KeyError:
                    self.statusbar.showMessage(
                        'Ошибка запроса. Почтовый индекс отсутствует', 2000)
                    self.address_line.setPlainText(get_full_address(
                        self.address.text()))

                self.getImage()
            else:
                QMessageBox.critical(self, 'Ошибка запроса',
                                     'Адрес введен неверно')

    def wheelEvent(self, event):
        """Масштабирование"""
        if event.angleDelta().y() > 0:
            self.z = min(19, self.z + 1)
            self.spn = max(self.spn / 2, 0.001)
        else:
            self.z = max(self.z - 1, 1)
            self.spn = min(self.spn * 2, 32.768)
        self.getImage()

    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши"""
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.dif_x = self.x - event.x()
            self.dif_y = self.y - event.y()
            self.LMB_hold_and_mouse_move = True

    def addressShow(self):
        """Функция для вывода адреса и почтового индекса"""
        if self.show_post_index.isChecked() and self.new_req:
            if self.pt is not None:
                try:
                    result = get_full_address(
                        self.address.text() if
                        self.address.text() and not self.click else
                        self.getPt(), postal_code=True)
                    self.address_line.setPlainText(result)
                except KeyError:
                    self.statusbar.showMessage(
                        'Ошибка запроса. Почтовый индекс отсутствует', 2000)
        elif self.new_req:
            if self.address.text() or self.pt is not None:
                self.address_line.setPlainText(get_full_address(
                    self.address.text() if self.address.text() and not
                    self.click else self.getPt()))

    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши"""
        if event.button() == Qt.LeftButton:
            self.setDefault()

            if self.LMB_hold_and_mouse_move and self.picture.y() <= event.y() \
                    <= self.picture.y() + self.picture.height():
                self.new_req = True
                self.click = True

                x0 = lonToX(self.ll[0]) * get_coeff(self.z) + (event.x() - self.width() // 2) * 2
                y0 = latToY(self.ll[1]) * get_coeff(self.z) + (self.height() // 2 - event.y()) * 2
                lon = xToLon(x0 / get_coeff(self.z))
                lat = yToLat(y0 / get_coeff(self.z))

                # self.ll = [lon, lat]

                # dif_x = self.x - event.x()
                # dif_y = self.y - event.y()
                #
                # one_pix_to_degree_x = self.spn / self.map_size[0]
                # one_pix_to_degree_y = self.spn / self.map_size[1]
                #
                # fake_ll = self.ll[0] - (
                #         dif_x * one_pix_to_degree_x) * 3.49, self.ll[1] + \
                #           (dif_y * one_pix_to_degree_y) * 1.43
                self.pt = [lon, lat]
                #
                self.addressShow()
                self.getImage()
            self.LMB_hold_and_mouse_move = False
        # elif event.button() == Qt.RightButton:
        #     dif_x = self.x - event.x()
        #     dif_y = self.y - event.y()
        #
        #     one_pix_to_degree_x = self.spn / self.map_size[0]
        #     one_pix_to_degree_y = self.spn / self.map_size[1]
        #
        #     fake_ll = self.ll[0] - (
        #         dif_x * one_pix_to_degree_x) * 3.49, self.ll[1] + \
        #               (dif_y * one_pix_to_degree_y) * 1.43
        #     self.pt = [fake_ll[0], fake_ll[1]]
        #     print(get_full_address(','.join(map(
        #         str, self.pt))))
        #     print(get_organization(get_full_address(','.join(map(
        #         str, self.pt)))))

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
            self.LMB_hold_and_mouse_move = False

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
                      'z': self.z}
        if self.pt is not None:
            parameters['pt'] = ','.join(map(str, self.pt)) + ',ya_ru'
        response = requests.get(static_api_server, params=parameters)

        if not response:
            if self.ll[0] > 179.9999:
                self.ll[0] = -179.9999
                if not self.moving:
                    self.ll[0] += self.spn * 3.49
                parameters['ll'] = ','.join(map(str, self.ll))
            elif self.ll[0] < -179.9999:
                self.ll[0] = 179.9999
                if not self.moving:
                    self.ll[0] -= self.spn * 3.49
                parameters['ll'] = ','.join(map(str, self.ll))
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

    def changeStatusColor(self):
        """Функция для изменения цвета status bar'а в случае ошибки"""
        if self.statusbar.currentMessage():
            self.statusbar.setStyleSheet(
                "QStatusBar{background:rgba(255,0,0,255);}")
        else:
            self.statusbar.setStyleSheet('')

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
        self.getImage() if event.key() in USEFUL_KEYS else None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())