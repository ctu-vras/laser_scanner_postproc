from __future__ import absolute_import, division, print_function
import numpy as np
from numpy.lib.recfunctions import structured_to_unstructured
import os

data_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))


def data_path(path):
    return os.path.join(data_dir, path)


class FileFormat(object):
    npy = 'npy'
    npz = 'npz'
    ptx = 'ptx'


def file_format(path):
    ext = os.path.splitext(path)[1]
    ext = ext.lower()[1:]
    return ext


def read_ptx_header(f):
    # number of rows
    # number of columns
    shape = int(f.readline()), int(f.readline())

    # st1 st2 st3 ; scanner registered position
    # sx1 sx2 sx3 ; scanner registered axis 'X'
    # sy1 sy2 sy3 ; scanner registered axis 'Y'
    # sz1 sz2 sz3 ; scanner registered axis 'Z'
    scanner_pose = np.eye(4)
    scanner_pose[:3, 3] = [float(x) for x in f.readline().strip().split()]
    scanner_pose[:3, 0] = [float(x) for x in f.readline().strip().split()]
    scanner_pose[:3, 1] = [float(x) for x in f.readline().strip().split()]
    scanner_pose[:3, 2] = [float(x) for x in f.readline().strip().split()]

    # r11 r12 r13 0 ; transformation matrix
    # r21 r22 r23 0 ; this is a simple rotation and translation 4x4 matrix
    # r31 r32 r33 0 ; just apply to each point to get the transformed coordinate
    # tr1 tr2 tr3 1 ; use double-precision variables
    cloud_pose = np.eye(4)
    cloud_pose[:, 0] = [float(x) for x in f.readline().strip().split()]
    cloud_pose[:, 1] = [float(x) for x in f.readline().strip().split()]
    cloud_pose[:, 2] = [float(x) for x in f.readline().strip().split()]
    cloud_pose[:, 3] = [float(x) for x in f.readline().strip().split()]

    return shape, scanner_pose, cloud_pose


def safe_read_ptx_header(f):
    try:
        return read_ptx_header(f)
    except Exception as ex:
        # print(ex)
        return None


def read_ptx_data(f, shape):
    cloud = None
    n = shape[0] * shape[1]
    for i in range(n):
        if i > 0 and i % 1000000 == 0:
            print('%i /  %i points read.' % (i, n))
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


def read_ptx(path, transform=False):
    """Read PTX file to NumPy structured arrays.

    :param path: PTX path to read.
    :param transform: Whether to transform read clouds.
    :return: List of tuples (cloud, scanner_pose, cloud_pose).
    """
    assert file_format(path) == FileFormat.ptx
    clouds = []
    scanner_poses = []
    cloud_poses = []
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
                from .clouds import transform_cloud
                cloud = transform_cloud(cloud, cloud_pose, inplace=True)

            clouds.append(cloud)
            scanner_poses.append(scanner_pose)
            cloud_poses.append(cloud_pose)

    ret = list(zip(clouds, scanner_poses, cloud_poses))

    return ret


def write_ptx_header(shape, scanner_pose, cloud_pose, f):
    assert len(shape) == 2
    for n in shape:
        f.write('%i\n' % n)

    for i in [3, 0, 1, 2]:
        f.write('%.6f %.6f %.6f\n' % tuple(scanner_pose[:3, i]))

    for i in range(4):
        f.write('%.6f %.6f %.6f %.6f\n' % tuple(cloud_pose[:, i]))


def write_ptx_data(cloud, f):
    cloud = structured_to_unstructured(cloud.ravel())
    assert cloud.shape[1] in (3, 4, 7)
    fmt = ' '.join(['%.6f', '%.6f', '%.6f', '%.6f', '%i', '%i', '%i'][:cloud.shape[1]]) + '\n'
    for i, pt in enumerate(cloud):
        if i > 0 and i % 1000000 == 0:
            print('%i / %i points written.' % (i, len(cloud)))
        f.write(fmt % tuple(pt))


def write_ptx(clouds, path):
    assert file_format(path) == FileFormat.ptx
    # with open(path, 'w', newline='\r\n') as f:
    with open(path, 'w') as f:
        for cloud in clouds:
            if isinstance(cloud, (list, tuple)):
                cloud, scanner_pose, cloud_pose = cloud
            else:
                scanner_pose = np.eye(4)
                cloud_pose = np.eye(4)
            assert isinstance(cloud, np.ndarray)
            cloud = cloud.reshape((cloud.shape[0], -1))
            write_ptx_header(cloud.shape, scanner_pose, cloud_pose, f)
            write_ptx_data(cloud, f)


def read_npy(path):
    assert file_format(path) == FileFormat.npy
    return np.load(path)


def write_npy(arr, path):
    assert file_format(path) == FileFormat.npy
    np.save(path, arr)


def read_npz(path):
    assert file_format(path) == FileFormat.npz
    arr = np.load(path)
    return arr


def write_npz(arr, path):
    assert file_format(path) == file_format.npz
    args = []
    kwargs = {}
    if isinstance(arr, np.ndarray):
        args = [arr]
    elif isinstance(arr, list):
        args = arr
    elif isinstance(arr, dict):
        kwargs = arr
    np.savez_compressed(path, *args, **kwargs)


def read(path, *args, **kwargs):
    fmt = file_format(path)
    if fmt == FileFormat.npy:
        return read_npy(path)
    elif fmt == FileFormat.npz:
        return read_npz(path)
    elif fmt == FileFormat.ptx:
        return read_ptx(path, *args, **kwargs)
    raise ValueError('Reading %s failed.' % path)


def write(arr, path):
    fmt = file_format(path)
    if fmt == FileFormat.npy:
        return write_npy(arr, path)
    elif fmt == FileFormat.npz:
        return write_npz(arr, path)
    elif fmt == FileFormat.ptx:
        return write_ptx([arr], path)
    raise ValueError('Writing %s failed.' % path)
