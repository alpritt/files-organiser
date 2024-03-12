import hashlib
import os, sys
import fnmatch

# This script scans through the contents of a folder and creates MD5 hashes
# for all the files (except those that match the patterns in the exclude file).

# The exclude file that I use is to avoid hashing large backup files which
# take forever to calculate an MD5 for and is something we didn't want to deal
# with anyway.

# I've not set up inputs for this, but instead am hard coding regular file paths
# and hashes I want to use.

def md5_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_exclusions(exclude_file):
    exclusions = []
    if os.path.exists(exclude_file):
        with open(exclude_file, 'r') as f:
            exclusions = f.read().split()
        print("Loaded exclusion list:", exclusions)
    return exclusions

def is_excluded(file_name, exclusions):
    for pattern in exclusions:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    return False

def write_hashes_to_file(start_path, output_file, exclude_file):

    # Check if the output file already exists
    if os.path.exists(output_file):
        print(f"The output file '{output_file}' already exists.")
        response = input("Do you want to overwrite it? (y/n): ")
        if response.lower() != 'y':
            print("Operation aborted by the user.")
            return
        else:
            print("Overwriting existing file.")

    exclusions = load_exclusions(exclude_file)
    print(exclusions)
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(start_path):
            for name in files:
                file_path = os.path.join(root, name)
                
                if is_excluded(file_path, exclusions):
                    print(f"Excluded: {file_path}")
                    continue
                
                # NOTE
                # I create symbolic links as part of copying files to the drive we are going to keep.
                # So I'm avoiding hashing them again. This could have consequences for hashing the 
                # source drives if you want to keep the files that the links point to, but in my case
                # I don't believe these exist so I'm not worrying about that problem. But it is worth
                # keeping in mind.
                if os.path.islink(file_path):
                    print(f"Skipping symbolic link: {file_path}")
                    continue
                
                try:
                    print(f"Processing {file_path}", end=' ')  # Feedback about processing file path
                    sys.stdout.flush()  # Explicitly flush the output buffer
                    file_hash = md5_hash(file_path)
                    print(f"Hash: {file_hash}")  # Print hash
                    f.write(f"{file_hash},{file_path}\n")
                    f.flush()  # Flush the output buffer to write to the file immediately
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

# Run this to hash the PC drive containing all the files we want to keep
def hash_collecting_to_keep_drive():
    write_hashes_to_file(
        start_path='H:/Dads Files/',
        output_file='drive_PC_H_Dads_Files.txt',
        exclude_file='hash_exclude'
    )

def hash_usb_backup_drive():
    write_hashes_to_file(
        start_path='D:/',
        output_file='D:/hashes.txt',
        exclude_file='hash_exclude'
    )

def hash_cd():
    write_hashes_to_file(
        start_path='M:/',
        output_file='drive_current_CD.txt',
        exclude_file='hash_exclude'
    )

# To make use of this, call write_hashes_to_file with the desired arguments.
#hash_usb_backup_drive()
#hash_cd()
#hash_collecting_to_keep_drive()