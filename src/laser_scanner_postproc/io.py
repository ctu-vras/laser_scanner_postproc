from __future__ import absolute_import, division, print_function
from .transform import transform_cloud
import numpy as np
import os


def extension(path):
    parts = os.path.basename(path).split('.')
    assert len(parts) >= 2
    ext = parts[-1]
    return ext


def read_ptx_header(f):
    # number of rows
    # number of columns
    shape = int(f.readline()), int(f.readline())
    print('Shape:', shape)

    # st1 st2 st3 ; scanner registered position
    # sx1 sx2 sx3 ; scanner registered axis 'X'
    # sy1 sy2 sy3 ; scanner registered axis 'Y'
    # sz1 sz2 sz3 ; scanner registered axis 'Z'
    scanner_pose = np.eye(4)
    scanner_pose[:3, 3] = [float(x) for x in f.readline().strip().split()]
    scanner_pose[:3, 0] = [float(x) for x in f.readline().strip().split()]
    scanner_pose[:3, 1] = [float(x) for x in f.readline().strip().split()]
    scanner_pose[:3, 2] = [float(x) for x in f.readline().strip().split()]
    print('Scanner pose:')
    print(scanner_pose)

    # r11 r12 r13 0 ; transformation matrix
    # r21 r22 r23 0 ; this is a simple rotation and translation 4x4 matrix
    # r31 r32 r33 0 ; just apply to each point to get the transformed coordinate
    # tr1 tr2 tr3 1 ; use double-precision variables
    cloud_pose = np.eye(4)
    cloud_pose[:, 0] = [float(x) for x in f.readline().strip().split()]
    cloud_pose[:, 1] = [float(x) for x in f.readline().strip().split()]
    cloud_pose[:, 2] = [float(x) for x in f.readline().strip().split()]
    cloud_pose[:, 3] = [float(x) for x in f.readline().strip().split()]
    print('Cloud pose:')
    print(scanner_pose)

    return shape, scanner_pose, cloud_pose


def safe_read_ptx_header(f):
    try:
        return read_ptx_header(f)
    except Exception as ex:
        # print(ex)
        return None


def read_ptx_data(f, shape):
    cloud = None
    for i in range(shape[0] * shape[1]):
        if i > 0 and i % 1000000 == 0:
            print('%i points read.' % i)
        vals = f.readline().strip().split()
        if cloud is None:
            dtype = [('x', 'f4'),
                     ('y', 'f4'),
                     ('z', 'f4'),
                     ('i', 'f4'),
                     ('r', 'u1'),
                     ('g', 'u1'),
                     ('b', 'u1')]
            dtype = dtype[:len(vals)]
            print('Type:', dtype)
            cloud = np.zeros(shape, dtype=dtype)
        vals = [float(x) for x in vals[:4]] + [int(x) for x in vals[4:]]
        vals = tuple(vals)
        cloud[i // shape[1], i % shape[1]] = vals
    return cloud


def safe_read_ptx_data(f, shape):
    try:
        return read_ptx_data(f, shape)
    except Exception as ex:
        # print(ex)
        return None


def read_ptx(path, return_scanner_pose=False, return_cloud_pose=False, transform=False, merge=True):
    """Read PTX file to NumPy structured array.

    :param path: PTX path to read.
    :param return_scanner_pose: Return scanner pose(s).
    :param return_cloud_pose: Return cloud transform(s).
    :param transform: Transform cloud(s) using the pose(s).
    :param merge: Merge all clouds into one.
    :return: Cloud(s) as NumPy structured array(s).
    """
    # https://sites.google.com/site/matterformscanner/learning-references/ptx-format
    # https://wiki.photoneo.com/index.php/PTX_file_format
    # https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2021/ENU/AutoCAD-Core/files/GUID-E658D5E7-EE5C-4A06-BF34-F71CDB363A71-htm.html
    clouds = []
    scanner_poses = []
    cloud_transforms = []
    with open(path, 'r') as f:
        while True:
            header = safe_read_ptx_header(f)
            if header is None:
                break
            shape, scanner_pose, cloud_pose = header
            cloud = safe_read_ptx_data(f, shape)
            if cloud is None:
                break

            if transform:
                cloud = transform_cloud(cloud, cloud_pose, inplace=True)

            clouds.append(cloud)
            scanner_poses.append(scanner_pose)
            cloud_transforms.append(cloud_pose)

    if not clouds:
        return None

    if merge:
        assert not return_scanner_pose
        assert not return_cloud_pose
        assert transform
        # print('Merging %i clouds.' % len(clouds))
        clouds = np.concatenate([c.ravel() for c in clouds])
        return clouds

    ret = (clouds,)
    if return_scanner_pose:
        ret += (scanner_poses,)
    if return_cloud_pose:
        ret += (cloud_transforms,)

    ret = list(zip(*ret))

    return ret


def read_npy(path):
    assert extension(path) == 'npy'
    return np.load(path)


def write_npy(arr, path):
    assert extension(path) == 'npy'
    np.save(path, arr)


def read_npz(path):
    assert extension(path) == 'npz'
    arr = np.load(path)
    # if all(k.startswith('arr_') for k in arr.keys()):
    # keys = sorted(arr.keys())
    # return [arr[k] for k in keys]
    return arr


def write_npz(arr, path):
    assert extension(path) == 'npz'
    args = []
    kwargs = {}
    if isinstance(arr, np.ndarray):
        args = [arr]
    elif isinstance(arr, list):
        args = arr
    elif isinstance(arr, dict):
        kwargs = arr
    np.savez_compressed(path, *args, **kwargs)


def read(path):
    ext = extension(path)
    if ext == 'npy':
        return read_npy(path)
    elif ext == 'npz':
        return read_npz(path)
    elif ext == 'ptx':
        return read_ptx(path)
    raise ValueError('Reading %s failed.' % path)


def write(arr, path):
    ext = extension(path)
    if ext == 'npy':
        return write_npy(arr, path)
    elif ext == 'npz':
        return write_npz(arr, path)
    elif ext == 'ptx':
        return read_ptx(path)
    raise ValueError('Writing %s failed.' % path)
