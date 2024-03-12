import os
import shutil
import hashlib
import logging

# Setup logging
logging.basicConfig(filename='backup_log.txt', level=logging.INFO, format='%(asctime)s %(message)s')

# This script backs up the files in the source drive/directory to the backup
# drive/directory. The two variables below are used to set the source and
# destination. Running these as command line parameters might be a better
# enhancement, but this worked well for my purposes.
#
# The script walks through the source folder and copies regular files
# across before doing a checksum to ensure the file copied correctly.
# Symbolic links do not work well between operating systems so I create a file
# called _symlinks_meta.txt to record that data in case I want to restore it
# later.

source_directory = "H:/Dads Files"
backup_directory = "D:/Dads Files"

def calculate_checksum(file_path):
    """Calculate MD5 checksum for a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def strip_extended_path_prefix(path):
    """Strip the '\\?\' prefix from a path if it exists, to normalize extended-length paths."""
    if path.startswith('\\\\?\\'):
        return path[4:]
    return path

def write_link_metadata(destination_dir, link_name, target_path):
    """Write symbolic link information to a metadata file."""
    metadata_file_path = os.path.join(destination_dir, "_symlinks_meta.txt")
    with open(metadata_file_path, "a") as metafile:
        metafile.write(f"{link_name}\t{target_path}\n")
    logging.info(f"Recorded symbolic link in metadata: {destination_dir}/{link_name} -> {target_path}")

def copy_file(source, source_root, destination, destination_root):
    normalized_source_base = os.path.normpath(strip_extended_path_prefix(source_root))
    
    if os.path.islink(source):

        link_target = os.readlink(source)

        normalized_link_target = os.path.normpath(strip_extended_path_prefix(link_target))
        relative_path_to_target = os.path.relpath(normalized_link_target, normalized_source_base)
        absolute_destination_target = os.path.normpath(os.path.join(destination_root, relative_path_to_target))
        
        destination_dir = os.path.dirname(destination)
        link_name = os.path.basename(source)
        write_link_metadata(destination_dir=destination_dir, link_name=link_name, target_path=absolute_destination_target)
        
    else:
        if not os.path.exists(destination):

            try:
                shutil.copy2(source, destination)
            except:
                print('Error copying', source, 'to', destination, 'length', len(destination))
                raise

            src_checksum = calculate_checksum(source)
            dst_checksum = calculate_checksum(destination)
            if src_checksum != dst_checksum:
                logging.error(f"Checksum mismatch: {source} -> {destination}")
                return False
        else:
            logging.info(f"File already exists and was not copied: {destination}")

    return True

def create_backup(src_dir, dst_dir):
    """Backup the directory incrementally."""
    for root, dirs, files in os.walk(src_dir):
        relative_path = os.path.relpath(root, src_dir)

        # Avoid creating paths with '.\' which denotes current directory in Windows
        if relative_path == ".":
            relative_path = ""

        dst_path = os.path.join(dst_dir, relative_path)
        print('Number of files', len(files), dst_path)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_path, file)

            # Copy if file doesn't exist or if it's modified (based on modification time)
            if not os.path.exists(dst_file) or os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                if copy_file(
                    source=src_file,
                    source_root=src_dir,
                    destination=dst_file,
                    destination_root=dst_dir,
                ):
                    pass
                    #logging.info(f"Copied: {src_file} to {dst_file}")
                else:
                    logging.error(f"Failed to copy: {src_file}")

try:
    create_backup(source_directory, backup_directory)
    logging.info("Backup completed successfully.")
except Exception as e:
    logging.error("Backup failed: " + str(e))
    raise