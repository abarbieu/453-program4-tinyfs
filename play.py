import sys
from libDisk import *
from libTinyFS import *

dnum = tfs_mkfs("tst.dsk")
tfs_mount("tst.dsk")
fd = tfs_open("file1.tst")
tfs_write(fd, [1, 2, 3, 4, 5])
tfs_close(fd)
fd = tfs_open("file1.tst")
tfs_write(fd, [9, 8, 7, 99, 9, ])
printMem()
print('\n\n')


tfs_mkfs("tst1.dsk")
tfs_unmount()
tfs_mkfs("tst1.dsk")
printMem()
print('\n\n')

fd = tfs_open("file2.tst")
tfs_write(fd, [6, 6, 6, 66])
tfs_close(fd)
fd = tfs_open("file2.tst")
tfs_write(fd, [8, 8, 8, 88, 8])
printMem()

tfs_unmount()
tfs_mount("tst.dsk")
printMem()


fd = tfs_open("file1.tst")
buf = Buffer()
tfs_readByte(fd, buf)
print(list(buf.data_bytes))


fd2 = tfs_open("file2")


tfs_seek(fd, 3)
tfs_readByte(fd, buf)
print('ff', list(buf.data_bytes))

tfs_readdir()
tfs_rename("file1.tst", "renamed")
tfs_readdir()


newFD = tfs_open("newfile")
tfs_write(newFD, list(range(20)))

tfs_readByte(newFD, buf)
print(list(buf.data_bytes))

tfs_seek(newFD, 10)
tfs_readByte(newFD, buf)
print(list(buf.data_bytes))


tfs_makeRO("newfile")
tfs_write(newFD, [9, 9, 9])
tfs_readByte(newFD, buf)
print(list(buf.data_bytes))
tfs_readByte(newFD, buf)
print(list(buf.data_bytes))
tfs_readByte(newFD, buf)
print(list(buf.data_bytes))

tfs_makeRW("newfile")
tfs_write(newFD, [9, 9, 9])
tfs_readByte(newFD, buf)
print(list(buf.data_bytes))
tfs_readByte(newFD, buf)
print(list(buf.data_bytes))
tfs_readByte(newFD, buf)
print(list(buf.data_bytes))
tfs_readByte(newFD, buf)
print(list(buf.data_bytes))
# printMem()
# tfs_unmount()
# printMem()
# tfs_mount("tst1.dsk")
# printMem()
# dirent = {
#     "a": 2,
#     "hellotxt": 42
# }
# out = bytearray()
# [out.extend((n+'\0').encode()) for n in list(dirent.keys())]
# print(out.decode().split('\x00')[:-1])

# for i in out:
#     print(i)
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
