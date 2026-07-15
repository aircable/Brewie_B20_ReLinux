Brewie B20
==========

This directory contains the Buildroot integration for the Brewie B20.

Building
========

Configure Buildroot with:

  make brewie_b20_defconfig

Then build the image with:

  make

Result
======

The main output is:

  output/images/sdcard.img

The image contains:

  - U-Boot SPL and U-Boot
  - a VFAT boot partition with the kernel and DTB
  - an ext4 root filesystem
