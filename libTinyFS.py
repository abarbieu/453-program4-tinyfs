from libDisk import *

###
# Phase 2: a simple file system
###

# MAX MEM SIZE: 65,536

# Error numbers
ERR_UNMOUNTED = -500
ERR_MOUNTED = -501
ERR_FS_FORMAT = -600
ERR_INCONSISTENT_BLOCKS = -400


# Bytes in block
BLOCKSIZE = 256

# 40 blocks worth of bytes available for every disk, can be updated
DEFAULT_DISK_SIZE = 10240
DISK_SIZE = DEFAULT_DISK_SIZE

# Default name for a new disk
DEFAULT_DISK_NAME = "tinyFSDisk"

# block types
SUPER_BLOCK = 1
FREE_BLOCK = 2
INODE_BLOCK = 3
DATA_BLOCK = 4
DIRENT_NAME = 5
DIRENT_NUM = 6

# named indecies
TYPE = 0
NEXT_BLOCK = 1
SIZE = 2

MAGIC_NUMBER = 0x5A


# ------------------------------------------------------------------------------------
# Dynamic resource table stores information about open files
# FD -> sought index, size, blocks
DRT = {}

# Stores file name/descriptor pairs
DIRENT = {}

# Disk reference number from libdisk
DISK = None


# Finds all bytes available from blockNum, including further blocks
def fetchBytes(blockNum):
    nextBlock = blockNum
    data = []  # list of data
    blockType = None
    while nextBlock > 0:
        blockData = Buffer()
        errCode = readBlock(DISK, blockNum, blockData)

        if errCode < 0:
            return errCode

        currBlockType = list(blockData)[TYPE]
        sz = list(blockData)[SIZE]

        if blockType is None:
            blockType = currBlockType

        elif currBlockType != blockType:
            # Error thrown because file contains pointers to block of different types
            return ERR_INCONSISTENT_BLOCKS

        if blockType == DIRENT_NAME:  # reading string data for names of files
            # ignore metadata and stop at size
            rawData = blockData[3:sz].decode("utf-8")
            rawData.split('n')
            data += rawData
        else:
            data += list(blockData[3:sz])
        if sz < BLOCKSIZE:  # block is interally fragmented, no further blocks to read
            break

        nextBlock = list(blockData[NEXT_BLOCK])
    return data

###
# Make an empty TinyFS of size nBytes on specified file
# Use libDisk to open file, format file to be mounted
# init data to 0x00, set magic numbers, init/write superblock and other metadata
#
# superblock entry in order: magic_number, root inode pointer, freeblock pointer
###
# tfs_mkfs(str, int) -> int (Success/Error Code)


def tfs_mkfs(filename, nBytes=DEFAULT_DISK_SIZE):
    global DISK_SIZE
    DISK_SIZE = nBytes
    # open new disk, check errors
    diskNum = openDisk(filename, nBytes)
    if diskNum < 0:
        return diskNum  # ERROR

    global DISK
    DISK = diskNum
    superBlock = [0]*3
    superBlock[0] = MAGIC_NUMBER
    # Root dirent structure always in first 2 blocks (points to other blocks for storage)
    superBlock[1] = 1  # INODE BLOCK NUMBER
    superBlock[2] = 2  # NAMES (separated by '\n')
    # first free block starts in third block, updated whenever blocks get filled
    superBlock[3] = 3
    supBuf = Buffer()
    supBuf.data_bytes = bytearray(superBlock)  # save superblock to disk
    writeBlock(DISK, 0, supBuf)

    # free all blocks after super root Inode
    for bNum in range(3, int(DISK_SIZE/BLOCKSIZE)):
        nextBlock = Buffer()
        nextBlock.data_bytes = bytearray([bNum+1])
        writeBlock(DISK, bNum, nextBlock)

    return 0


###
# Mount a TinyFS file found on filename
# Verify type/format of FS, only one system mounted at a time
###
# tfs_mount(str) -> int (Success/Error Code)
def tfs_mount(filename):
    diskNum = openDisk(filename, 0)  # open without overwriting data
    tfs_unmount()
    superBlock = Buffer()
    readRet = readBlock(diskNum, 0, superBlock)  # fetch super block
    if readRet < 0:
        return readRet  # Error

    superBlock = list(superBlock.data_bytes)

    if superBlock[0] != 0x5A:
        return ERR_FS_FORMAT  # Invalid FS format

    direntBlocks = fetchBytes(superBlock[1])  # fetches Inode block numbers
    direntNames = fetchStrings(superBlock[2])  # fetches file names


###
# Cleanly unmount the current filesystem
###
# tfs_unmount() -> int (Success/Error Code)
def tfs_unmount():
    # if DISK is None:
    #     return ERR_UNMOUNTED

    # saveData()
    return -1


###
# Within the current mounted system, open a file to read and write
# create dynamic resource table entry with internal file pointer, etc.
###
# tfs_open(str) -> int (file descriptor/Error Code)
def tfs_open(name):
    fd = None
    global DIRENT_CACHE
    if name in DIRENT_CACHE:
        fd = DIRENT_CACHE[name]
    else:

        # search for name
        #   create file?
        #

        ###
        # Closes file at fileDescriptor, removes dynamic resource table entry
        ###
        # tfs_close(fileDescriptor) -> int (Success/Error Code)


def tfs_close(fileDescriptor):
    pass


###
# Write to FD: buffer "buffer" of size "size", representing entire file's contents
# Set file pointer to start of file (0)
###
# tfs_write(fileDescriptor, Buffer, int) -> int (Success/Error Code)
def tfs_write(FD, buffer, size):
    pass


###
# Deletes file @ FD in FS and sets its blocks to free
###
# tfs_delete(fileDescriptor) -> int (Success/Error Code)
def tfs_delete(FD):
    pass


###
# read one bute from file @ FD and copies it to buffer
# increments file pointer by 1, return error if at end of file
###
# tfs_readByte(fileDescriptor, Buffer) -> int (Success/Error Code)
def tfs_readByte(FD, buffer):
    pass


###
# Change file pointer location of file @ FD to offset (relative to beginning)
###
# tfs_seek(fileDescriptor, int) -> int (Success/Error Code)
def tfs_seek(FD, offset):
    pass


###
#


# if __name__ == "__main__":
#     tfs_mkfs("disk1.dsk")
#     tfs_mount("disk1.dsk")
#     tfs_
