#!/bin/sh

ffmpeg -f rawvideo -pixel_format rgb24 -video_size 512x512 -framerate $1 -i raw_video -vf "vflip" result.gif
