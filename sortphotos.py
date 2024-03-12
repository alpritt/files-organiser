import os
from PIL import Image
import shutil
import glob
import datetime

# I didn't want to copy every file type (mostly photos), so this splits up what
# I am copying across based on the file extension. Anything not included brought
# up a prompt so I could choose to copy it or skip it or load the file if it was
# an image to help me decide. These should be in lowercase to match, and they
# should have a dot to avoid false positives.
definitely_copy = ('.jpg', '.jpeg', '.odt', '.cpt', '.3gp', '.gft', '.xmp', '.cr2', '.png', '.dng', '.gif', '.txt', '.bmp', '.css', '.avi', '.htm', '.html', '.rtf', '.mht', '.tiff', '.tif', '.wmf', '.pdf', '.mov', '.doc', '.docx', '.psd', '.pdd', '.fpt', '.xls')
definitely_ignore_extensions = ('.ini', '.cab', '.toc', '.gif', '.vif', '.tlv', '.cam', '.chk', '.dat', '.db', '.info', '.bin', '.wbcat', '.js', '.lnk', '.shs', '.crw', '.thm', '.alb', '.tmp', '.ncd', '.cxf', '.zdp', '.cld', '.inf', '.rmg', 'zdx', '.cdx', '.dbf', '.dll')

def preview_image(file_path):
    try:
        # Open the image using PIL
        img = Image.open(file_path)
        img.show()
    except Exception as e:
        print(f"Error previewing '{file_path}': {str(e)}")


def organise_by_hash(input_files):

    hashes = {}
    for input_file in input_files:
        with open(input_file, 'r') as f:
            for line in f:
                try:
                    hash_md5, file_path = line.strip().split(',', 1)
                except ValueError:
                    print("Error processing line:", line)
                    continue  # Skip this line and continue with the next

                if hash_md5 in hashes:
                    hashes[hash_md5].append(file_path)
                else:
                    hashes[hash_md5] = [file_path]

    return hashes
	
# This just displays which hashes are duplicates.
def find_duplicates(input_files):
    hashes = organise_by_hash(input_files)
    for hash_md5, files in hashes.items():
        if len(files) > 1:
            print(f"Duplicate files for hash {hash_md5}:")
            for file in files:
                print(f"    {file}")

# This counts how many hashes appear more than once vs only once and prints that result.
# It might make more sense to display it by number of duplicates.
def count_duplicates_vs_single_reference(input_files):
    hashes = organise_by_hash(input_files)
    single_reference_counter = 0
    duplicates_counter = 0
    for hash_md5, files in hashes.items():
        if len(files) > 1:
            duplicates_counter += 1
        elif len(files) == 1:
            single_reference_counter += 1
        else:
            raise Exception('Should not be reachable')

    print(f"duplicates {duplicates_counter}")
    print(f"single reference {single_reference_counter}")
	
def delete_duplicates(input_files):
    # Organize files by their hash
    hashes = organise_by_hash(input_files)
    
    # Iterate through the organized hashes
    for hash_md5, possible_files in hashes.items():

        files = []  # To store files that still exist on the file system
	
        if len(possible_files) > 1:
		
            # Check if each file exists
            for file_path in possible_files:
                if os.path.exists(file_path):
                    files.append(file_path)
	
        if len(files) > 1:
            print(f"Duplicate files for hash {hash_md5}:")
			
			# Display the first file
            first_file = files[0]
            #os.system(f'start "" "{first_file}"')
            #subprocess.Popen(['start', '', first_file], shell=True)
            preview_image(first_file)

            # Enumerate and display files with index
            for idx, file in enumerate(files, start=1):
                print(f"    {idx}. {file}")
            
            # Display options
            while True:
                option = input("Press 'd' followed by a number to delete the file, "
                               "'o' followed by a number to open the file in windows, "
                               "or 'c' to continue to the next set of files: ").strip()
                
                if option.startswith('d'):
                    try:
                        # Extract the index after 'd'
                        file_idx = int(option[1:])
                        if 1 <= file_idx <= len(files):
                            # Delete the selected file
                            file_to_delete = files[file_idx - 1]
                            os.remove(file_to_delete)
                            print(f"File '{file_to_delete}' deleted.")
                            # Remove the deleted file from the list
                            files.pop(file_idx - 1)
                            if not files:
                                print("No more files for this hash.")
                            break
                        else:
                            print("Invalid file index.")
                    except ValueError:
                        print("Invalid input.")
                    
                elif option.startswith('o'):
                    try:
                        # Extract the index after 'o'
                        file_idx = int(option[1:])
                        if 1 <= file_idx <= len(files):
                            # Open the selected file in Windows (you may need to specify the software here)
                            file_to_open = files[file_idx - 1]
                            os.system(f'start "" "{file_to_open}"')
                            print(f"Opening '{file_to_open}' in Windows.")
                        else:
                            print("Invalid file index.")
                    except ValueError:
                        print("Invalid input.")
                
                elif option == 'c':
                    break
                else:
                    print("Invalid option. Please enter 'd', 'o', or 'c'.")
			
def collect_hashes_from_file(file_path):
    hashes = {}

    try:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    hash_md5, file_path = line.strip().split(',', 1)
                except ValueError:
                    print("Error processing line:", line)
                    continue  # Skip this line and continue with the next

                if hash_md5 in hashes:
                    hashes[hash_md5].append(file_path)
                else:
                    hashes[hash_md5] = [file_path]
    except Exception as e:
        print(f"Error reading file '{file_path}': {str(e)}")
        raise

    return hashes
			
			 
def compare_hashes(hash_filepath_A, hash_filepath_B, exclude: list[str]=[]):
    # Collect hashes and file paths from the primary source file
    source_hashes = collect_hashes_from_file(hash_filepath_A)
    destination_hashes = collect_hashes_from_file(hash_filepath_B)
    added_hashes = get_added_hashes()
    for hash_md5 in added_hashes:
        if hash_md5 not in destination_hashes:
            destination_hashes[hash_md5] = added_hashes[hash_md5]

    print('These are the first few hashes for the two hash files. It can be used to tell if the source and destination match to some extent:')
    print('Primary source:', list(destination_hashes.keys())[0:5])
    print('Other source', list(source_hashes.keys())[0:5])

    # Initialize counters
    exist_count = 0
    ignore_count = 0
    not_exist_count = 0
    not_exist_files = []
    exist_files = []

    # Iterate through the hashes in the other sources
    for hash_md5 in source_hashes:

        source_path = source_hashes[hash_md5][0].lower()

        if source_path.endswith(definitely_ignore_extensions):
            ignore_count += 1
        elif any(excl in source_path for excl in exclude):
            ignore_count += 1
        elif hash_md5 in destination_hashes:
            exist_count += 1
            for item in source_hashes[hash_md5]:
                exist_files.append(f"{hash_md5} - {item}")
        else:
            not_exist_count += 1
            for item in source_hashes[hash_md5]:
                not_exist_files.append(f"{hash_md5} - {item}")

    if not_exist_count > 0:
        print("Files that do not exist in destination source:")
        for file_path in not_exist_files:
            print(f"    {file_path}")
            pass
			
    if exist_count > 0:
        print("Files that do exist in destination source:")
        for file_path in exist_files:
            #print(f"    {file_path}")
            pass

    print("")
    print(f"Comparison results:")
    print(f"    Exist in destination source: {exist_count}")
    print(f"    Do not exist in destination source: {not_exist_count}")
    print(f"    Ignored: {ignore_count}")
	


def verify_symlink(target_path, link_path):
    # Ensure the link exists and is a symlink
    if not os.path.islink(link_path):
        return False
    # Resolve the symlink to its ultimate target
    symlink_target = os.path.realpath(link_path)
    # Compare the resolved symlink target with the target's real path
    return os.path.realpath(symlink_target) == os.path.realpath(target_path)


def get_added_hashes():

    added_hashes = {}

    # Read content from all added_hashes.{timestamp}.txt files in the current directory
    for added_hashes_filename in glob.glob('added_hashes.*.txt'):
        with open(added_hashes_filename, 'r') as added_hashes_file:
            for line in added_hashes_file:
                line = line.strip()
                if line:
                    hash_md5, file_paths = line.split(',', 1)
                    file_paths = file_paths.split(',')
                    if hash_md5 in added_hashes:
                        # Merge or update the file paths associated with this hash
                        added_hashes[hash_md5].extend(file_paths)
                    else:
                        added_hashes[hash_md5] = file_paths

    return added_hashes

def copy_over_files(destination_directory, source_root_directory, destination_hash_filepath, source_hash_filepath):
    # Collect hashes and file paths from the primary source file
    destination_hashes = collect_hashes_from_file(destination_hash_filepath)
    added_hashes = get_added_hashes()
    for hash_md5 in added_hashes:
        if hash_md5 not in destination_hashes:
            destination_hashes[hash_md5] = added_hashes[hash_md5]
    source_hashes = collect_hashes_from_file(source_hash_filepath)

    # Create a set to keep track of copied hashes to avoid duplicates
    copied_hashes = set()

    # Iterate through the hashes in the other source
    for hash_md5 in source_hashes:
        if hash_md5 not in destination_hashes:

            destination_paths_with_numbers = []
            for idx, source_path in enumerate(source_hashes[hash_md5], start=1):
                relative_path = os.path.relpath(source_path, start=source_root_directory)
                destination_path = os.path.join(destination_directory, relative_path)
                destination_paths_with_numbers.append((idx, destination_path, source_path))

            source_path = destination_paths_with_numbers[0][2].lower()

            if source_path.endswith(definitely_copy):
                copy_or_symlink_file(destination_paths_with_numbers)

            elif source_path.endswith(definitely_ignore_extensions):
                # Don't copy, proceed to the next iteration.
                continue
    
            else:
                deal_with_copy_file_user_input(destination_paths_with_numbers, hash_md5, source_hashes)

            copied_hashes.add(hash_md5)

    # Generate a new filename with the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"added_hashes.{timestamp}.txt"

    # Save the list of copied hashes to 'added_hashes.txt' file
    with open(new_filename, 'w') as added_hashes_file:
        for hash_md5 in copied_hashes:
            file_paths = source_hashes[hash_md5]
            added_hashes_file.write(f"{hash_md5},{','.join(file_paths)}\n")

def deal_with_copy_file_user_input(destination_paths_with_numbers, hash_md5, source_hashes):

    print(f"Hash '{hash_md5}' {destination_paths_with_numbers[0][2]} does not exist in the primary source and we do not recongise the file extension.")

    # Create a list of file paths with corresponding numbers

    user_input = input("Enter s to skip, o to open the file or c to copy: ")
    user_input = user_input.strip()

    if user_input == 's':
        return  # Skip to the next hash
            
    elif user_input == 'o':
        file_to_open = source_hashes[hash_md5][0]
        preview_image(file_to_open)
        deal_with_copy_file_user_input(destination_paths_with_numbers, hash_md5, source_hashes)

    elif user_input == 'c':
        copy_or_symlink_file(destination_paths_with_numbers)

    else:
        print('Invalid response')
        deal_with_copy_file_user_input(destination_paths_with_numbers, hash_md5, source_hashes)

def copy_or_symlink_file(destination_paths_with_numbers):

    the_copy_path = None

    for file_data in destination_paths_with_numbers:
        index = file_data[0]
        destination_path = file_data[1]
        source_path = file_data[2]

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Copy the selected file to the chosen destination directory
        
        # The first instance of the file should be copied and then everything else should
        # be linked to that same copy.

        try:
            if os.path.exists(destination_path):
                print(f"File already exists at {destination_path}. Skipping.")
            else:

                if index == 1:
                    shutil.copy(source_path, destination_path)
                    the_copy_path = destination_path
                    print(f"Copied {index}-{source_path} to {destination_path}")
                elif the_copy_path:
                    if os.path.exists(destination_path):
                        print(f"File already exists at {destination_path}. Skipping.")
                    else:
                        the_copy_path = os.path.abspath(the_copy_path)
                        destination_path = os.path.abspath(destination_path)
                        os.symlink(the_copy_path, destination_path)
                        if verify_symlink(the_copy_path, destination_path):
                            print(f"Linked {source_path} to {destination_path} as a link to {the_copy_path}")
                        else:
                            print(f"Failed to create a valid symlink for {the_copy_path} at {destination_path}.")

        except FileExistsError:
            print(f"File already exists at {destination_path}. Skipping.")
        except Exception as e:
            print(f"Error: {e}")