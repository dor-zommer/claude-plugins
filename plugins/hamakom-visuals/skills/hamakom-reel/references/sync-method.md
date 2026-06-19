# שיטת הסינק — וידאו ואודיו בנפרד

## למה לא קונקט רגיל
קונקט (demuxer) של מקטעים עם אודיו צובר סטייה: ל-AAC יש priming samples וכל מקטע
תורם אופסט זעיר. אחרי 8–9 מקטעים הסאונד זולג מקליפ לקליפ (קרה בפועל, דור שמע).
concat filter פותר אבל מקודד מחדש את הכל — איטי מדי למגבלת 45 שניות לקריאה.

## הפתרון: וידאו -c copy, אודיו לפי פריימים

### 1. וידאו
כל המקטעים מקודדים `-an` (בלי אודיו), באותם פרמטרים (libx264, fps=30, yuv420p):
```bash
printf "file 'q1.mp4'\nfile 'q2.mp4'\n..." > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy body.mp4
```
וידאו CFR בלי אודיו מתחבר בלי דריפט.

### 2. ספירת פריימים — לא להניח, לספור
```bash
for f in q1 q2 ...; do
  ffprobe -v error -select_streams v:0 -count_frames \
    -show_entries stream=nb_read_frames -of csv=p=0 $f.mp4
done
```
מקטע "6 שניות" יוצא לרוב 179 פריימים, לא 180. האופסטים נגזרים מהספירה בפועל:
`offset_n = sum(frames[0..n-1]) / 30` (בשניות; ×1000 ל-adelay).

### 3. חילוץ אודיו מקור (רק מקטעים שמשמיעים)
חלון זהה לחיתוך הווידאו, מנורמל, ובאורך מדויק של המקטע (לפי הפריימים):
```bash
ffmpeg -y -ss SS -t T -i SRC -vn -af "aresample=44100,\
loudnorm=I=-16:TP=-1.5:LRA=11,\
aformat=sample_fmts=s16:channel_layouts=stereo,\
atrim=0:T,apad=whole_dur=T" aN.wav
```

### 4. מיקס סופי
```bash
ffmpeg -y -i body.mp4 -i music.wav -i a3.wav -i a5.wav ... -filter_complex "
[2:a]adelay=12433|12433[d3];
[3:a]adelay=40267|40267[d5];
...
[d3][d5]...amix=inputs=N:duration=longest:normalize=0,\
apad=whole_dur=TOTAL,atrim=0:TOTAL,\
aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,asplit=2[nat1][nat2];
[1:a]atrim=0:TOTAL,asetpts=PTS-STARTPTS,volume=0.95,\
aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[m];
[m][nat1]sidechaincompress=threshold=0.02:ratio=6:attack=80:release=600:makeup=1[duck];
[duck][nat2]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k reel.mp4
```
הערות:
- `aformat` לפני sidechaincompress חובה — בלעדיו: "could not choose their formats".
- TOTAL = סך כל הפריימים ÷ 30. גם HIT_TIME של המוזיקה (אקורד הסיום) = אופסט הסגיר.
- sidechain מנמיך את המוזיקה אוטומטית כשיש אודיו מקור ומעלה אותה בקטעים אילמים.

### 5. בדיקה
```bash
ffprobe -show_entries format=duration ...   # וידאו
ffprobe -select_streams a:0 -show_entries stream=duration ...   # אודיו
```
הפרש מעל 0.05 שנ' = משהו השתבש, לחזור לספירת הפריימים.
