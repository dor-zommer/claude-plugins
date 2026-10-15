#!/usr/bin/env python3
"""lyria_gen.py <out.mp3> <seconds> "<prompt>" [bpm]
Lyria RealTime (models/lyria-realtime-exp) via google-genai live music API.
Collects PCM s16le 48 kHz stereo, then ffmpeg -> mp3 with fades + loudnorm.
Run with SSL_CERT_FILE=$(python -c 'import certifi;print(certifi.where())')."""
import os, sys, asyncio, subprocess
from google import genai
from google.genai import types

out, secs, prompt = sys.argv[1], float(sys.argv[2]), sys.argv[3]
bpm = int(sys.argv[4]) if len(sys.argv) > 4 else 60
env = dict(l.strip().split("=", 1) for l in open(os.path.expanduser("~/.claude/.env")) if "=" in l and not l.startswith("#"))
client = genai.Client(api_key=env["GEMINI_API_KEY"].strip().strip('"'), http_options={"api_version": "v1alpha"})
target = int(secs * 48000 * 2 * 2)  # bytes of s16le stereo 48k
raw = bytearray()

async def main():
    async with client.aio.live.music.connect(model="models/lyria-realtime-exp") as session:
        await session.set_weighted_prompts(prompts=[types.WeightedPrompt(text=prompt, weight=1.0)])
        await session.set_music_generation_config(config=types.LiveMusicGenerationConfig(
            bpm=bpm, temperature=0.9, density=0.25, brightness=0.35, guidance=4.0))
        await session.play()
        async for msg in session.receive():
            if msg.server_content and msg.server_content.audio_chunks:
                for ch in msg.server_content.audio_chunks:
                    raw.extend(ch.data)
            if len(raw) >= target:
                break
        await session.stop()

asyncio.run(main())
pcm = out + ".pcm"
open(pcm, "wb").write(raw[:target])
subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", "48000", "-ac", "2", "-i", pcm,
                "-af", f"afade=t=in:st=0:d=2,afade=t=out:st={secs-4}:d=4,loudnorm=I=-16:TP=-2:LRA=7",
                "-c:a", "libmp3lame", "-b:a", "256k", "-y", out], check=True, stdin=subprocess.DEVNULL)
os.remove(pcm)
print("wrote", out, f"{len(raw)/192000:.1f}s raw")
