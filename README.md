# f(ile)f(older)size
Python script to quickly check the size and crc of all files and folders in a directory or export as a csv. Useful when comparing between OSs since windows only reports file sizes and du reports file + folder sizes.
```
usage: ffsize.py [-h] [--crc] [--csv] [--delim CHAR] [--enc ENCODING] path

Counts all the files, folders, and total sizes. Matches the total in windows
when checking folder properties and du for unix.

positional arguments:
  path

optional arguments:
  -h, --help      show this help message and exit
  --crc           take checksum (CRC32) of files
  --csv           write list of files, folders, and info as filelist.csv
  --delim CHAR    set csv delimeter
  --enc ENCODING  set csv encoding, see
                  https://docs.python.org/3/library/codecs.html#standard-
                  encodings
```
