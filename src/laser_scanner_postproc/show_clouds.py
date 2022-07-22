from __future__ import absolute_import, division, print_function
from .clouds import filter_grid, merge_clouds
from .io import read
from .visualization import show_cloud
from argparse import ArgumentParser
import numpy as np


def show_clouds(paths, grid_res=0.0):
    clouds = []
    cloud_poses = []
    for i, p in enumerate(paths):
        cloud = read(p)
        if 'cloud' in cloud and 'cloud_pose' in cloud:
            cloud, cloud_pose = cloud['cloud'], cloud['cloud_pose']
        else:
            cloud_pose = np.eye(4)
        print(i, cloud.shape)
        if grid_res:
            cloud = filter_grid(cloud, grid_res, keep='last', log=True)
        clouds.append(cloud)
        cloud_poses.append(cloud_pose)

    cloud = merge_clouds(clouds, cloud_poses)
    cloud = filter_grid(cloud, grid_res, keep='last', log=True)
    show_cloud(cloud)


def main():
    parser = ArgumentParser()
    parser.add_argument('--grid-res', '-g', type=float, default=0.0)
    parser.add_argument('input', nargs='+', type=str)
    args = parser.parse_args()
    show_clouds(args.input, grid_res=args.grid_res)


if __name__ == '__main__':
    main()
