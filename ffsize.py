import argparse
import csv
import os
import shutil
import sys
import zlib

class StatusBar:
    def __init__(self, title: str, total: int, display: bool) -> "StatusBar":
        self.total = total
        self.display = display
        terminal_width = shutil.get_terminal_size()[0]
        if terminal_width < 16 or total <= 0:
            self.display = False
        if self.display:
            self.bar_len = min(100, terminal_width - (7 + len(title)))
            self.progress = 0
            self.bar_progress = 0
            sys.stdout.write(title + ": [" + "-"*self.bar_len + "]\b" + "\b"*self.bar_len)
            sys.stdout.flush()

    def initTotal(self, total: int) -> None:
        if total <= 0:
            self.endProgress()
        elif self.progress == 0:
            self.total = total

    def update(self) -> None:
        if self.display:
            self.progress += 1
            bar_progression = int(self.bar_len * self.progress // self.total) - self.bar_progress
            if bar_progression != 0:
                self.bar_progress += bar_progression
                sys.stdout.write("#" * bar_progression)
                sys.stdout.flush()

    def endProgress(self) -> None:
        if self.display:
            sys.stdout.write("#" * (self.bar_len - self.bar_progress) + "]\n")
            sys.stdout.flush()
            self.display = False

def crc(file_name, prev = 0):
    with open(file_name,"rb") as f:
        for line in f:
            prev = zlib.crc32(line, prev)
    return prev

def prettyCrc(prev):
    return "%X"%(prev & 0xFFFFFFFF)

def writeCsv(file_name, data, enc = None, delimiter = ","):
    with open(file_name, "w", newline="", encoding=enc, errors="backslashreplace") as f:
        writer = csv.writer(f, delimiter=delimiter)
        for row in data:
            writer.writerow(row)

def main():
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
            crc_status = StatusBar("Scanning files", 1, True)
            crc_status.initTotal(sum(len(f) for r, d, f in os.walk(args.path, topdown=False)))
        fileCount = 0
        dirCount = 0
        totalFileSize = 0
        totalFolderSize = 0
        rootDir = args.path
        # os.silly.walk
        for dir_path, sub_dir_list, file_list in os.walk(rootDir):
            sub_dir_list.sort()
            dirCount += len(sub_dir_list)
            fileCount += len(file_list)
            totalFolderSize += os.path.getsize(dir_path)
            if args.csv:
                csvList.append([dir_path, "", "", len(sub_dir_list), len(file_list), os.path.getsize(dir_path)])
            # check each file
            for f in sorted(file_list):
                fullPath = os.path.join(dir_path, f)
                totalFileSize += os.path.getsize(fullPath)
                # equivalent: totalSize += os.stat(dir_path + os.path.sep + f).st_size
                if args.csv and args.crc:
                    fileCrc = crc(fullPath)
                    totalCrc = (totalCrc + fileCrc) % (0xFFFFFFFF + 1)
                    csvList.append([f, os.path.getsize(fullPath), prettyCrc(fileCrc), "", "", ""])
                elif args.csv:
                    csvList.append([f, os.path.getsize(fullPath), "", "", "", ""])
                elif args.crc:
                    # match 7-zip CRC32
                    totalCrc += crc(fullPath)
                    totalCrc %= (0xFFFFFFFF + 1)
                    # alternative: totalCrc = crc(fullPath, totalCrc)
                    crc_status.update()
        if args.crc:
            crc_status.endProgress()
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

if __name__ == "__main__":
    sys.exit(main())
