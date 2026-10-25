import os
import sys
import time
import math
import struct
import wave
import shutil
import subprocess
import json
import random
import logging
import asyncio
import datetime
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import requests
import edge_tts
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Option3ReelGenerator")

# Configuration & Credentials (loaded safely from .env)
def load_env_file():
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

load_env_file()

GH_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO = os.getenv("GITHUB_REPOSITORY", "sky140052-ops/automotin")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "108660975139622")
IG_USER_ID = os.getenv("IG_USER_ID", "17841451753810185")
CREATOR_HANDLE = os.getenv("CREATOR_HANDLE", "@rauth_jee")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path("assets/fonts")
FONT_BOLD_PATH = FONT_DIR / "Mukta-Bold.ttf"
FONT_REGULAR_PATH = FONT_DIR / "Mukta-Regular.ttf"

def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH
    if path.exists():
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            pass
    fallback = FONT_DIR / "NotoSansDevanagari-Bold.ttf" if bold else FONT_DIR / "NotoSansDevanagari-Regular.ttf"
    if fallback.exists():
        try:
            return ImageFont.truetype(str(fallback), size)
        except Exception:
            pass
    return ImageFont.load_default()

def get_ffmpeg_binary() -> str:
    candidates = [
        "ffmpeg",
        r"C:\Users\HP\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe",
        r"C:\Users\HP\AppData\Local\CapCut\Apps\9.2.0.3931\ffmpeg.exe"
    ]
    for c in candidates:
        if shutil.which(c) or os.path.exists(c):
            return c
    return "ffmpeg"

def generate_cinematic_news_soundtrack(output_path: str, duration: float = 18.0) -> str:
    sr = 44100
    total_samples = int(sr * duration)
    frames = bytearray()
    bpm = 108.0
    beat_samples = int(sr * (60.0 / bpm))

    chord = [110.0, 130.81, 164.81, 220.0]

    for i in range(total_samples):
        t = i / sr

        # 1. Taiko Drum Hit
        t_hit_0 = (i % (beat_samples * 2)) / sr
        drum_hit = 0.0
        if 0 <= t_hit_0 < 0.45:
            pitch_0 = 45.0 + 75.0 * math.exp(-t_hit_0 * 18.0)
            drum_hit += 0.85 * math.sin(2 * math.pi * pitch_0 * t_hit_0) * math.exp(-t_hit_0 * 4.5)
            drum_hit += 0.3 * (random.random() * 2.0 - 1.0) * math.exp(-t_hit_0 * 40.0)

        # Beat 2: Snare / Clap Hit
        t_hit_2 = ((i - beat_samples * 2) % (beat_samples * 4)) / sr
        if 0 <= t_hit_2 < 0.3:
            drum_hit += 0.45 * (random.random() * 2.0 - 1.0) * math.exp(-t_hit_2 * 25.0)
            drum_hit += 0.4 * math.sin(2 * math.pi * 90.0 * t_hit_2) * math.exp(-t_hit_2 * 12.0)

        # 2. Dramatic Deep Orchestral Strings Pad
        pad = 0.0
        for f in chord:
            pad += (0.15 * math.sin(2 * math.pi * f * t) +
                    0.08 * math.sin(2 * math.pi * (f * 2.0) * t) +
                    0.04 * math.sin(2 * math.pi * (f * 0.5) * t))
        pad *= (0.7 + 0.3 * math.sin(2 * math.pi * 0.5 * t))

        # 3. News Heartbeat Sub-Bass Pulse (55Hz)
        sub_pulse = 0.4 * math.sin(2 * math.pi * 55.0 * t) * (1.0 if (i % beat_samples) < (beat_samples * 0.35) else 0.1)

        # Total mix (Quiet background bed for voiceover, approx -22dB)
        total = (drum_hit * 0.35 + pad * 0.25 + sub_pulse * 0.2) * 0.30
        total = max(-0.95, min(0.95, total))
        sample_val = int(total * 32000)

        frames.extend(struct.pack("<hh", sample_val, sample_val))

    with wave.open(output_path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(frames)

    return output_path

async def generate_voiceover_and_cues(script_sentences: List[str], voice_audio_path: str) -> List[Dict[str, Any]]:
    full_text = " ".join(script_sentences)
    logger.info(f"Generating AI Hindi Voiceover (hi-IN-MadhurNeural): {full_text[:60]}...")
    communicate = edge_tts.Communicate(full_text, "hi-IN-MadhurNeural", rate="+6%")
    
    sentence_cues = []
    with open(voice_audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                start = chunk["offset"] / 10_000_000
                dur = chunk["duration"] / 10_000_000
                sentence_cues.append({
                    "start": start,
                    "end": start + dur,
                    "text": chunk["text"].strip()
                })

    # Break sentence cues down into word-level highlight cues
    word_cues = []
    for s in sentence_cues:
        words = s["text"].split()
        if not words:
            continue
        word_dur = (s["end"] - s["start"]) / len(words)
        for i, w in enumerate(words):
            w_start = s["start"] + i * word_dur
            w_end = w_start + word_dur
            word_cues.append({
                "word": w,
                "start": w_start,
                "end": w_end,
                "sentence": s["text"],
                "sentence_start": s["start"],
                "sentence_end": s["end"]
            })

    logger.info(f"Generated Voiceover ({len(sentence_cues)} sentences, {len(word_cues)} words).")
    return word_cues

def get_audio_duration(audio_path: str) -> float:
    ffmpeg_bin = get_ffmpeg_binary()
    try:
        cmd = [ffmpeg_bin, "-i", audio_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in res.stderr.splitlines():
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    except Exception:
        pass
    return 16.0

def mix_voice_and_music(voice_path: str, music_path: str, output_path: str, total_duration: float) -> str:
    ffmpeg_bin = get_ffmpeg_binary()
    logger.info(f"Mixing voice and background soundtrack into {output_path}...")
    # Voice upfront (volume 1.25), Music at background (volume 0.22 with fadeout)
    filter_complex = f"[0:a]volume=1.25[a0];[1:a]volume=0.22,afade=t=out:st={total_duration - 1.5}:d=1.5[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[out]"
    cmd = [
        ffmpeg_bin, "-y",
        "-i", voice_path,
        "-i", music_path,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(total_duration),
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def render_option3_reel_video(
    news_data: Dict[str, Any],
    bg_image_path: str,
    word_cues: List[Dict[str, Any]],
    mixed_audio_path: str,
    output_video_path: str
) -> str:
    logger.info("Rendering Option 3 Video Reel (1080x1920) with Kinetic Word Subtitles...")
    W, H = 1080, 1920
    fps = 24
    total_duration = get_audio_duration(mixed_audio_path) + 0.5
    total_frames = int(total_duration * fps)

    # 1. Base Visual Backdrop (Loaded & Pre-composed)
    try:
        bg_raw = Image.open(bg_image_path).convert("RGB")
    except Exception:
        bg_raw = Image.new("RGB", (W, H), "#07203A")

    # Fit & center crop background to 1080x1920
    bw, bh = bg_raw.size
    scale = max(W / bw, H / bh)
    tw, th = int(bw * scale), int(bh * scale)
    bg_scaled = bg_raw.resize((tw, th), Image.Resampling.LANCZOS)
    cx, cy = (tw - W) // 2, (th - H) // 2
    bg_base = bg_scaled.crop((cx, cy, cx + W, cy + H))

    # Add dark broadcast tint overlay to make text pop
    tint = Image.new("RGBA", (W, H), (7, 32, 58, 160))
    bg_base.paste(tint, (0, 0), tint)

    frames_dir = OUTPUT_DIR / "temp_opt3_frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    dept_tag = news_data.get("dept_tag", "बिहार सरकार • रोजगार व कल्याण")
    headline_red = news_data.get("headline_red", "बिहार पुलिस सिपाही व दारोगा बहाली")
    headline_black = news_data.get("headline_black", "21,391 पदों पर बड़ी भर्ती का ऐलान")
    portal = news_data.get("portal", "csbc.bih.nic.in")

    logger.info(f"Rendering {total_frames} frames ({total_duration:.1f}s @ {fps}fps)...")
    t0 = time.time()

    for idx in range(total_frames):
        cur_time = idx / fps
        progress = idx / total_frames

        # Gentle Ken Burns camera zoom (1.00 -> 1.06)
        zoom = 1.0 + 0.06 * progress
        zw, zh = int(W * zoom), int(H * zoom)
        frame = bg_base.resize((zw, zh), Image.Resampling.BILINEAR)
        fcx, fcy = (zw - W) // 2, (zh - H) // 2
        frame = frame.crop((fcx, fcy, fcx + W, fcy + H)).convert("RGB")

        d = ImageDraw.Draw(frame)

        # -------------------------------------------------------------
        # 1. Top Header Bar (Masthead & Branding)
        # -------------------------------------------------------------
        d.rectangle((0, 0, W, 140), fill="#07203A")
        # Glowing progress bar
        bar_w = int(W * progress)
        d.rectangle([(0, 0), (bar_w, 8)], fill=(220, 38, 38))
        d.rectangle([(0, 8), (bar_w, 12)], fill=(250, 204, 21))

        # Red Breaking Badge
        d.rounded_rectangle((36, 40, 290, 115), radius=12, fill="#DC2626")
        d.text((54, 52), "🔴 ब्रेकिंग बुलेटिन", font=get_font(32, bold=True), fill="#FFFFFF")
        d.text((315, 52), "BBCC SKILL HUB", font=get_font(34, bold=True), fill="#FACC15")
        d.text((318, 92), "दैनिक जागरण & शिक्षा विशेषांक", font=get_font(20, bold=False), fill="#E2E8F0")

        # -------------------------------------------------------------
        # 2. Upper News Card
        # -------------------------------------------------------------
        card_y = 165
        card_h = 240
        d.rounded_rectangle((36, card_y, W - 36, card_y + card_h), radius=16, fill="#FFFFFF", outline="#FACC15", width=3)
        # Dept pill
        d.rounded_rectangle((56, card_y + 16, 560, card_y + 54), radius=8, fill="#07203A")
        d.text((72, card_y + 20), f"🏛️ {dept_tag}", font=get_font(20, bold=True), fill="#FACC15")
        # Headline text
        d.text((56, card_y + 70), headline_red, font=get_font(36, bold=True), fill="#DC2626")
        d.text((56, card_y + 120), headline_black, font=get_font(32, bold=True), fill="#0F172A")
        # Portal pill
        d.rounded_rectangle((56, card_y + 180, 480, card_y + 220), radius=6, fill="#EFF6FF", outline="#2563EB", width=1)
        d.text((72, card_y + 186), f"🌐 आधिकारिक पोर्टल: {portal}", font=get_font(18, bold=True), fill="#1E40AF")

        # -------------------------------------------------------------
        # 3. Center Screen: Dynamic Kinetic Word Subtitles Box
        # -------------------------------------------------------------
        # Find active word and active sentence at cur_time
        active_word_item = None
        for item in word_cues:
            if item["start"] <= cur_time <= item["end"]:
                active_word_item = item
                break
        if not active_word_item and word_cues:
            # Pick closest past or first
            past = [w for w in word_cues if w["start"] <= cur_time]
            active_word_item = past[-1] if past else word_cues[0]

        sub_box_y = 520
        sub_box_h = 420
        # Dark glass container
        d.rounded_rectangle((36, sub_box_y, W - 36, sub_box_y + sub_box_h), radius=20, fill="#0F172A", outline="#38BDF8", width=2)
        d.rounded_rectangle((56, sub_box_y + 16, 260, sub_box_y + 54), radius=8, fill="#0284C7")
        d.text((72, sub_box_y + 22), "🎙️ लाइव समाचार वॉइस", font=get_font(18, bold=True), fill="#FFFFFF")

        if active_word_item:
            cur_sentence = active_word_item["sentence"]
            cur_word = active_word_item["word"]

            # Wrap sentence words nicely
            words = cur_sentence.split()
            lines = []
            cur_l = []
            for w in words:
                cur_l.append(w)
                if len(" ".join(cur_l)) > 26:
                    lines.append(cur_l)
                    cur_l = []
            if cur_l:
                lines.append(cur_l)

            sy = sub_box_y + 80
            for l_words in lines:
                sx = 60
                for w in l_words:
                    font_sub = get_font(36, bold=True)
                    bbox = d.textbbox((sx, sy), w, font=font_sub)
                    w_width = bbox[2] - bbox[0]

                    is_current = (w.strip("।,!?") == cur_word.strip("।,!?"))
                    if is_current:
                        # Draw glowing yellow highlight pill behind current word
                        d.rounded_rectangle((sx - 6, sy - 4, sx + w_width + 6, sy + 44), radius=8, fill="#FACC15")
                        d.text((sx, sy), w, font=font_sub, fill="#07203A")
                    else:
                        d.text((sx, sy), w, font=font_sub, fill="#FFFFFF")
                    sx += w_width + 16
                sy += 64

        # -------------------------------------------------------------
        # 4. Middle Graphic Strip (Key Notice Checkmarks)
        # -------------------------------------------------------------
        info_y = 970
        info_h = 240
        d.rounded_rectangle((36, info_y, W - 36, info_y + info_h), radius=16, fill="#FFFFFF", outline="#16A34A", width=2)
        d.rounded_rectangle((56, info_y + 16, 310, info_y + 54), radius=8, fill="#15803D")
        d.text((72, info_y + 22), "✅ मुख्य बिंदु व निर्देश", font=get_font(18, bold=True), fill="#FFFFFF")

        d.text((60, info_y + 70), "• आधिकारिक नोटिफिकेशन व योग्यता विवरण पोर्टल पर लाइव", font=get_font(23, bold=True), fill="#0F172A")
        d.text((60, info_y + 115), "• आवेदन प्रक्रिया व परीक्षा कैलेंडर के लिए तैयार रहें", font=get_font(23, bold=True), fill="#0F172A")
        d.text((60, info_y + 160), "• किसी भी फर्जी या भ्रामक खबरों से सावधान रहें", font=get_font(23, bold=True), fill="#DC2626")
        d.text((60, info_y + 198), "• केवल अधिकृत सरकारी स्रोत से ही पुष्टि करें", font=get_font(20, bold=False), fill="#475569")

        # -------------------------------------------------------------
        # 5. Bottom Sponsor Commercial Advertisements
        # -------------------------------------------------------------
        ad_y = 1240
        ad_w = (W - 72 - 16) // 2
        ad_h = 240

        # Ad 1 (BBCC Skill Hub)
        ad1_x = 36
        d.rounded_rectangle((ad1_x, ad_y, ad1_x + ad_w, ad_y + ad_h), radius=14, fill="#EFF6FF", outline="#2563EB", width=2)
        d.rounded_rectangle((ad1_x + 12, ad_y + 10, ad1_x + 230, ad_y + 36), radius=6, fill="#DC2626")
        d.text((ad1_x + 18, ad_y + 12), "विशेष: BBCC SKILL HUB", font=get_font(14, bold=True), fill="#FFFFFF")
        d.text((ad1_x + 14, ad_y + 44), "अपने कोचिंग का रजिस्ट्रेशन करें!", font=get_font(21, bold=True), fill="#0F172A")
        d.text((ad1_x + 14, ad_y + 72), "कोचिंग 100% ऑनलाइन ले जाएं", font=get_font(18, bold=True), fill="#DC2626")
        d.text((ad1_x + 14, ad_y + 100), "Google पर सर्च करें 'BBCC SKILL HUB'", font=get_font(15, bold=False), fill="#334155")
        d.text((ad1_x + 14, ad_y + 126), "डिजिटल क्लास, ऑनलाइन टेस्ट पोर्टल", font=get_font(15, bold=False), fill="#334155")
        d.rounded_rectangle((ad1_x + 14, ad_y + ad_h - 48, ad1_x + ad_w - 14, ad_y + ad_h - 12), radius=8, fill="#FACC15")
        d.text((ad1_x + 85, ad_y + ad_h - 40), "Google सर्च करें", font=get_font(18, bold=True), fill="#07203A")

        # Ad 2 (PTCC+BBCC Chakdah Chowk Madhubani)
        ad2_x = ad1_x + ad_w + 16
        d.rounded_rectangle((ad2_x, ad_y, ad2_x + ad_w, ad_y + ad_h), radius=14, fill="#F0FDF4", outline="#16A34A", width=2)
        d.rounded_rectangle((ad2_x + 12, ad_y + 10, ad2_x + 230, ad_y + 36), radius=6, fill="#15803D")
        d.text((ad2_x + 18, ad_y + 12), "शैक्षणिक: PTCC+BBCC", font=get_font(14, bold=True), fill="#FFFFFF")
        d.text((ad2_x + 14, ad_y + 44), "Class 1st to 10th (All)", font=get_font(21, bold=True), fill="#0F172A")
        d.text((ad2_x + 14, ad_y + 72), "चकदाह चौक, मधुबनी", font=get_font(18, bold=True), fill="#DC2626")
        d.text((ad2_x + 14, ad_y + 100), "अनुभवी शिक्षकों द्वारा संपूर्ण तैयारी", font=get_font(15, bold=False), fill="#334155")
        d.text((ad2_x + 14, ad_y + 126), "नया सत्र 2026-27 के लिए नए बैच शुरू", font=get_font(15, bold=False), fill="#334155")
        d.rounded_rectangle((ad2_x + 14, ad_y + ad_h - 48, ad2_x + ad_w - 14, ad_y + ad_h - 12), radius=8, fill="#BBF7D0")
        d.text((ad2_x + 65, ad_y + ad_h - 40), "प्रवेश प्रारंभ | मधुबनी", font=get_font(18, bold=True), fill="#14532D")

        # -------------------------------------------------------------
        # 6. Bottom Footer Banner
        # -------------------------------------------------------------
        d.rectangle((0, H - 90, W, H), fill="#07203A")
        d.text((36, H - 72), "सटीक व प्रामाणिक शिक्षा-रोजगार समाचार", font=get_font(22, bold=True), fill="#FFFFFF")
        d.text((36, H - 38), f"रोज़ाना सबसे पहले अपडेट के लिए पेज फॉलो करें ({CREATOR_HANDLE})", font=get_font(16, bold=False), fill="#94A3B8")
        d.rounded_rectangle((820, H - 76, 1044, H - 24), radius=10, fill="#FACC15")
        d.text((865, H - 62), "पेज राउत जी", font=get_font(22, bold=True), fill="#07203A")

        frame.save(frames_dir / f"f_{idx:04d}.jpg", quality=88)

    logger.info(f"Rendered {total_frames} frames in {time.time() - t0:.2f}s. Assembling MP4 with FFmpeg...")

    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [
        ffmpeg_bin, "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "f_%04d.jpg"),
        "-i", mixed_audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video_path
    ]
    subprocess.run(cmd, check=True)
    shutil.rmtree(frames_dir, ignore_errors=True)
    logger.info(f"Option 3 Reel Video generated: {output_video_path}")
    return output_video_path

def push_video_to_github_cdn(local_path: str, repo_path: str = "output/option3_latest_reel.mp4") -> Optional[str]:
    import base64
    if not GH_TOKEN:
        logger.warning("No GH_TOKEN available for CDN hosting.")
        return None
    try:
        logger.info(f"Uploading Reel video ({local_path}) to GitHub CDN...")
        with open(local_path, "rb") as f:
            content_bytes = f.read()
        encoded = base64.b64encode(content_bytes).decode("utf-8")
        url = f"https://api.github.com/repos/{REPO}/contents/{repo_path}"
        headers = {
            "Authorization": f"token {GH_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Option3ReelBot"
        }
        sha = None
        try:
            req_get = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req_get, timeout=12) as r:
                sha = json.loads(r.read().decode()).get("sha")
        except Exception:
            pass

        payload = {"message": f"Upload Option 3 video reel {int(time.time())}", "content": encoded, "branch": "main"}
        if sha:
            payload["sha"] = sha
        req_put = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
        with urllib.request.urlopen(req_put, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            logger.info(f"Newspaper Reel uploaded to GitHub CDN: commit {data.get('commit', {}).get('sha')[:8]}")
            ts = int(time.time())
            return f"https://raw.githubusercontent.com/{REPO}/main/{repo_path}?v={ts}"
    except Exception as e:
        logger.error(f"GitHub CDN video upload failed: {e}")
        return None

def publish_to_instagram_reel(video_url: str, caption: str) -> Optional[str]:
    logger.info("Publishing Option 3 Video to Instagram Reels (@rauth_jee)...")
    try:
        r1 = requests.post(
            f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": "true",
                "access_token": FB_ACCESS_TOKEN
            },
            timeout=45
        ).json()
        cid = r1.get("id")
        if not cid:
            logger.warning(f"Instagram reel container creation failed: {r1}")
            return None

        logger.info(f"Waiting for Meta processing (creation_id: {cid})...")
        for attempt in range(25):
            time.sleep(6)
            status_resp = requests.get(
                f"https://graph.facebook.com/v22.0/{cid}?fields=status_code&access_token={FB_ACCESS_TOKEN}",
                timeout=20
            ).json()
            status = status_resp.get("status_code")
            logger.info(f"Meta check attempt {attempt+1}: {status}")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                logger.error(f"Meta encoding error for reel: {status_resp}")
                return None

        r2 = requests.post(
            f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish",
            data={"creation_id": cid, "access_token": FB_ACCESS_TOKEN},
            timeout=45
        ).json()
        mid = r2.get("id")
        if mid:
            logger.info(f"🎉 Instagram Reel published! Media ID: {mid}")
            return str(mid)
        else:
            logger.warning(f"Instagram reel publish failed: {r2}")
    except Exception as e:
        logger.error(f"Instagram reel post failed: {e}")
    return None

def generate_press_photo(image_prompt: str, output_path: str) -> str:
    encoded = urllib.parse.quote(f"{image_prompt}, authentic documentary editorial news photograph, 8k, realistic")
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={random.randint(1000, 999999)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
        return output_path
    except Exception as e:
        logger.warning(f"Press photo fetch warning: {e}. Generating clean backdrop.")
        im = Image.new("RGB", (1080, 1920), "#0B2038")
        im.save(output_path)
        return output_path

async def run_option3_pipeline():
    logger.info("================================================================================")
    logger.info("STARTING OPTION 3: AI HINDI VOICEOVER + MOTION CLIPS + KINETIC WORD SUBTITLES REEL")
    logger.info("================================================================================")

    # 1. Topic & Script Definition
    news_data = {
        "sector": "पुलिस एवं दारोगा भर्ती",
        "dept_tag": "बिहार पुलिस मुख्यालय • CSBC भर्ती 2026",
        "headline_red": "बिहार पुलिस सिपाही व दारोगा बहाली!",
        "headline_black": "21,391 पदों के लिए नई प्रक्रिया शुरू",
        "portal": "csbc.bih.nic.in"
    }

    script_sentences = [
        "बिहार पुलिस सिपाही और दारोगा बहाली को लेकर बड़ा अपडेट सामने आया है!",
        "राज्य सरकार ने पुलिस मुख्यालय के नए रोस्टर और भर्ती कैलेंडर को हरी झंडी दे दी है।",
        "अभ्यर्थी अपनी शारीरिक और लिखित परीक्षा की तैयारी तेज कर दें।",
        "सटीक व प्रामाणिक अपडेट के लिए हमारे पेज राउत जी को फॉलो करें,",
        "और अपनी कोचिंग को ऑनलाइन ले जाने के लिए आज ही BBCC Skill Hub से जुड़ें!"
    ]

    # 2. Generate AI Voiceover & Word Cues
    voice_path = str(OUTPUT_DIR / "opt3_voice.mp3")
    word_cues = await generate_voiceover_and_cues(script_sentences, voice_path)

    # 3. Generate Cinematic Background Music & Mix Audio
    total_audio_dur = get_audio_duration(voice_path) + 1.0
    music_path = str(OUTPUT_DIR / "opt3_music.wav")
    generate_cinematic_news_soundtrack(music_path, duration=total_audio_dur)

    mixed_audio_path = str(OUTPUT_DIR / "opt3_final_mix.aac")
    mix_voice_and_music(voice_path, music_path, mixed_audio_path, total_duration=total_audio_dur)

    # 4. Generate Cinematic Visual Backdrop
    bg_photo_path = str(OUTPUT_DIR / "opt3_bg_press.jpg")
    generate_press_photo("Bihar police officers inspection parade Patna headquarters", bg_photo_path)

    # 5. Render 1080x1920 Vertical Video Reel with Kinetic Subtitles
    out_video_path = str(OUTPUT_DIR / "opt3_reel_final.mp4")
    render_option3_reel_video(news_data, bg_photo_path, word_cues, mixed_audio_path, out_video_path)

    # 6. Craft Caption
    caption = f"""🎙️ दैनिक जागरण & BBCC Skill Hub विशेष वॉइसओवर बुलेटिन 🎙️

🔴 {news_data['headline_red']}
⚫ {news_data['headline_black']}

🏛️ {news_data['dept_tag']}
🌐 आधिकारिक पोर्टल: {news_data['portal']}

📢 विशेष विज्ञापन (BBCC SKILL HUB):
अपने कोचिंग का रजिस्ट्रेशन करें और 100% ऑनलाइन ले जाएं! Google पर सर्च करें 'BBCC SKILL HUB' और तुरंत रजिस्ट्रेशन करें। डिजिटल क्लास, टेस्ट और स्टूडेंट मैनेजमेंट।

🎓 शैक्षणिक विज्ञापन (PTCC+BBCC):
Class 1st to 10th (All Subjects) - चकदाह चौक, मधुबनी (Chakdah Chowk) में नए सत्र 2026-27 के लिए प्रवेश प्रारंभ!

👤 हमारे पेज {CREATOR_HANDLE} को फॉलो करें और रोज़ाना सबसे पहले सटीक व प्रामाणिक अपडेट प्राप्त करें।

#BBCCSkillHub #rauth_jee #BiharPolice #CSBC #PoliceBharti #SarkariNaukri #Reels #Patna #Madhubani #Jobs2026"""

    # 7. Upload to GitHub CDN
    public_video_url = push_video_to_github_cdn(out_video_path)

    # 8. Publish directly to Instagram Reels
    reel_id = None
    if public_video_url:
        reel_id = publish_to_instagram_reel(public_video_url, caption)

    logger.info("================================================================================")
    logger.info("OPTION 3 REEL PIPELINE EXECUTION COMPLETE")
    logger.info(f"Instagram Reel Post:  {'SUCCESS (ID: ' + reel_id + ')' if reel_id else 'FAILED'}")
    logger.info(f"Facebook Auto-Mirror: ACTIVE via Meta Accounts Center (@rauth_jee)")
    logger.info("================================================================================")

if __name__ == "__main__":
    asyncio.run(run_option3_pipeline())
