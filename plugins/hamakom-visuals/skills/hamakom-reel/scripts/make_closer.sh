#!/bin/bash
# ** הסגיר הקנוני הוא closer_v3.mp4 מתיקיית החומרים הקבועה
#    (/Users/dorzommer/Desktop/"חומרים להכנת וידאו לרילז " — רווח בסוף!) —
#    משתמשים בו כמות שהוא. הסקריפט הזה רק כשצריך טקסט CTA אחר. **
# את האודיו של הסגיר הקנוני מחלצים פעם אחת ל-wav מ-closer_v3 עצמו.
#
# סגיר דרמטי 6 שנ' (HaMakom DS 2026) — קונספט "המניפסט":
#   חושך מתוח → שלוש מכות טיפוגרפיות מצטברות ("בלי בעלי הון" / "בלי פרסומות" /
#   "בלי בולשיט" בטרקוטה), כל אחת בקאט חד + זעזוע-מסך + הבזק לבן + מכת סאונד
#   מתגברת → הכל מתלכד ללוגו שננעל עם בּוּם + הבזק → פס-חתימה טריקולור וכרטיס
#   CTA ("התחקיר המלא באתר" + סלוגן + URL). גרעין-פילם + וינייטה לכל האורך.
#
# דורש קודם:  python3 scripts/make_closer_assets.py   → fA..fD.png + sting.wav
# צבעי חתימה: אברש #8E6FA8 · מרווה #788C5D · טרקוטה #D97757 (שמאל→ימין).
set -e
WORKDIR="${REEL_WORKDIR:-/tmp/vid}"
OUT="${1:-$WORKDIR/closer.mp4}"

# מעטפת מכה מתפוגגת סביב שלושת הביטים (0.6 / 1.3 / 2.0 שנ')
B='(exp(-16*(t-0.6))*gte(t,0.6)+exp(-16*(t-1.3))*gte(t,1.3)+exp(-16*(t-2.0))*gte(t,2.0))'
SHX="22*sin(90*t)*$B + 30*sin(70*t)*exp(-11*(t-2.85))*gte(t,2.85)"   # זעזוע אופקי
SHY="20*cos(85*t)*$B + 26*cos(66*t)*exp(-11*(t-2.85))*gte(t,2.85)"   # זעזוע אנכי

ffmpeg -y -v error \
 -loop 1 -t 6 -i "$WORKDIR/fA.png" \
 -loop 1 -t 6 -i "$WORKDIR/fB.png" \
 -loop 1 -t 6 -i "$WORKDIR/fC.png" \
 -loop 1 -t 6 -i "$WORKDIR/fD.png" \
 -f lavfi -t 6 -i color=c=0x141413:s=1080x1920:r=30 \
 -f lavfi -t 6 -i color=c=white:s=1080x1920:r=30 \
 -f lavfi -t 6 -i color=c=white:s=1080x1920:r=30 \
 -i "$WORKDIR/sting.wav" \
 -filter_complex "\
[4:v]format=rgba[ink];\
[ink][0:v]overlay=enable='between(t,0.6,1.3)'[a];\
[a][1:v]overlay=enable='between(t,1.3,2.0)'[b];\
[b][2:v]overlay=enable='between(t,2.0,2.85)'[c];\
[c][3:v]overlay=enable='gte(t,2.85)'[d];\
[d]scale=1210:2150,crop=1080:1920:x='65+($SHX)':y='115+($SHY)'[sh];\
[sh]noise=alls=6:allf=t,vignette=PI/4.5[gr];\
[5:v]format=rgba,colorchannelmixer=aa=0.75[w1];\
[6:v]format=rgba,colorchannelmixer=aa=0.92[w2];\
[gr][w1]overlay=enable='between(t,0.6,0.667)+between(t,1.3,1.367)+between(t,2.0,2.067)'[wf];\
[wf][w2]overlay=enable='between(t,2.85,2.95)',format=yuv420p,setsar=1[v]" \
 -map "[v]" -map "7:a" -t 6 \
 -c:v libx264 -preset medium -crf 19 -c:a aac -b:a 192k -shortest "$OUT"
