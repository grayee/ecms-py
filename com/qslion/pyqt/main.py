# 使用 pyinstaller -Fw main.py 编译为可执行文件

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from com.qslion.pyqt.pdf2Img_ui import *


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.labelFileName = QLabel(self.statusbar)  # 状态栏上的文件名


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
