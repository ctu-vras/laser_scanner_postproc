# Format Support

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
