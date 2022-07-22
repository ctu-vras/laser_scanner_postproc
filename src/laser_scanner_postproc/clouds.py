from __future__ import absolute_import, division, print_function
import numpy as np
from numpy.lib.recfunctions import structured_to_unstructured, unstructured_to_structured

default_rng = np.random.default_rng(135)


def filter_grid(cloud, grid_res, keep='random', preserve_order=False, log=False, rng=default_rng):
    """Keep single point within each cell. Order is not preserved."""
    assert isinstance(cloud, np.ndarray)
    assert isinstance(grid_res, float) and grid_res > 0.0
    assert keep in ('first', 'random', 'last')

    # Convert to numpy array with positions.
    if cloud.dtype.names:
        cloud = cloud.ravel()
        x = structured_to_unstructured(cloud[['x', 'y', 'z']])
    else:
        x = cloud

    # Create voxel indices.
    keys = np.floor(x / grid_res).astype(int).tolist()

    # Last key will be kept, shuffle if needed.
    # Create index array for tracking the input points.
    ind = list(range(len(keys)))
    if keep == 'first':
        # Make the first item last.
        keys = keys[::-1]
        ind = ind[::-1]
    elif keep == 'random':
        # Make the last item random.
        rng.shuffle(ind)
        # keys = keys[ind]
        keys = [keys[i] for i in ind]
    elif keep == 'last':
        # Keep the last item last.
        pass

    # Convert to immutable keys (tuples).
    keys = [tuple(i) for i in keys]

    # Dict keeps the last value for each key (already reshuffled).
    key_to_ind = dict(zip(keys, ind))
    if preserve_order:
        ind = sorted(key_to_ind.values())
    else:
        ind = list(key_to_ind.values())

    if log:
        print('%.3f = %i / %i points kept (grid res. %.3f m).'
              % (len(ind) / len(keys), len(ind), len(keys), grid_res))

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


def merge_clouds(clouds, transforms=None):
    merged = []
    for i in range(len(clouds)):
        cloud = clouds[i]
        if transforms:
            cloud = transform_cloud(cloud, transforms[i])
        merged.append(cloud)
    merged = np.concatenate([c.ravel() for c in merged])
    return merged
