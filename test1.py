from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PyQt5.QtCore import Qt, QThread
import sys

class WaitingCursorThread(QThread):
    def run(self):
        self.waiting_cursor = WaitingCursor()
        self.waiting_cursor.show()

        # 通过等待窗口关闭来保持线程的运行状态
        while self.waiting_cursor.isVisible():
            self.msleep(100)  # 等待100毫秒

class WaitingCursor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('等待中')
        self.setFixedSize(100, 100)

        self.label = QLabel(self)
        self.movie = QMovie("loading.gif")  # 替换 "loading.gif" 为你的等待光标动画文件路径
        self.label.setMovie(self.movie)
        self.movie.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle('添加等待光标示例')
    window.setGeometry(100, 100, 300, 200)

    button = QPushButton('点击我显示等待光标', window)
    button.setGeometry(50, 50, 200, 50)

    def show_waiting_cursor():
        waiting_cursor_thread = WaitingCursorThread()
        waiting_cursor_thread.start()

    button.clicked.connect(show_waiting_cursor)
    window.show()
    sys.exit(app.exec_())
