#!/usr/bin/env python3
"""
================================================================================
Cyber Security Social Media Automation Bot (Hindi Edition)
Automated 3x Daily Multi-Format Publisher:
1. Instagram Feed Post
2. Instagram Story
3. Instagram Reel with Cyber Tech Music
Runs 24/7 Serverless on GitHub Actions
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

# Suppress deprecation and future warnings for clean automated logs
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Load local environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure UTF-8 for cross-platform console compatibility (prevents Windows cp1252 emoji crash)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CyberSocialBot")

# ==============================================================================
# CONFIGURATION & ENVIRONMENT VALIDATION
# ==============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "").strip()
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "").strip()
IG_USER_ID = os.getenv("IG_USER_ID", "").strip()
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "sky140052-ops/automotin").strip()
CREATOR_HANDLE = os.getenv("CREATOR_HANDLE", "@rauth_jee").strip()
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

# Curated high-impact Hindi fallback tips
FALLBACK_TIPS_HINDI = [
    {
        "headline": "MFA Fatigue अटैक से सावधान रहें!",
        "category": "पहचान और पासवर्ड सुरक्षा",
        "tip": "हैकर्स देर रात आपके फोन पर लगातार 2FA/MFA अप्रूवल नोटिफिकेशन भेजते हैं, ताकि आप परेशान होकर 'Approve' दबा दें। अगर आपने खुद लॉगिन नहीं किया है, तो कभी भी 'Approve' पर क्लिक न करें।",
        "action_step": "SMS OTP की जगह Google Authenticator या Microsoft Authenticator ऐप का इस्तेमाल करें।",
        "caption": "🚨 सतर्क रहें: MFA Fatigue Attacks बहुत तेजी से बढ़ रहे हैं!\n\nहैकर्स अब सिर्फ पासवर्ड नहीं चुराते, बल्कि आपको बार-बार नोटिफिकेशन भेजकर थका देते हैं ताकि आप गलती से 'Approve' दबा दें।\n\nबचने के उपाय:\n1. बिना मांगे आए किसी भी नोटिफिकेशन को अप्रूव न करें।\n2. तुरंत अपना पासवर्ड बदलें।\n3. Authenticator ऐप का उपयोग करें।\n\n🛡️ खुद को और अपने दोस्तों को सुरक्षित रखें!",
        "hashtags": ["#CyberSecurityHindi", "#TechTipsHindi", "#OnlineSafety", "#PasswordSecurity", "#CyberSafety"]
    },
    {
        "headline": "ब्राउज़र में पासवर्ड कभी सेव न करें!",
        "category": "डेटा और प्राइवेसी सुरक्षा",
        "tip": "Chrome या Edge जैसे ब्राउज़र्स में सेव किए गए पासवर्ड्स को 'Infostealer' वायरस सिर्फ 5 सेकंड में चुरा लेते हैं। एक गलत डाउनलोड आपकी सारी पर्सनल आईडी और बैंकिंग डिटेल्स लीक कर सकता है।",
        "action_step": "ब्राउज़र से सारे पासवर्ड हटाएं और Bitwarden या 1Password जैसे सुरक्षित पासवर्ड मैनेजर का इस्तेमाल करें।",
        "caption": "⚠️ क्या आपके पासवर्ड्स ब्राउज़र में सेव हैं?\n\nसावधान! आज के सबसे खतरनाक मैलवेयर (जैसे Lumma, RedLine) सीधे आपके ब्राउज़र के पासवर्ड कैश को निशाना बनाते हैं।\n\nसुरक्षा नियम:\n• ब्राउज़र के 'Auto-Save Password' को बंद करें\n• एक डेडिकेटेड एन्क्रिप्टेड पासवर्ड वॉल्ट इस्तेमाल करें\n• टू-स्टेप वेरिफिकेशन (2FA) हमेशा ऑन रखें",
        "hashtags": ["#CyberSecurity", "#TechNewsHindi", "#PrivacyFirst", "#DataProtection", "#CyberAwareness"]
    },
    {
        "headline": "फर्जी QR कोड (Quishing) से बचें!",
        "category": "ऑनलाइन फ्रॉड से बचाव",
        "tip": "धोखेबाज़ असली पेमेंट या मेनू QR कोड के ऊपर अपना फर्जी QR कोड चिपका देते हैं। इसे स्कैन करते ही आपका फोन नकली वेबसाइट पर चला जाता है और आपकी यूपीआई या लॉगिन जानकारी चोरी हो जाती है।",
        "action_step": "QR कोड स्कैन करने के बाद लिंक के असली स्पेलिंग और डोमेन को ध्यान से देखकर ही आगे बढ़ें।",
        "caption": "📱 कोई भी QR Code स्कैन करने से पहले 2 बार सोचें!\n\nआजकल 'Quishing' (QR Phishing) बहुत तेज़ी से फैल रहा है क्योंकि सामान्य एंटी-वायरस QR कोड के अंदर छिपे खतरे को नहीं पकड़ पाते।\n\nसावधानी:\n1. सार्वजनिक जगहों पर लगे क्यूआर कोड पर कोई दूसरा स्टिकर तो नहीं चिपका, यह जांचें।\n2. पेमेंट करते समय प्राप्तकर्ता का नाम ज़रूर चेक करें।\n3. अनजान क्यूआर से आए किसी भी लिंक पर पासवर्ड न डालें।",
        "hashtags": ["#Quishing", "#UPIFraud", "#OnlineScamAlert", "#DigitalIndia", "#CyberSecurityHindi"]
    }
]

# ==============================================================================
# 1. AI CONTENT GENERATOR (HINDI GEMINI)
# ==============================================================================

def generate_cyber_content() -> Dict[str, Any]:
    """Generates unique viral Cyber Security tip in Hindi with Google Gemini."""
    logger.info("🤖 Generating Hindi Cyber Security Tip with Google Gemini...")

    if not GEMINI_API_KEY or "your_gemini" in GEMINI_API_KEY.lower():
        logger.warning("⚠️ Valid GEMINI_API_KEY not found. Using curated Hindi fallback tip.")
        return random.choice(FALLBACK_TIPS_HINDI)

    prompt = """
You are an expert Cyber Security Educator creating viral tech content in HINDI (Devanagari script).
Generate a high-impact, practical daily Cyber Security tip for everyday users and tech professionals.

You must return ONLY a valid JSON object (no markdown, no backticks) with these exact keys:
{
  "headline": "Punchy Hindi title under 6 words (e.g. 'MFA Fatigue अटैक से सावधान!')",
  "category": "Security domain in Hindi (e.g. 'पासवर्ड और डेटा सुरक्षा')",
  "tip": "The main security insight in clear, simple HINDI for an image graphic. Must be under 45 words, impactful, easy to understand.",
  "action_step": "1 actionable sentence in Hindi telling the reader what action to take right now.",
  "caption": "An engaging, well-formatted Hindi caption for Instagram with bullet points and a call-to-action.",
  "hashtags": ["#CyberSecurityHindi", "#TechTipsHindi", "#OnlineSafety", "#CyberDefense"]
}
"""

    raw_response_text = ""

    # Strategy A: Modern google-genai SDK
    for model_name in ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            raw_response_text = response.text or ""
            if raw_response_text:
                logger.info(f"✅ Generated content using google-genai SDK ({model_name}).")
                break
        except Exception as e_genai:
            logger.info(f"Model {model_name} attempt: {e_genai}")

    # Strategy B: Fallback to google-generativeai SDK
    if not raw_response_text:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=GEMINI_API_KEY)
            for legacy_model in ["gemini-1.5-flash", "gemini-2.0-flash"]:
                try:
                    model = legacy_genai.GenerativeModel(legacy_model)
                    response = model.generate_content(prompt)
                    raw_response_text = response.text or ""
                    if raw_response_text:
                        logger.info(f"✅ Generated content using legacy SDK ({legacy_model}).")
                        break
                except Exception:
                    continue
        except Exception as e_legacy:
            logger.error(f"Legacy Gemini API error: {e_legacy}")

    if not raw_response_text:
        logger.warning("🔄 Reverting to curated Hindi fallback tip.")
        return random.choice(FALLBACK_TIPS_HINDI)

    try:
        cleaned = raw_response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        required_keys = ["headline", "category", "tip", "action_step", "caption", "hashtags"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing key: {key}")
        logger.info(f"🎯 Successfully parsed Hindi Tip: '{data['headline']}'")
        return data
    except Exception as parse_err:
        logger.error(f"⚠️ Error parsing Gemini JSON ({parse_err}). Using fallback.")
        return random.choice(FALLBACK_TIPS_HINDI)

# ==============================================================================
# 2. IMAGE & VISUAL GENERATOR (PILLOW 1080x1920 with Devanagari Hindi support)
# ==============================================================================

def get_devanagari_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Finds and loads best available Devanagari Hindi font across Windows & Linux."""
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
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = font.getbbox(test_line)
        line_w = bbox[2] - bbox[0]
        if line_w > max_width:
            current_line.pop()
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_cyber_graphic(
    content: Dict[str, Any],
    output_path: str = "output/daily_tip.png",
    face_path: str = "assets/my_face.jpg"
) -> str:
    """Renders 1080x1920 vertical Hindi cyber graphic with user face branding."""
    logger.info("🎨 Rendering 1080x1920 Hindi Cyber Security Visual Graphic...")
    width, height = 1080, 1920

    # 1. Base Gradient Canvas
    base = Image.new("RGBA", (width, height), (7, 11, 20, 255))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        r = int(7 * (1 - ratio) + 13 * ratio)
        g = int(11 * (1 - ratio) + 21 * ratio)
        b = int(20 * (1 - ratio) + 38 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Glowing Ambient Halos (Cyan Top-Right, Violet Bottom-Left)
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    gdraw.ellipse([width - 450, -150, width + 250, 550], fill=(0, 240, 255, 45))
    gdraw.ellipse([-200, height - 600, 500, height + 100], fill=(139, 92, 246, 40))
    gdraw.ellipse([width // 2 - 300, height // 2 - 300, width // 2 + 300, height // 2 + 300], fill=(14, 165, 233, 20))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(80))
    base = Image.alpha_composite(base, glow_layer)

    # 3. Subtle Cyber Grid Overlay
    grid_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    griddraw = ImageDraw.Draw(grid_layer)
    grid_size = 90
    for x in range(0, width, grid_size):
        griddraw.line([(x, 0), (x, height)], fill=(0, 240, 255, 12), width=1)
    for y in range(0, height, grid_size):
        griddraw.line([(0, y), (width, y)], fill=(0, 240, 255, 12), width=1)
    base = Image.alpha_composite(base, grid_layer)

    # 4. Hindi Typography
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

    ui_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    uidraw = ImageDraw.Draw(ui_layer)

    # Top Security Badge Pill
    badge_w, badge_h = 580, 60
    badge_x = (width - badge_w) // 2
    badge_y = 110
    uidraw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=30,
        fill=(0, 240, 255, 25),
        outline=(0, 240, 255, 190),
        width=2
    )
    uidraw.text(
        (width // 2, badge_y + badge_h // 2),
        "🛡️ दैनिक साइबर सुरक्षा अलर्ट",
        font=font_badge,
        fill=(0, 240, 255, 255),
        anchor="mm"
    )

    # Creator Branding / Face Photo
    profile_y = 220
    avatar_size = 150
    avatar_x = 80

    if os.path.exists(face_path):
        try:
            face_img = Image.open(face_path).convert("RGBA")
            face_img = face_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            m_draw = ImageDraw.Draw(mask)
            m_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            ui_layer.paste(face_img, (avatar_x, profile_y), mask)
            uidraw.ellipse(
                (avatar_x - 3, profile_y - 3, avatar_x + avatar_size + 3, profile_y + avatar_size + 3),
                outline=(0, 240, 255, 230),
                width=4
            )
        except Exception as e:
            logger.warning(f"Error loading face photo ({e})")
    else:
        uidraw.ellipse(
            (avatar_x, profile_y, avatar_x + avatar_size, profile_y + avatar_size),
            fill=(15, 23, 42, 240),
            outline=(0, 240, 255, 220),
            width=3
        )
        uidraw.text(
            (avatar_x + avatar_size // 2, profile_y + avatar_size // 2),
            "PRO",
            font=font_badge,
            fill=(0, 240, 255, 255),
            anchor="mm"
        )

    # Brand Title and Credential
    text_x = avatar_x + avatar_size + 30
    uidraw.text((text_x, profile_y + 35), CREATOR_HANDLE, font=font_handle, fill=(255, 255, 255, 255))
    uidraw.text((text_x, profile_y + 85), "फाउंडर • साइबर डिफेंस एक्सपर्ट", font=font_sub, fill=(148, 163, 184, 255))

    # Main Glassmorphism Content Card
    card_margin = 70
    card_x1 = card_margin
    card_x2 = width - card_margin
    card_y1 = 410
    card_y2 = 1690

    uidraw.rounded_rectangle(
        [card_x1, card_y1, card_x2, card_y2],
        radius=40,
        fill=(13, 20, 36, 230),
        outline=(0, 240, 255, 130),
        width=2
    )

    # Category Tag
    tag_y = card_y1 + 50
    category_text = f"// {content.get('category', 'साइबर सुरक्षा').upper()}"
    uidraw.text((card_x1 + 60, tag_y), category_text, font=font_cat, fill=(0, 240, 255, 255))

    # Headline
    headline_y = tag_y + 60
    headline_text = content.get("headline", "साइबर सुरक्षा नियम")
    headline_lines = wrap_text_lines(headline_text, font_headline, (card_x2 - card_x1) - 120)
    cur_y = headline_y
    for hline in headline_lines:
        uidraw.text((card_x1 + 60, cur_y), hline, font=font_headline, fill=(255, 255, 255, 255))
        cur_y += 68

    # Neon Divider
    div_y = cur_y + 30
    uidraw.line([(card_x1 + 60, div_y), (card_x2 - 60, div_y)], fill=(30, 41, 59, 255), width=2)
    uidraw.line([(card_x1 + 250, div_y), (card_x1 + 250, div_y)], fill=(0, 240, 255, 255), width=3)

    # Body Tip Content
    body_y = div_y + 55
    max_text_w = (card_x2 - card_x1) - 120
    tip_text = content.get("tip", "")
    tip_lines = wrap_text_lines(tip_text, font_body, max_text_w)

    for line in tip_lines:
        uidraw.text((card_x1 + 60, body_y), line, font=font_body, fill=(226, 232, 240, 255))
        body_y += 62

    # Inner Action Box
    action_box_y1 = body_y + 50
    action_box_y2 = min(action_box_y1 + 240, card_y2 - 60)
    uidraw.rounded_rectangle(
        [card_x1 + 50, action_box_y1, card_x2 - 50, action_box_y2],
        radius=25,
        fill=(20, 32, 54, 240),
        outline=(139, 92, 246, 160),
        width=2
    )
    uidraw.text(
        (card_x1 + 80, action_box_y1 + 35),
        "⚡ तुरंत यह कदम उठाएं (Action Step)",
        font=font_action_title,
        fill=(167, 139, 250, 255)
    )

    action_text = content.get("action_step", "अपनी सुरक्षा सेटिंग्स तुरंत चेक करें।")
    action_lines = wrap_text_lines(action_text, font_action_body, max_text_w - 40)
    act_y = action_box_y1 + 85
    for aline in action_lines:
        uidraw.text((card_x1 + 80, act_y), aline, font=font_action_body, fill=(241, 245, 249, 255))
        act_y += 46

    # Bottom CTA Footer
    footer_y = height - 150
    uidraw.line([(card_margin, footer_y - 30), (width - card_margin, footer_y - 30)], fill=(30, 41, 59, 200), width=1)
    uidraw.text(
        (width // 2, footer_y),
        "पोस्ट को SAVE करें • दूसरों को सुरक्षित रखने के लिए SHARE करें",
        font=font_footer,
        fill=(0, 240, 255, 255),
        anchor="mm"
    )
    uidraw.text(
        (width // 2, footer_y + 50),
        f"रोज़ाना नई जानकारी के लिए {CREATOR_HANDLE} को फॉलो करें",
        font=font_footer_sub,
        fill=(148, 163, 184, 255),
        anchor="mm"
    )

    # Save
    final_img = Image.alpha_composite(base, ui_layer).convert("RGB")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_img.save(output_path, "PNG")
    logger.info(f"✅ Hindi graphic saved to: {output_path}")
    return output_path

# ==============================================================================
# 3. REEL / VIDEO GENERATOR WITH CYBER MUSIC
# ==============================================================================

def generate_synth_music(music_path: str = "assets/music.wav", duration: float = 8.0):
    """Generates a rhythmic cyber synth audio track if not already present."""
    if os.path.exists(music_path):
        return music_path
    os.makedirs(os.path.dirname(music_path), exist_ok=True)
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    bpm = 120
    beat_len = sample_rate * 60 / bpm
    notes = [146.83, 174.61, 196.00, 220.00, 261.63, 293.66, 349.23, 440.00]

    with wave.open(music_path, "w") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            beat_pos = (i % int(beat_len)) / beat_len
            kick_freq = 150 * math.exp(-beat_pos * 15) + 40
            kick = math.sin(2 * math.pi * kick_freq * t) * math.exp(-beat_pos * 8) if beat_pos < 0.5 else 0
            bass_note = 73.42 if (i // int(beat_len * 2)) % 2 == 0 else 65.41
            bass = 0.5 * math.sin(2 * math.pi * bass_note * t) + 0.25 * math.sin(2 * math.pi * bass_note * 2 * t)
            step = int(i // (beat_len / 4)) % len(notes)
            arp = math.sin(2 * math.pi * notes[step] * t) * math.exp(-((i % int(beat_len / 4)) / (beat_len / 4)) * 5) * 0.4
            sample = int((kick * 0.7 + bass * 0.5 + arp * 0.4) * 20000)
            sample = max(-32767, min(32767, sample))
            frames.extend(struct.pack("<hh", sample, sample))
        wav_file.writeframes(frames)
    return music_path

def create_cyber_reel(
    image_path: str = "output/daily_tip.png",
    output_video_path: str = "output/daily_reel.mp4",
    duration: int = 8
) -> Optional[str]:
    """Combines graphic and audio into an Instagram-compliant 1080x1920 MP4 Reel."""
    logger.info("🎬 Rendering 1080x1920 Cyber Reel MP4 with background music...")
    try:
        music_path = generate_synth_music("assets/music.wav")
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg_exe = "ffmpeg"

    cmd = [
        ffmpeg_exe, "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", music_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-t", str(duration),
        output_video_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if res.returncode == 0 and os.path.exists(output_video_path):
            logger.info(f"✅ Reel MP4 generated successfully: {output_video_path}")
            return output_video_path
        else:
            logger.error(f"FFmpeg error: {res.stderr}")
            return None
    except Exception as e:
        logger.error(f"Failed to generate Reel MP4: {e}")
        return None

# ==============================================================================
# 4. CLOUD MEDIA HOSTING (ImgBB & GitHub Raw CDN)
# ==============================================================================

def upload_image_to_imgbb(image_path: str) -> Optional[str]:
    """Uploads image to ImgBB and returns direct HTTPS URL."""
    if not IMGBB_API_KEY:
        return None
    try:
        url = "https://api.imgbb.com/1/upload"
        with open(image_path, "rb") as f:
            res = requests.post(url, data={"key": IMGBB_API_KEY}, files={"image": f}, timeout=30)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                direct_url = data["data"]["url"]
                logger.info(f"✅ Image uploaded to ImgBB: {direct_url}")
                return direct_url
    except Exception as e:
        logger.error(f"ImgBB upload error: {e}")
    return None

def host_video_on_github(video_path: str) -> Optional[str]:
    """Commits Reel MP4 to public GitHub repository to get direct raw CDN link."""
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main/{video_path.replace(os.sep, '/')}"
    if not GITHUB_TOKEN:
        logger.warning("No GITHUB_TOKEN found; using predicted raw URL.")
        return raw_url

    try:
        import base64
        with open(video_path, "rb") as f:
            v_b64 = base64.b64encode(f.read()).decode("utf-8")
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
        api_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/contents/{video_path.replace(os.sep, '/')}"
        check = requests.get(api_url, headers=headers)
        payload = {
            "message": "Automated update: daily reel MP4 for Instagram Reels API",
            "content": v_b64,
            "branch": "main"
        }
        if check.status_code == 200:
            payload["sha"] = check.json()['sha']
        put_res = requests.put(api_url, headers=headers, json=payload, timeout=60)
        if put_res.status_code in (200, 201):
            logger.info(f"✅ Reel video pushed to GitHub CDN: {raw_url}")
            return raw_url
    except Exception as e:
        logger.warning(f"GitHub video commit warning: {e}")
    return raw_url

# ==============================================================================
# 5. META INSTAGRAM MULTI-FORMAT PUBLISHER (POST + STORY + REEL)
# ==============================================================================

class InstagramMultiPublisher:
    def __init__(self, access_token: str, ig_user_id: str):
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.graph_base = "https://graph.facebook.com/v19.0"

    def publish_feed_post(self, image_url: str, caption: str) -> Optional[str]:
        """Publishes 1080x1920 feed post."""
        logger.info("🚀 1/3 Publishing Feed Post to Instagram...")
        try:
            r1 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media", data={
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }, timeout=45)
            cdata = r1.json()
            if "id" not in cdata:
                logger.error(f"Feed container failed: {cdata}")
                return None
            creation_id = cdata["id"]
            time.sleep(6)
            r2 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media_publish", data={
                "creation_id": creation_id,
                "access_token": self.access_token
            }, timeout=45)
            pdata = r2.json()
            if "id" in pdata:
                logger.info(f"🎉 Feed Post Published! Media ID: {pdata['id']}")
                return pdata["id"]
            else:
                logger.error(f"Feed publish error: {pdata}")
        except Exception as e:
            logger.error(f"Feed post exception: {e}")
        return None

    def publish_story(self, image_url: str) -> Optional[str]:
        """Publishes 1080x1920 Story to Instagram."""
        logger.info("🚀 2/3 Publishing Story to Instagram...")
        try:
            r1 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media", data={
                "media_type": "STORIES",
                "image_url": image_url,
                "access_token": self.access_token
            }, timeout=45)
            cdata = r1.json()
            if "id" not in cdata:
                logger.error(f"Story container failed: {cdata}")
                return None
            creation_id = cdata["id"]
            time.sleep(6)
            r2 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media_publish", data={
                "creation_id": creation_id,
                "access_token": self.access_token
            }, timeout=45)
            pdata = r2.json()
            if "id" in pdata:
                logger.info(f"🎉 Story Published! ID: {pdata['id']}")
                return pdata["id"]
            else:
                logger.error(f"Story publish error: {pdata}")
        except Exception as e:
            logger.error(f"Story post exception: {e}")
        return None

    def publish_reel(self, video_url: str, caption: str) -> Optional[str]:
        """Publishes 1080x1920 Reel with music to Instagram."""
        logger.info("🚀 3/3 Publishing Reel with Music to Instagram...")
        try:
            r1 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media", data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": "true",
                "access_token": self.access_token
            }, timeout=45)
            cdata = r1.json()
            if "id" not in cdata:
                logger.error(f"Reel container failed: {cdata}")
                return None
            creation_id = cdata["id"]

            # Poll until Meta finishes video processing
            logger.info("⏳ Waiting for Meta to process Reel video...")
            for attempt in range(15):
                time.sleep(5)
                status_res = requests.get(
                    f"{self.graph_base}/{creation_id}?fields=status_code&access_token={self.access_token}",
                    timeout=30
                ).json()
                status_code = status_res.get("status_code")
                if status_code == "FINISHED":
                    break
                elif status_code == "ERROR":
                    logger.error(f"Video processing error: {status_res}")
                    return None

            r2 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media_publish", data={
                "creation_id": creation_id,
                "access_token": self.access_token
            }, timeout=45)
            pdata = r2.json()
            if "id" in pdata:
                logger.info(f"🎉 Reel Published! Media ID: {pdata['id']}")
                return pdata["id"]
            else:
                logger.error(f"Reel publish error: {pdata}")
        except Exception as e:
            logger.error(f"Reel post exception: {e}")
        return None

# ==============================================================================
# 6. MAIN ORCHESTRATION PIPELINE
# ==============================================================================

def main():
    logger.info("================================================================================")
    logger.info("🛡️ STARTING HINDI CYBER SECURITY SOCIAL MEDIA AUTOMATION PIPELINE")
    logger.info("================================================================================")

    # 1. Content Generation in Hindi
    content = generate_cyber_content()
    hashtags_str = " ".join(content.get("hashtags", ["#CyberSecurityHindi", "#TechTipsHindi", "#OnlineSafety"]))
    full_caption = f"{content.get('caption', '')}\n\n.\n.\n{hashtags_str}\n\n🛡️ रोज़ाना सुरक्षा टिप्स के लिए फॉलो करें: {CREATOR_HANDLE}"

    # 2. Render Hindi Graphic
    output_image = "output/daily_tip.png"
    face_path = "assets/my_face.jpg"
    create_cyber_graphic(content, output_path=output_image, face_path=face_path)

    # 3. Render Cyber Reel MP4 with Music
    output_reel = "output/daily_reel.mp4"
    create_cyber_reel(image_path=output_image, output_video_path=output_reel, duration=8)

    # Dry-Run Check
    if DRY_RUN:
        logger.info("⚡ DRY_RUN is active. All media generated. Skipping Instagram publish.")
        return

    # 4. Host Media
    public_img_url = upload_image_to_imgbb(output_image)
    public_video_url = host_video_on_github(output_reel)

    if not public_img_url:
        logger.error("❌ Could not get public image URL. Aborting publish.")
        return

    # 5. Multi-Format Publish to Instagram
    publisher = InstagramMultiPublisher(
        access_token=FB_ACCESS_TOKEN,
        ig_user_id=IG_USER_ID
    )

    # 5A. Publish Feed Post
    post_id = publisher.publish_feed_post(public_img_url, full_caption)

    # 5B. Publish Story
    story_id = publisher.publish_story(public_img_url)

    # 5C. Publish Reel with Music
    reel_id = None
    if public_video_url:
        reel_id = publisher.publish_reel(public_video_url, full_caption)

    logger.info("================================================================================")
    logger.info("📊 MULTI-FORMAT EXECUTION SUMMARY")
    logger.info(f"• Content Title: '{content.get('headline')}'")
    logger.info(f"• Feed Post Status: {'✅ SUCCESS (ID: ' + post_id + ')' if post_id else '❌ FAILED'}")
    logger.info(f"• Story Status:     {'✅ SUCCESS (ID: ' + story_id + ')' if story_id else '❌ FAILED'}")
    logger.info(f"• Reel with Song:   {'✅ SUCCESS (ID: ' + reel_id + ')' if reel_id else '❌ FAILED'}")
    logger.info("================================================================================")

if __name__ == "__main__":
    main()
