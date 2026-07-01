#!/bin/bash
# סגיר מונפש 5 שנ' (HaMakom DS 2026):
#   רקע דיו עם גרעין-פילם + וינייטה (עומק, לא שטוח) →
#   הלוגו המרובע עולה ומתגלה → פס-חתימה טריקולור נמשח מתחתיו →
#   כרטיס CTA (כותרת Suez One + סלוגן + URL).
# דורש: $REEL_WORKDIR/sq_ivory.png (הלוגו המרובע בשנהב) ו-cards/CTA.png.
# צבעי חתימה: אברש #8E6FA8 · מרווה #788C5D · טרקוטה #D97757 (שמאל→ימין).
set -e
WORKDIR="${REEL_WORKDIR:-/tmp/vid}"
OUT="${1:-$WORKDIR/closer.mp4}"
ffmpeg -y -v error \
 -f lavfi -i color=c=0x141413:s=1080x1920:d=5:r=30 \
 -loop 1 -t 5 -i "$WORKDIR/sq_ivory.png" \
 -loop 1 -t 5 -i "$WORKDIR/cards/CTA.png" \
 -f lavfi -t 5 -i color=c=0x8E6FA8:s=187x10 \
 -f lavfi -t 5 -i color=c=0x788C5D:s=186x10 \
 -f lavfi -t 5 -i color=c=0xD97757:s=187x10 \
 -filter_complex "\
[0:v]noise=alls=7:allf=t,vignette=PI/4.5[bg];\
[1:v]scale=560:-1,format=rgba,fade=t=in:st=0.2:d=0.9:alpha=1[lg];\
[3:v][4:v][5:v]hstack=inputs=3,format=rgba,fade=t=in:st=1.7:d=0.5:alpha=1[sig];\
[2:v]format=rgba,fade=t=in:st=2.0:d=0.7:alpha=1[cta];\
[bg][lg]overlay=(W-w)/2:'470-40*min(t/1.1,1)':format=auto[v1];\
[v1][sig]overlay=(W-w)/2:'1069-14*min(max(t-1.7\,0)/0.5,1)':format=auto[v2];\
[v2][cta]overlay=0:1330:format=auto,format=yuv420p,setsar=1[v]" \
 -map "[v]" -an -t 5 -c:v libx264 -preset veryfast -crf 20 "$OUT"
