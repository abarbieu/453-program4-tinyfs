import sys
from libDisk import *
from libTinyFS import *

dnum = tfs_mkfs("tst.dsk")
tfs_mount("tst.dsk")
tfs_unmount()

# diskNum = openDisk("test", 1024)

# names = ["a\n", "b\n", "fuckthis\n"]

# # blocks = [2, 95, 1]


# superblock = Buffer()
# superblock.filled = 1

# dirent = bytearray()
# dirent.extend(bytearray([9, 2]))

# for i in range(3):
#     # print(bytes(bytearray(names[i].encode())))
#     dirent.extend(bytes(bytearray(names[i].encode('utf-8'))))

# print(len(dirent))
# superblock.data_bytes = dirent

# writeBlock(diskNum, 0, superblock)

# newSB = Buffer()

# readBlock(diskNum, 0, newSB)

# print(newSB.data_bytes[2:].decode("utf-8").split("\n"))
# print(list(newSB.data_bytes[:2]))
