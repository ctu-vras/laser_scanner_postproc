from __future__ import absolute_import, division, print_function
from .io import read, read_ptx, write
from .visualization import show_cloud, show_rgb_image
import os

data_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))


def data_path(path):
    return os.path.join(data_dir, path)


def main():
    # cloud = o3d.io.read_point_cloud(data_path('robingas-cimicky-1 1.las'))
    # print('las: %s' % cloud)
    # o3d.visualization.draw_geometries([cloud])

    # cloud = o3d.io.read_point_cloud(data_path('robingas-cimicky-1 1.ptg'))
    # print('ptg: %s' % cloud)
    # o3d.visualization.draw_geometries([cloud])

    # cloud = o3d.io.read_point_cloud(data_path('robingas-cimicky-haj- Setup585.ptx'))
    # print('ptx: %s' % cloud)
    # o3d.visualization.draw_geometries([cloud])

    # cloud = o3d.io.read_point_cloud(data_path(os.path.join('separate_e57', 'robingas-cimicky-haj- Setup585.e57')))
    # print('e57: %s' % cloud)
    # o3d.visualization.draw_geometries([cloud])

    # cloud = o3d.io.read_point_cloud(data_path('robingas-cimicky-1 1.pts'))
    # print('pts: %s' % cloud)
    # o3d.visualization.draw_geometries([cloud])

    # cloud = read_ptx(data_path('robingas-cimicky-1 1.ptx'))
    # cloud = read(data_path('robingas-cimicky-haj- Setup585.ptx'))
    # cloud, scanner_pose, cloud_pose = \
    #     read_ptx(data_path('robingas-cimicky-haj- Setup586.ptx'),
    #              return_scanner_pose=True,
    #              return_cloud_pose=True,
    #              transform=False,
    #              merge=False)[0]
    cloud = read_ptx(data_path('robingas-cimicky-1 1.ptx'),
                     transform=True,
                     merge=True)

    # assert len(scanner_pose) == 1
    # print('ptx: %s' % (cloud.shape,))
    # write(cloud, data_path('robingas-cimicky-haj- Setup585.npy'))
    # write({'cloud': cloud, 'scanner_pose': scanner_pose, 'cloud_pose': cloud_pose},
    #       data_path('robingas-cimicky-haj- Setup585.npz'))
    # write({'cloud': cloud, 'scanner_pose': scanner_pose, 'cloud_pose': cloud_pose},
    #       data_path('robingas-cimicky-haj- Setup586.npz'))
    # write({'cloud': cloud},
    #       data_path('robingas-cimicky-1 1.npz'))

    # data = read(data_path('robingas-cimicky-haj- Setup586.npz'))
    # data = read(data_path('robingas-cimicky-1 1.npz'))
    # cloud, scanner_pose, cloud_pose = data['cloud'], data['scanner_pose'], data['cloud_pose']
    # cloud = data['cloud']

    show_cloud(cloud)
    # Rotate 90 counter-clockwise due to vertical scan lines (rows).
    show_rgb_image(cloud, 90.0)


if __name__ == '__main__':
    main()
