from __future__ import absolute_import, division, print_function
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
