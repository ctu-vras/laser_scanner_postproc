# Laser Scanner Post-Processing

## Usage

```shell
cd laser_scanner_postproc
export PYTHONPATH=`pwd`/src:$PYTHONPATH
scripts/convert -o npz data/setup_*.ptx
scripts/merge_clouds -b '[[-25, -25, -3], [25, 25, 0]]' -r '[0, 25]' -g '[0.05, random]' data/setup_*.npz data/ground_map_5cm.npz
scripts/merge_clouds -b '[[-25, -25, -25], [25, 25, 25]]' -r '[0, 25]' -g '[0.05, random]' data/setup_*.npz data/map_5cm.npz
scripts/show_clouds data/ground_map_5cm.npz
scripts/convert -o ptx data/ground_map_5cm.npz data/map_5cm.npz
```

## Format Support

|                           | E57   | LAS | PTG | PTS   | PTX   |
|---------------------------|-------|-----|-----|-------|-------|
| Leica Register 360 export | B / S | B   | B   | B / S | B / S |
| Open3D import             |       |     |     | Y     |       |
| MeshLab import            |       |     |     | Y     | Y     |

Bundle (B) contains multiple registered scans (S).
Scan is also called setup.

Both PTS and [PTX](https://sites.google.com/site/matterformscanner/learning-references/ptx-format) are easy-to-read ASCII formats.
PTX keeps 2D scanning structure (represents also invalid points) and contains a header with registering transformation.
[E57](http://www.libe57.org/documentation.html) stores point clouds, images, and metadata produced by 3D imaging systems in an XML-like hierarchical tree structure.

### Leica BLK360 + Register 360

The best export option seems to be exporting the bundle as separated PTX files which keeps the original data, exports the registration information along it, and produces files of a reasonable size (~500 MB for middle density with LDR color).
E57 provides better support for images but is harder to read.
