# -*- coding: utf-8 -*-
"""מוזיקת מתח מסונתזת — **fallback אחרון בלבד!**
סדר העדיפויות למוזיקת רקע (ראו SKILL.md שלב 7):
  1. טראק מוכן מתיקיית החומרים הקבועה (Desktop/"חומרים להכנת וידאו לרילז " — רווח בסוף)
  2. ElevenLabs Music API (המפתח ב-~/Developer/video-use/.env)
  3. רק אם שניהם לא זמינים — הסקריפט הזה.

שימוש: python3 make_music.py DURATION HIT_TIME OUT.wav
DURATION = אורך הריל המדויק (סך פריימים ÷ 30). HIT_TIME = אופסט הסגיר —
שם מכה אקורד הסיום הדרמטי ומצלצל עד הסוף. שכבות: דרון סאו נמוך מסונן,
פעימת לב 92bpm שמתגברת, טיקים מלחיצים, סוועלים בסקונדה מינורית, רייזר."""
import numpy as np, wave, sys

DUR = float(sys.argv[1]); HIT = float(sys.argv[2]); OUTPATH = sys.argv[3]
SR = 44100
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)
out = np.zeros(N)
BODY_END = HIT - 0.15            # כל השכבות נעצרות רגע לפני האקורד

# דרון: סאו מנוחתך סביב A1 עם LFO איטי, low-pass חד-קוטבי
drone = np.zeros(N)
for f0, amp in [(55, 0.30), (55.7, 0.22), (82.5, 0.10), (110, 0.07)]:
    ph = 2*np.pi*f0*t + 0.3*np.sin(2*np.pi*0.05*t)
    drone += amp * (2*((ph/(2*np.pi)) % 1) - 1)
alpha = 0.015; acc = 0.0; flt = np.zeros(N)
for i in range(N):
    acc += alpha * (drone[i] - acc); flt[i] = acc
mask = np.ones(N); n_be = int(BODY_END*SR); mask[n_be:] = 0
fo = int(1.2*SR); mask[n_be-fo:n_be] = np.linspace(1, 0, fo)
out += flt * 1.1 * mask

# פעימת לב (lub-DUB) שמתגברת לאורך הריל — הלחץ עולה
bpm = 92.0; beat = 60/bpm
kl = int(0.22*SR); kt = np.arange(kl)/SR
kick = np.sin(2*np.pi*(50*np.exp(-kt*9))*kt) * np.exp(-kt*18)
i = 0.0
while i < BODY_END - 0.6:
    pos = int(i*SR); inten = 0.25 + 0.55*min(1.0, i/(BODY_END*0.85))
    end = min(pos+kl, N); out[pos:end] += kick[:end-pos]*inten
    pos2 = int((i+0.32)*SR); end2 = min(pos2+kl, N)
    if pos2 < N: out[pos2:end2] += kick[:end2-pos2]*inten*0.55
    i += beat

# טיקים — מצטרפים אחרי האינטרו ומתעצמים
tl = int(0.03*SR); tt = np.arange(tl)/SR
i = 0.0
while i < BODY_END - 0.3:
    if i > 12:
        pos = int(i*SR)
        nz = rng.standard_normal(tl)*np.exp(-tt*200)
        out[pos:pos+tl] += np.diff(nz, prepend=0)*0.08*(0.5+0.5*min(1.0,(i-12)/50))
    i += beat/2

# סוועלים — סקונדה מינורית צורמת, פרושים לאורך הגוף
seg = BODY_END/5
for k, (f1, f2, amp) in enumerate([(146.8,155.6,0.05),(146.8,155.6,0.07),(110,116.5,0.08),(146.8,155.6,0.10)]):
    start = seg*(k+0.6); length = seg*1.4
    n0 = int(start*SR); n1 = min(int((start+length)*SR), n_be); sn = n1-n0
    if sn <= 0: continue
    tt2 = np.arange(sn)/SR
    e = np.sin(np.pi*tt2/(sn/SR))**2
    out[n0:n1] += (np.sin(2*np.pi*f1*tt2)+np.sin(2*np.pi*f2*tt2+0.5))*e*amp

# רייזר אל האקורד
rise_len = min(8.0, HIT*0.12+4)
n0 = int((HIT-rise_len)*SR); n1 = int(HIT*SR)
tt3 = np.arange(n1-n0)/SR
out[n0:n1] += np.sin(2*np.pi*(180+25*tt3)*tt3)*np.linspace(0, 0.11, n1-n0)
out[n0:n1] += np.diff(rng.standard_normal(n1-n0), prepend=0)*np.linspace(0, 0.06, n1-n0)

# אקורד סיום: A מינור נמוך + מכת סאב, מצלצל עד סוף הריל
n0 = int(HIT*SR); rem = N-n0
tt4 = np.arange(rem)/SR
chord = np.zeros(rem)
for f, a in [(55,0.55),(82.5,0.30),(110,0.30),(130.8,0.24),(220,0.10),(261.6,0.07)]:
    chord += a*np.sin(2*np.pi*f*tt4 + 0.1*np.sin(2*np.pi*0.7*tt4))
chord *= np.exp(-tt4*0.55)
sub = np.sin(2*np.pi*(45*np.exp(-tt4*6))*tt4)*np.exp(-tt4*7)*0.9
out[n0:] += chord + sub

# מאסטר
fade = int(1.0*SR)
out[:fade] *= np.linspace(0, 1, fade)
out[-int(0.8*SR):] *= np.linspace(1, 0, int(0.8*SR))
out = np.tanh(out*1.4); out = out/np.max(np.abs(out))*0.88
pcm = (out*32767).astype(np.int16)
st = np.repeat(pcm[:, None], 2, axis=1)
with wave.open(OUTPATH, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(st.tobytes())
print('music:', DUR, 's, hit at', HIT)
