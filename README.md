# Laser Scanner Post-Processing

## Format Support

|                     | E57   | LAS | PTG | PTS   | PTX   |
|---------------------|-------|-----|-----|-------|-------|
| Register 360 export | B / S | B   | B   | B / S | B / S |
| Open3D import       |       |     |     | Y     |       |
| MeshLab import      |       |     |     | Y     | Y     |

Bundle (B) contains multiple registered scans (S).
Scan is also called setup.

Both PTS and [PTX](https://sites.google.com/site/matterformscanner/learning-references/ptx-format) ([another description](https://wiki.photoneo.com/index.php/PTX_file_format)) are easy-to-read ASCII formats.
PTX keeps 2D scanning structure (represents also invalid points) and contains a header with registering transformation.

### Related References
- [E57 library](http://www.libe57.org/documentation.html)
- [User Coordinate System (UCS)](https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2021/ENU/AutoCAD-Core/files/GUID-E658D5E7-EE5C-4A06-BF34-F71CDB363A71-htm.html)
- [Open3D I/O](http://www.open3d.org/docs/latest/tutorial/Basic/file_io.html)

## Leica BLK360

One can export the bundle as PTS or PTX and individual scans as PTX.
The best export option seems to be exporting the bundle as separated PTX files which keeps the original data, exports the registration information along it, and produces files of a reasonable size (~500 MB for middle density with LDR color).
