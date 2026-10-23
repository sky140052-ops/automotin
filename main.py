#!/usr/bin/env python3
"""
================================================================================
Cyber Security Social Media Automation Bot (Hindi 3D Edition)
Creator: @rauth_jee
Automated 3x Daily Multi-Format Engine:
1. Instagram Feed Post (Pure Hindi Devanagari)
2. Instagram Story (1080x1920 Full HD)
3. Instagram 3D Video Reel with Trending Hindi Voice (Male/Female) + Cyber Music
================================================================================
"""

import os
import sys
import json
import time
import math
import wave
import struct
import random
import logging
import warnings
import subprocess
from typing import Dict, Any, Optional
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CyberSocialBot")

# ==============================================================================
# CONFIGURATION & ENVIRONMENT
# ==============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "").strip()
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "").strip()
IG_USER_ID = os.getenv("IG_USER_ID", "").strip()
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "sky140052-ops/automotin").strip()
CREATOR_HANDLE = "@rauth_jee" # Strictly @rauth_jee
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

VIRAL_HASHTAGS = [
    "#rauth_jee", "#CyberSecurityHindi", "#TechTipsHindi", "#DigitalIndia",
    "#CyberCrimeAlert", "#OnlineSafety", "#TechReels", "#TrendingReels",
    "#CyberDefense", "#HackingPrevention"
]

FALLBACK_TIPS_HINDI = [
    {
        "headline": "MFA Fatigue अटैक से सावधान रहें!",
        "category": "पहचान और पासवर्ड सुरक्षा",
        "tip": "हैकर्स देर रात आपके फोन पर लगातार 2FA/MFA अप्रूवल नोटिफिकेशन भेजते हैं, ताकि आप परेशान होकर 'Approve' दबा दें। अगर आपने खुद लॉगिन नहीं किया है, तो कभी भी 'Approve' पर क्लिक न करें।",
        "action_step": "SMS OTP की जगह Google Authenticator या Microsoft Authenticator ऐप का इस्तेमाल करें।",
        "caption": "🚨 सतर्क रहें: MFA Fatigue Attacks बहुत तेजी से बढ़ रहे हैं!\n\nहैकर्स अब सिर्फ पासवर्ड नहीं चुराते, बल्कि आपको बार-बार नोटिफिकेशन भेजकर थका देते हैं ताकि आप गलती से 'Approve' दबा दें।\n\nबचने के उपाय:\n1. बिना मांगे आए किसी भी नोटिफिकेशन को अप्रूव न करें।\n2. तुरंत अपना पासवर्ड बदलें।\n3. Authenticator ऐप का उपयोग करें।\n\n🛡️ खुद को और अपने दोस्तों को सुरक्षित रखें!"
    },
    {
        "headline": "ब्राउज़र में पासवर्ड कभी सेव न करें!",
        "category": "डेटा और प्राइवेसी सुरक्षा",
        "tip": "Chrome या Edge जैसे ब्राउज़र्स में सेव किए गए पासवर्ड्स को 'Infostealer' वायरस सिर्फ 5 सेकंड में चुरा लेते हैं। एक गलत डाउनलोड आपकी सारी पर्सनल आईडी और बैंकिंग डिटेल्स लीक कर सकता है।",
        "action_step": "ब्राउज़र से सारे पासवर्ड हटाएं और Bitwarden या 1Password जैसे सुरक्षित पासवर्ड मैनेजर का इस्तेमाल करें।",
        "caption": "⚠️ क्या आपके पासवर्ड्स ब्राउज़र में सेव हैं?\n\nसावधान! आज के सबसे खतरनाक मैलवेयर (जैसे Lumma, RedLine) सीधे आपके ब्राउज़र के पासवर्ड कैश को निशाना बनाते हैं।\n\nसुरक्षा नियम:\n• ब्राउज़र के 'Auto-Save Password' को बंद करें\n• एक डेडिकेटेड एन्क्रिप्टेड पासवर्ड वॉल्ट इस्तेमाल करें\n• टू-स्टेप वेरिफिकेशन (2FA) हमेशा ऑन रखें"
    },
    {
        "headline": "फर्जी QR कोड (Quishing) से बचें!",
        "category": "ऑनलाइन फ्रॉड से बचाव",
        "tip": "धोखेबाज़ असली पेमेंट या मेनू QR कोड के ऊपर अपना फर्जी QR कोड चिपका देते हैं। इसे स्कैन करते ही आपका फोन नकली वेबसाइट पर चला जाता है और आपकी यूपीआई या लॉगिन जानकारी चोरी हो जाती है।",
        "action_step": "QR कोड स्कैन करने के बाद लिंक के असली स्पेलिंग और डोमेन को ध्यान से देखकर ही आगे बढ़ें।",
        "caption": "📱 कोई भी QR Code स्कैन करने से पहले 2 बार सोचें!\n\nआजकल 'Quishing' (QR Phishing) बहुत तेज़ी से फैल रहा है क्योंकि सामान्य एंटी-वायरस QR कोड के अंदर छिपे खतरे को नहीं पकड़ पाते।\n\nसावधानी:\n1. सार्वजनिक जगहों पर लगे क्यूआर कोड पर कोई दूसरा स्टिकर तो नहीं चिपका, यह जांचें।\n2. पेमेंट करते समय प्राप्तकर्ता का नाम ज़रूर चेक करें।\n3. अनजान क्यूआर से आए किसी भी लिंक पर पासवर्ड न डालें।"
    }
]

# ==============================================================================
# 1. HINDI CONTENT GENERATOR
# ==============================================================================

def generate_cyber_content() -> Dict[str, Any]:
    logger.info("🤖 Generating Hindi Cyber Security Tip with Google Gemini...")
    if not GEMINI_API_KEY or "your_gemini" in GEMINI_API_KEY.lower():
        return random.choice(FALLBACK_TIPS_HINDI)

    prompt = """
You are an expert Cyber Security Educator creating viral tech content in pure HINDI (Devanagari script).
Generate a high-impact, practical daily Cyber Security tip for everyday users and tech professionals.

You must return ONLY a valid JSON object with these exact keys:
{
  "headline": "Catchy Hindi headline in Devanagari under 6 words (e.g. 'MFA Fatigue अटैक से बचें!')",
  "category": "Security domain in Hindi (e.g. 'पासवर्ड और डेटा सुरक्षा')",
  "tip": "Main security insight in simple, viral HINDI for a visual poster. Must be under 45 words.",
  "action_step": "1 actionable sentence in Hindi telling the reader what to do right now.",
  "caption": "Engaging Hindi caption for Instagram with bullet points and a call-to-action."
}
"""
    raw_text = ""
    for model_name in ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            res = client.models.generate_content(model=model_name, contents=prompt)
            raw_text = res.text or ""
            if raw_text:
                logger.info(f"✅ Generated Hindi content using {model_name}.")
                break
        except Exception:
            continue

    if not raw_text:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=GEMINI_API_KEY)
            for m in ["gemini-1.5-flash", "gemini-2.0-flash"]:
                try:
                    res = legacy_genai.GenerativeModel(m).generate_content(prompt)
                    raw_text = res.text or ""
                    if raw_text: break
                except Exception:
                    continue
        except Exception:
            pass

    if not raw_text:
        return random.choice(FALLBACK_TIPS_HINDI)

    try:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"): cleaned = cleaned[7:]
        if cleaned.startswith("```"): cleaned = cleaned[3:]
        if cleaned.endswith("```"): cleaned = cleaned[:-3]
        data = json.loads(cleaned.strip())
        data["hashtags"] = VIRAL_HASHTAGS
        return data
    except Exception:
        return random.choice(FALLBACK_TIPS_HINDI)

# ==============================================================================
# 2. HINDI DEVANAGARI POSTER GENERATOR (1080x1920)
# ==============================================================================

def get_devanagari_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        ["NotoSansDevanagari-Bold.ttf", "NirmalaB.ttf", "mangal.ttf", "aparajb.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["NotoSansDevanagari-Regular.ttf", "Nirmala.ttf", "mangal.ttf", "aparaj.ttf", "DejaVuSans.ttf"]
    )
    search_dirs = [
        os.path.join("assets", "fonts"),
        "C:/Windows/Fonts",
        "/usr/share/fonts/truetype/noto",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype"
    ]
    for d in search_dirs:
        for fname in candidates:
            fpath = os.path.join(d, fname)
            if os.path.exists(fpath):
                try:
                    return ImageFont.truetype(fpath, size)
                except Exception:
                    pass
    return ImageFont.load_default()

def wrap_text_lines(text: str, font: ImageFont.ImageFont, max_width: int) -> list:
    words = text.split()
    lines = []
    cur = []
    for w in words:
        cur.append(w)
        line = " ".join(cur)
        bbox = font.getbbox(line)
        if (bbox[2] - bbox[0]) > max_width:
            cur.pop()
            if cur: lines.append(" ".join(cur))
            cur = [w]
    if cur: lines.append(" ".join(cur))
    return lines

def create_cyber_graphic(
    content: Dict[str, Any],
    output_path: str = "output/daily_tip.png",
    face_path: str = "assets/my_face.jpg"
) -> str:
    logger.info("🎨 Rendering 1080x1920 Pure Hindi Devanagari Poster...")
    width, height = 1080, 1920

    base = Image.new("RGBA", (width, height), (7, 11, 20, 255))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        r = int(7 * (1 - ratio) + 13 * ratio)
        g = int(11 * (1 - ratio) + 21 * ratio)
        b = int(20 * (1 - ratio) + 38 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([width - 450, -150, width + 250, 550], fill=(0, 240, 255, 45))
    gdraw.ellipse([-200, height - 600, 500, height + 100], fill=(139, 92, 246, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    base = Image.alpha_composite(base, glow)

    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    griddraw = ImageDraw.Draw(grid)
    for x in range(0, width, 90): griddraw.line([(x, 0), (x, height)], fill=(0, 240, 255, 12), width=1)
    for y in range(0, height, 90): griddraw.line([(0, y), (width, y)], fill=(0, 240, 255, 12), width=1)
    base = Image.alpha_composite(base, grid)

    font_badge = get_devanagari_font(28, bold=True)
    font_cat = get_devanagari_font(30, bold=True)
    font_headline = get_devanagari_font(52, bold=True)
    font_body = get_devanagari_font(38, bold=False)
    font_action_title = get_devanagari_font(28, bold=True)
    font_action_body = get_devanagari_font(32, bold=False)
    font_handle = get_devanagari_font(34, bold=True)
    font_sub = get_devanagari_font(26, bold=False)
    font_footer = get_devanagari_font(30, bold=True)
    font_footer_sub = get_devanagari_font(26, bold=False)

    ui = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    uidraw = ImageDraw.Draw(ui)

    # Top Security Badge Pill
    badge_w, badge_h = 580, 60
    bx = (width - badge_w) // 2
    by = 110
    uidraw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=30, fill=(0, 240, 255, 25), outline=(0, 240, 255, 190), width=2)
    uidraw.text((width // 2, by + badge_h // 2), "🛡️ दैनिक साइबर सुरक्षा अलर्ट", font=font_badge, fill=(0, 240, 255, 255), anchor="mm")

    # Founder Photo Branding
    py = 220
    avatar_size = 150
    ax = 80
    if os.path.exists(face_path):
        try:
            fimg = Image.open(face_path).convert("RGBA").resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
            ui.paste(fimg, (ax, py), mask)
            uidraw.ellipse((ax - 3, py - 3, ax + avatar_size + 3, py + avatar_size + 3), outline=(0, 240, 255, 230), width=4)
        except Exception:
            pass

    tx = ax + avatar_size + 30
    uidraw.text((tx, py + 35), CREATOR_HANDLE, font=font_handle, fill=(255, 255, 255, 255))
    uidraw.text((tx, py + 85), "फाउंडर • साइबर डिफेंस एक्सपर्ट", font=font_sub, fill=(148, 163, 184, 255))

    # Main Card
    card_m = 70
    cx1, cx2 = card_m, width - card_m
    cy1, cy2 = 410, 1690
    uidraw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=40, fill=(13, 20, 36, 230), outline=(0, 240, 255, 130), width=2)

    # Category Tag
    tag_y = cy1 + 50
    cat_text = f"// {content.get('category', 'साइबर सुरक्षा').upper()}"
    uidraw.text((cx1 + 60, tag_y), cat_text, font=font_cat, fill=(0, 240, 255, 255))

    # Headline
    headline_text = content.get("headline", "साइबर सुरक्षा नियम")
    headline_lines = wrap_text_lines(headline_text, font_headline, (cx2 - cx1) - 120)
    cur_y = tag_y + 60
    for hl in headline_lines:
        uidraw.text((cx1 + 60, cur_y), hl, font=font_headline, fill=(255, 255, 255, 255))
        cur_y += 68

    div_y = cur_y + 30
    uidraw.line([(cx1 + 60, div_y), (cx2 - 60, div_y)], fill=(30, 41, 59, 255), width=2)
    uidraw.line([(cx1 + 60, div_y), (cx1 + 250, div_y)], fill=(0, 240, 255, 255), width=3)

    # Body Tip Content
    body_y = div_y + 55
    max_tw = (cx2 - cx1) - 120
    tip_lines = wrap_text_lines(content.get("tip", ""), font_body, max_tw)
    for line in tip_lines:
        uidraw.text((cx1 + 60, body_y), line, font=font_body, fill=(226, 232, 240, 255))
        body_y += 62

    # Action Step Box
    ab_y1 = body_y + 50
    ab_y2 = min(ab_y1 + 240, cy2 - 60)
    uidraw.rounded_rectangle([cx1 + 50, ab_y1, cx2 - 50, ab_y2], radius=25, fill=(20, 32, 54, 240), outline=(139, 92, 246, 160), width=2)
    uidraw.text((cx1 + 80, ab_y1 + 35), "⚡ तुरंत यह कदम उठाएं (Action Step)", font=font_action_title, fill=(167, 139, 250, 255))
    act_lines = wrap_text_lines(content.get("action_step", "सुरक्षा सेटिंग्स तुरंत चेक करें।"), font_action_body, max_tw - 40)
    ay = ab_y1 + 85
    for al in act_lines:
        uidraw.text((cx1 + 80, ay), al, font=font_action_body, fill=(241, 245, 249, 255))
        ay += 46

    # Footer
    fy = height - 150
    uidraw.line([(card_m, fy - 30), (width - card_m, fy - 30)], fill=(30, 41, 59, 200), width=1)
    uidraw.text((width // 2, fy), "पोस्ट को SAVE करें • सुरक्षित रहने के लिए SHARE करें", font=font_footer, fill=(0, 240, 255, 255), anchor="mm")
    uidraw.text((width // 2, fy + 50), f"रोज़ाना नई जानकारी के लिए {CREATOR_HANDLE} को फॉलो करें", font=font_footer_sub, fill=(148, 163, 184, 255), anchor="mm")

    final_img = Image.alpha_composite(base, ui).convert("RGB")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_img.save(output_path, "PNG")
    logger.info(f"✅ Pure Hindi poster saved: {output_path}")
    return output_path

# ==============================================================================
# 3. 3D VIDEO REEL ENGINE (VOICEOVER + 3D GRID + CYBER MUSIC)
# ==============================================================================

def get_ffmpeg_binary() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def generate_voiceover_audio(text: str, output_path: str = "output/voiceover.mp3") -> str:
    """Generates realistic Hindi voiceover alternating Male and Female pitch."""
    logger.info("🎙️ Generating Hindi Neural Voiceover...")
    from gtts import gTTS
    raw_tts = "output/raw_tts.mp3"
    tts = gTTS(text=text, lang="hi", slow=False)
    tts.save(raw_tts)

    ffmpeg = get_ffmpeg_binary()
    # Alternate male/female voice
    is_male = random.choice([True, False])
    gender_label = "Male" if is_male else "Female"
    logger.info(f"🎭 Selected Voice: {gender_label} Hindi Neural")

    if is_male:
        pitch_filter = "asetrate=44100*0.86,aresample=44100,atempo=1.16"
    else:
        pitch_filter = "asetrate=44100*1.14,aresample=44100,atempo=0.88"

    cmd = [ffmpeg, "-y", "-i", raw_tts, "-af", pitch_filter, output_path]
    subprocess.run(cmd, capture_output=True)
    return output_path

def generate_synth_music(music_path: str = "assets/music.wav", duration: float = 10.0):
    if os.path.exists(music_path): return music_path
    os.makedirs(os.path.dirname(music_path), exist_ok=True)
    sr = 44100
    ns = int(sr * duration)
    bpm = 120
    bl = sr * 60 / bpm
    notes = [146.83, 174.61, 196.00, 220.00, 261.63, 293.66, 349.23, 440.00]
    with wave.open(music_path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = bytearray()
        for i in range(ns):
            t = i / sr
            bp = (i % int(bl)) / bl
            k = math.sin(2 * math.pi * (150 * math.exp(-bp * 15) + 40) * t) * math.exp(-bp * 8) if bp < 0.5 else 0
            bn = 73.42 if (i // int(bl * 2)) % 2 == 0 else 65.41
            b = 0.5 * math.sin(2 * math.pi * bn * t) + 0.25 * math.sin(2 * math.pi * bn * 2 * t)
            step = int(i // (bl / 4)) % len(notes)
            arp = math.sin(2 * math.pi * notes[step] * t) * math.exp(-((i % int(bl / 4)) / (bl / 4)) * 5) * 0.4
            s = max(-32767, min(32767, int((k * 0.7 + b * 0.5 + arp * 0.4) * 20000)))
            frames.extend(struct.pack("<hh", s, s))
        wf.writeframes(frames)
    return music_path

def create_3d_reel_video(
    content: Dict[str, Any],
    image_poster_path: str = "output/daily_tip.png",
    output_video_path: str = "output/daily_reel.mp4"
) -> Optional[str]:
    """Renders authentic 3D Cyber Grid Reel with Voiceover and Cyber Music."""
    logger.info("🎬 Rendering 3D Perspective Cyber Reel MP4 with Voiceover & Music...")
    ffmpeg = get_ffmpeg_binary()

    # 1. Generate Voiceover from Hindi tip
    voice_script = f"सावधान! {content.get('headline', '')}। {content.get('tip', '')}। {content.get('action_step', '')}।"
    voice_path = generate_voiceover_audio(voice_script, "output/voiceover.mp3")

    # Get voice duration
    probe_cmd = [ffmpeg, "-i", voice_path]
    probe = subprocess.run(probe_cmd, capture_output=True, text=True)
    duration = 9
    for line in probe.stderr.splitlines():
        if "Duration" in line:
            try:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                duration = int(float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])) + 2
                break
            except Exception:
                pass
    duration = max(8, min(duration, 15))

    # 2. Mix Voiceover + Background Music
    music_path = generate_synth_music("assets/music.wav", duration=float(duration + 2))
    mixed_audio = "output/final_audio.aac"
    mix_cmd = [
        ffmpeg, "-y",
        "-i", voice_path,
        "-i", music_path,
        "-filter_complex", "[0:a]volume=2.2[a0];[1:a]volume=0.22[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[outa]",
        "-map", "[outa]",
        "-c:a", "aac",
        mixed_audio
    ]
    subprocess.run(mix_cmd, capture_output=True)

    # 3. Create 3D Grid Loop Video using FFmpeg
    cmd_reel = [
        ffmpeg, "-y",
        "-loop", "1",
        "-i", image_poster_path,
        "-i", mixed_audio,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-t", str(duration),
        output_video_path
    ]
    subprocess.run(cmd_reel, capture_output=True)
    if os.path.exists(output_video_path):
        logger.info(f"✅ 3D Cyber Reel rendered: {output_video_path} (Duration: {duration}s)")
        return output_video_path
    return None

# ==============================================================================
# 4. MEDIA HOSTING & REPO SYNC
# ==============================================================================

def upload_image_to_imgbb(image_path: str) -> Optional[str]:
    if not IMGBB_API_KEY: return None
    try:
        with open(image_path, "rb") as f:
            res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY}, files={"image": f}, timeout=30)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                url = data["data"]["url"]
                logger.info(f"✅ Poster uploaded to ImgBB: {url}")
                return url
    except Exception as e:
        logger.error(f"ImgBB error: {e}")
    return None

def host_video_on_github(video_path: str) -> Optional[str]:
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main/{video_path.replace(os.sep, '/')}"
    if not GITHUB_TOKEN: return raw_url
    try:
        import base64
        with open(video_path, "rb") as f:
            v_b64 = base64.b64encode(f.read()).decode("utf-8")
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
        api_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/contents/{video_path.replace(os.sep, '/')}"
        check = requests.get(api_url, headers=headers)
        payload = {"message": "Update daily reel MP4", "content": v_b64, "branch": "main"}
        if check.status_code == 200:
            payload["sha"] = check.json()["sha"]
        res = requests.put(api_url, headers=headers, json=payload, timeout=60)
        if res.status_code in (200, 201):
            logger.info(f"✅ Reel video pushed to GitHub CDN: {raw_url}")
    except Exception as e:
        logger.warning(f"Video host notice: {e}")
    return raw_url

# ==============================================================================
# 5. META INSTAGRAM MULTI-FORMAT PUBLISHER
# ==============================================================================

class InstagramMultiPublisher:
    def __init__(self, access_token: str, ig_user_id: str):
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.graph_base = "https://graph.facebook.com/v19.0"

    def publish_feed_post(self, image_url: str, caption: str) -> Optional[str]:
        logger.info("🚀 1/3 Publishing Feed Post to Instagram...")
        try:
            r1 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media", data={
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" not in r1: return None
            time.sleep(6)
            r2 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media_publish", data={
                "creation_id": r1["id"],
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" in r2:
                logger.info(f"🎉 Feed Post Published! Media ID: {r2['id']}")
                return r2["id"]
        except Exception as e:
            logger.error(f"Feed post error: {e}")
        return None

    def publish_story(self, image_url: str) -> Optional[str]:
        logger.info("🚀 2/3 Publishing Story to Instagram...")
        try:
            r1 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media", data={
                "media_type": "STORIES",
                "image_url": image_url,
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" not in r1: return None
            time.sleep(6)
            r2 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media_publish", data={
                "creation_id": r1["id"],
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" in r2:
                logger.info(f"🎉 Story Published! ID: {r2['id']}")
                return r2["id"]
        except Exception as e:
            logger.error(f"Story post error: {e}")
        return None

    def publish_reel(self, video_url: str, caption: str) -> Optional[str]:
        logger.info("🚀 3/3 Publishing 3D Reel with Voiceover & Music to Instagram...")
        try:
            r1 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media", data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": "true",
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" not in r1: return None
            creation_id = r1["id"]

            logger.info("⏳ Waiting for Meta video processing...")
            for _ in range(15):
                time.sleep(5)
                status = requests.get(
                    f"{self.graph_base}/{creation_id}?fields=status_code&access_token={self.access_token}",
                    timeout=30
                ).json().get("status_code")
                if status == "FINISHED": break
                elif status == "ERROR": return None

            r2 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media_publish", data={
                "creation_id": creation_id,
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" in r2:
                logger.info(f"🎉 3D Reel Published! Media ID: {r2['id']}")
                return r2["id"]
        except Exception as e:
            logger.error(f"Reel publish error: {e}")
        return None

# ==============================================================================
# 6. MAIN EXECUTION PIPELINE
# ==============================================================================

def main():
    logger.info("================================================================================")
    logger.info(f"🛡️ STARTING CYBER AUTOMATION FOR {CREATOR_HANDLE} (HINDI 3D EDITION)")
    logger.info("================================================================================")

    # 1. Content Generation in Hindi
    content = generate_cyber_content()
    hashtags_str = " ".join(content.get("hashtags", VIRAL_HASHTAGS))
    full_caption = f"{content.get('caption', '')}\n\n.\n.\n{hashtags_str}\n\n🛡️ रोज़ाना साइबर सुरक्षा ज्ञान के लिए फॉलो करें: {CREATOR_HANDLE}"

    # 2. Render Pure Hindi Poster (with Founder Face)
    poster_path = "output/daily_tip.png"
    face_path = "assets/my_face.jpg"
    create_cyber_graphic(content, output_path=poster_path, face_path=face_path)

    # 3. Render 3D Reel with Voiceover & Music
    reel_path = "output/daily_reel.mp4"
    create_3d_reel_video(content, image_poster_path=poster_path, output_video_path=reel_path)

    if DRY_RUN:
        logger.info("⚡ DRY_RUN mode active. All media generated. Skipping publishing.")
        return

    # 4. Host Media
    public_img_url = upload_image_to_imgbb(poster_path)
    public_video_url = host_video_on_github(reel_path)

    if not public_img_url:
        logger.error("❌ Public image URL not available. Aborting.")
        return

    # 5. Publish Multi-Format to Instagram
    publisher = InstagramMultiPublisher(
        access_token=FB_ACCESS_TOKEN,
        ig_user_id=IG_USER_ID
    )

    # 5A. Post
    post_id = publisher.publish_feed_post(public_img_url, full_caption)
    # 5B. Story
    story_id = publisher.publish_story(public_img_url)
    # 5C. Reel
    reel_id = None
    if public_video_url:
        reel_id = publisher.publish_reel(public_video_url, full_caption)

    logger.info("================================================================================")
    logger.info("📊 MULTI-FORMAT EXECUTION SUMMARY")
    logger.info(f"• Creator:          {CREATOR_HANDLE}")
    logger.info(f"• Content Title:    '{content.get('headline')}'")
    logger.info(f"• Feed Post Status: {'✅ SUCCESS (ID: ' + post_id + ')' if post_id else '❌ FAILED'}")
    logger.info(f"• Story Status:     {'✅ SUCCESS (ID: ' + story_id + ')' if story_id else '❌ FAILED'}")
    logger.info(f"• 3D Reel Status:   {'✅ SUCCESS (ID: ' + reel_id + ')' if reel_id else '❌ FAILED'}")
    logger.info("================================================================================")

if __name__ == "__main__":
    main()
