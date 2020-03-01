# Exifdate_folder

Rename all the image files in a directory ("folder") and subdirectories after its EXIF date (output filename: YYYYMMDD_HHMMSS.jpg).

I wrote this small script because Olympus digital and most phones store its camera images with filenames like IMG_XXXX.jpg or DCIM_XXXX.jpg. 

I prefer to have all the images with standard "sortable" names like 20200301_110000.jpg (YYYYMMDD_HHMMSS.jpg).

Please note that this program just covers an specific use-case: that I needed to rename all the Phone and Olympus pictures to date-based names for easier clasification. Feel free to adapt it for your own needs!

## Getting Started and prerequisites

Just clone the repository. The program is a small and simple standalone script that only uses standard python libraries (os, re, sys, datetime) plus the python-exifread module that should be available on all major Linux distributions.

### Running Exifdate_folder

You can easily convert all the images in a directory and its subdirectories. Just move into the folder containing the image/images and run:

```
# python exifdate_folder.py .
```

Files will be renamed, like in the following example:

```
$ python /path/to/exifdate_folder.py .
- PROCESSING 'P2161162.JPG' ('./P2161162.JPG')
  - RENAMED: 'P2161162.JPG' -> '20200216_123907.jpg'
- PROCESSING 'P2161189.JPG' ('./P2161189.JPG')
  - RENAMED: 'P2161189.JPG' -> '20200216_125204.jpg'
- PROCESSING 'P2161180.JPG' ('./P2161180.JPG')
  - RENAMED: 'P2161180.JPG' -> '20200216_125002.jpg'
- PROCESSING 'P2161198.JPG' ('./P2161198.JPG')
(...)
```

I usually shoot fotos in both JPG+RAW, so if the folder has any RAW image (.raw or .orf), it will be renamed matching its image file.

In the example above, `P2161180.JPG` was converted to `20200216_125002.jpg` so `P2161180.ORF` will be converted to `20200216_125002.orf` too.

## Built With

* VIM editor.
* Python 
* Exifread

## Authors

* **Santiago Romero** - *Initial work* - [sromeroi](https://github.com/sromeroi)

## License

This project is licensed under the GNU GPL v3 LICENSE.

