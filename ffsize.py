import os
import argparse
import csv
import zlib

def crc(fileName, prev = 0):
    with open(fileName,"rb") as f:
        for line in f:
            prev = zlib.crc32(line, prev)
    return prev

def prettyCrc(prev):
    return "%X"%(prev & 0xFFFFFFFF)

def writeCsv(fName, data, enc = None, delimiter = ","):
    with open(fName, "w", newline="", encoding=enc, errors="backslashreplace") as f:
        writer = csv.writer(f, delimiter=delimiter)
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    readme = ("Counts all the files, folders, and total sizes. "
              "Matches the total in windows when checking folder properties "
              "and du for unix.")
    parser = argparse.ArgumentParser(description=readme)
    parser.add_argument("path", action="store", type=str)
    parser.add_argument("--crc", action="store_true",
                        help="take checksum (CRC32) of files")
    parser.add_argument("--csv", action="store_true",
                        help="write list of files, folders, and info as filelist.csv")
    parser.add_argument("--delim", action="store", type=str, default=",", metavar="CHAR",
                        help="set csv delimeter")
    parser.add_argument("--enc", action="store", type=str, default=None, metavar="ENCODING",
                        help="set csv encoding, see https://docs.python.org/3/library/codecs.html#standard-encodings")
    args = parser.parse_args()
    if os.path.isdir(args.path):
        # Initialize variables
        if args.csv:
            csvList = []
        if args.crc:
            totalCrc = 0
        fileCount = 0
        dirCount = 0
        totalFileSize = 0
        totalFolderSize = 0
        rootDir = args.path
        # os.silly.walk
        for dirName, subdirList, fileList in os.walk(rootDir):
            subdirList.sort()
            dirCount += len(subdirList)
            fileCount += len(fileList)
            totalFolderSize += os.path.getsize(dirName)
            if args.csv:
                csvList.append([dirName, "", "", len(subdirList), len(fileList), os.path.getsize(dirName)])
            # check each file
            for f in sorted(fileList):
                fullPath = os.path.join(dirName, f)
                totalFileSize += os.path.getsize(fullPath)
                # equivalent: totalSize += os.stat(dirName + os.path.sep + f).st_size
                if args.csv and args.crc:
                    fileCrc = crc(fullPath)
                    totalCrc = (totalCrc + fileCrc) % 4294967296
                    csvList.append([f, os.path.getsize(fullPath), prettyCrc(fileCrc), "", "", ""])
                elif args.csv:
                    csvList.append([f, os.path.getsize(fullPath), "", "", "", ""])
                elif args.crc:
                    # match 7-zip CRC32
                    totalCrc += crc(fullPath)
                    totalCrc %= 4294967296 # 0xFFFFFFFF + 1
                    # alternate: totalCrc += crc(fullPath, totalCrc)
        # return results
        duSize = totalFileSize + totalFolderSize
        print("Total files: %s" %(fileCount))
        print("Total folders: %s" %(dirCount))
        print("Total file size: %s bytes" %("{:,}".format(totalFileSize)))
        print("Total file + folder size: %s bytes" %("{:,}".format(duSize)))
        if args.crc:
            print("CRC32 checksum for data is: %s" %(prettyCrc(totalCrc)))
        if args.csv:
            writeCsv("filelist.csv", csvList, args.enc, args.delim)
    else:
        print("Input %s is not a valid path" %(args.path))
