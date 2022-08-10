# Laser Scanner Post-Processing

## Leica BLK360 + Register 360

The best export option seems to be exporting the bundle as separated PTX files (see [formats](formats.md) for details) which keeps the original data, exports the registration information along it, and produces files of a reasonable size (~500 MB for middle density with LDR color).
E57 provides better support for images but is harder to read.

Exported PTX scans can be converted to NumPy NPZ files for convenience and composite point clouds can be created as follows:
```shell
cd laser_scanner_postproc
export PYTHONPATH=`pwd`/src:$PYTHONPATH
scripts/convert -o npz data/setup_*.ptx
scripts/merge_clouds -b '[[-25, -25, -3], [25, 25, 0]]' -r '[0, 25]' -g '[0.05, random]' data/setup_*.npz data/ground_map_5cm.npz
scripts/merge_clouds -b '[[-25, -25, -25], [25, 25, 25]]' -r '[0, 25]' -g '[0.05, random]' data/setup_*.npz data/map_5cm.npz
scripts/show_clouds data/ground_map_5cm.npz
scripts/convert -o ptx data/ground_map_5cm.npz data/map_5cm.npz
```
