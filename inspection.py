import numpy as np
from matplotlib import pyplot as plt
import open3d as o3d
import matplotlib as mpl
from PyQt5.QtWidgets import QApplication, QDialog, QProgressDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

def on_button3_clicked(self):

    # 创建QProgressDialog
    progress_dialog = QProgressDialog(self)
    progress_dialog.setWindowTitle("请等待")
    progress_dialog.setLabelText("正在进行检测焊点，请稍候...")
    progress_dialog.setCancelButton(None)  # 不显示取消按钮
    progress_dialog.setWindowModality(Qt.ApplicationModal)
    progress_dialog.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
    progress_dialog.setFixedSize(240, 60)
    # 设置进度条标题文字居中的样式表
    style_sheet = "QLabel#qt_spinbox_label {qproperty-alignment: AlignCenter; font-size: 18pt;}"
    progress_dialog.setStyleSheet(style_sheet)
    # 设置循环转圈圈的样式
    progress_dialog.setRange(0, 0)
    # 显示进度条对话框
    progress_dialog.show()
    # 模拟一个耗时的任务
    for i in range(50000):
        # 更新进度条
        progress_dialog.setValue(i)
        # 让应用程序处理事件，以允许界面更新
        QApplication.processEvents()
    # 关闭进度条对话框
    progress_dialog.close()

    self.tabWidget.setCurrentIndex(1)
