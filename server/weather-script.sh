#!/bin/sh

cd "$(dirname "$0")"

python2 weather-script.py
rsvg-convert --background-color=white -o clock-output.png clock-output.svg
mogrify -rotate 90 clock-output.png
pngcrush -c 0 -ow clock-output.png
cp -f clock-output.png /home/ryansturmer/ryansturmer.com/www/kindle.png

