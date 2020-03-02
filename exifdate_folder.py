#!/usr/bin/env python
#
# Rename image files after its EXIF date. If a RAW/ORF file exists matching
# the image file, it will be renamed also to YYYYMMDD_HHMMSS.ext to match it.
#
# Author: Santiago Romero - Jan-2020
#
# TODO: support globs

import os
import sys
import re
import exifread
import datetime

image_pattern = re.compile(r".*\.(jpe?g|png|gif)$", re.IGNORECASE)
exifdate_pattern = re.compile(r"^\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}$", re.IGNORECASE)
output_pattern = re.compile(r"^\d{4}\d{2}\d{2}_\d{2}\d{2}\d{2}\.\w+$", re.IGNORECASE)

date_tags = [
    'EXIF DateTimeOriginal',
    'EXIF DateTimeDigitized',
    'Image DateTime',
]

possible_raw_extensions = [ "ORF", "RAW" ]

#------------------------------------------------------------------------------
def info():
    '''Display info about the purpose of the program.'''
    msg = ("\nExifdate_folder: Rename images filenames to YYYYMMDD_HHMMSS"
           " (from EXIF).")
    print(msg)

#------------------------------------------------------------------------------
def usage(exit_status):
    '''Show command line usage.'''
    msg = ('\nUsage:     $ python exifdate_folder.py foldername\n'
           '           $ python exifdate_folder.py filename\n\n'
           'Renames image file specified or inside folder as YYYYMMDD_HHMMSS.ext.\n'
           'Matching RAW/ORF files it will follow the renaming of the matching image.\n\n'
           'Examples:  $ python exifdate_folder.py .\n'
           '           $ python exifdate_folder.py IMG_1234.JPG\n'
    )
    print(msg)
    sys.exit(exit_status)


#------------------------------------------------------------------------------
def buildFileList(walk_dir, pattern):
    '''Build list of files matching the specified re pattern'''

    filelist = []

    #pylint: disable=unused-variable
    for folder, subdirs, files in os.walk(walk_dir):
        for filename in files:
            fullpath = os.path.join(folder, filename)
            if pattern.match(filename):
                filelist.append( [filename, folder, fullpath ] )
    return filelist


#------------------------------------------------------------------------------
def renameImgToExif( filename, folder, fullpath, orig_base_path, abs_base_path ):
    '''Do the actual renaming of the file.'''

    file_from_base_path = remove_base_path( fullpath, abs_base_path )
    if file_from_base_path is None:
        file_from_base_path = fullpath
    else:
        file_from_base_path = file_from_base_path.lstrip('/') 
        file_from_base_path = os.path.join(orig_base_path, file_from_base_path)

    print("- PROCESSING '{0}' ('{1}')".format(filename, file_from_base_path))

    if output_pattern.match(filename):
        print("  - Skipping file (already in the desired format).")
        return True

    # Open File and read EXIF tags
    with open(fullpath, 'rb') as fp:

        tags = exifread.process_file(fp)
        if not tags:
            print("  - ERROR: No EXIF information found.")
            return False

    # Tags read. Now check if there's any valid EXIF DATE key
    foundKey = False

    for tag in date_tags:
        if tag in tags:
            try:
                exifdate = tags[tag].values
                foundKey = True
            except KeyError:
                continue

            if not exifdate_pattern.match(exifdate):
                continue

    if not foundKey:
        print("  - ERROR: No valid exif tag found.")
        return False

    # Key found, start name conversion by converting EXIF date value to filename:
    srcformat = "%Y:%m:%d %H:%M:%S"
    dstformat = '%Y%m%d_%H%M%S'
    filedate = datetime.datetime.strptime(exifdate, srcformat).strftime(dstformat)
    filename_wo_ext, file_extension = os.path.splitext(fullpath)
    file_extension = file_extension.lower()
    new_filename = "{0}{1}".format(os.path.join(folder, filedate), file_extension)

    suffix = 0
    while os.path.exists(new_filename) or os.path.isdir(new_filename):
        suffix += 1
        new_filename = "{0}_{1}{2}".format(os.path.join(folder, filedate), suffix, file_extension)

    # At this point, examples for "tag", "exifdate", "filedate":
    # "Image DateTime", "2020:02:16 13:19:03", "20200216_131903"
    try:
        os.rename(fullpath, new_filename)
    except:
        print("  - ERROR: renaming '{0}' to '{1}'".format(fullpath, new_filename))
        return False

    print("  - RENAMED: '{0}' -> '{1}'".format(filename, os.path.basename(new_filename)))

    # Check if there is a valid RAW file matching the image
    for raw_extension in possible_raw_extensions:
        possible_raw = "{0}.{1}".format( filename_wo_ext, raw_extension )
        raw_file = getfile_insensitive(possible_raw)
        if raw_file is None:
            continue
        else:
            break

    # We found a RAW file matching the Image, rename it
    if raw_file is not None:
        #pylint: disable=unused-variable
        raw_filename_wo_ext, raw_file_extension = os.path.splitext(raw_file)
        raw_file_extension = raw_file_extension.lower()

        if suffix == 0:
            new_raw_filename = "{0}{1}".format(os.path.join(folder, filedate), raw_file_extension)
        else:
            new_raw_filename = "{0}_{1}{2}".format(os.path.join(folder, filedate), suffix, raw_file_extension)

        while os.path.exists(new_raw_filename) or os.path.isdir(new_raw_filename):
            suffix += 1
            new_raw_filename = "{0}_{1}{2}".format(os.path.join(folder, filedate), suffix, raw_file_extension)

        try:
            os.rename(raw_file, new_raw_filename)
        except:
            print("  - ERROR: renaming '{0}' to '{1}'".format(raw_file, new_raw_filename))
            return False

    return True


#------------------------------------------------------------------------------
def getfile_insensitive(path):
    '''Check if file exists in any case (.JPG, .jpg...) and return its name'''
    directory, filename = os.path.split(path)
    directory, filename = (directory or '.'), filename.lower()
    for f in os.listdir(directory):
        newpath = os.path.join(directory, f)
        if os.path.isfile(newpath) and f.lower() == filename:
            return newpath

#------------------------------------------------------------------------------
def isfile_insensitive(path):
    return getfile_insensitive(path) is not None

#------------------------------------------------------------------------------
def remove_base_path(fullpath, basepath):
    '''Turns absolute path into relative by removing {basepath} from it'''

    if fullpath.startswith(basepath):
        return fullpath.replace(basepath, '')

    return None

#------------------------------------------------------------------------------
def confirm(message="OK to push to continue [Y/N]? "):
    """
    Ask user to enter Y or N (case-insensitive).
    """
    answer = ""
    if sys.version_info[:2] <= (2, 7):
        #pylint: disable=undefined-variable
        get_input = raw_input
    else:
        #pylint: disable=undefined-variable
        get_input = input
    while answer not in ["y", "n"]:
        answer = get_input(message).lower()
    return answer == "y"

#------------------------------------------------------------------------------
def main():

    info()
    if len(sys.argv) < 2:
        usage(1)

    param = sys.argv[1]

    # Build list of images...
    ok = False
    filelist = []

    # Process folder:
    if os.path.isdir(param):
        ok = confirm("\nProcess selected folder and rename all images into it? (y/n): ")
        if ok:
            orig_path = param
            walk_dir = os.path.abspath(param)
            filelist = buildFileList(walk_dir, image_pattern)

    # Process single file:
    elif os.path.isfile(param):
        if not image_pattern.match(param):
            print("\n- Specified file is not an image file. Aborting...")
            sys.exit(2)
        ok = confirm("\nProcess selected file and rename it after its EXIF date? (y/n): ")
        if ok:
            orig_path = os.path.dirname(param)
            walk_dir = os.path.abspath(param)
            filelist.append( [param, orig_path, walk_dir] )

    if not ok:
        print("Aborting...")
        sys.exit(0)

    if len(filelist) == 0:
        print("- No images found.")
        sys.exit(0)

    # ... and process each of the files:
    pending = []
    for record in filelist:
        filename = record[0]
        folder = record[1]
        fullpath = record[2]
        retcode = renameImgToExif( filename, folder, fullpath, orig_path, walk_dir )

        if not retcode:
            pending.append(fullpath)

#------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
