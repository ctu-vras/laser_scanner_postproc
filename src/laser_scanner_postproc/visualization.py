from __future__ import absolute_import, division, print_function
import matplotlib
matplotlib.use('Agg')
import matplotlib.ticker
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.recfunctions import structured_to_unstructured
from PIL import Image
import open3d as o3d


def to_open3d_cloud(cloud):
    assert isinstance(cloud, np.ndarray)

    pcd = o3d.geometry.PointCloud()

    if not cloud.dtype.names:
        assert cloud.shape[1] == 3
        pcd.points = o3d.utility.Vector3dVector(cloud)
        return pcd

    xyz = structured_to_unstructured(cloud.ravel()[['x', 'y', 'z']])
    pcd.points = o3d.utility.Vector3dVector(xyz)

    if 'r' in cloud.dtype.names:
        rgb = structured_to_unstructured(cloud.ravel()[['r', 'g', 'b']])
        rgb = rgb.astype(dtype=np.float32) / 255.
        pcd.colors = o3d.utility.Vector3dVector(rgb)

    return pcd


def show_cloud(cloud):
    cloud = to_open3d_cloud(cloud)
    o3d.visualization.draw_geometries([cloud])


def to_rgb_image(cloud):
    rgb = structured_to_unstructured(cloud[['r', 'g', 'b']])
    return rgb


def show_rgb_image(cloud, rotate=0):
    assert cloud.ndim == 2
    rgb = to_rgb_image(cloud)
    if rotate == 90.0:
        rgb = rgb.transpose((1, 0, 2))[::-1]
    Image.fromarray(rgb).show()


def show_ortho(cloud, axes='xy', grid=10.0):
    cloud = cloud.ravel()
    x = cloud[axes[0]]
    y = cloud[axes[1]]
    rgb = structured_to_unstructured(cloud[['r', 'g', 'b']]) / 255.
    xlim = [np.floor(x.min() / grid) * grid, np.ceil(x.max() / grid) * grid]
    ylim = [np.floor(y.min() / grid) * grid, np.ceil(y.max() / grid) * grid]
    nx = round((xlim[1] - xlim[0]) / grid)
    ny = round((ylim[1] - ylim[0]) / grid)
    xticks = np.linspace(xlim[0], xlim[1], nx + 1)
    yticks = np.linspace(ylim[0], ylim[1], ny + 1)
    fig, ax = plt.subplots(1, 1, figsize=(nx, ny))
    ax.scatter(x, y, s=1, c=rgb, marker=',', lw=0, alpha=0.5)
    ax.grid()
    ax.axis('equal')
    ax.set_xlabel('%s [m]' % axes[0])
    ax.set_ylabel('%s [m]' % axes[1])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    plt.tight_layout()
    return fig
