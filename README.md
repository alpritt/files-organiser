# files-organiser
*Some scripts related to organising files, backups, sorting, finding duplicates, etc.*

This is something you would want to edit for your own purposes as it is quite scrappy and only fit for my own unique task. But I've described what is going on to help share the approach.

These are a small collection of Python scripts for sorting through an old collection of my Dad's photographs. I didn't really understand his organisational system. There were intentionally many duplicates, and various drives, SD cards, USB sticks and CDs as well as data on two computers, so I wasn't 100% sure what was the original and possibly only copy and what was a backup.

So I created one script that creates a MD5 hash of every file in the format:

hash,full file path

For example:

```
ba3fcbebdc274c195e12812a29026671,F:/Documents\Photos\My Picture.jpg
6e33f29cdbbc53cc00bd3f9d65f3ffef,F:/Documents\Photos\My Picture 2.jpg
e99629c66f12c055ebe941a85db89a0f,F:/Documents\Photos\A document.doc
```

This let's us identify each unique file even if it has a different file name so we can check for duplicates.

It defaults to include every file, but I am filtering out anything from a text file named hash_exclude which includes lines like:

```
*.nbd
*.ndf
*.zip
```

This was mainly because files with these extensions were large and so the MD5 hashing got stuck. I also knew I didn't need them anyway so this was a simple way to filter through them. But I could have checked for large file sizes.

I ran this on every folder I wanted to examine.

Then I copied one folder of pictures that I definitely wanted to keep, over to a new location to get started, and hashed this as well. I called this my 'keep' folder.

There is a function within the sortphotos.py script that allowed me to count duplicates in a single source. Once I was satisfied there weren't many duplicates that would bloat my backup unnecessarily, my next task was to merge in the other sources of data. 

So I ran a comparison of the file hashes in my 'keep' folder with the hashes from the first external drive. I run the copy_over_files() function in sortphotos.py which looks for any md5 hashes from the drive with the hashes in the 'keep' folder. If the hash doesn't exist in the 'keep' folder it checks if it is a file with an extension I intentionally have no interest in keeping. If it is in my list of file types to definitly copy it just goes ahead and copies it. Another list of file extensions automatically gets ignored. And anything unusual prompts the user to copy, skip or if it is an image try to open it up to help make the decision. If a copy is to be made, it will only make one copy and anything else will be turned into a symbolic link to avoid lots of duplicates. The symbolic link was made because my dad had lots of copies for organisational purposes and I didn't want to mess with that, but I also didn't want an unnessarily big backup either. Once everything is copied, the new hashes are saved to a file so that I could then repeat this process for the next drive while ensuring the hash of the 'keep' folder was kept up-to-date.

So for a bunch of drives and CDs the process was: mount the drive/CD, create a file with hashes of the drive, produce a report comparing the hashes on this drive with my 'keep' folder, copy over any files that didn't exist on my keep folder while filtering out file types I wasn't interested in and turning duplicates into symbolic links. Repeat about 100 times.

The initial hashing takes quite a lot of time, but the comparision is very fast once the hashes exist.

Then I created a script to backup the resulting 'keep' folder to other drives. Since symbolic links don't work well between operating systems, I create a file in each directory that describes all the symbolic links so they could be recreated. Afterwards, I do an MD5 hash again of the entire contents of the drive to ensure everything copied successfully. I'll probably return to this and set up a RAID system instead though.

## Explanation of scripts
**backup-drive.py** This backups one folder into another folder. At the top of the file is a source_directory and backup_directory variable. Point these to the correct location. You will have less issues by using a / rather than \ in directory names. This will not copy symbolic links but instead add a reference to a file called _symlinks_meta.txt which is placed in each directory. This lists the original location of any file. Symbolic links don't work well across operating systems, but this should allow us to recreate them if ever necessary. Or perhaps we could add other metadata.

**hash-drive.py** will walk through all the files in a specified location and create an MD5 hash of them. This file can then be used to check what files exist on that drive and their location. This is useful for comparing one source of the data with another, for example to ensure that a backup is complete. Originally it was used to help merge multiple drives/folders with duplicate content in different locations so we didn't create lots of duplicates.

**sort-photos.py** contains the bulk of functions used to compare hashes and merge folder contents.

These scripts would all need to be edited to run for other scenarios. At the very least to choose which function to run when and which directories to work on. They are not really set up as proper end use scripts.

