import numpy as np
import open3d as o3d

def pass_through(cloud, limit_min, limit_max, filter_value_name="z"):
    """
    直通滤波
    :param cloud:输入点云
    :param limit_min: 滤波条件的最小值
    :param limit_max: 滤波条件的最大值
    :param filter_value_name: 滤波字段(x or y or z)
    :return: 位于[limit_min,limit_max]范围的点云
    """
    points = np.asarray(cloud.points)
    if filter_value_name == "x":
        ind = np.where((points[:, 0] >= limit_min) & (points[:, 0] <= limit_max))[0]
        x_cloud = cloud.select_by_index(ind)
        return x_cloud
    elif filter_value_name == "y":
        ind = np.where((points[:, 1] >= limit_min) & (points[:, 1] <= limit_max))[0]
        y_cloud = cloud.select_by_index(ind)
        return y_cloud
    elif filter_value_name == "z":
        ind = np.where((points[:, 2] >= limit_min) & (points[:, 2] <= limit_max))[0]
        z_cloud = cloud.select_by_index(ind)
        return z_cloud

# # -------------------读取点云数据并可视化------------------------
# pcd = o3d.io.read_point_cloud("pointcloud data/RGBPoints(2).ply")
# filtered_cloud = pass_through(pcd,
#                               limit_min=1000,
#                               limit_max=2000,
#                               filter_value_name="z")
# o3d.visualization.draw_geometries([filtered_cloud], window_name="直通滤波")

