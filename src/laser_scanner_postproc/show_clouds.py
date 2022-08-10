from __future__ import absolute_import, division, print_function
from .clouds import merge_clouds
from .visualization import show_cloud, show_ortho
from argparse import ArgumentParser
import yaml


def main():
    parser = ArgumentParser()
    parser.add_argument('--box', '-b', type=str, default='[[-.inf, -.inf, -.inf], [.inf, .inf, .inf]]')
    parser.add_argument('--range', '-r', type=str, default='[0.0, .inf]')
    parser.add_argument('--grid', '-g', type=str, default='[0.0, "first"]')
    parser.add_argument('--ortho', type=str, default=None)
    parser.add_argument('--ortho-axes', type=str, default='xy')
    parser.add_argument('--ortho-grid', type=float, default=10.0)
    parser.add_argument('input', nargs='+', type=str)
    args = parser.parse_args()
    args.box = yaml.safe_load(args.box)
    args.range = yaml.safe_load(args.range)
    args.grid = yaml.safe_load(args.grid)

    cloud = merge_clouds(args.input, args.box, args.range, args.grid)
    show_cloud(cloud)
    if args.ortho is not None:
        fig = show_ortho(cloud, axes=args.ortho_axes, grid=args.ortho_grid)
        if args.ortho:
            fig.savefig(args.ortho, bbox_inches='tight', dpi=300)
            print('Ortho image saved to %s.' % args.ortho)


if __name__ == '__main__':
    main()
