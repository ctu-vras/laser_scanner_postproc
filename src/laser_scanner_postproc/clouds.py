from __future__ import absolute_import, division, print_function
from .io import file_format, FileFormat, read, read_npy, read_npz, read_ptx, write, write_npy, write_npz, write_ptx
import multiprocessing as mp
import numpy as np
from numpy.lib.recfunctions import structured_to_unstructured, unstructured_to_structured

default_rng = np.random.default_rng(135)


class Keys(object):
    cloud = 'cloud'
    sensor_pose = 'sensor_pose'  # legacy
    sensor_to_cloud = 'sensor_to_cloud'
    cloud_pose = 'cloud_pose'  # legacy
    cloud_to_map = 'cloud_to_map'


def position(cloud):
    """Cloud to point positions (xyz)."""
    if cloud.dtype.names:
        x = structured_to_unstructured(cloud[['x', 'y', 'z']])
    else:
        x = cloud
    return x


def filter_box(cloud, min, max, log=False):
    """Keep points within the box."""
    assert isinstance(cloud, np.ndarray)
    min = np.asarray(min).reshape((1, -1))
    max = np.asarray(max).reshape((1, -1))
    assert np.all(min <= max)
    if np.all(min == -np.inf) and np.all(max == np.inf):
        return cloud

    cloud = cloud.ravel()
    x = position(cloud)
    mask = np.all(min <= x, axis=1) & np.all(x <= max, axis=1)
    print(cloud.shape, x.shape, min.shape, max.shape, mask.shape)

    if log:
        print('%.3f = %i / %i points kept (min %s, max %s).'
              % (mask.sum() / len(cloud), mask.sum(), len(cloud), min[0], max[0]))

    filtered = cloud[mask]
    return filtered


def filter_range(cloud, min, max, log=False):
    """Keep points within range interval."""
    assert isinstance(cloud, np.ndarray), type(cloud)
    assert isinstance(min, (float, int)), min
    assert isinstance(max, (float, int)), max
    assert min <= max, (min, max)
    min = float(min)
    max = float(max)
    if min <= 0.0 or max == np.inf:
        return cloud

    cloud = cloud.ravel()
    x = position(cloud)
    r = np.linalg.norm(x, axis=1)
    mask = (min <= r) & (r <= max)

    if log:
        print('%.3f = %i / %i points kept (range min %s, max %s).'
              % (mask.sum() / len(cloud), mask.sum(), len(cloud), min, max))

    filtered = cloud[mask]
    return filtered


def filter_grid(cloud, grid, keep='first', log=False, rng=default_rng):
    """Keep single point within each cell. Order is not preserved."""
    assert isinstance(cloud, np.ndarray)
    assert cloud.dtype.names
    assert isinstance(grid, (float, int)) and grid > 0.0
    assert keep in ('first', 'random', 'last')

    cloud = cloud.ravel()
    if keep == 'first':
        pass
    elif keep == 'random':
        rng.shuffle(cloud)
    elif keep == 'last':
        cloud = cloud[::-1]

    x = position(cloud)
    keys = np.floor(x / grid).astype(int)
    assert keys.size > 0
    _, ind = np.unique(keys, return_index=True, axis=0)

    if log:
        print('%.3f = %i / %i points kept (grid res. %.3f m).'
              % (len(ind) / len(keys), len(ind), len(keys), grid))

    filtered = cloud[ind]
    return filtered


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


def read_cloud(path, return_dict=False):
    """Read cloud as numpy.ndarray or dict with fields 'cloud', 'sensor_to_cloud', 'cloud_to_map'."""

    fmt = file_format(path)
    if fmt == FileFormat.ptx:
        cloud = read_ptx(path)
        cloud = cloud[0]  # 1st cloud tuple
        cloud = {Keys.cloud: cloud[0],
                 Keys.sensor_to_cloud: cloud[1],
                 Keys.cloud_to_map: cloud[2]}
    else:
        cloud = read(path)  # npy, npz

    if isinstance(cloud, np.ndarray):  # npy
        cloud = {Keys.cloud: cloud}

    cloud = dict(cloud)
    assert isinstance(cloud, dict)

    if Keys.sensor_to_cloud not in cloud:
        if Keys.sensor_pose in cloud:
            cloud[Keys.sensor_to_cloud] = cloud[Keys.sensor_pose]
            del cloud[Keys.sensor_pose]
        else:
            cloud[Keys.sensor_to_cloud] = np.eye(4)

    if Keys.cloud_to_map not in cloud:
        if Keys.cloud_pose in cloud:
            cloud[Keys.cloud_to_map] = cloud[Keys.cloud_pose]
            del cloud[Keys.cloud_pose]
        else:
            cloud[Keys.cloud_to_map] = np.eye(4)

    if return_dict:
        return cloud

    return cloud[Keys.cloud]


def write_cloud(cloud, path):
    """Write cloud as read using read_cloud to given path."""

    if isinstance(cloud, np.ndarray):
        cloud = {Keys.cloud: cloud}

    if Keys.sensor_to_cloud not in cloud:
        cloud[Keys.sensor_to_cloud] = np.eye(4)
    if Keys.cloud_to_map not in cloud:
        cloud[Keys.cloud_to_map] = np.eye(4)

    fmt = file_format(path)
    if fmt == FileFormat.npy:
        write_npy(cloud['cloud'], path)
    elif fmt == FileFormat.npz:
        write_npz(cloud, path)
    elif fmt == FileFormat.ptx:
        write_ptx([(cloud['cloud'],
                    cloud['sensor_to_cloud'],
                    cloud['cloud_to_map'])], path)


def process_cloud(args):
    # Args as list to be able to run it with map.
    cloud, box, range, grid, pose = args
    if isinstance(cloud, str):
        assert pose is None
        path = cloud
        cloud = read_cloud(path, return_dict=True)
        cloud, pose = cloud['cloud'], cloud['cloud_to_map']
        print(path, cloud.shape)

    # if box is not None and (np.any(box[0] > -np.inf) or np.any(box[1] < np.inf)):
    if box is not None:
        cloud = filter_box(cloud, box[0], box[1], log=True)

    if range is not None and (range[0] > 0.0 or range[1] < np.inf):
        cloud = filter_range(cloud, range[0], range[1], log=True)

    if grid[0] > 0.0:
        cloud = filter_grid(cloud, grid[0], keep=grid[1], log=True)

    if pose is not None and np.any(pose != np.eye(4)):
        cloud = transform_cloud(cloud, pose)

    return cloud


def merge_clouds(clouds, box=None, range=None, grid=None, poses=None, workers=max(mp.cpu_count() // 2, 1)):
    if poses is None:
        poses = len(clouds) * [None]
    assert len(clouds) == len(poses)
    p = mp.Pool(workers)
    args = [[cloud, box, range, grid, pose] for cloud, pose in zip(clouds, poses)]
    clouds = p.map(process_cloud, args)
    merged = np.concatenate([c.ravel() for c in clouds])
    if grid[0] > 0.0:
        merged = filter_grid(merged, grid[0], keep=grid[1], log=True)
    return merged
