if ($args.Count -ne 1) {
    Write-Host "Usage: .\gengif.ps1 fps"
} else {
    ffmpeg -f rawvideo -pixel_format rgb24 -video_size 512x512 -framerate $args[0] -i raw_video -vf "vflip" result.gif
}
