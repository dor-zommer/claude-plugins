#!/bin/bash
# נרמול מקטע ריל: IN OUT SS T CARD — וידאו בלבד (-an), האודיו נבנה בנפרד!
# 1080x1920, רקע מטושטש, overlay.png (גרדיאנט דיו + לוגו ריבועי + URL + פס-חתימה),
# כרטיס עם fade+rise, פייד כניסה/יציאה למקטע, 30fps.
#
# *** SAFE ZONES (עודכן 02.08.2026 אחרי פידבק דור — פוסט שדרות) ***
# ה-UI של טיקטוק מכסה: תחתית ~484px (קאפשן+CTA), ימין ~150px (לייקים/פלייליסט),
# למעלה ~130px (סטטוס-בר/טאבים). לכן:
#   - תחתית הכרטיס לעולם לא נמוכה מ-y=1420  →  BOTTOM_MARGIN=500 (לא 240!)
#   - כלל-אצבע חוצה-פלטפורמות: כל הטקסט בתוך מלבן 900×1400 ממורכז.
# מקור: kreatli.com/guides/tiktok-safe-zone · zeely.ai/blog/tiktok-safe-zones
#
# דורש: $REEL_WORKDIR/overlay.png (מ-make_overlay.py; ברירת מחדל /tmp/vid).
# קליפ מקור >40 שנ' — לפצל קודם.
set -e
WORKDIR="${REEL_WORKDIR:-/tmp/vid}"
IN="$1"; OUT="$2"; SS="$3"; T="$4"; CARD="$5"
BOTTOM_MARGIN=500   # safe zone תחתון של טיקטוק (484px) + באפר
CH=$(python3 -c "from PIL import Image; print(Image.open('$CARD').height)")
Y=$((1920-CH-BOTTOM_MARGIN))
FO=$(python3 -c "print(max(0,$T-0.25))")
# הכרטיס הוא PNG סטטי — חובה -loop 1 לפני ה-input שלו, אחרת fade האלפא
# פועל על פריים בודד ומשאיר אותו שקוף לנצח (באג שנמצא 02.08.2026).
ffmpeg -y -v error -ss "$SS" -t "$T" -i "$IN" -i "$WORKDIR/overlay.png" -loop 1 -t "$T" -i "$CARD" \
 -filter_complex "[0:v]scale=135:240,boxblur=10:2,scale=1080:1920,eq=brightness=-0.08[bg];\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2[base];\
[base][1:v]overlay=0:0[wl];\
[2:v]fps=30,format=rgba,fade=t=in:st=0:d=0.5:alpha=1[card];\
[wl][card]overlay=x=0:y='$Y+40*pow(max(0,1-t/0.5),3)',\
fade=t=in:st=0:d=0.25,fade=t=out:st=$FO:d=0.25,format=yuv420p,fps=30,setsar=1[v]" \
 -map "[v]" -an -c:v libx264 -preset veryfast -crf 20 "$OUT"
echo "$OUT done"
