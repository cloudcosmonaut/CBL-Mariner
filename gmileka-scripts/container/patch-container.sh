#!/bin/bash

set -x
set -e

mkdir -p /build
qemu-img convert -O raw /input/core-3.0.20240129.1326.vhdx /build/image.raw
targetDevice=$(losetup --show -f -P /build/image.raw)
echo $targetDevice
filter=$(basename $targetDevice)
lsblk --raw -a --output "NAME,MAJ:MIN" --noheadings | grep $filter | while read LINE; do
    DEV=/dev/$(echo $LINE | cut -d' ' -f1)
    MAJMIN=$(echo $LINE | cut -d' ' -f2)
    MAJ=$(echo $MAJMIN | cut -d: -f1)
    MIN=$(echo $MAJMIN | cut -d: -f2)
    [ -b "$DEV" ] || mknod "$DEV" b $MAJ $MIN
done
# mknod ${targetDevice}p1 b 259 2
# mknod ${targetDevice}p2 b 259 3
losetup -d $targetDevice
