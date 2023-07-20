import sys
from concurrent.futures import ThreadPoolExecutor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_template import FigureCanvas
from qdarkstyle import LightPalette

from mainwindow import Ui_MainWindow
import os
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QDir, Qt, QSize
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QMenu, QAction, QTreeWidgetItem, QInputDialog, QMessageBox, \
    QHeaderView, QSizePolicy, QTableWidgetItem, QApplication, QMainWindow, QLabel, QProgressDialog, QGraphicsView, \
    QPushButton
import open3d as o3d
import numpy as np
import pandas as pd
from pyglet.gl import glLineWidth
from pyglet.gl.gl_compat import glColor3f, glBegin, glVertex3f, glEnd, GL_LINES
from pyqtgraph.opengl import GLViewWidget
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from filter_voxel import Ui_Dialog_voxel
from filter_uniform import Ui_Dialog_uniform
from filter_random import Ui_Dialog_random
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QPalette, QColor, QVector3D, QFont
from PyQt5.QtGui import QCursor
from datetime import datetime
from PyQt5.QtCore import QTimer
from pathlib import Path
from PyQt5.QtGui import QIcon
from shutil import copyfile
import shutil
from collections import OrderedDict
import matplotlib as mpl
import icons_rc
from inspection import on_button3_clicked
from Pont_Cloud_filter import point_cloud_filter
# from demo_1 import ProcessDialog

class myTreeWidget:
    def __init__(self, objTree):
        self.myTree = objTree
        # 设置列数
        # self.myTree.setColumnCount(1)
        # 设置树形控件头部的标题
        # self.myTree.setHeaderLabels(['DB树'])

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            self.clearSelection()
        super(myTreeWidget, self).mousePressEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("mainwindow.ui", self)
        self.setWindowTitle("焊点检测程序")
        icon = QIcon(":/xjtu.png")
        self.setWindowIcon(icon)
        self.resize(1200, 800)
        # 初始更新时间
        self.update_time()
        # 设置状态栏字体大小和样式
        font = QFont("Arial", 11)
        self.statusBar.setFont(font)
        # 创建一个 QTimer 对象，并设置更新时间的间隔（以毫秒为单位）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        # 启动定时器，时间间隔为 1000 毫秒（1秒）
        self.timer.start(1000)
        # self.point_cloud_dict = {}  # 存储已打开的点云对象及其显示对象的字典
        # 创建一个有序字典来保存点云
        self.point_cloud_dict = OrderedDict()
        self.bbox_dict = {}  # 用于存储包裹框的字典
        self.axis_dict = {}  # 用于存储坐标轴的字典
        # 在状态栏中添加标签用于显示信息
        # 创建一个标签并设置字体大小和样式
        label1 = QLabel("This is a label with larger font size.")
        label1.setStyleSheet("font-size: 18px; font-Family: 宋体")
        self.status_label = label1
        self.statusBar.addPermanentWidget(self.status_label)
        # 初始化状态栏信息
        self.setStatusMessage("西安交通大学中国西部质量科学与技术研究院")

        #更改显示比例
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setChildrenCollapsible(False)

        self.splitter_1.setStretchFactor(0, 3)
        self.splitter_1.setStretchFactor(1, 2)
        self.splitter_1.setChildrenCollapsible(False)

        self.splitter_2.setStretchFactor(0, 40)
        self.splitter_2.setStretchFactor(1, 1)
        self.splitter_2.setChildrenCollapsible(False)
        # 设置按钮点击事件
        self.action.triggered.connect(self.importPointCloud)
        self.action_13.triggered.connect(self.savePointCloudAs)
        self.action_2.triggered.connect(self.createProject)
        self.action_5.triggered.connect(self.openProject)
        self.action_exit.triggered.connect(self.on_exit)  # 将退出动作连接到退出函数
        self.action_10.triggered.connect(self.saveLogToFile)
        self.action_17.triggered.connect(self.onLightThemeClicked)
        self.action_18.triggered.connect(self.onDarkThemeClicked)
        self.action_19.triggered.connect(self.onOgriginThemeClicked)

        self.VoxelDialog = Filter_voxel()
        self.action_7.triggered.connect(self.dialog_filter_voxel)
        self.UniformDialog = Filter_uniform()
        self.action_8.triggered.connect(self.dialog_filter_uniform)
        self.RandomDialog = Filter_random()

        self.action_6.triggered.connect(self.dialog_filter_random)
        self.button1.clicked.connect(self.data_preprocessing)
        self.button4.clicked.connect(self.importCSVToProject)
        self.button5.clicked.connect(self.refreshTree)
        self.button3.clicked.connect(self.handle_button3_click)
        self.button2.clicked.connect(self.handle_button2_click)
        # 在工具栏区域添加文件工具栏
        tb = self.addToolBar('File')
        # 添加图形按钮
        new = QAction(QIcon(':/new.png'), 'new', self)
        tb.addAction(new)
        new.triggered.connect(self.createProject)
        new.setToolTip("创建项目")

        open = QAction(QIcon(':/open.png'), 'open', self)
        tb.addAction(open)
        open.triggered.connect(self.openProject)
        open.setToolTip("打开项目")

        save = QAction(QIcon(':/save.png'), 'save', self)
        tb.addAction(save)
        save.triggered.connect(self.savePointCloudAs)
        save.setToolTip("保存点云")

        import_csv = QAction(QIcon(':/import.png'), 'open', self)
        tb.addAction(import_csv)
        import_csv.triggered.connect(self.importCSVToProject)
        import_csv.setToolTip("导入原始CSV数据")

        import_pointcloud = QAction(QIcon(':/import_point.png'), 'open', self)
        tb.addAction(import_pointcloud)
        import_pointcloud.triggered.connect(self.importPointCloud)
        import_pointcloud.setToolTip("导入点云")

        # 在文件工具栏上添加分隔符
        file_toolbar = self.addToolBar('File')
        file_toolbar.addSeparator()

        # 添加六个视图动作按钮
        action1 = QtWidgets.QAction(QIcon(':/fushi.png'), 'Action 1', self)
        file_toolbar.addAction(action1)
        action1.setToolTip("俯视图")
        action1.triggered.connect(self.on_action1_triggered)

        action2 = QtWidgets.QAction(QIcon(':/houshi.png'), 'Action 2', self)
        file_toolbar.addAction(action2)
        action2.setToolTip("后视图")
        action2.triggered.connect(self.on_action2_triggered)

        action3 = QtWidgets.QAction(QIcon(':/zuoshi.png'), 'Action 3', self)
        file_toolbar.addAction(action3)
        action3.setToolTip("左视图")
        action3.triggered.connect(self.on_action3_triggered)

        action4 = QtWidgets.QAction(QIcon(':/yangshi.png'), 'Action 4', self)
        file_toolbar.addAction(action4)
        action4.setToolTip("仰视图")
        action4.triggered.connect(self.on_action4_triggered)

        action5 = QtWidgets.QAction(QIcon(':/qianshi.png'), 'Action 5', self)
        file_toolbar.addAction(action5)
        action5.setToolTip("前视图")
        action5.triggered.connect(self.on_action5_triggered)

        action6 = QtWidgets.QAction(QIcon(':/youshi.png'), 'Action 6', self)
        file_toolbar.addAction(action6)
        action6.setToolTip("右视图")
        action6.triggered.connect(self.on_action6_triggered)

        action7 = QtWidgets.QAction(QIcon(':/shitu.png'), 'Action 7', self)
        file_toolbar.addAction(action7)
        action7.setToolTip("正面等距视图")
        action7.triggered.connect(self.on_action7_triggered)

        action8 = QtWidgets.QAction(QIcon(':/jia.png'), 'Action 8', self)
        file_toolbar.addAction(action8)
        action8.setToolTip("点云放大")
        action8.triggered.connect(self.on_action8_triggered)

        action9 = QtWidgets.QAction(QIcon(':/jian.png'), 'Action 9', self)
        file_toolbar.addAction(action9)
        action9.setToolTip("推远视角")
        action9.triggered.connect(self.on_action9_triggered)

        # ------------------------------------------------------------
        self.graphicsView = GLViewWidget(self)
        # self.gridLayout_9.addWidget(self.graphicsView)
        self.horizontalLayout_5.addWidget(self.graphicsView)
        self.horizontalLayout_5.insertWidget(1, self.graphicsView)
        # self.graphicsView.setWindowTitle('pyqtgraph example: GLScatterPlotItem')  # 定义窗口标题
        self.graphicsView.setBackgroundColor(145, 158, 164)

        self.tabWidget.setCurrentIndex(0) # 默认在第一个界面
        # 1. 创建画板组件
        self.figure = plt.figure()
        self.figure.set_facecolor("#919ea4")

        # self.canvas = FigureCanvas(self.figure)
        self.canvas = FigureCanvasQTAgg(self.figure)
        # self.gridLayout_5.addWidget(self.canvas)
        # self.horizontalLayout_5.addWidget(self.canvas)
        self.verticalLayout_3.addWidget(self.canvas)
        self.horizontalLayout_5.setStretch(1,1)
        self.horizontalLayout_5.setStretch(0,20)
        self.horizontalLayout_5.setSpacing(0)

        self.tab_3.setStyleSheet("background-color: #919ea4;")
        # 添加按钮并设置图标
        self.button6 = QPushButton()
        icon = QIcon(':/global.png')  # 将global.png替换为您的图标文件路径
        icon_size = QSize(40, 40)
        self.button6.setIcon(icon)
        # button6.setIconSize(icon.actualSize(button6.size()))
        self.verticalLayout_3.addWidget(self.button6)
        self.verticalLayout_3.setStretch(0, 5)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_3.setSpacing(0)
        self.button6.setFixedSize(50, 100)
        self.button6.setIconSize(icon_size)
        self.button6.setFlat(True)
        self.button6.clicked.connect(self.on_action7_triggered)
        # button6.setStyleSheet('background-color: #919ea4;')

        self.graphicsView_4 = GLViewWidget(self)
        self.gridLayout_4.addWidget(self.graphicsView_4)
        self.graphicsView_4.setBackgroundColor(255, 255, 255)

        self.treeWidget.itemChanged.connect(self.itemStateChanged)
        # 创建树控件对象
        # 创建树控件对象
        self.myTreeTest = myTreeWidget(self.treeWidget)
        # 设置样式表
        self.treeWidget.setStyleSheet("QTreeView::item { margin-right: 0px; }")
        # 存储已存在的项目名称
        self.existingProjects = set()
        # self.graphicsView.opts['distance'] = 10  # 初始视角高度
        # print(self.graphicsView.cameraPosition())
        self.graphicsView.setCameraPosition(distance=2000)
        # axis = gl.GLAxisItem()
        # axis.setSize(x=2000, y=2000, z=2000)
        # self.graphicsView.addItem(axis)
        # self.show_axis_with_point_cloud()
        # g = gl.GLGridItem()#添加网格
        # g.setSize(100, 100)  # 设置网格的大小（X轴范围和Y轴范围）
        # g.setSpacing(10)  # 设置网格的每个网格的大小
        # self.graphicsView.addItem(g)
        # self.show_axis_in_bottom_right
        self.treeWidget.itemSelectionChanged.connect(self.onItemSelected)
        self.graphicsView.installEventFilter(self)
        # 在树控件上安装事件过滤器
        self.treeWidget.viewport().installEventFilter(self)
        # 初始化点云对象和文件列表
        self.point_cloud = None
        self.file_list = []
        # 设置鼠标点击事件过滤器
        self.installEventFilter(self)
        # 显示窗口
        self.ui.show()
        # # 右键事件功能函数

    def handle_button3_click(self):
        # 调用按钮处理函数，并传递tabWidget作为参数
        on_button3_clicked(self)
    def handle_button2_click(self):
        # 调用按钮处理函数，并传递tabWidget作为参数
        point_cloud_filter(self)
    def setStatusMessage(self, message):
        # 设置状态栏中显示的信息
        self.status_label.setText(message)

    def saveLogToFile(self):
        log_text = self.textBrowser.toPlainText()
        log_filename = "log_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"

        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        save_path, _ = QFileDialog.getSaveFileName(self, "保存日志文件", log_filename,
                                                   "Text Files (*.txt);;All Files (*)", options=options)

        if save_path:
            with open(save_path, "w") as file:
                file.write(log_text)
            QMessageBox.information(self, "提示", "日志保存成功！", QMessageBox.NoButton)
            self.textBrowser.append("[" + self.update_time() + "]" + "日志保存成功!")
    def on_action1_triggered(self):
        self.set_camera_position(distance=self.calculate_camera_distance(), elevation=90, azimuth=90)
    def on_action2_triggered(self):
        self.set_camera_position(distance=self.calculate_camera_distance(), elevation=180, azimuth=90)
    def on_action3_triggered(self):
        self.set_camera_position(distance=self.calculate_camera_distance(), elevation=0, azimuth=0)
    def on_action4_triggered(self):
        self.set_camera_position(distance=self.calculate_camera_distance(), elevation=-90, azimuth=90)
    def on_action5_triggered(self):
        self.set_camera_position(distance=self.calculate_camera_distance(), elevation=0, azimuth=90)
    def on_action6_triggered(self):
        self.set_camera_position(distance=self.calculate_camera_distance(), elevation=0, azimuth=180)
    def on_action7_triggered(self):
        self.set_camera_position(distance=self.calculate_camera_distance(), elevation=45, azimuth=45)

    def calculate_camera_distance(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            # 获取第一个选中的节点
            current_item = selected_items[0]
            # 获取节点对应的文件路径
            file_path = current_item.data(0, 32)
            # 检查文件路径是否在点云字典的键中
            if file_path in self.point_cloud_dict:
                # 获取选中点云对应的点云对象和绘制对象（我们不需要绘制对象）
                point_cloud, _ = self.point_cloud_dict[file_path]
                # 获取点云的包围盒
                bbox = point_cloud.get_axis_aligned_bounding_box()
                # 计算包围盒的对角线长度作为相机距离
                diagonal_length = np.linalg.norm(bbox.max_bound - bbox.min_bound)
                # 将相机距离设置为包围盒对角线长度的一个倍数，例如1.1倍
                distance = diagonal_length * 1.1
                return distance
            return 100000
        # 如果没有选中点云或者选中的点云不在字典中，则返回默认的相机距离 2000
        return 100000

    def set_camera_position(self, distance=None, elevation=None, azimuth=None):
        """Set the camera position and direction."""
        if distance is not None:
            self.graphicsView.setCameraPosition(distance=distance)
        if elevation is not None and azimuth is not None:
            self.graphicsView.opts['elevation'] = elevation
            self.graphicsView.opts['azimuth'] = azimuth

    def on_action8_triggered(self):
        print("放大点云")

    def on_action9_triggered(self):
        print("减小点云")

    def on_exit(self):
        reply = QMessageBox.question(self, "退出确认", "确定要退出吗？", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.close()

    # def eventFilter(self, obj, event):
    #     if obj == self and event.type() == QtCore.QEvent.MouseButtonPress:
    #         # 如果点击了空白区域，则取消当前选中的节点
    #         if not self.treeWidget.indexAt(event.pos()).isValid():
    #             self.treeWidget.clearSelection()
    #     return super().eventFilter(obj, event)

    def eventFilter(self, obj, event):
        if obj == self.graphicsView and event.type() == QtCore.QEvent.MouseButtonPress:
            # 如果点击了点云显示界面，则不进行任何操作
            return True
        if obj == self and event.type() == QtCore.QEvent.MouseButtonPress:
            # 如果点击了空白区域，则取消当前选中的节点
            if not self.treeWidget.indexAt(event.pos()).isValid():
                self.treeWidget.clearSelection()
        if obj == self.treeWidget.viewport() and event.type() == QtCore.QEvent.MouseButtonPress:
            # 如果点击树控件的空白区域，取消当前的选择
            index = self.treeWidget.indexAt(event.pos())
            if not index.isValid():
                self.treeWidget.clearSelection()

        return super().eventFilter(obj, event)


    def contextMenuEvent(self, event):
        # 将全局坐标转换为树形控件的局部坐标
        local_pos = self.treeWidget.mapFromGlobal(event.globalPos())
        # 获取树形控件的区域
        tree_rect = self.treeWidget.rect()

        # 判断鼠标点击的位置是否在树形控件的区域内
        if tree_rect.contains(local_pos):
            # 创建右键菜单
            menu = QMenu(self)
            # 获取当前选中的节点
            selected_items = self.treeWidget.selectedItems()
            if selected_items:
                current_item = selected_items[0]
                file_path = current_item.data(0, 32)

                if file_path:
                    if file_path:
                        # 创建下拉二级菜单
                        submenu = QMenu("另存为", self)
                        # 添加其他功能到下拉二级菜单，如保存项目功能
                        # 添加“另存为”功能，并根据条件设置其可用性
                        save_action = QAction("保存点云", self)
                        save_action.triggered.connect(self.savePointCloudAs)
                        # 根据条件设置“另存为”功能的可用性
                        save_action.setEnabled(file_path.lower().endswith(".ply"))
                        submenu.addAction(save_action)

                        # 添加“另存为”功能，并根据条件设置其可用性
                        save_project_action = QAction("保存项目", self)
                        save_project_action.triggered.connect(self.saveProjectAs)
                        # 根据条件设置“另存为”功能的可用性
                        save_project_action.setEnabled(self.is_folder_selected())
                        submenu.addAction(save_project_action)

                        # 将下拉二级菜单添加到主菜单中
                        menu.addMenu(submenu)

                        # 添加“原始数据处理”功能，并根据条件设置其可用性
                        visual_action = QAction("原始数据处理", self)
                        visual_action.triggered.connect(self.data_preprocessing)
                        # 根据条件设置“原始数据处理”功能的可用性
                        visual_action.setEnabled(file_path.lower().endswith(".csv"))
                        menu.addAction(visual_action)

                        # 添加“原始数据导入”功能
                        import_csv_action = QAction("原始数据导入", self)
                        import_csv_action.triggered.connect(self.importCSVToProject)
                        menu.addAction(import_csv_action)

                        # 添加“点云导入”功能
                        import_ply_action = QAction("点云导入", self)
                        import_ply_action.triggered.connect(self.importPointCloud)
                        menu.addAction(import_ply_action)

                        # 添加“关闭文件”功能
                        delete_action = QAction("关闭文件", self)
                        delete_action.triggered.connect(self.deletePointCloud)
                        menu.addAction(delete_action)

                        # 添加“从系统文件夹删除”功能  真正删除
                        clear_action = QAction("从本地删除", self)
                        clear_action.triggered.connect(self.delete)
                        menu.addAction(clear_action)

            # 添加“刷新”功能
            refresh_action = QAction("刷新", self)
            refresh_action.triggered.connect(self.refreshTree)
            menu.addAction(refresh_action)
            # 在鼠标右键点击的位置显示菜单
            menu.exec_(event.globalPos())

    def is_folder_selected(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            # 判断当前选中的节点是否为文件夹
            return not current_item.data(0, 32).lower().endswith(".ply")
        return False

    def delete(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            file_path = current_item.data(0, 32)
            if file_path:
                # 确认用户是否真的要删除文件或文件夹
                msg_box = QMessageBox(QMessageBox.Warning, "确认删除", "是否从本地删除此文件或文件夹？",
                                      QMessageBox.Yes | QMessageBox.No, self)
                result = msg_box.exec_()
                if result == QMessageBox.Yes:
                    try:
                        if os.path.isfile(file_path):
                            # 删除文件
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            # 删除文件夹及其内容
                            shutil.rmtree(file_path)
                        # 递归删除子节点的点云
                        self.delete_children_point_cloud(current_item)
                        # 从树形控件中移除节点
                        parent_item = current_item.parent()
                        if parent_item:
                            parent_item.removeChild(current_item)
                        else:
                            self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(current_item))
                        self.textBrowser.append("[" + self.update_time() + "]" + "已从本地中删除："+ file_path)
                        if file_path in self.point_cloud_dict:
                            # 从字典中获取点云对象和显示对象
                            point_cloud, plot = self.point_cloud_dict[file_path]
                            # 在OpenGL窗口中移除显示对象
                            self.graphicsView.removeItem(plot)
                            # 从字典中移除点云对象和显示对象
                            del self.point_cloud_dict[file_path]
                    except Exception as e:
                        self.textBrowser.append("[" + self.update_time() + "]" + "删除失败：" + str(e))
                else:
                    self.textBrowser.append("[" + self.update_time() + "]" + "取消删除")

    def savePointCloudAs(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()

        if selected_items:
            current_item = selected_items[0]
            file_path = current_item.data(0, 32)

            if file_path.lower().endswith(".ply"):
                options = QFileDialog.Options()
                options |= QFileDialog.DontUseNativeDialog
                # save_path, _ = QFileDialog.getSaveFileName(self, "保存点云文件", file_path, "PLY Files (*.ply)")
                save_path, _ = QFileDialog.getSaveFileName(self, "保存PLY文件", "", "PLY Files (*.ply)")

                if save_path:
                    # 复制文件到指定路径
                    source_file = Path(file_path)
                    destination_file = Path(save_path)
                    if source_file != destination_file:
                        destination_file.write_bytes(source_file.read_bytes())
                    self.textBrowser.append("[" + self.update_time() + "]" + "已保存点云到:"+save_path)
                    QMessageBox.information(self, "保存成功", "点云文件已成功保存！")
            # else:
            #     # 根据条件设置“另存为”功能的可用性
            #     self.action_13.setEnabled(file_path.lower().endswith(".ply"))
        else:
            # self.action_13.setEnabled(0)
            self.textBrowser.append("[" + self.update_time() + "]" + "未选择点云!" )

    def saveProjectAs(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if not selected_items:
            return
        # 获取选中节点的数据
        current_item = selected_items[0]
        file_path = current_item.data(0, 32)
        if file_path:
            # 假设项目名称存储在第一列的文本中
            project_name = current_item.text(0)
            # 获取项目文件夹路径
            project_folder = file_path
            # 选择保存项目的目录
            save_dir, _ = QFileDialog.getSaveFileName(self, "选择保存项目的目录", "")
            if save_dir:
                # 创建项目文件夹
                project_save_path = os.path.join(save_dir, project_name)
                try:
                    shutil.copytree(project_folder, project_save_path)
                    self.textBrowser.append("[" + self.update_time() + "]" + "保存项目成功：" + project_save_path)
                except Exception as e:
                    self.textBrowser.append("[" + self.update_time() + "]" + "保存项目失败：" + str(e))

    def deletePointCloud(self, item):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            file_path = current_item.data(0, 32)

            if file_path:
                # 递归删除子节点的点云
                self.delete_children_point_cloud(current_item)
                # 从树形控件中移除节点
                parent_item = current_item.parent()
                if parent_item:
                    parent_item.removeChild(current_item)
                else:
                    self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(current_item))
                if file_path in self.point_cloud_dict:
                    # 从字典中获取点云对象和显示对象
                    point_cloud, plot = self.point_cloud_dict[file_path]
                    # 在OpenGL窗口中移除显示对象
                    self.graphicsView.removeItem(plot)
                    # 从字典中移除点云对象和显示对象
                    del self.point_cloud_dict[file_path]
                # QMessageBox.information(self, "删除成功", "文件已成功删除！")

    def delete_children_point_cloud(self, parent_item):
        # 递归删除子节点的点云
        child_count = parent_item.childCount()
        for i in range(child_count):
            child_item = parent_item.child(i)
            child_path = child_item.data(0, 32)
            if child_path in self.point_cloud_dict:
                # 从字典中获取点云对象和显示对象
                point_cloud, plot = self.point_cloud_dict[child_path]
                # 在OpenGL窗口中移除显示对象
                self.graphicsView.removeItem(plot)
                # 从字典中移除点云对象和显示对象
                del self.point_cloud_dict[child_path]

            # 递归删除子节点的子节点
            self.delete_children_point_cloud(child_item)
    def set_all_items_collapsed(self, item):
        stack = [item]
        while stack:
            current_item = stack.pop()
            current_item.setExpanded(False)
            for i in range(current_item.childCount()):
                child_item = current_item.child(i)
                stack.append(child_item)

    def refreshTree(self):
        # 清除之前的显示
        # self.graphicsView.clear()
        # self.point_cloud_dict = {}
        # self.treeWidget.clear()  # 清空树形控件
        # 获取根节点的路径
        root_paths = self.get_all_root_paths()
        # 重新添加父节点到树形控件中
        self.treeWidget.clear()
        for project_dir in root_paths:
            # 获取项目名称
            project_name = os.path.basename(project_dir)
            self.textBrowser.append("[" + self.update_time() + "]" + "打开项目:" + project_dir)
            # 递归遍历项目文件夹，添加子节点
            # self.traverseFolder(project_dir, project_item)
            # 判断是文件还是文件夹
            if os.path.isdir(project_dir):
                # 递归遍历项目文件夹，添加子节点
                # 在树形控件中添加项目节点
                project_item = QTreeWidgetItem(self.treeWidget)
                project_item.setText(0, project_name)
                project_item.setData(0, 32, project_dir)  # 存储项目文件夹路径
                self.traverseFolder(project_dir, project_item)
            elif project_dir.lower().endswith(".ply"):
                # 直接导入的.ply文件，添加到"point_cloud"节点下
                # self.add_ply_to_tree(project_dir, self.treeWidget)
                # 获取文件名
                file_name = QFileInfo(project_dir).fileName()
                file_item = QTreeWidgetItem(self.treeWidget)
                file_item.setCheckState(0, Qt.Unchecked)  # 设置复选框为选中状态
                file_item.setText(0, file_name)
                file_item.setText(1, project_dir)
                # 将文件路径存储在自定义角色中
                # file_item.setData(0, Qt.UserRole, file_path)
                file_item.setData(0, 32, project_dir)  # 存储文件路径
            # 展开项目节点
            self.treeWidget.expandItem(project_item)

    def get_all_root_paths(self):
        root_paths = []
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            root_paths.append(self.get_root_path(item))
        return root_paths

    def get_root_path(self, item):
        parent_item = item.parent()
        if parent_item:
            # 递归获取父节点的路径，直到找到根节点
            return self.get_root_path(parent_item)
        else:
            # 返回根节点的路径
            return item.data(0, 32)

    def importPointCloud(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择点云文件", "", "点云文件 (*.pcd *.xyz *.ply)")
        if file_path:
            self.textBrowser.append("["+self.update_time()+"]"+"打开文件:"+file_path)
            # 获取文件名
            file_name = QFileInfo(file_path).fileName()
            # # 创建或找到名为point_cloud的父节点
            # point_cloud_item = None
            # for i in range(self.treeWidget.topLevelItemCount()):
            #     item = self.treeWidget.topLevelItem(i)
            #     if item.text(0) == "point_cloud":
            #         point_cloud_item = item
            #         break
            # if not point_cloud_item:
            #     point_cloud_item = QTreeWidgetItem(self.treeWidget)
            #     point_cloud_item.setText(0, "point_cloud")

            # 创建文件节点并添加到point_cloud的子节点中
            file_item = QTreeWidgetItem(self.treeWidget)
            file_item.setCheckState(0, Qt.Unchecked)  # 设置复选框为选中状态
            file_item.setText(0, file_name)
            file_item.setText(1, file_path)
            # 将文件路径存储在自定义角色中
            # file_item.setData(0, Qt.UserRole, file_path)
            file_item.setData(0, 32, file_path)  # 存储文件路径

    def createProject(self):
        project_name, ok = QInputDialog.getText(self, "输入项目名称", "项目名称")
        if not ok or project_name.strip() == "":
            return
        # 弹出文件选择对话框，选择保存项目的目录
        project_dir = QFileDialog.getExistingDirectory(self, "选择项目保存目录", "")
        if not project_dir:
            return
        # 检查保存的目录下是否已经存在同名的项目文件夹
        project_folder = os.path.join(project_dir, project_name)
        if os.path.exists(project_folder):
            QMessageBox.warning(self, "目录已存在",
                                "保存的目录下已经存在同名的项目文件夹，请重新输入项目名称或选择其他目录!")
            return
        # 扫描当前树形结构，检查目录是否已经打开
        existing_item = self.findItemByPath(project_dir)
        if existing_item:
            # 在已存在的目录下创建项目文件夹
            project_folder = os.path.join(project_dir, project_name)
            os.makedirs(project_folder)
            # 在已存在的目录下添加新项目节点
            project_item = QTreeWidgetItem(existing_item)
            project_item.setText(0, project_name)
            project_item.setData(0, 32, project_folder)  # 存储项目文件夹路径
            self.textBrowser.append("[" + self.update_time() + "]" + "新建项目:" + project_folder)
            # 将项目名称添加到已存在的项目集合中
            self.existingProjects.add(project_name)
            # 展开项目节点
            self.treeWidget.expandItem(existing_item)
        else:
            # 创建项目文件夹
            project_folder = os.path.join(project_dir, project_name)
            os.makedirs(project_folder)
            # 在树形控件中添加新项目节点
            project_item = QTreeWidgetItem(self.treeWidget)
            project_item.setText(0, project_name)
            project_item.setData(0, 32, project_folder)  # 存储项目文件夹路径
            self.textBrowser.append("[" + self.update_time() + "]" + "新建项目:" + project_folder)
            # 将项目名称添加到已存在的项目集合中
            self.existingProjects.add(project_name)
            # 展开项目节点
            self.treeWidget.expandItem(project_item)

    def findItemByPath(self, path):
        # 在树形控件中查找指定路径的节点
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if item.data(0, 32) == path:
                return item
            result = self.findItemByPathRecursive(item, path)
            if result:
                return result
        return None

    def findItemByPathRecursive(self, parent_item, path):
        # 在树形控件中递归查找指定路径的节点
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            if item.data(0, 32) == path:
                return item
            result = self.findItemByPathRecursive(item, path)
            if result:
                return result
        return None

    def traverseFolder(self, folder_path, parent_item):
        # 递归遍历文件夹
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isdir(file_path):
                # 添加子文件夹节点
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, file_name)
                child_item.setData(0, 32, file_path)  # 存储文件夹路径
                child_item.setData(0, Qt.UserRole, file_path)
                # child_item.setFirstColumnSpanned(True)  # 设置子节点在第一列上不跨越父节点
                self.traverseFolder(file_path, child_item)
            else:
                # 添加文件节点
                file_item = QTreeWidgetItem(parent_item)
                file_item.setText(0, file_name)
                file_item.setText(1, file_path)
                file_item.setData(0, 32, file_path)  # 存储文件路径
                # 判断是否为.ply文件并在其前添加复选框
                if file_name.lower().endswith('.ply'):
                    # checkbox = QtWidgets.QCheckBox()
                    # checkbox.setCheckState(0, Qt.Unchecked)  # 设置复选框为未选中状态
                    # self.treeWidget.setItemWidget(file_item, checkbox)
                    file_item.setCheckState(0, Qt.Unchecked)  # 设置复选框为选中状态

    def openProject(self):
        # 弹出文件选择对话框，选择要打开的项目文件夹
        project_dir = QFileDialog.getExistingDirectory(self, "打开项目","")
        if not project_dir:
            return
         # 检查是否已经打开了该项目文件夹
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if item.data(0, 32) == project_dir:
                QMessageBox.warning(self, "项目已打开", "所选项目已经打开")
                return
        # 获取项目名称
        project_name = os.path.basename(project_dir)
        self.textBrowser.append("["+self.update_time()+"]"+"打开项目:"+project_dir)
        # 在树形控件中添加项目节点
        project_item = QTreeWidgetItem(self.treeWidget)
        project_item.setText(0, project_name)
        project_item.setData(0, 32, project_dir)  # 存储项目文件夹路径


        # 递归遍历项目文件夹，添加子节点
        self.traverseFolder(project_dir, project_item)
        # 展开项目节点
        self.treeWidget.expandItem(project_item)

    def itemStateChanged(self, item, column):
        if item.checkState(column) == Qt.Checked:
            # 复选框被选中，执行打开点云显示的操作
            file_path = item.text(1)
            self.textBrowser.append("["+self.update_time()+"]"+"正在渲染点云："+file_path)
            self.openPointCloud(file_path)
        else:
            # 复选框被取消选中，执行关闭当前显示的操作
            # self.textBrowser.append("--关闭当前显示--")
            self.closePointCloud(item)
            file_path = item.text(1)
            if file_path in self.bbox_dict:
                bbox_plot = self.bbox_dict[file_path]
                self.graphicsView.removeItem(bbox_plot)
                del self.bbox_dict[file_path]
                axis = self.axis_dict[file_path]
                self.graphicsView.removeItem(axis)
                del self.axis_dict[file_path]

    def show_axis_with_point_cloud(self):
        # 移除之前的坐标轴对象
        if self.axis is not None:
            self.graphicsView.removeItem(self.axis)
        if self.point_cloud_dict:
            # 获取最新的点云对象
            latest_point_cloud = next(reversed(self.point_cloud_dict.values()))[0]
            # print(latest_point_cloud)
            if latest_point_cloud is not None:
                # 获取点云的包围盒
                bbox = latest_point_cloud.get_axis_aligned_bounding_box()
                # 计算包围盒的尺寸
                bbox_size = np.abs(bbox.max_bound - bbox.min_bound)
                # 创建坐标轴对象，并根据包围盒尺寸设置坐标轴大小
                self.axis = gl.GLAxisItem()
                self.axis.setSize(bbox_size[1]*0.7, bbox_size[1]*0.7, bbox_size[1]*0.7)
                # 将新的坐标轴添加到 OpenGL 窗口中
                self.graphicsView.addItem(self.axis)
            else:
                self.axis = gl.GLAxisItem()
                self.axis.setSize(2000,2000,2000)
                # 将新的坐标轴添加到 OpenGL 窗口中
                self.graphicsView.addItem(self.axis)
        else:
            self.axis = gl.GLAxisItem()
            self.axis.setSize(2000, 2000, 2000)
            # 将新的坐标轴添加到 OpenGL 窗口中
            self.graphicsView.addItem(self.axis)

    def color_mapping(self, np_points):
        # zhot_colors = np.zeros([np_points.shape[0], 3])
        z_values = np_points[:, 2]
        # z_max = np.max(z_values)
        # z_min = np.min(z_values)
        # delta_z = abs(z_max - z_min) / (255 * 2)
        # # 计算颜色值，使用NumPy的广播功能进行向量化操作
        # color_n = (z_values - z_min) / delta_z
        # zhot_colors[:, 0] = np.where(color_n <= 255, 0, (color_n - 255) / 255)
        # zhot_colors[:, 1] = np.where(color_n <= 255, 1 - color_n / 255, 0)
        # zhot_colors[:, 2] = np.where(color_n <= 255, 1, 1)
        # return colors
        zhot_colors = plt.get_cmap('hsv')((z_values - z_values.min()) / (z_values.max() - z_values.min()))
        zhot_colors = zhot_colors[:, :3]
        # # 获取 z 轴排序后的索引
        sorted_indices = np.argsort(z_values)
        # 根据排序后的索引对颜色重新排列
        sorted_colors = zhot_colors[sorted_indices]
        # 将颜色值缩放到 0-1 范围
        # norm = mpl.colors.Normalize(vmin=z_min, vmax=z_max)
        # sorted_colors = norm(sorted_colors)
        return sorted_colors, zhot_colors

    def colorbar(self,np_points):
        z_values = np_points[:, 2]
        z_max = np.max(z_values)
        z_min = np.min(z_values)
        # print(z_max)
        colors,_ = self.color_mapping(np_points)
        cmap = mpl.colors.ListedColormap(colors)
        plt.clf()
        plt.axis('off')
        ax3 = plt.axes([0, 0.25, 0.15, 0.6])  # 四个参数分别是左、下、宽、长
        norm1 = mpl.colors.Normalize(vmin=z_min, vmax=z_max)
        im1 = mpl.cm.ScalarMappable(norm=norm1, cmap=cmap)
        bounds = np.linspace(z_min, z_max, 11)
        # bounds = np.linspace(-2000, 2000, 11)
        cbar1 = plt.colorbar(im1, ax3, ticks=bounds, format='%.1f')
        cbar1.ax.set_title("h/(mm)", fontsize=8, loc='left',color='#ffdb3a')
        cbar1.ax.tick_params(labelsize=7,labelcolor='#ffdb3a',color='#ffdb3a')
        # display the plot
        self.canvas.draw()

    def openPointCloud(self, file_path):
        # 打开点云显示的函数
        # print("打开点云显示:", file_path)
        if file_path in self.point_cloud_dict:
            # 如果当前要渲染的点云路径已经存在于字典中，则直接从字典中获取点云对象并显示
            point_cloud, plot = self.point_cloud_dict[file_path]
            self.graphicsView.addItem(plot)
        point_cloud = o3d.io.read_point_cloud(file_path)
        if point_cloud is not None:
            np_points = np.asarray(point_cloud.points)
            # print("1")
            # np_points = np.asarray(point_cloud.points)
            plot = gl.GLScatterPlotItem()
            bbox = point_cloud.get_axis_aligned_bounding_box()
            # print("-2",bbox)
            bbox_size = np.array(bbox.get_max_bound()) - np.array(bbox.get_min_bound())
            bbox_center = (bbox.get_max_bound() + bbox.get_min_bound()) / 2
            center = np.mean(np_points, axis=0)
            # 将数据平移到中心位置
            # np_points -= bbox_center
            np_points[:, :2] -= bbox_center[:2]
            # 根据高度生成颜色
            _,colors = self.color_mapping(np_points)
            # print("3")
            # 设置显示数据
            plot.setData(pos=np_points, color=colors, size=0.1, pxMode=False)  # 0.1表示点的大小
            # self.show_axis_with_point_cloud()
            # 将点云对象和绘制对象（plot）组成一个元组，添加到字典中，使用文件路径作为键
            self.point_cloud_dict[file_path] = (point_cloud, plot)
            # 显示点云
            self.graphicsView.addItem(plot)
            self.colorbar(np_points)
            # print("4")
            self.textBrowser.append("["+self.update_time()+"]"+file_path+"点云可视化完成")
        else:
            self.textBrowser.clear()
            self.textBrowser.append("["+self.update_time()+"]"+"未选择点云")


    def closePointCloud(self,item):
        # 关闭当前显示的函数
        file_path = item.text(1)
        if file_path in self.point_cloud_dict:
            plt.clf()
            self.canvas.draw()
            # 获取最新的点云对象
            # latest_point_cloud = next(iter(self.point_cloud_dict.values()))[0]
            # 从字典中获取点云对象和显示对象
            point_cloud, plot = self.point_cloud_dict[file_path]
            # 在OpenGL窗口中移除显示对象
            self.graphicsView.removeItem(plot)
            # 从字典中移除点云对象和显示对象
            del self.point_cloud_dict[file_path]

    def importCSVToProject(self):
        # 检查是否有新建的项目
        if self.treeWidget.topLevelItemCount() == 0:
            QMessageBox.warning(self, "请先新建项目", "请先新建或选择项目，然后再导入CSV文件!")
            return
        # 获取当前选中的项目节点
        selected_items = self.treeWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "请选择项目", "请选择要导入CSV文件的项目")
            return
        # 获取当前选中的项目节点
        current_item = selected_items[0]
        # 打开文件选择对话框，选择要导入的CSV文件
        file_path, _ = QFileDialog.getOpenFileName(self, "选择CSV文件", "", "CSV Files (*.csv)")
        # 用户选择了文件
        if file_path:
            self.textBrowser.append("[" + self.update_time() + "]" + "数据提取：" + file_path)
            # 获取文件名
            file_name = os.path.basename(file_path)
            # 获取项目文件夹路径
            project_dir = current_item.data(0, 32)
            # 将CSV文件复制到项目文件夹中
            destination_file_path = os.path.join(project_dir, file_name)
            copyfile(file_path, destination_file_path)
            # 在树形控件中添加新的子节点，表示导入的CSV文件
            csv_item = QTreeWidgetItem(current_item)
            csv_item.setText(0, file_name)
            csv_item.setData(0, 32, destination_file_path)  # 存储文件路径
            self.textBrowser.append("["+self.update_time()+"]"+"CSV文件已导入到项目：" + current_item.text(0))

    def data_preprocessing(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            file_path = current_item.data(0, 32)
            if file_path:
                if file_path.lower().endswith(".csv"):
                    x_range = range(1, 2964)
                    y_range = range(1, 1201)
                    # 从 CSV 文件中导入 z 坐标
                    df = pd.read_csv(file_path, skiprows=27, header=None)
                    df = df.iloc[:, :2963]
                    df = df.iloc[::2]

                    # 检查 CSV 文件的维度是否与坐标范围匹配
                    if df.shape != (1200, 2963):
                        self.textBrowser.append("[" + self.update_time() + "]" + "请选择正确的Csv文件！")
                        return
                    # 创建坐标列表
                    coordinates = []
                    # 将数据框转换为 NumPy 数组
                    data_array = df.values
                    # 遍历 x 和 y 坐标范围
                    for x in x_range:
                        for y in y_range:
                            # 获取对应的 z 坐标值
                            z = data_array[y - 1, x - 1]  # 坐标从 1 开始，而索引从 0 开始，因此要减 1
                            # 创建包含 x、y、z 坐标的元组，并添加到坐标列表中
                            coordinates.append((-37 * x + 1518, -37 * y + 637, z))
                    # 创建点云对象
                    point_cloud = o3d.geometry.PointCloud()
                    # 从之前生成的坐标列表中提取 x、y、z 坐标值
                    # points = np.array(coordinates)
                    points = np.array([coord for coord in coordinates])[:, :3]
                    # print(points.size)
                    # self.textBrowser.append(str(points.size))
                    # 设置点云的坐标值
                    point_cloud.points = o3d.utility.Vector3dVector(points)

                    # 获取当前CSV文件的目录和文件名
                    csv_dir = os.path.dirname(file_path)
                    csv_filename = os.path.basename(file_path)
                    # 构造保存处理结果的PLY文件路径
                    ply_filename = f"processed_{csv_filename[:-4]}.ply"  # 移除.csv后缀，并加上前缀
                    ply_file_path = os.path.join(csv_dir, ply_filename)
                    o3d.io.write_point_cloud(ply_file_path, point_cloud)
                    # 在树形控件中添加新的子节点，表示导入的PLY文件
                    ply_item = QTreeWidgetItem(current_item.parent())
                    ply_item.setText(0, os.path.basename(ply_file_path))
                    ply_item.setData(0, 32, ply_file_path)  # 存储文件路径
                    ply_item.setText(1, ply_file_path)
                    ply_item.setCheckState(0, Qt.Unchecked)  # 设置复选框为选中状态
                    self.textBrowser.append("[" + self.update_time() + "]" + file_path + "原始数据处理完成")
                else:
                    self.textBrowser.append("[" + self.update_time() + "]" + "请选择正确的Csv文件！")
        else:
            self.textBrowser.append("[" + self.update_time() + "]" + "未选择原始Csv文件")

            # -----------------------滤波-------------------------------------
    def dialog_filter_voxel(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            self.VoxelDialog.show()
            if(self.VoxelDialog.exec_()):
                self.open3d_function_filter_voxel(self.VoxelDialog.get_data())
    def open3d_function_filter_voxel(self,data_str):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            file_path = current_item.data(0, 32)
            if file_path:
                if file_path.lower().endswith(".ply"):
                    point_cloud = o3d.io.read_point_cloud(file_path)
                    self.textBrowser.append("[" + self.update_time() + "]"+"体素下采样：体素栅格为："+data_str)
                    point_cloud = point_cloud.voxel_down_sample(voxel_size=float(data_str))
                    # print(self.pcd)
                    # 获取 Numpy 数组
                    np_points = np.asarray(point_cloud.points)
                    self.textBrowser.append("[" + self.update_time() + "]"+ file_path+ "体素下采样完成")
                    # 获取当前点云文件的目录和文件名
                    csv_dir = os.path.dirname(file_path)
                    csv_filename = os.path.basename(file_path)
                    # 构造保存处理结果的PLY文件路径
                    ply_filename = f"filter_voxel_{csv_filename[:-4]}.ply"
                    ply_file_path = os.path.join(csv_dir, ply_filename)
                    o3d.io.write_point_cloud(ply_file_path, point_cloud)
                    # 添加新的子节点表示导入的PLY文件
                    ply_item = QTreeWidgetItem(current_item.parent() if current_item.parent() else self.treeWidget)
                    ply_item.setText(0, os.path.basename(ply_file_path))
                    ply_item.setData(0, 32, ply_file_path)  # 存储文件路径
                    ply_item.setText(1, ply_file_path)
                    ply_item.setCheckState(0, Qt.Unchecked)  # 设置复选框为未选中状态
                    # 将新的子节点添加到当前选中节点的父节点或者根节点下
                    if current_item.parent():
                        current_item.parent().addChild(ply_item)
                    else:
                        self.treeWidget.addTopLevelItem(ply_item)
                else:
                    self.textBrowser.append("[" + self.update_time() + "]" + "请选择正确的点云文件")
            else:
                self.textBrowser.append("[" + self.update_time() + "]" + "请选择点云")
        else:
            self.textBrowser.append("[" + self.update_time() + "]" + "请选择点云")

    def dialog_filter_uniform(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            self.UniformDialog.show()
            if(self.UniformDialog.exec_()):
                self.open3d_function_filter_uniform(self.UniformDialog.get_data())
    def open3d_function_filter_uniform(self,data_str):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            file_path = current_item.data(0, 32)
            if file_path:
                if file_path.lower().endswith(".ply"):
                    point_cloud = o3d.io.read_point_cloud(file_path)
                    self.textBrowser.append("[" + self.update_time() + "]"+"均匀下采样：采样参数为："+data_str)
                    point_cloud = point_cloud.uniform_down_sample(every_k_points=int(data_str))
                    # print(self.pcd)
                    # 获取 Numpy 数组
                    np_points = np.asarray(point_cloud.points)
                    self.textBrowser.append("[" + self.update_time() + "]"+file_path+"均匀下采样完成，点云数量为：" + str(int(np_points.size / 3)))
                    # 获取当前点云文件的目录和文件名
                    csv_dir = os.path.dirname(file_path)
                    csv_filename = os.path.basename(file_path)
                    # 构造保存处理结果的PLY文件路径
                    ply_filename = f"filter_uniform_{csv_filename[:-4]}.ply"
                    ply_file_path = os.path.join(csv_dir, ply_filename)
                    o3d.io.write_point_cloud(ply_file_path, point_cloud)
                    # 添加新的子节点表示导入的PLY文件
                    ply_item = QTreeWidgetItem(current_item.parent() if current_item.parent() else self.treeWidget)
                    ply_item.setText(0, os.path.basename(ply_file_path))
                    ply_item.setData(0, 32, ply_file_path)  # 存储文件路径
                    ply_item.setText(1, ply_file_path)
                    ply_item.setCheckState(0, Qt.Unchecked)  # 设置复选框为未选中状态
                    # 将新的子节点添加到当前选中节点的父节点或者根节点下
                    if current_item.parent():
                        current_item.parent().addChild(ply_item)
                    else:
                        self.treeWidget.addTopLevelItem(ply_item)
                else:
                    self.textBrowser.append("[" + self.update_time() + "]" + "请选择正确的点云文件")
            else:
                self.textBrowser.append("[" + self.update_time() + "]" + "请选择点云")
        else:
            self.textBrowser.append("[" + self.update_time() + "]" + "请选择点云")

    def dialog_filter_random(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            self.RandomDialog.show()
            if (self.RandomDialog.exec_()):
                self.open3d_function_filter_random(self.RandomDialog.get_data())

    def open3d_function_filter_random(self, data_str):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            file_path = current_item.data(0, 32)
            if file_path:
                if file_path.lower().endswith(".ply"):
                    point_cloud = o3d.io.read_point_cloud(file_path)
                    self.textBrowser.append("[" + self.update_time() + "]" + "随机下采样：采样比例为：" + data_str)
                    point_cloud = point_cloud.random_down_sample(sampling_ratio=float(data_str))
                    # print(self.pcd)
                    # 获取 Numpy 数组
                    np_points = np.asarray(point_cloud.points)
                    self.textBrowser.append(
                        "[" + self.update_time() + "]" + file_path+ "均匀下采样完成，点云数量为：" + str(int(np_points.size / 3)))
                    # 获取当前点云文件的目录和文件名
                    csv_dir = os.path.dirname(file_path)
                    csv_filename = os.path.basename(file_path)
                    # 构造保存处理结果的PLY文件路径
                    ply_filename = f"filter_random_{csv_filename[:-4]}.ply"
                    ply_file_path = os.path.join(csv_dir, ply_filename)
                    o3d.io.write_point_cloud(ply_file_path, point_cloud)
                    # 添加新的子节点表示导入的PLY文件
                    ply_item = QTreeWidgetItem(current_item.parent() if current_item.parent() else self.treeWidget)
                    ply_item.setText(0, os.path.basename(ply_file_path))
                    ply_item.setData(0, 32, ply_file_path)  # 存储文件路径
                    ply_item.setText(1, ply_file_path)
                    ply_item.setCheckState(0, Qt.Unchecked)  # 设置复选框为未选中状态
                    # 将新的子节点添加到当前选中节点的父节点或者根节点下
                    if current_item.parent():
                        current_item.parent().addChild(ply_item)
                    else:
                        self.treeWidget.addTopLevelItem(ply_item)
                else:
                    self.textBrowser.append("[" + self.update_time() + "]" + "请选择正确的点云文件")
            else:
                self.textBrowser.append("[" + self.update_time() + "]" + "请选择点云")
        else:
            self.textBrowser.append("[" + self.update_time() + "]" + "请选择点云")

    def removeBBoxes(self):
        # 删除界面中显示的所有包裹框
        for bbox_plot in self.bbox_dict.values():
            self.graphicsView.removeItem(bbox_plot)
        # 清空字典
        self.bbox_dict.clear()

    def removeAxis(self):
        # 删除界面中显示的所有包裹框
        for axis in self.axis_dict.values():
            self.graphicsView.removeItem(axis)
        # 清空字典
        self.axis_dict.clear()

    def onItemSelected(self):
        # 获取当前选中的节点
        selected_items = self.treeWidget.selectedItems()
        # print("zheli")
        # print(selected_items)
        if selected_items:
            current_item = selected_items[0]
            file_path = current_item.data(0, 32)
            # print(file_path)
            if file_path and file_path.lower().endswith(".ply"):
                # 判断选中的点云是否在字典中
                if file_path in self.point_cloud_dict:
                    # 点云文件被选中
                    if current_item.checkState(0) == Qt.Checked:
                        self.removeBBoxes()
                        self.removeAxis()
                        # 如果点云在字典中，则获取对应的点云对象
                        point_cloud, _ = self.point_cloud_dict[file_path]
                        # print("kuang")
                        # 使用Open3D计算包裹框的尺寸和中心
                        bbox = point_cloud.get_axis_aligned_bounding_box()
                        # print("-2",bbox)
                        bbox_size = np.array(bbox.get_max_bound()) - np.array(bbox.get_min_bound())
                        bbox_center = (bbox.get_max_bound()+bbox.get_min_bound())/2+bbox.get_min_bound()
                        bbox_center[2] = ((bbox.get_max_bound()+bbox.get_min_bound())/2)[2]-bbox_size[2]/2
                        # print("-1", bbox_center)
                        # 将NumPy数组转换为QVector3D
                        bbox_size_qvec = QVector3D(*bbox_size)
                        # print("0", bbox_size_qvec)
                        bbox_center_qvec = QVector3D(*bbox_center)
                        # print("1",bbox_center_qvec)
                        # 在OpenGL窗口中绘制包裹框
                        bbox_plot = gl.GLBoxItem(size=bbox_size_qvec, glOptions='translucent', color=(255, 220, 0, 100))
                        bbox_plot.translate(bbox_center_qvec.x(), bbox_center_qvec.y(), bbox_center_qvec.z())
                        # 设置线条粗细为5（可以根据需要调整）
                        # gl.glLineWidth(5)
                        self.graphicsView.addItem(bbox_plot)
                        self.bbox_dict[file_path] = bbox_plot
                        # 计算包围盒尺寸中的最大值
                        max_size = max(bbox_size)
                        # 创建坐标轴对象，并根据包围盒尺寸设置坐标轴大小
                        axis = gl.GLAxisItem()
                        axis.setSize(max_size, max_size, max_size)
                        # grid_color = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
                        np_points = np.asarray(point_cloud.points)
                        # 将新的坐标轴添加到 OpenGL 窗口中
                        self.graphicsView.addItem(axis)
                        self.axis_dict[file_path] = axis
                        # print("坐标轴字典",self.axis_dict)
                        # self.show_axis_with_point_cloud()

                        self.colorbar(np_points)
                    else:
                        # 取消选择，删除包裹框
                        if file_path in self.bbox_dict:
                            # print("shanchu")
                            bbox_plot = self.bbox_dict[file_path]
                            self.graphicsView.removeItem(bbox_plot)
                            del self.bbox_dict[file_path]
                            axis = self.axis_dict[file_path]
                            self.graphicsView.removeItem(axis)
                            del self.axis_dict[file_path]
                else:
                    self.removeBBoxes()
                    self.removeAxis()
                # 读取点云数据
                point_cloud = o3d.io.read_point_cloud(file_path)
                if point_cloud is not None:
                    np_points = np.asarray(point_cloud.points)
                    num_points = np_points.shape[0]
                    # x_length = np.max(np_points[:, 0]) - np.min(np_points[:, 0])
                    # y_length = np.max(np_points[:, 1]) - np.min(np_points[:, 1])
                    # z_length = np.max(np_points[:, 2]) - np.min(np_points[:, 2])
                    center = np.mean(np_points, axis=0)
                    # 获取点云的包围盒
                    bbox = point_cloud.get_axis_aligned_bounding_box()
                    # print("2", bbox)
                    # 计算包围盒的尺寸
                    bbox_size = np.abs(bbox.max_bound - bbox.min_bound)
                    x_length = bbox_size[0]
                    y_length = bbox_size[1]
                    z_length = bbox_size[2]

                    box_center = (bbox.max_bound+bbox.min_bound)/2
                    # print(box_center)
                    # 在表格中显示相关信息
                    self.tableWidget.setRowCount(11)
                    self.tableWidget.setColumnCount(2)
                    self.tableWidget.verticalHeader().setVisible(False)
                    self.tableWidget.horizontalHeader().setVisible(False)
                    # self.tableWidget.setColumnWidth(0, 100)
                    # self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                    self.tableWidget.setShowGrid(True)
                    self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
                    self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
                    self.tableWidget.setColumnWidth(0, 75)
                    #    tableWidget是你控件的名字，这段代码添加到设置Ui中

                    self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

                    # self.tableWidget.setVerticalHeaderLabels(["点云个数", "包裹框尺寸", "包裹框中心"])
                    # self.tableWidget.setHorizontalHeaderLabels(["属性", "值"])
                    # 设置表格的大小策略为Expanding，让它填满可用空间
                    # self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    # self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
                    # 设置表头自适应内容
                    header = self.tableWidget.horizontalHeader()
                    # header.setSectionResizeMode(QHeaderView.ResizeToContents)
                    self.tableWidget.setItem(0, 0, QTableWidgetItem("属性"))
                    self.tableWidget.setItem(0, 1, QTableWidgetItem("值"))
                    # 合并第二行和第三行的单元格，设置标题为 "包裹框尺寸"
                    self.tableWidget.setSpan(2, 0, 3, 1)
                    self.tableWidget.setSpan(5, 0, 3, 1)
                    self.tableWidget.setSpan(8, 0, 3, 1)
                    self.tableWidget.setItem(1, 0, QTableWidgetItem("点云个数"))
                    self.tableWidget.setItem(5, 0, QTableWidgetItem("包络框维度"))
                    # self.tableWidget.setItem(2, 0, QTableWidgetItem("y"))
                    # self.tableWidget.setItem(3, 0, QTableWidgetItem("z"))
                    # 合并第五行和第六行的单元格，设置标题为 "包裹框中心"
                    self.tableWidget.setItem(2, 0, QTableWidgetItem("全局中心"))
                    self.tableWidget.setItem(8, 0, QTableWidgetItem("包络框中心"))
                    # self.tableWidget.setItem(5, 0, QTableWidgetItem("y"))
                    # self.tableWidget.setItem(6, 0, QTableWidgetItem("z"))
                    # self.tableWidget.setVerticalHeaderLabels(["点云个数", "包裹框尺寸", "包裹框中心"])
                    self.tableWidget.setItem(1, 1, QTableWidgetItem(str(num_points)))
                    self.tableWidget.setItem(5, 1, QTableWidgetItem("X: "+"{:.2f}".format(x_length)))
                    self.tableWidget.setItem(6, 1, QTableWidgetItem("Y: "+"{:.2f}".format(y_length)))
                    self.tableWidget.setItem(7, 1, QTableWidgetItem("Z: "+"{:.2f}".format(z_length)))
                    self.tableWidget.setItem(2, 1, QTableWidgetItem("X: "+"{:.2f}".format(center[0])))
                    self.tableWidget.setItem(3, 1, QTableWidgetItem("Y: "+"{:.2f}".format(center[1])))
                    self.tableWidget.setItem(4, 1, QTableWidgetItem("Z: "+"{:.2f}".format(center[2])))
                    self.tableWidget.setItem(8, 1, QTableWidgetItem("X: " + "{:.2f}".format(box_center[0])))
                    self.tableWidget.setItem(9, 1, QTableWidgetItem("Y: " + "{:.2f}".format(box_center[1])))
                    self.tableWidget.setItem(10, 1, QTableWidgetItem("Z: " + "{:.2f}".format(box_center[2])))
        else:
            # 取消选择，删除包裹框
            # 删除所有的包裹框
            self.removeBBoxes()
            self.removeAxis()

    def update_time(self):
        # 获取当前时间并更新界面显示
        now_time = datetime.now()
        now_time_str = now_time.strftime("%Y-%m-%d %H:%M:%S")
        # 在状态栏中显示时间
        self.statusBar.showMessage(now_time_str)
        return now_time_str

    def onOgriginThemeClicked(self):
        # 切换到原生主题
        self.graphicsView.setBackgroundColor(145, 158, 164)
        self.graphicsView_4.setBackgroundColor(255, 255, 255)
        self.figure.set_facecolor("#919ea4")
        self.tab_3.setStyleSheet("background-color: #919ea4;")
        self.canvas.draw()
        app.setStyleSheet("")

    def onLightThemeClicked(self):
        # 切换到浅色主题
        # 切换到浅色主题（恢复到原生主题）
        self.graphicsView.setBackgroundColor(145, 158, 164)
        self.graphicsView_4.setBackgroundColor(255, 255, 255)
        self.figure.set_facecolor("#919ea4")
        self.tab_3.setStyleSheet("background-color: #919ea4;")
        self.canvas.draw()
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))


    def onDarkThemeClicked(self):
        # 切换到深色主题
        self.graphicsView.setBackgroundColor(3, 32, 48)
        self.graphicsView_4.setBackgroundColor(0, 0, 0)
        self.figure.set_facecolor('#032030')
        self.tab_3.setStyleSheet("background-color: #032030;")
        self.canvas.draw()
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
#体素
class Filter_voxel(QtWidgets.QDialog, Ui_Dialog_voxel):
    signal=QtCore.pyqtSignal(str)
    def __init__(self):
        super(Filter_voxel, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        # self.accepted.connect(self.emit_slot)
    def get_data(self):
        data_str=self.lineEdit.text()
        return data_str
#均匀
class Filter_uniform(QtWidgets.QDialog, Ui_Dialog_uniform):
    signal=QtCore.pyqtSignal(str)
    def __init__(self):
        super(Filter_uniform, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        # self.accepted.connect(self.emit_slot)
    def get_data(self):
        data_str=self.lineEdit.text()
        return  data_str
#随机
class Filter_random(QtWidgets.QDialog, Ui_Dialog_random):
    signal=QtCore.pyqtSignal(str)
    def __init__(self):
        super(Filter_random, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        # self.accepted.connect(self.emit_slot)
    def get_data(self):
        data_str=self.lineEdit.text()
        return  data_str

import qdarkstyle
if __name__=="__main__":
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))
    window = MainWindow()
    sys.exit(app.exec_())
