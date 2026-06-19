#!/bin/bash
# נרמול מקטע ריל: IN OUT SS T CARD — וידאו בלבד (-an), האודיו נבנה בנפרד!
# 1080x1920, רקע מטושטש, לוגו למעלה, כרטיס בשליש תחתון, 30fps.
# דורש: $REEL_WORKDIR/logo.png (ברירת מחדל /tmp/vid). קליפ מקור >40 שנ' — לפצל קודם.
set -e
WORKDIR="${REEL_WORKDIR:-/tmp/vid}"
IN="$1"; OUT="$2"; SS="$3"; T="$4"; CARD="$5"
CH=$(python3 -c "from PIL import Image; print(Image.open('$CARD').height)")
Y=$((1920-CH-140))
ffmpeg -y -v error -ss "$SS" -t "$T" -i "$IN" -i "$WORKDIR/logo.png" -i "$CARD" \
 -filter_complex "[0:v]scale=135:240,boxblur=10:2,scale=1080:1920,eq=brightness=-0.08[bg];\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2[base];[1:v]scale=380:-1[lg];\
[base][lg]overlay=(W-w)/2:80[wl];[wl][2:v]overlay=0:$Y,format=yuv420p,fps=30,setsar=1[v]" \
 -map "[v]" -an -c:v libx264 -preset veryfast -crf 20 "$OUT"
