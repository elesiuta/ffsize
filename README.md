# f(ile)f(older)size
Python script to quickly check the size and optionally crc of all files and folders in a directory and its contents recursively. Also includes a status bar and can export a list of contents with size and crc as a csv.  

Prints:
- file count
- folder count
- total file size
- total file + folder size
- total crc for all data (with `--crc`)
- [any file/folder read/access errors]

Get from PyPI: https://pypi.org/project/ffsize/
```
usage: ffsize [options] path

Counts all the files, folders, total sizes, and optionally crc in the directory
recursively.

positional arguments:
  path

optional arguments:
  -h, --help      show this help message and exit
  -v, --version   show program's version number and exit
  -c, --crc       take checksum (CRC32) of files
  -s, --sym       follow symbolic links that resolve to directories
  -w, --csv       write list of files, folders, and info to ffsize.csv
  --enc encoding  set csv encoding, see
                  https://docs.python.org/3/library/codecs.html#standard-encodings
```
