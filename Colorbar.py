import open3d as o3d
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import matplotlib as mpl



def colorbar(path):

    fig = plt.figure(figsize = (12, 8))
    ax = plt.axes(projection ="3d")
    plt.axis('off')
    # Creating the 3D plot
    # sctt = ax.scatter3D(x, y, z,alpha = 0.8,c = C,marker =',')
    plt.gca().set_box_aspect((12, 7, 35))# 缩放比例
    ax.view_init(0, -90)
    ax3 = fig.add_axes([0.7, 0.1, 0.01, 0.8]) # 四个参数分别是左、下、宽、长
    norm1 = mpl.colors.Normalize(vmin=-0.10, vmax=0.10)
    im1 = mpl.cm.ScalarMappable(norm=norm1, cmap="jet")
    bounds = np.linspace(-0.10, 0.10, 11)
    cbar1 = fig.colorbar(im1, ax3,ticks=bounds,format='%.3f')
    font = {'family': 'serif',
    'color' : 'k',
    'weight' : 'normal',
    'size' : 10
    }
    cbar1.ax.set_title('ColorBar',fontdict=font)
    # display the plot
    plt.show()

if __name__ == '__main__':
    colorbar("data/test.ply")