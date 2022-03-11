from libTinyFS import *
import libTinyFS
import unittest
import libDisk

print("-----------------Basic Testing with one File System----------------------")
# Generate a file system
print("Start by creating a file system")
tfs_mkfs("demo_1.dsk")
print("Initial Memory Disk 1: \n", libTinyFS.FREE_MASK)

print("\n")  # Create a file
print("Create a file")
disk_location = tfs_open("first_file")
print("first_file: \n",  "disk_location: ", disk_location)

print("\n")  # Write to the file
print("Writing to the file")
data_in = bytearray()
data_in.append(0xFF)
zeros = bytearray(10)
data_in = data_in + zeros
data_in.append(0xFF)
print("\tdata", str(data_in))
write_test = tfs_write(disk_location, data_in)
if(write_test == 0):
    print("Write Sucessful", disk_location)
else:
    print("Write Failed", disk_location)

print("\n")  # Close the file
print("Attempting to close the file")
close_test = tfs_close(disk_location)
if(close_test == 0):
    print("Close Sucessful", disk_location)
else:
    print("Close Failed", disk_location)

print("\n")  # Attemting to write to a closed file
print("Attempting to write on the closed file")
write_test = tfs_write(disk_location, data_in)
if(write_test == 0):
    print("Write Sucessful", disk_location)
else:
    print("Write Failed", disk_location)
    print("Error Code:", write_test)

print("\n")  # Attempting to read first Byte from closed file
print("Attempting read on closed file")
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)

else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

print("\n")  # Reopening closed file
print("Reopening the 'first_file'")
disk_location = tfs_open("first_file")
print("first_file: \n",  "disk_location: ", disk_location)

print("\n")  # Attempting to read first Byte from open file
print("Attempting read on open file")
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)

else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

print("\n")  # Attempting to read from open file again
print("Attempting read on open file again")
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)

else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

print("\n")  # Attempting to read from open file again
print("Using seek to shift the file pointer to 11 (to the end)")
tfs_seek(disk_location, 11)

print("\n")  # Attempting to read from open file again
print("Attempting read on open file again")
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)

else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

# Final memory for filesystem 1
print("Final Memory Disk 1: \n", libTinyFS.FREE_MASK)

print("Unmounting Disk 1")
unmount_test = tfs_unmount()
if(unmount_test < 0):
    print("Unmount Failed", unmount_test)

else:
    print("Unmount Sucessful")

print("\n\n------------------Demo with multiple file systems---------------------")

# Generate a second file system
print("Creating a second file system")
tfs_mkfs("demo_2.dsk")
print("Initial Memory Disk 2: \n", libTinyFS.FREE_MASK)

print("\n")  # Adding several files to disk 2
print("Adding several files")
files = []
files_names = ["file1", "file2", "file3"]
files.append(tfs_open(files_names[0]))
files.append(tfs_open(files_names[1]))
files.append(tfs_open(files_names[2]))
print("files:")
for i, f in enumerate(files):
    print("\t", files_names[i], ":", f)

print("Updated Memory Disk 2: \n", libTinyFS.FREE_MASK)

print("\n")  # Write to the file2
print("Writing to the 'file2'")
data_in = bytearray()
data_in.append(0xAA)
zeros = bytearray(11)
data_in = data_in + zeros
data_in.append(0xAA)
print("\tdata", str(data_in))
write_test = tfs_write(files[1], data_in)
if(write_test == 0):
    print("Write Sucessful", files[1])
else:
    print("Write Failed", files[1])

print("Memory Disk 2: \n", libTinyFS.FREE_MASK)

print("\n")  # Write to the file3
print("Writing to the 'file3'")
data_in = bytearray()
data_in.append(0xBB)
zeros = bytearray(300)
data_in = data_in + zeros
data_in.append(0xBB)
print("\tdata", str(data_in))
write_test = tfs_write(files[2], data_in)
if(write_test == 0):
    print("Write Sucessful", files[2])
else:
    print("Write Failed", files[2])
print("Memory Disk 2: \n", libTinyFS.FREE_MASK)

print("\n")  # Unmounting disk 2 and remounting disk1
print("Swapping back to disk 1")
unmount_test = tfs_unmount()
tfs_mount("demo_1.dsk")

print("\n")  # printing first value in memory of 'first_file'
print("Reading first byte from 'first_file'")
disk_location = tfs_open('first_file')
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)

else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

print("\n")  # Unmounting disk 1 and remounting disk2
print("Swapping back to disk 2")
unmount_test = tfs_unmount()
tfs_mount("demo_2.dsk")

print("\n")  # printing first value in memory of 'file2' and 'file3'
print("Reading first byte from 'file2' and 'file3'")
print('file2')
disk_location = tfs_open('file2')
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)
else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

print('file3')
disk_location = tfs_open('file3')
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)
else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

print("\n")  # deleting'file3'
print("Memory Disk 2: \n", libTinyFS.FREE_MASK)
tfs_delete(disk_location)
print("Deleting 'file3'")
print("Memory Disk 2: \n", libTinyFS.FREE_MASK)

print("\n")  # Reopening closed file with same name
print("Reopening a new file with the same name 'file3'")
disk_location = tfs_open("file3")
print("file3: \n",  "disk_location: ", disk_location)

print("\n")  # Attempting to print data from new file to check previous data was removed
print('Attempting to print data from new file to check previous data was removed')
disk_location = tfs_open('file3')
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)
else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

print("\n\n------------------Demo with Additional Features---------------------")
print("###Listing all files on disk, and remaning files")
# Attempting to print all files
print('Print all the files on the disk (Note we only have one directory)')
tfs_readdir()

print("\n")  # Rename 'file2' -> 'newFileName!'
print("Rename 'file2' -> 'newFileName!'")
tfs_rename('file2', 'newFileName')

print("\n")  # Attempting to print all files
print('Print all the files on the disk')
tfs_readdir()

print("\n")  # Attempting to read from renamed file to data still acessible
print('Attempting to read from renamed file to data still acessible')
disk_location = tfs_open('newFileName')
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)
else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)

print("\n###Allowing for Read-only and writeByte support")
print("Changing 'newFileName' to read only")
tfs_makeRO('newFileName')

print("\n")  # Write to the file
print("Writing to the 'newFileName'")
disk_location = tfs_open('newFileName')
data_in = bytearray()
data_in.append(0xCC)
zeros = bytearray(10)
data_in = data_in + zeros
data_in.append(0xCC)
print("\tdata", str(data_in))
write_test = tfs_write(disk_location, data_in)
if(write_test == 0):
    print("Write Sucessful", disk_location)
else:
    print("Write Failed", disk_location)

print("\nChanging 'newFileName' back to write AND read")
tfs_makeRW('newFileName')

print("\n")  # Write to the file
print("Writing to the 'newFileName'")
disk_location = tfs_open('newFileName')
data_in = bytearray()
data_in.append(0xCC)
zeros = bytearray(10)
data_in = data_in + zeros
data_in.append(0xCC)
print("\tdata", str(data_in))
write_test = tfs_write(disk_location, data_in)
if(write_test == 0):
    print("Write Sucessful", disk_location)
else:
    print("Write Failed", disk_location)

print("\n")  # Attempting to read from 'newFileName'
print("Attempting to read from 'newFileName'")
disk_location = tfs_open('newFileName')
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)
else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)


print("\n")  # Attempting to write over the second byte in 'newFileName'
print("Attempting to write over the second byte in 'newFileName'")

print("Using seek to shift the file pointer to index 1")
tfs_seek(disk_location, 1)

print("Writing in the Byte '5'")
tfs_writeByte(disk_location, 5)

print("Using seek to shift the file pointer to index 1")
tfs_seek(disk_location, 1)

# Attempting to read from 'newFileName'
print("Attempting to read from 'newFileName'")
buffer = Buffer()
read_test = tfs_readByte(disk_location, buffer)
if(read_test < 0):
    print("Read Failed", disk_location)
else:
    print("Read Sucessful", disk_location)
    print("Byte:", buffer.data_bytes)
