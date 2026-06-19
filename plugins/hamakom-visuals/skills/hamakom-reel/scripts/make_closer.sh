#!/bin/bash
# סגיר מונפש 5 שנ': OUT — לוגו מרובע עולה ומתגלה, ואז כרטיס CTA.
# דורש: $REEL_WORKDIR/sq_ivory.png (הלוגו המרובע בשנהב) ו-cards/CTA.png.
set -e
WORKDIR="${REEL_WORKDIR:-/tmp/vid}"
OUT="${1:-$WORKDIR/closer.mp4}"
ffmpeg -y -v error -f lavfi -i color=c=0x1F1E1B:s=1080x1920:d=5:r=30 \
 -loop 1 -t 5 -i "$WORKDIR/sq_ivory.png" -loop 1 -t 5 -i "$WORKDIR/cards/CTA.png" \
 -filter_complex "[1:v]scale=560:-1,format=rgba,fade=t=in:st=0.2:d=0.9:alpha=1[lg];\
[2:v]format=rgba,fade=t=in:st=1.4:d=0.7:alpha=1[cta];\
[0:v][lg]overlay=(W-w)/2:'470-40*min(t/1.1,1)':format=auto[v1];\
[v1][cta]overlay=0:1330:format=auto,format=yuv420p,setsar=1[v]" \
 -map "[v]" -an -t 5 -c:v libx264 -preset veryfast -crf 20 "$OUT"
