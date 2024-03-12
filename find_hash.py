# This just helps me find a particular hash within a file of hashes so I can
# find out where those files are located.

def find_hash(hash_file, hash_to_find):
    files = []
    with open(hash_file, 'r') as f:
        for line in f:
            try:
                hash_md5, file_path = line.strip().split(',', 1)
            except ValueError:
                print("Error processing line:", line)
                continue  # Skip this line and continue with the next

            if hash_md5 == hash_to_find:
                print(file_path)
                files.append(file_path)


    return files
	

find_hash('drive_PC_H_Collecting_to_keep.txt', 'f8be58ab0c5fb7bdce242e1de18279ab')
