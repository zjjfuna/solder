import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget, QPushButton, QVBoxLayout, QWidget, QSlider
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class PointCloudWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.point_size = 5  # 初始点的大小
        self.max_point_size = 20  # 最大点的大小
        self.zoom_speed = 0.01  # 缩放速度
        self.ctrl_pressed = False  # 标志Ctrl键的状态

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 1, 100)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -10)
        # 设置点的大小
        glPointSize(self.point_size)
        # 在这里使用OpenGL绘制点云
        # 示例：
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glVertex3f(1, 1, 1)
        glEnd()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = False

    def wheelEvent(self, event):
        if self.ctrl_pressed:
            self.point_size += event.angleDelta().y() * self.zoom_speed
            self.point_size = min(self.point_size, self.max_point_size)  # 限制点的最大大小
            if self.point_size < 1:
                self.point_size = 1
            self.update()

    def set_point_size(self, size):
        self.point_size = min(size, self.max_point_size)  # 限制点的最大大小
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.point_cloud_widget = PointCloudWidget()
        self.setCentralWidget(self.point_cloud_widget)

        self.point_size_slider = QSlider(Qt.Horizontal)
        self.point_size_slider.setMinimum(1)
        self.point_size_slider.setMaximum(self.point_cloud_widget.max_point_size)
        self.point_size_slider.setValue(self.point_cloud_widget.point_size)
        self.point_size_slider.valueChanged.connect(self.set_point_size)

        self.zoom_in_btn = QPushButton('放大')
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn = QPushButton('缩小')
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        layout = QVBoxLayout()
        layout.addWidget(self.point_cloud_widget)
        layout.addWidget(self.point_size_slider)
        layout.addWidget(self.zoom_in_btn)
        layout.addWidget(self.zoom_out_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('3D点云查看器')
        self.show()

    def zoom_in(self):
        self.set_point_size(self.point_cloud_widget.point_size + 1)

    def zoom_out(self):
        self.set_point_size(self.point_cloud_widget.point_size - 1)

    def set_point_size(self, size):
        self.point_cloud_widget.set_point_size(size)
        self.point_size_slider.setValue(size)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
