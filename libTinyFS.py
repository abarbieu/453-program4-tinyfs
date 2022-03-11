from asyncore import write
from curses.ascii import VT
from tkinter.tix import NoteBook

from numpy import byte
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
ERR_NO_FREE_BLOCK = -410
ERR_FILE_CLOSED = -420
ERR_FILE_NOT_FOUND = -430
ERR_EOF = -399
ERR_MOUNTED = -650
ERR_PERMISSIONS = -333


# Bytes in block
BLOCKSIZE = 256

# Bytes in metadata header
META_SIZE = 8

# 40 blocks worth of bytes available for every disk, can be updated
DEFAULT_DISK_SIZE = 10240
DISK_SIZE = DEFAULT_DISK_SIZE

# Default name for a new disk
DEFAULT_DISK_NAME = "tinyFSDisk"

# block types
FREE_BLOCKT = 0
INODE_BLOCKT = 3
DATA_BLOCKT = 4
DIRENT_NAMET = 5
DIRENT_NUMT = 6
FREE_MASKT = 7

# named indecies in block
TYPE_BYTE = 0
SIZE_BYTE = 1
REM_BYTE = 2  # size of last block in file, stored in inode
RW_BYTE = 3  # read write byte, permissions below

# permissions
P_RW = 0
P_READ = 1

# named superblock indecies
SUPER_BLOCK = 0
SB_FREE = 1
SB_NUM = 2
SB_NAME = 3

MAGIC_NUMBER = 0x5A


# ------------------------------------------------------------------------------------
# Dynamic resource table stores information about open files
# FD -> sought index, size, blocks
DRT = {}

# Super block internal structure (array of indecies, essentially)
SB = None

# Stores file name/descriptor pairs
DIRENT = {}

# Disk reference number from libdisk
DISK = None

# 0 is a free block, 1 is filled
FILLED = 1
EMPTY = 0
FREE_MASK = None


# Searches bit mask for first or last 0, sets it to 1
def claimFreeBlock(first=True):
    global FREE_MASK
    bNum = None
    if first:
        bNum = next((i for i, x in enumerate(FREE_MASK) if x == EMPTY), None)
    else:
        bNum = len(FREE_MASK) - next((i for i, x in enumerate(
            reversed(FREE_MASK)) if x == EMPTY), None) - 1
    FREE_MASK[bNum] = FILLED
    return bNum


# finds free block, writes data to it, returns bnum
# blocks: block numbers inode points to
def createInode(blocks, bType=INODE_BLOCKT):
    # set metadata
    idata = [0]*META_SIZE
    idata[TYPE_BYTE] = bType
    idata[SIZE_BYTE] = len(blocks)  # size of data
    idata += blocks
    # 8 bytes of meta data space then all the blocks

    ibuf = Buffer()
    ibuf.data_bytes = bytearray(idata)

    # find and claim free block, first if dirent or other, last if inode (arbitrary?)
    blockNum = claimFreeBlock(first=(bType != INODE_BLOCKT))
    if blockNum is None:
        print(f"createInode: ERR_NO_FREE_BLOCK")
        return ERR_NO_FREE_BLOCK

    if writeBlock(DISK, blockNum, ibuf) < 0:
        print(f"createInode: ERR_DISK")
        return ERR_DISK
    return blockNum


# from inode block number, reads all blocks pointed to by inode
def readViaInode(inodeBNum, meta=False):
    iBuf = Buffer()
    if readBlock(DISK, inodeBNum, iBuf) < 0:
        print("readFromInode: ERR_DISK")
        return ERR_DISK

    iData = list(iBuf.data_bytes)
    meta = iData[:META_SIZE]
    blocks = iData[META_SIZE:]

    allData = []
    # read all blocks and combine them
    for bNum in blocks[:meta[SIZE_BYTE]]:
        buf = Buffer()
        readBlock(DISK, bNum, buf)
        bData = list(buf.data_bytes)
        # from block, read all data after meta data, up to end of block
        allData += bData[META_SIZE:bData[SIZE_BYTE] + META_SIZE]
    return allData


# Write to a block and updates its metadata, returns data that can't fit into block
def writeBlockMeta(bNum, data):
    toWrite = [0]*META_SIZE
    # Either write all data or fill available space
    dataWriteLen = min(BLOCKSIZE-META_SIZE, len(data))
    toWrite[SIZE_BYTE] = dataWriteLen
    toWrite[TYPE_BYTE] = DATA_BLOCKT

    # only write data that we can
    toWrite += data[:dataWriteLen]
    wBuf = Buffer()
    wBuf.data_bytes = bytearray(toWrite)
    writeBlock(DISK, bNum, wBuf)

    return data[dataWriteLen:]  # returns data not written


# finds inode via block number, writes data (bytearray), overwriting, updates metadata
def writeViaInode(inodeBNum, data):
    iBuf = Buffer()
    readBlock(DISK, inodeBNum, iBuf)
    iMeta = list(iBuf.data_bytes)[:META_SIZE]
    iData = list(iBuf.data_bytes)[META_SIZE:]
    if iMeta[RW_BYTE] == P_READ:
        print(f"ERR: READ ONLY FD: {inodeBNum}")
        return ERR_PERMISSIONS

    restData = data
    numBlocksUsed = 0  # used to index into inode claimed blocks
    usedBNums = []  # keep track of what blocks we write to
    while len(restData) > 0:
        currBlock = None
        # if inode already claimed a block for this chunk
        if numBlocksUsed < iMeta[SIZE_BYTE]:
            currBlock = iData[numBlocksUsed]
        else:  # inode needs new block
            currBlock = claimFreeBlock(
                first=(iMeta[TYPE_BYTE] != INODE_BLOCKT))  # claim first block if dirent or freemask, last otherwise
        usedBNums.append(currBlock)
        # write data to block, updating its header, save data that couldn't fit
        restData = writeBlockMeta(currBlock, restData)
        numBlocksUsed += 1

    # used fewer blocks than previously allocated
    if numBlocksUsed < iMeta[SIZE_BYTE]:
        for i in range(numBlocksUsed, iMeta[SIZE_BYTE]):
            emptyBuf = Buffer()
            emptyBuf.data_bytes = bytearray([0] * (BLOCKSIZE-META_SIZE))
            writeBlock(DISK, iData[i], emptyBuf)

    # update meta data for this inode
    newInodeData = iMeta
    newInodeData[SIZE_BYTE] = numBlocksUsed
    newInodeData += usedBNums

    newIBuf = Buffer()
    newIBuf.data_bytes = bytearray(newInodeData)
    writeBlock(DISK, inodeBNum, newIBuf)
    return 0


# prints first 50 bytes of first and last 10 blocks
def printMem():
    for i in range(10):
        b = Buffer()
        readBlock(DISK, i, b)
        print(f"Block {i}: {list(b.data_bytes)[:50]}")
    print("...\nlast10:\n...")
    for i in range(int(DISK_SIZE/BLOCKSIZE)-10, int(DISK_SIZE/BLOCKSIZE)):
        b = Buffer()
        readBlock(DISK, i, b)
        print(f"Block {i}: {list(b.data_bytes)[:50]}")


###
# Make an empty TinyFS of size nBytes on specified file
# Use libDisk to open file, format file to be mounted
# init data to 0x00, set magic numbers, init/write superblock and other metadata
#
# superblock entry in order: magic_number, root inode pointer, freeblock pointer
###
# tfs_mkfs(str, int) -> int (Success/Error Code)
def tfs_mkfs(filename, nBytes=DEFAULT_DISK_SIZE):
    global DISK
    if DISK is not None:
        print(f"tfs_mkfs: ERR_MOUNTED, mounted disk: {DISK}")
        return ERR_MOUNTED
    numBlocks = int(nBytes/BLOCKSIZE)
    global DISK_SIZE
    DISK_SIZE = nBytes
    # open new disk, check errors
    diskNum = openDisk(filename, nBytes)
    if diskNum < 0:
        print("tfs_mkfs: ERR_DISK_CREATION")
        return diskNum  # ERROR

    DISK = diskNum
    global SB
    SB = [0] * META_SIZE
    SB[0] = MAGIC_NUMBER

    global FREE_MASK
    FREE_MASK = [EMPTY] * numBlocks  # len(Freemask) = # blocks
    FREE_MASK[SUPER_BLOCK] = FILLED  # super block is not free

    freeMaskBlock = claimFreeBlock()
    # free block bit mask
    SB[SB_FREE] = createInode([freeMaskBlock], bType=FREE_MASKT)

    direntNumBlock = claimFreeBlock()
    # inode for inode block bumbers
    SB[SB_NUM] = createInode([direntNumBlock], bType=DIRENT_NUMT)

    direntNameBlock = claimFreeBlock()
    # file names stored via this INode
    SB[SB_NAME] = createInode([direntNameBlock], bType=DIRENT_NAMET)

    # save Free mask
    writeViaInode(SB[SB_FREE], bytearray(FREE_MASK))

    supBuf = Buffer()
    supBuf.data_bytes = bytearray(SB)  # save SB to disk
    if writeBlock(DISK, SUPER_BLOCK, supBuf) < 0:
        return ERR_DISK

    return 0


###
# Mount a TinyFS file found on filename
# Verify type/format of FS, only one system mounted at a time
###
# tfs_mount(str) -> int (Success/Error Code)
def tfs_mount(filename):
    global DISK
    if DISK is not None:
        print(f"tfs_mkfs: ERR_MOUNTED, mounted disk: {DISK}")
        return ERR_MOUNTED
    diskNum = openDisk(filename, 0)  # open without overwriting data
    DISK = diskNum

    superBlock = Buffer()
    if readBlock(diskNum, 0, superBlock) < 0:  # fetch super block
        return ERR_DISK  # Error

    global SB
    SB = list(superBlock.data_bytes)

    if SB[0] != 0x5A:
        return ERR_FS_FORMAT  # Invalid FS format

    # load free mask into memory
    global FREE_MASK
    FREE_MASK = readViaInode(SB[SB_FREE])

    # load root dir into memory
    global DIRENT
    DIRENT = {}
    dirNums = readViaInode(SB[SB_NUM])
    # decode array of ascii numbers into array of file names
    dirNames = readViaInode(SB[SB_NAME])
    dirNames = bytearray(dirNames).decode().split("\x00")[:-1]

    for i in range(len(dirNums)):
        DIRENT[dirNames[i]] = dirNums[i]

    return 0


###
# Cleanly unmount the current filesystem
# write any important data to superblock, close all files (?)
###
# tfs_unmount() -> int (Success/Error Code)
def tfs_unmount():
    global DISK
    global DIRENT
    global DRT
    supBuf = Buffer()
    supBuf.data_bytes = bytearray(SB)  # save SB to disk
    if writeBlock(DISK, SUPER_BLOCK, supBuf) < 0:
        return ERR_DISK
    writeViaInode(SB[SB_FREE], bytearray(FREE_MASK))
    writeViaInode(SB[SB_NUM], list(DIRENT.values()))
    encodedNames = bytearray()
    [encodedNames.extend((n+'\0').encode()) for n in list(DIRENT.keys())]
    writeViaInode(SB[SB_NAME], encodedNames)
    DISK = None
    DIRENT = {}
    DRT = {}
    return 0


###
# Within the current mounted system, open a file to read and write
# create dynamic resource table entry with internal file pointer, etc.
###
# tfs_open(str) -> int (file descriptor/Error Code)
def tfs_open(name):
    global DIRENT
    if name not in DIRENT:
        DIRENT[name] = createInode([])  # create empty inode
    DRT[DIRENT[name]] = 0
    return DIRENT[name]


###
# Closes file at fileDescriptor, removes dynamic resource table entry
###
# tfs_close(fileDescriptor) -> int (Success/Error Code)
def tfs_close(fileDescriptor):
    del DRT[fileDescriptor]
    return 0


###
# Write to FD: buffer "buffer" of size "size", representing entire file's contents
# Set file pointer to start of file (0)
###
# tfs_write(fileDescriptor, list, int) -> int (Success/Error Code)
def tfs_write(FD, data):
    if FD not in DRT:
        return ERR_FILE_CLOSED
    err = writeViaInode(FD, data)
    if err >= 0:
        DRT[FD] = 0
        return 0
    else:
        return err


###
# Deletes file @ FD in FS and sets its blocks to free
###
# tfs_delete(fileDescriptor) -> int (Success/Error Code)
def tfs_delete(FD):
    iBuf = Buffer()
    readBlock(DISK, FD, iBuf)
    meta = list(iBuf.data_bytes)[:META_SIZE]
    blocks = list(iBuf.data_bytes)[META_SIZE:]

    # 'free' all blocks pointed to by FD
    global FREE_MASK
    for i in range(meta[SIZE_BYTE]):
        emptyBuf = Buffer()
        emptyBuf.data_bytes = bytearray([0] * (BLOCKSIZE-META_SIZE))
        writeBlock(DISK, blocks[i], emptyBuf)
        FREE_MASK[blocks[i]] = EMPTY
    emptyBuf = Buffer()
    emptyBuf.data_bytes = bytearray([0] * (BLOCKSIZE-META_SIZE))
    writeBlock(DISK, FD, emptyBuf)  # clear inode block and set it to free
    FREE_MASK[FD] = EMPTY
    global DIRENT
    # remove file name from DIRENT
    del DIRENT[list(DIRENT.keys())[list(DIRENT.values()).index(FD)]]


###
# read one byte from file @ FD and copies it to buffer
# increments file pointer by 1, return error if at end of file
###
# tfs_readByte(fileDescriptor, Buffer) -> int (Success/Error Code)
def tfs_readByte(FD, buffer):
    if FD not in DRT:
        print(f"tfs_readByte: ERR_FILE_CLOSED, FD: {FD}")
        return ERR_FILE_CLOSED

    data = readViaInode(FD)
    if DRT[FD] >= len(data):
        print(f"tfs_readByte: ERR_EOF, FD: {FD}, len: {len(data)}")
        return ERR_EOF
    dbyte = data[DRT[FD]]
    DRT[FD] += 1
    buffer.data_bytes = bytearray([dbyte])
    return 0


###
# Change file pointer location of file @ FD to offset (relative to beginning)
###
# tfs_seek(fileDescriptor, int) -> int (Success/Error Code)
def tfs_seek(FD, offset):
    if FD not in DRT:
        print(f"tfs_seek: ERR_FILE_CLOSED, FD: {FD}")
    data = readViaInode(FD)  # this is dumb
    if offset > len(data):
        print(
            f"tfs_seek: ERR_EOF, FD: {FD}, len: {len(data)}, sought: {offset}")
        return ERR_EOF
    DRT[FD] = offset


# renames file named oldName to newName...
def tfs_rename(oldName, newName):
    global DIRENT
    if oldName not in DIRENT:
        print(f"tfs_rename: ERR_FILE_NOT_FOUND name: {oldName}")
        return ERR_FILE_NOT_FOUND

    oldFD = DIRENT[oldName]
    del DIRENT[oldName]
    DIRENT[newName] = oldFD


# prints all files in dir (and dirs, but no hierarchical dirs)
def tfs_readdir():
    [print(f) for f in list(DIRENT.keys())]


# make file indicated by name write only
def tfs_makeRO(name):
    if name not in DIRENT:
        print(f"tfs_makeRO: ERR_FILE_NOT_FOUND name: {name}")
        return ERR_FILE_NOT_FOUND
    b = Buffer()
    readBlock(DISK, DIRENT[name], b)
    meta = list(b.data_bytes)[:META_SIZE]
    meta[RW_BYTE] = P_READ
    newMeta = Buffer()
    newMeta.data_bytes = bytearray(meta)
    writeBlock(DISK, DIRENT[name], newMeta)
    return 0


# make file read write
def tfs_makeRW(name):
    if name not in DIRENT:
        print(f"tfs_makeRO: ERR_FILE_NOT_FOUND name: {name}")
        return ERR_FILE_NOT_FOUND
    b = Buffer()
    readBlock(DISK, DIRENT[name], b)
    meta = list(b.data_bytes)[:META_SIZE]
    meta[RW_BYTE] = P_RW
    newMeta = Buffer()
    newMeta.data_bytes = bytearray(meta)
    writeBlock(DISK, DIRENT[name], newMeta)
    return 0
