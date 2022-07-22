from __future__ import absolute_import, division, print_function
from .io import safe_read_ptx_header
from .visualization import show_cloud
from argparse import ArgumentParser
import numpy as np


def show_path(paths):
    n = len(paths)
    t = np.zeros((n, 4, 4))
    for i, p in enumerate(paths):
        with open(p) as f:
            shape, _, t[i] = safe_read_ptx_header(f)
            print(i, shape, t[i, :3, 3])
    positions = t[:, :3, 3].reshape((-1, 3))
    show_cloud(positions)


def main():
    parser = ArgumentParser()
    parser.add_argument('input', nargs='+', type=str)
    args = parser.parse_args()
    show_path(args.input)


if __name__ == '__main__':
    main()
