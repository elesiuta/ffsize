import argparse
import csv
import os
import signal
import shutil
import sys
import zlib

VERSION = "1.0.4"

class StatusBar:
    def __init__(self, title):
        terminal_width = shutil.get_terminal_size()[0]
        self.bar_len = min(100, terminal_width - (7 + len(title)))
        self.progress = 0
        self.bar_progress = 0
        sys.stdout.write(title + ": [" + "-"*self.bar_len + "]\b" + "\b"*self.bar_len)
        sys.stdout.flush()

    def initTotal(self, total):
        if total <= 0:
            self.endProgress()
        self.total = total

    def update(self, progress = 1):
        self.progress += progress
        bar_progression = int(self.bar_len * self.progress // self.total) - self.bar_progress
        if bar_progression != 0:
            self.bar_progress += bar_progression
            sys.stdout.write("#" * bar_progression)
            sys.stdout.flush()

    def endProgress(self):
        sys.stdout.write("#" * (self.bar_len - self.bar_progress) + "]\n")
        sys.stdout.flush()

def crc(file_name, prev = 0):
    with open(file_name,"rb") as f:
        for line in f:
            prev = zlib.crc32(line, prev)
    return prev

def prettyCrc(prev):
    return str("%X"%(prev & 0xFFFFFFFF)).zfill(8)

def writeCsv(file_name, data, enc = None, delimiter = ","):
    with open(file_name, "w", newline="", encoding=enc, errors="backslashreplace") as f:
        writer = csv.writer(f, delimiter=delimiter)
        for row in data:
            writer.writerow(row)

def main() -> int:
    signal.signal(signal.SIGINT, lambda *args: sys.exit(128 + signal.SIGINT))
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(128 + signal.SIGTERM))
    readme = ("Counts all the files, folders, total sizes, and optionally crc in the directory recursively.")
    parser = argparse.ArgumentParser(description=readme, usage="%(prog)s [options] path")
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    parser.add_argument("path", action="store", type=str)
    parser.add_argument("-c", "--crc", action="store_true",
                        help="take checksum (CRC32) of files")
    parser.add_argument("-s", "--sym", action="store_true",
                        help="follow symbolic links that resolve to directories")
    parser.add_argument("-w", "--csv", action="store_true",
                        help="write list of files, folders, and info to ffsize.csv")
    parser.add_argument("--enc", action="store", type=str, default=None, metavar="encoding",
                        help="set csv encoding, see https://docs.python.org/3/library/codecs.html#standard-encodings")
    args = parser.parse_args()
    if os.path.isdir(args.path):
        # Initialize variables
        count_status = StatusBar("Calculating sizes")
        count_status.initTotal(sum(len(f) for r, d, f in os.walk(args.path, topdown=False, followlinks=args.sym)))
        csvList = [["Name", "File Size", "CRC", "Folders", "Files", "Folder Size"]]
        csvDict = {}
        fileCount = 0
        errorCrcCount = 0
        errorFileCount = 0
        errorFolderCount = 0
        dirCount = 0
        returnCode = 0
        totalFileSize = 0
        totalFolderSize = 0
        rootDir = args.path
        # os.silly.walk
        for dir_path, subdir_list, file_list in os.walk(rootDir, followlinks=args.sym):
            subdir_list.sort()
            dirCount += len(subdir_list)
            fileCount += len(file_list)
            totalFolderSize += os.path.getsize(dir_path)
            if args.csv:
                relPath = os.path.relpath(dir_path, rootDir)
                if relPath == ".":
                    relPath = os.path.abspath(dir_path)
                csvList.append([relPath, "", "", len(subdir_list), len(file_list), os.path.getsize(dir_path)])
            # check folders for errors (onerror only passes exception in args)
            for f in subdir_list:
                fullPath = os.path.join(dir_path, f)
                try:
                    os.scandir(fullPath)
                except (KeyboardInterrupt, InterruptedError):
                        return 128 + signal.SIGINT
                except Exception:
                    errorFolderCount += 1
                    if args.csv:
                        relPath = os.path.relpath(fullPath, rootDir)
                        csvList.append([relPath, "", "", -1, -1, -1])
            # check each file
            for f in sorted(file_list):
                fullPath = os.path.join(dir_path, f)
                try:
                    fileSize = os.path.getsize(fullPath)
                    totalFileSize += fileSize
                except (KeyboardInterrupt, InterruptedError):
                        return 128 + signal.SIGINT
                except Exception:
                    fileSize = -1
                    errorFileCount += 1
                if args.csv:
                    if args.crc:
                        csvList.append(fullPath)
                        csvDict[fullPath] = {"name": f, "size": fileSize}
                    else:
                        csvList.append([f, fileSize, "", "", "", ""])
                count_status.update()
        count_status.endProgress()
        # print results
        duSize = totalFileSize + totalFolderSize
        print("Total files: %s" %(fileCount))
        print("Total folders: %s" %(dirCount))
        print("Total file size: %s bytes" %("{:,}".format(totalFileSize)))
        print("Total file + folder size: %s bytes" %("{:,}".format(duSize)))
        if errorFileCount > 0:
            print("Error: %s file(s) could not be accessed, check permissions" %(errorFileCount), file=sys.stderr)
            returnCode = 1
        if errorFolderCount > 0:
            print("Error: %s folder(s) could not be accessed, check permissions" %(errorFolderCount), file=sys.stderr)
            returnCode = 1
        # do crc after, time saved by doing everything together is negligible
        if args.crc:
            crc_status = StatusBar("Calculating CRC")
            crc_status.initTotal(totalFileSize)
            totalCrc = 0
            for dir_path, subdir_list, file_list in os.walk(rootDir, followlinks=args.sym):
                for f in file_list:
                    fullPath = os.path.join(dir_path, f)
                    try:
                        # match 7-zip CRC32 total for data
                        fileCrc = crc(fullPath)
                        totalCrc = (totalCrc + fileCrc) % (0xFFFFFFFF + 1)
                        if args.csv:
                            csvDict[fullPath]["crc"] = prettyCrc(fileCrc)
                            crc_status.update(csvDict[fullPath]["size"])
                        else:
                            crc_status.update(os.path.getsize(fullPath))
                    except (KeyboardInterrupt, InterruptedError):
                        return 128 + signal.SIGINT
                    except Exception:
                        errorCrcCount += 1
                        if args.csv:
                            csvDict[fullPath]["crc"] = -1
            if args.csv:
                for i in range(1, len(csvList)):
                    if type(csvList[i]) == str:
                        f = csvDict[csvList[i]]
                        csvList[i] = [f["name"], f["size"], f["crc"], "", "", ""]
            crc_status.endProgress()
            print("CRC32 checksum for data: %s" %(prettyCrc(totalCrc)))
            if errorCrcCount > 0:
                print("Error: %s file(s) could not be read, check permissions" %(errorCrcCount), file=sys.stderr)
                returnCode = 1
        if args.csv:
            writeCsv("ffsize.csv", csvList, args.enc)
        return returnCode
    else:
        print("Input %s is not a valid path" %(args.path))
        return 1

if __name__ == "__main__":
    sys.exit(main())
