from __future__ import absolute_import, division, print_function
from .clouds import merge_clouds
from .io import write
from argparse import ArgumentParser
import yaml


def main():
    parser = ArgumentParser()
    parser.add_argument('--box', '-b', type=str, default='[[-.inf, -.inf, -.inf], [.inf, .inf, .inf]]')
    parser.add_argument('--range', '-r', type=str, default='[0.0, .inf]')
    parser.add_argument('--grid', '-g', type=str, default='[0.0, "first"]')
    parser.add_argument('input', nargs='+', type=str)
    parser.add_argument('output', type=str)
    args = parser.parse_args()
    args.box = yaml.safe_load(args.box)
    args.range = yaml.safe_load(args.range)
    args.grid = yaml.safe_load(args.grid)

    print(args)
    cloud = merge_clouds(args.input, args.box, args.range, args.grid)
    write({'cloud': cloud}, args.output)


if __name__ == '__main__':
    main()
