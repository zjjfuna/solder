import os
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QDialog, QProgressDialog, QLabel, QVBoxLayout, QDesktopWidget, \
    QTreeWidgetItem, QMainWindow
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtCore import Qt, QFileInfo, QThread
import open3d as o3d
from pass_through import pass_through
def processdialog(self):
    # 创建QProgressDialog
    progress_dialog = QProgressDialog(self)
    # 获取主窗口的位置和大小
    main_window_geometry = self.geometry()
    main_window_x = main_window_geometry.x()
    main_window_y = main_window_geometry.y()
    main_window_width = main_window_geometry.width()
    main_window_height = main_window_geometry.height()
    # 计算进度条位置
    progress_width = 150
    progress_height = 30
    progress_x = main_window_x + (main_window_width - progress_width) // 2
    progress_y = main_window_y + (main_window_height - progress_height) // 2
    # 设置进度条位置和大小
    progress_dialog.setGeometry(progress_x, progress_y, progress_width, progress_height)

    progress_dialog.setWindowTitle("请等待")
    progress_dialog.setLabelText("点云预处理中，请稍候...")
    progress_dialog.setCancelButton(None)  # 不显示取消按钮

    # progress_dialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint)
    # progress_dialog.setEnabled(False)
    progress_dialog.setWindowModality(Qt.ApplicationModal)
    # progress_dialog.setFixedSize(240, 100)
    # 设置进度条标题文字居中的样式表
    style_sheet = "QLabel#qt_spinbox_label {qproperty-alignment: AlignCenter; font-size: 18pt;}"
    progress_dialog.setStyleSheet(style_sheet)
    # 设置循环转圈圈的样式
    progress_dialog.setRange(0, 0)
    # 显示进度条对话框
    progress_dialog.show()
    # 模拟一个耗时的任务
    # for i in range(50000 + 1):
        # 更新进度条
    # progress_dialog.setValue(i)
    # 让应用程序处理事件，以允许界面更新
    QApplication.processEvents()
    # 关闭进度条对话框
    return progress_dialog

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

def point_cloud_filter(self):
    # 获取当前选中的节点
    selected_items = self.treeWidget.selectedItems()
    if selected_items:
        current_item = selected_items[0]
        file_path = current_item.data(0, 32)
        if file_path:
            if file_path.lower().endswith(".ply"):
                point_cloud = o3d.io.read_point_cloud(file_path)
                # 进行直通滤波
                filtered1_point_cloud = pass_through(point_cloud, 0, 500, filter_value_name="z")
                # filtered_point_cloud = pass_through(point_cloud, -30000, 30000, filter_value_name="y")
                filtered_point_cloud = pass_through(filtered1_point_cloud, -50000, 50000, filter_value_name="x")
                # 可视化滤波后的点云
                # o3d.visualization.draw_geometries([filtered_point_cloud])
                # 获取当前点云文件的目录和文件名
                ply_dir = os.path.dirname(file_path)
                ply_filename = os.path.basename(file_path)
                # 构造保存处理结果的PLY文件路径
                ply_filename = f"preprocessed_{ply_filename[:-4]}.ply"
                ply_file_path = os.path.join(ply_dir, ply_filename)
                o3d.io.write_point_cloud(ply_file_path,  filtered_point_cloud)
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
                refreshTree(self)
                self.textBrowser.append("[" + self.update_time() + "]" + file_path + "点云预处理处理完成")
            else:
                self.textBrowser.append("[" + self.update_time() + "]" + "请选择正确的点云文件")
        else:
            self.textBrowser.append("[" + self.update_time() + "]" + "请选择点云")
    else:
        self.textBrowser.append("[" + self.update_time() + "]" + "请选择点云")

