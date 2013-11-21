#!/bin/bash

for img in `find . -name '*.jpg'`
do
    convert -resize 15% $img $img._thumb.jpg
    x=$(echo $img._thumb.jpg|sed 's/\.jpg.//g')
    mv $img._thumb.jpg $x
done

for img in `find . -name '*.png'`
do
    convert -resize 15% $img $img._thumbpng.
    x=$(echo $img._thumb.jpg|sed 's/\.png.//g')
    mv $img._thumb.png $x
done
