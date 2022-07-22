from __future__ import absolute_import, division, print_function
import numpy as np
from numpy.lib.recfunctions import structured_to_unstructured, unstructured_to_structured


def transform_cloud(cloud, transform, inplace=False):
    if not inplace:
        cloud = cloud.copy()
    xyz = structured_to_unstructured(cloud[['x', 'y', 'z']])
    xyz = xyz.reshape((-1, 3))
    xyz = np.matmul(xyz, transform[:3, :3].T) + transform[:3, 3:].T
    xyz = xyz.astype(np.float32)
    xyz = unstructured_to_structured(xyz, names=['x', 'y', 'z'])
    xyz = xyz.reshape(cloud.shape)
    cloud[['x', 'y', 'z']] = xyz
    return cloud
