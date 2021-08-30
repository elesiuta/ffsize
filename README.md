# f(ile)f(older)size
Python script to quickly check the size and crc of all files and folders in a directory or export as a csv. Useful when comparing between OSs since windows only reports file sizes and du reports file + folder sizes.

Get from PyPI: https://pypi.org/project/ffsize/
```
usage: ffsize [-h] [--crc] [--csv] [--delim CHAR] [--enc ENCODING] path

Counts all the files, folders, and total sizes. Matches the total in windows
when checking folder properties and du for unix.

positional arguments:
  path

optional arguments:
  -h, --help      show this help message and exit
  --version       show program's version number and exit
  --crc           take checksum (CRC32) of files
  --csv           write list of files, folders, and info as ffsize.csv
  --enc ENCODING  set csv encoding, see
                  https://docs.python.org/3/library/codecs.html#standard-
                  encodings
```
