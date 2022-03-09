from libDisk import openDisk

###
# Phase 2: a simple file system
###


# class Superblock:
# Store meta data about FS, stored at logical block 0
##
# magicNumber: detect if disk has formatted FS to be mounted 0x5A, first byte
# rootInode: block number of root directory (tracks name-inode pairs)
# freeBlockHead: head of linked list for free block data structure


# class Inode:

# Keep track of meta data for each file
##
# creation, access time
# start of file
# next inode

# class DataBlock:
# Fixed sized block containing file data

# class FreeBlock:
# Empty DataBlock ready to be allocated (to store inode or data)
# Contains means of finding other free blocks?


# ------------------------------------------------------------------------------------
# Bytes in block
BLOCKSIZE = 256

# 40 blocks worth of bytes available for every disk, can be updated
DEFAULT_DISK_SIZE = 10240

# Default name for a new disk
DEFAULT_DISK_NAME = "tinyFSDisk"

# Dynamic resource table stores
DRT = {}


###
# Make an empty TinyFS of size nBytes on specified file
# Use libDisk to open file, format file to be mounted
# init data to 0x00, set magic numbers, init/write superblock and other metadata
###
# tfs_mkfs(str, int) -> int (Success/Error Code)
def tfs_mkfs(filename, nBytes):
    pass


###
# Mount a TinyFS file found on filename
# Verify type/format of FS, only one system mounted at a time
###
# tfs_mount(str) -> int (Success/Error Code)
def tfs_mount(filename):
    pass


###
# Cleanly unmount the current filesystem
###
# tfs_unmount() -> int (Success/Error Code)
def tfs_unmount():
    pass


###
# Within the current mounted system, open a file to read and write
# create dynamic resource table entry with internal file pointer, etc.
###
# tfs_open(str) -> int (file descriptor/Error Code)
def tfs_open(name):
    pass


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
