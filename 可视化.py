import tkinter as tk
from tkinter import filedialog
import open3d as o3d
import pandas as pd
import numpy as np
import pyglet

# 创建 Tkinter 应用程序窗口
window = tk.Tk()
window.title("点云可视化")
# 设置窗口的宽度和高度
window_width = 800
window_height = 600

# 获取屏幕的宽度和高度
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# 计算窗口的左上角坐标使其居中显示
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# 设置窗口的初始大小和位置
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 定义全局变量
point_cloud = None
# 定义导入 CSV 文件的回调函数
def import_csv():
    global point_cloud  # 声明 point_cloud 为全局变量
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        # 从 CSV 文件中导入 z 坐标
        df = pd.read_csv(file_path, skiprows=27, header=None)
        df = df.iloc[:, :2963]
        df = df.iloc[::2]

        # 创建坐标列表
        coordinates = []
        # 创建 x 和 y 坐标的范围
        x_range = range(1, 2964)
        y_range = range(1, 1201)
        # 将数据框转换为 NumPy 数组
        data_array = df.values
        # 遍历 x 和 y 坐标范围
        for x in x_range:
            for y in y_range:
                # 获取对应的 z 坐标值
                z = data_array[y - 1, x - 1]  # 坐标从 1 开始，而索引从 0 开始，因此要减 1
                # 创建包含 x、y、z 坐标的元组，并添加到坐标列表中
                coordinates.append((-37 * x - 363, -37 * y + 37, z))

        # 创建点云对象
        point_cloud = o3d.geometry.PointCloud()
        # 从之前生成的坐标列表中提取 x、y、z 坐标值
        points = np.array([coord for coord in coordinates])[:, :3]
        # 设置点云的坐标值
        point_cloud.points = o3d.utility.Vector3dVector(points)


# 定义保存为 PLY 文件的回调函数
def save_ply():
    global point_cloud  # 声明 point_cloud 为全局变量
    if point_cloud:
        # 打开文件保存对话框
        save_file_path = filedialog.asksaveasfilename(defaultextension=".ply", filetypes=[("PLY Files", "*.ply")])
        if save_file_path:
            # 保存点云为 PLY 文件
            o3d.io.write_point_cloud(save_file_path, point_cloud)
    else:
        print("保存失败")

# 定义可视化点云的回调函数
def visualize_point_cloud():
    global point_cloud  # 声明 point_cloud 为全局变量
    if point_cloud:
        # 可视化点云
        o3d.visualization.draw_geometries([point_cloud])

    else:
        print("可视化失败")

# 创建按钮用于导入 CSV 文件
import_button = tk.Button(window, text="导入 CSV 文件", command=import_csv)
import_button.grid(row=0, column=0, padx=10, pady=10)

# 创建按钮用于可视化点云
visualize_button = tk.Button(window, text="可视化点云", command=visualize_point_cloud)
visualize_button.grid(row=0, column=1, padx=10, pady=10)

# 创建按钮用于保存为 PLY 文件
save_button = tk.Button(window, text="保存为 PLY 文件", command=save_ply)
save_button.grid(row=0, column=2, padx=10, pady=10)


# 运行 Tkinter 主循环
window.mainloop()
