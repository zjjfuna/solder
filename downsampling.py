import os
from PyQt5 import QtWidgets, QtCore
import numpy as np
import open3d as o3d
from PyQt5 import Qt
from PyQt5.QtWidgets import QTreeWidgetItem

from filter_random import Ui_Dialog_random
from filter_uniform import Ui_Dialog_uniform
from filter_voxel import Ui_Dialog_voxel


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
class DownSampling:
    def __init__(self, treeWidget):
        self.treeWidget = treeWidget
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
                    self.textBrowser.append("[" + self.update_time() + "]"+"体素下采样")
                    self.textBrowser.append("[" + self.update_time() + "]" + "体素栅格为："+data_str)
                    point_cloud = point_cloud.voxel_down_sample(voxel_size=float(data_str))
                    # print(self.pcd)
                    # 获取 Numpy 数组
                    np_points = np.asarray(point_cloud.points)
                    self.textBrowser.append("[" + self.update_time() + "]"+"体素下采样完成，点云数量为：" + str(int(np_points.size / 3)))
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