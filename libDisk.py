import unittest
import os

###
# Implement Basic Block Operations
###

BLOCKSIZE = 256  # Bytes

# Tracks the disks
#Key is the disk #
# Value is (Filename, state) 1 - Open, 0 - Closed
diskTracker_Dic = {}

# Buffer of size BLOCKSIZE bytes


class Buffer:
    filled = 0
    data_bytes = []


###
# Opens a UNIX file and designates the first nBytes for the emulated disk. nBytes should be divisible by the BLOCKSIZE...
# If nBytes > 0 and file already exisits it should be overwritten.
# If nBytes = 0, an existing disk is opened and should NOT be overwritten
# Errors must be returned for other failures
###
# openDisk(str, int) -> int (disk#/Error Code)
def openDisk(filename, nBytes):
    global diskTracker_Dic
    # The file exists and should be set to open
    if(nBytes == 0):
        for key, value in diskTracker_Dic.items():
            if value[0] == filename:
                diskTracker_Dic.update({key: (filename, 1)})
                return key
        # Error code for if attempting to open a disk that does no exists.
        return -100
    else:
        with open(filename, 'wb') as binfile:
            # This writes BLOCKSIZE * nBytes, it should be just nBytes (divisible by BLOCKSIZE)
            # binfile.write(b'\x00' * BLOCKSIZE * nBytes)
            binfile.write(b'\x00' * nBytes)

    diskNum = len(diskTracker_Dic)
    diskTracker_Dic.update({diskNum: (filename, 1)})
    return diskNum


###
# Reads the entire block of BLOCKSIZE bytes from an open disk and copy to a local buffer (with size of at least BLOCKSIZE)
# bNum is logical block number, nBum * BLOCKSIZE = bytes into the disk
# If function is sucessful return 0
# Errors must be returned for other failures
###
# readBlock(int, int, Buffer) -> int (0/Error Code)
def readBlock(disk, bNum, block):
    global BLOCKSIZE
    global diskTracker_Dic

    starting_byte = BLOCKSIZE * bNum
    # Get the file if the disk exists and it is "open"
    if disk in diskTracker_Dic and diskTracker_Dic[disk][1] == 1:
        filename = diskTracker_Dic[disk][0]
    else:
        return -101  # Error code for atteempts to read from a disk that is closed or does not exists

    # Read the file
    with open(filename, "rb") as binfile:
        binfile.seek(starting_byte)  # skip the initial bytes
        data = binfile.read(BLOCKSIZE)
        # Fill the provided block (Buffer)
        block.data_bytes = data
        block.filled = 1
    return 0


###
# Writs the content of the provided buffer to the disk and location defined
# The disk must be OPEN
###
# writeBlock(int, int, Buffer) -> int (0/Error Code)
def writeBlock(disk, bNum, block):
    global BLOCKSIZE
    global diskTracker_Dic

    starting_byte = BLOCKSIZE * bNum
    # Get the file if the disk exists and it is "open"
    if disk in diskTracker_Dic and diskTracker_Dic[disk][1] == 1:
        filename = diskTracker_Dic[disk][0]
    else:
        return -101  # Error code for attempting to read from a disk that is closed or does not exists

    # Write to the file
    with open(filename, "r+b") as binfile:
        binfile.seek(starting_byte)  # skip the initial bytes
        binfile.write(block.data_bytes)
        # Empty the provided block (Buffer)
        block.data_bytes = []  # bytearray(0)
        block.filled = 0
    return 0


###
# Closes the disk that is provided so it is no longer open to I/O calls.
# Calls to the close disk (reads/writes) should result in an error
# Any underlying files and uncommited writes should be closed.
###
# closeDisk(int) -> int (0/Error Code)
def closeDisk(disk):
    global diskTracker_Dic

    # Check that this disk exists
    if disk in diskTracker_Dic:
        diskTracker_Dic.update({disk: (diskTracker_Dic[disk][0], 0)})
    else:
        return -102  # Error code for attempting to close a file that does not exist
    return 0


### Error Codes ###
# -100 #Error code for if attempting to open a disk that does no exists.
# -101 #Error code for atteempts to read from a disk that is closed or does not exists
# -102 #Error code for attempting to close a file that does not exist

### Testing ###
class TestlibDiskMethods(unittest.TestCase):
    def test_openDisk_newfile(self):
        global diskTracker_Dic
        functionReturn = openDisk("testing_openDisk", 2)
        with open("testing_openDisk", 'rb') as binfile:
            contentLen = len(binfile.read())
        self.assertEqual(contentLen, BLOCKSIZE * 2)
        self.assertEqual(functionReturn, 0)
        os.remove("testing_openDisk")
        diskTracker_Dic = {}

    def test_openDisk_overwrite(self):
        global diskTracker_Dic
        openDisk("testing_openDisk", 2)
        functionReturn = openDisk("testing_openDisk", 1)
        with open("testing_openDisk", 'rb') as binfile:
            contentLen = len(binfile.read())
        self.assertEqual(contentLen, BLOCKSIZE * 1)
        self.assertEqual(functionReturn, 1)

        os.remove("testing_openDisk")
        diskTracker_Dic = {}

    def test_openDisk_openExisting(self):
        global diskTracker_Dic
        openDisk("testing_openDisk", 1)
        functionReturn = openDisk("testing_openDisk", 0)
        self.assertEqual(functionReturn, 0)
        os.remove("testing_openDisk")
        diskTracker_Dic = {}

    def test_openDisk_openNONExisting(self):
        global diskTracker_Dic
        functionReturn = openDisk("NOT_AN_openDisk", 0)
        self.assertEqual(functionReturn, -100)
        diskTracker_Dic = {}

    def test_readBlock_openDisk(self):
        global diskTracker_Dic
        functionReturn = openDisk("testing_openDisk", 2)

        ff_bytes = []  # bytearray()
        ff_bytes.append(0xFF)

        # Change byte 255 to FF just to check
        fh = open("testing_openDisk", "r+b")
        fh.seek(255)
        fh.write(ff_bytes)
        fh.close()

        block = Buffer()
        functionReturn = readBlock(functionReturn, 0, block)
        self.assertEqual(functionReturn, 0)
        self.assertEqual(block.filled, 1)
        self.assertEqual(block.data_bytes, bytearray(BLOCKSIZE - 1) + ff_bytes)

        os.remove("testing_openDisk")
        diskTracker_Dic = {}

    def test_readBlock_closedDisk(self):
        global diskTracker_Dic
        functionReturn = openDisk("NOT_AN_openDisk", 0)
        block = Buffer()
        functionReturn = readBlock(0, 0, block)
        self.assertEqual(functionReturn, -101)
        self.assertEqual(block.filled, 0)
        self.assertNotEqual(block.data_bytes, bytearray(BLOCKSIZE))

        diskTracker_Dic = {}

    def test_writeBlock_openDisk(self):
        global diskTracker_Dic
        diskNumber = openDisk("testing_openDisk", 2)

        ff_bytes = bytearray()
        ff_bytes.append(0xFF)

        # Change byte 255 to FF just to check
        fh = open("testing_openDisk", "r+b")
        fh.seek(255)
        fh.write(ff_bytes)
        fh.close()

        block = Buffer()
        functionReturn = readBlock(diskNumber, 0, block)
        self.assertEqual(functionReturn, 0)
        self.assertEqual(block.filled, 1)
        self.assertEqual(block.data_bytes, bytearray(BLOCKSIZE - 1) + ff_bytes)

        functionReturn = writeBlock(diskNumber, 1, block)
        self.assertEqual(functionReturn, 0)
        self.assertEqual(block.filled, 0)
        self.assertEqual(block.data_bytes, bytearray(0))

        with open("testing_openDisk", 'rb') as binfile:
            fullFile = binfile.read()
        self.assertEqual(fullFile, bytearray(BLOCKSIZE - 1) +
                         ff_bytes + bytearray(BLOCKSIZE - 1) + ff_bytes)

        os.remove("testing_openDisk")
        diskTracker_Dic = {}

    def test_writeBlock_closedDisk(self):
        global diskTracker_Dic

        functionReturn = openDisk("NOT_AN_openDisk", 0)
        block = Buffer()
        functionReturn = writeBlock(0, 0, block)
        self.assertEqual(functionReturn, -101)
        self.assertEqual(block.filled, 0)
        self.assertEqual(block.data_bytes, bytearray(0))

        diskTracker_Dic = {}

    def test_closeDisk_existingDisk(self):
        global diskTracker_Dic

        disk = openDisk("testing_openDisk", 2)
        self.assertEqual(disk, 0)
        self.assertEqual(diskTracker_Dic[disk][1], 1)

        functionReturn = closeDisk(disk)
        self.assertEqual(functionReturn, 0)
        self.assertEqual(diskTracker_Dic[disk][1], 0)

        os.remove("testing_openDisk")
        diskTracker_Dic = {}


if __name__ == '__main__':
    unittest.main()
