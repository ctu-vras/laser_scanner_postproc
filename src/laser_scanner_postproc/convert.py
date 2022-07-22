from __future__ import absolute_import, division, print_function
from argparse import ArgumentParser
from laser_scanner_postproc.io import read_ptx, write_npz
import os


def convert(input_paths, output_path, input_type, output_type):
    assert isinstance(input_paths, list)
    assert isinstance(output_path, str)
    assert input_type == 'ptx'
    assert output_type == 'npz'
    for i, input_path in enumerate(input_paths):
        dir = os.path.dirname(input_path)
        name, _ = os.path.splitext(os.path.basename(input_path))
        ext = '.' + output_type
        output_path = '{dir}/{name}{ext}'.format(dir=dir, name=name, ext=ext)
        print(i, input_path, output_path)
        if input_type == 'ptx':
            cloud, scanner_pose, cloud_pose = read_ptx(input_path)[0]
            write_npz({'cloud': cloud, 'scanner_pose': scanner_pose, 'cloud_pose': cloud_pose}, output_path)


def main():
    parser = ArgumentParser()
    parser.add_argument('--input-type', '-i', type=str, default='ptx')
    parser.add_argument('--output-type', '-o', type=str, default='npz')
    parser.add_argument('--output', type=str, default='{dir}/{name}{ext}')
    parser.add_argument('input', nargs='+', type=str)
    args = parser.parse_args()
    print(args)
    convert(args.input, args.output, args.input_type, args.output_type)


if __name__ == '__main__':
    main()
