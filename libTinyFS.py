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
ERR_DIR_ALIGNMENT = -601
ERR_DISK = -100


# Bytes in block
BLOCKSIZE = 256

# 40 blocks worth of bytes available for every disk, can be updated
DEFAULT_DISK_SIZE = 10240
DISK_SIZE = DEFAULT_DISK_SIZE

# Default name for a new disk
DEFAULT_DISK_NAME = "tinyFSDisk"

# block types
SUPER_BLOCK = 0
FREE_BLOCK = 2
INODE_BLOCK = 3
DATA_BLOCK = 4
DIRENT_NAME = 5
DIRENT_NUM = 6

# named indecies
TYPE = 0
NEXT_BLOCK = 1
SIZE = 2

SB_NUM = 1
SB_NAME = 2
SB_FREE = 3

MAGIC_NUMBER = 0x5A


# ------------------------------------------------------------------------------------
# Dynamic resource table stores information about open files
# FD -> sought index, size, blocks
DRT = {}

# Stores file name/descriptor pairs
DIRENT = {}

# Disk reference number from libdisk
DISK = None

# First free block, points to next free block
FREE_HEAD = None


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
            rawData.split('\n')
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
    superBlock = [0]*5
    superBlock[0] = MAGIC_NUMBER
    # Root dirent structure always in first 2 blocks (points to other blocks for storage)
    superBlock[SB_NUM] = 1  # INODE BLOCK NUMBERS
    superBlock[SB_NAME] = 2  # NAMES (separated by '\n')
    # first free block starts in third block, updated whenever blocks get filled
    superBlock[SB_FREE] = 3
    global FREE_HEAD  # so we can change it later
    FREE_HEAD = 3

    supBuf = Buffer()
    supBuf.data_bytes = bytearray(superBlock)  # save superblock to disk
    if writeBlock(DISK, 0, supBuf):
        return ERR_DISK

    # set up dirent block number block
    numBuf = Buffer()
    numData = [0] * 3
    numData[TYPE] = DIRENT_NUM
    numBuf.data_bytes = bytearray(numData)
    if writeBlock(DISK, superBlock[SB_NUM], numBuf) < 0:
        return ERR_DISK

    # set up dirent file name block
    nameBuf = Buffer()
    nameData = [0] * 3
    nameData[TYPE] = DIRENT_NAME
    nameBuf.data_bytes = bytearray(nameData)
    if writeBlock(DISK, superBlock[SB_NAME], nameBuf) < 0:
        return ERR_DISK

    # free all blocks after super root Inode
    for bNum in range(3, int(DISK_SIZE/BLOCKSIZE)-1):
        nextBlock = Buffer()
        freeInfo = [0]*3
        freeInfo[TYPE] = FREE_BLOCK
        freeInfo[NEXT_BLOCK] = bNum+1
        nextBlock.data_bytes = bytearray(freeInfo)
        if writeBlock(DISK, bNum, nextBlock) < 0:
            return ERR_DISK

    # Info for final free block, points nowhere but is free
    lastInfo = [0]*5
    lastInfo[TYPE] = FREE_BLOCK
    buf = Buffer()
    buf.data_bytes = bytearray(lastInfo)
    if writeBlock(DISK, int(DISK_SIZE/BLOCKSIZE)-1, buf) < 0:
        return ERR_DISK

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
    if readBlock(diskNum, 0, superBlock) < 0:  # fetch super block
        return ERR_DISK  # Error

    superBlock = list(superBlock.data_bytes)

    if superBlock[0] != 0x5A:
        return ERR_FS_FORMAT  # Invalid FS format

    direntBlocks = fetchBytes(superBlock[1])  # fetches Inode block numbers
    direntNames = fetchBytes(superBlock[2])  # fetches file names

    if len(direntBlocks) != len(direntNames):  # there should be an inode for every name
        return ERR_DIR_ALIGNMENT

    # connect file names to inode block locations in local structure
    global DIRENT
    for i in range(len(direntBlocks)):
        DIRENT[direntNames[i]] = direntBlocks[i]


###
# Cleanly unmount the current filesystem
# write any important data to superblock, close all files (?)
###
# tfs_unmount() -> int (Success/Error Code)
def tfs_unmount():
    global DISK
    if DISK is None:
        return ERR_UNMOUNTED

    supData = [0]*5
    supData[SB_FREE] = FREE_HEAD  # free block head probably moved
    supBuf = Buffer()
    supBuf.data_bytes = bytearray(supData)
    if writeBlock(DISK, SUPER_BLOCK, supBuf) < 0:
        return ERR_DISK

    if closeDisk(DISK) < 0:
        return ERR_DISK

    DISK = None
    return -1


###
# Within the current mounted system, open a file to read and write
# create dynamic resource table entry with internal file pointer, etc.
###
# tfs_open(str) -> int (file descriptor/Error Code)
def tfs_open(name):
    inode = None
    global DIRENT
    if name in DIRENT:
        inode = DIRENT[name]
    else:
        pass
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
