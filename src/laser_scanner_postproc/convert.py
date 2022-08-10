from __future__ import absolute_import, division, print_function
from argparse import ArgumentParser
from .clouds import read_cloud, write_cloud
import os


def convert(input_paths, output_path, output_format):
    assert isinstance(input_paths, list)
    assert isinstance(output_path, str)

    for i, input_path in enumerate(input_paths):
        dir = os.path.dirname(input_path)
        name, _ = os.path.splitext(os.path.basename(input_path))
        ext = '.' + output_format
        output_path = '{dir}/{name}{ext}'.format(dir=dir, name=name, ext=ext)
        print(i, input_path, output_path)
        cloud = read_cloud(input_path, return_dict=True)
        write_cloud(cloud, output_path)


def main():
    parser = ArgumentParser()
    parser.add_argument('--output-format', '-o', type=str, default='npz')
    parser.add_argument('--output', '-O', type=str, default='{dir}/{name}{ext}')
    parser.add_argument('input', nargs='+', type=str)
    args = parser.parse_args()

    convert(args.input, args.output, args.output_format)


if __name__ == '__main__':
    main()
