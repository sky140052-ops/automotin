"""
BBCC SKILL HUB - Authentic Newspaper Photo Automation Bot (Local Daemon)
Author: @rauth_jee / Antigravity AI
Features:
  - Generates authentic 1080x1920 Dainik Jagran style newspaper poster (Photo Only)
  - Zero Tofu / Missing Box glyphs (Google Mukta bilingual fonts)
  - Both Commercial Ads: BBCC Skill Hub Coaching Registration + PTCC+BBCC Chakdah Chowk Madhubani
  - Multi-Sector Google News RSS (Education, Police, Railways, Health, Agriculture, MSME, Banking, etc.)
  - Posts Photo directly to Facebook Page (@rauth_jee) and Instagram Feed (@rauth_jee)
  - Automatically posts Story to Instagram (up to 6 times daily)
  - Automatically replies to Instagram comments
  - Runs every 10 minutes between 06:00 AM and 06:00 PM IST
"""

import os
import sys
import time
import json
import random
import logging
import datetime
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Any
from pathlib import Path

import requests
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("NewspaperPhotoBot")

# Configuration & Credentials (loaded from .env or environment)
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CREATOR_HANDLE = os.getenv("CREATOR_HANDLE", "@rauth_jee")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TOPICS_FILE = OUTPUT_DIR / "posted_topics.json"
STORY_HISTORY_FILE = OUTPUT_DIR / "story_history.json"

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

def get_ist_now() -> datetime.datetime:
    utc = datetime.datetime.now(datetime.timezone.utc)
    return utc + datetime.timedelta(hours=5, minutes=30)

def is_within_publishing_hours() -> bool:
    ist = get_ist_now()
    curr_min = ist.hour * 60 + ist.minute
    # 05:45 AM (345 min) to 06:15 PM (1095 min)
    return 345 <= curr_min <= 1095

def load_posted_topics() -> List[str]:
    if TOPICS_FILE.exists():
        try:
            with open(TOPICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_posted_topic(title: str):
    topics = load_posted_topics()
    topics.append(title)
    if len(topics) > 500:
        topics = topics[-500:]
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)

def should_publish_story() -> bool:
    if not STORY_HISTORY_FILE.exists():
        return True
    try:
        with open(STORY_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        history = data.get("timestamps", [])
        now_ts = time.time()
        recent = [t for t in history if now_ts - t < 86400]
        if len(recent) >= 6:
            return False
        if recent and (now_ts - recent[-1]) < 12600:  # ~3.5 hours
            return False
        return True
    except Exception:
        return True

def record_story_published():
    history = []
    if STORY_HISTORY_FILE.exists():
        try:
            with open(STORY_HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f).get("timestamps", [])
        except Exception:
            pass
    history.append(time.time())
    with open(STORY_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"timestamps": history[-30:]}, f, indent=2)

NEWS_SECTORS = [
    {"name": "शिक्षा एवं शिक्षक भर्ती", "query": "बिहार शिक्षक भर्ती OR BPSC TRE OR STET परीक्षा"},
    {"name": "पुलिस एवं दारोगा भर्ती", "query": "बिहार पुलिस बहाली OR दारोga भर्ती OR CSBC BPSSC"},
    {"name": "रेलवे एवं केंद्रीय भर्ती", "query": "रेलवे भर्ती 2026 OR RRB NTPC ग्रुप डी OR SSC भर्ती"},
    {"name": "कृषि एवं ग्रामीण विकास", "query": "बिहार कृषि मौसम किसान योजना OR ग्रामीण कार्य"},
    {"name": "स्वास्थ्य एवं चिकित्सा", "query": "बिहार स्वास्थ्य विभाग AIIMS पटना PMCH अस्पताल"},
    {"name": "बैंकिंग एवं वित्त", "query": "RBI नियम बैंक लोन ब्याज दर बैंकिंग अपडेट"},
    {"name": "महिला कल्याण एवं जीविका", "query": "बिहार महिला रोजगार जीविका दीदी सरकारी योजना"},
    {"name": "भूमि सुधार एवं राजस्व", "query": "बिहार जमीन सर्वे दाखिल खारिज राजस्व विभाग रजिस्ट्री"},
    {"name": "उद्योग एवं MSME", "query": "बिहार उद्योग व्यापार MSME उद्यम योजना स्वरोजगार"},
    {"name": "साइबर सुरक्षा एवं तकनीक", "query": "साइबर फ्रॉड अलर्ट डिजिटल अवेयरनेस ऑनलाइन सुरक्षा"}
]

def fetch_unique_live_news() -> Optional[Dict[str, str]]:
    posted_topics = load_posted_topics()
    random.shuffle(NEWS_SECTORS)
    logger.info("Scanning Google News RSS across diverse government & public sectors...")

    for sector in NEWS_SECTORS:
        encoded = urllib.parse.quote(sector["query"])
        url = f"https://news.google.com/rss/search?q={encoded}&hl=hi&gl=IN&ceid=IN:hi"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                root = ET.fromstring(resp.read())
            for item in root.findall(".//item")[:10]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                if not title or len(title) < 15:
                    continue
                # Check duplication
                is_duplicate = False
                for p in posted_topics:
                    words = set(title.split())
                    p_words = set(p.split())
                    common = words.intersection(p_words)
                    if len(common) >= 5 or (len(words) > 0 and len(common) / len(words) > 0.45):
                        is_duplicate = True
                        break
                if not is_duplicate:
                    logger.info(f"Found Fresh Story ({sector['name']}): {title[:75]}...")
                    return {
                        "title": title,
                        "link": link,
                        "sector": sector["name"],
                        "summary": ""
                    }
        except Exception as e:
            logger.warning(f"Error fetching RSS for {sector['name']}: {e}")

    # Fallback breaking headline
    return {
        "title": "बिहार में युवाओं और छात्रों के लिए नई कल्याणकारी योजनाओं की शुरुआत",
        "link": "https://news.google.com",
        "sector": "सरकारी योजना एवं रोजगार",
        "summary": "राज्य सरकार ने युवाओं के सर्वांगीण विकास एवं कौशल निर्माण हेतु कई महत्वपूर्ण निर्णय लिए हैं।"
    }

def format_news_with_gemini(news_item: Dict[str, str]) -> Dict[str, Any]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
    You are the Chief Editor of Dainik Jagran Bihar edition and BBCC Skill Hub.
    Raw Story: {news_item['title']}
    Sector: {news_item['sector']}

    Convert this into an authentic Hindi newspaper article with the following exact JSON format:
    {{
        "headline_red": "मुख्य 4-7 शब्दों की सुर्ख़ी (Catchy Red Headline)",
        "headline_black": "बाकी 7-12 शब्दों की उप-सुर्ख़ी (Bold Black Sub-headline)",
        "lead_city": "पटना / नई दिल्ली / बिहार",
        "key_highlights": [
            "पहला मुख्य तथ्य (संख्या/तथ्य सहित)",
            "दूसरा मुख्य बिंदु (पात्रता/नियम/फायदा)",
            "तीसरा महत्वपूर्ण फैसला या दिशा-निर्देश",
            "चौथा बिंदु (अंतिम तिथि, पोर्टल या प्रक्रिया)",
            "पाँचवाँ बिंदु (अभ्यर्थियों/जनता के लिए आवश्यक निर्देश)"
        ],
        "detailed_analysis": "2-3 वाक्यों का गंभीर संपादकीय विश्लेषण और भविष्य का प्रभाव।",
        "ai_image_prompt": "A realistic documentary press photo showing authentic Indian context relating to this news, editorial news style, 8k photo, cinematic lighting"
    }}
    Return ONLY pure valid JSON, no markdown codeblocks.
    """
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:].strip()
            return json.loads(text)
    except Exception as e:
        logger.warning(f"Gemini formatting error: {e}. Using intelligent fallback.")
        words = news_item["title"].split()
        mid = min(5, len(words) // 2)
        return {
            "headline_red": " ".join(words[:mid]),
            "headline_black": " ".join(words[mid:14]),
            "lead_city": "पटना (विशेष संवाददाता)",
            "key_highlights": [
                f"{news_item['sector']} को लेकर शासन का बड़ा फैसला लागू।",
                "संबंधित विभाग द्वारा विस्तृत दिशा-निर्देश जारी किए गए।",
                "नागरिकों और अभ्यर्थियों को आधिकारिक पोर्टल से सीधे लाभ मिलेगा।",
                "पारदर्शिता और गुणवत्ता बनाए रखने के लिए सख्त निगरानी के निर्देश।",
                "अधिक जानकारी एवं सूचना हेतु संबंधित विभागीय वेबसाइट देखें।"
            ],
            "detailed_analysis": "विशेषज्ञों के अनुसार इस फैसले से राज्य के युवाओं, छात्रों एवं आम नागरिकों को बड़ा संबल मिलेगा और प्रशासनिक प्रक्रियाओं में तेजी आएगी।",
            "ai_image_prompt": f"Documentary editorial press photo of {news_item['sector']} in Bihar India, high resolution news photography"
        }

def generate_press_photo(image_prompt: str, output_path: str) -> str:
    encoded = urllib.parse.quote(f"{image_prompt}, authentic documentary editorial news photograph, 8k, realistic")
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1000&height=560&nologo=true&seed={random.randint(1000, 999999)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
        logger.info(f"AI Press Photo saved: {output_path}")
        return output_path
    except Exception as e:
        logger.warning(f"Pollinations photo error: {e}. Generating clean gradient backdrop.")
        im = Image.new("RGB", (1000, 560), "#1a365d")
        d = ImageDraw.Draw(im)
        d.text((400, 260), "दैनिक प्रेस रिपोर्ट", font=get_font(40, bold=True), fill="#ffcf58")
        im.save(output_path)
        return output_path

def draw_wrapped_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, fill: str, x: int, y: int, max_width: int, line_height: int) -> int:
    words = text.split()
    lines = []
    curr = ""
    for w in words:
        cand = (curr + " " + w).strip()
        bbox = draw.textbbox((0, 0), cand, font=font)
        if bbox[2] - bbox[0] > max_width and curr:
            lines.append(curr)
            curr = w
        else:
            curr = cand
    if curr:
        lines.append(curr)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y

def create_newspaper_poster(news_data: Dict[str, Any], photo_path: str, output_path: str) -> str:
    W, H = 1080, 1920
    im = Image.new("RGB", (W, H), "#FAF8F5")  # Authentic newspaper newsprint cream
    d = ImageDraw.Draw(im)

    # 1. Top Header Banner
    d.rectangle((0, 0, W, 100), fill="#0B2038")
    d.text((36, 22), "BBCC SKILL HUB", font=get_font(34, bold=True), fill="#FFD700")
    d.text((340, 25), "| दैनिक समाचार विशेषांक", font=get_font(28, bold=True), fill="#FFFFFF")
    d.text((36, 64), "Learn • Grow • Build Your Future | हमारे पेज राउत जी को फॉलो करें", font=get_font(18, bold=False), fill="#D1D5DB")
    # Yellow badge right
    d.rounded_rectangle((820, 20, 1044, 80), radius=10, fill="#FFD700")
    d.text((855, 34), "ताज़ा न्यूज़ आज", font=get_font(24, bold=True), fill="#000000")

    # Double rule
    d.line((0, 106, W, 106), fill="#0B2038", width=3)
    d.line((0, 112, W, 112), fill="#D1D5DB", width=1)

    # 2. Dainik Jagran Masthead
    d.ellipse((36, 126, 96, 186), fill="#EA580C")  # Rising Sun
    d.text((108, 122), "दैनिक जागरण", font=get_font(60, bold=True), fill="#111827")
    d.text((720, 142), "सत्य के साथ हर कदम", font=get_font(22, bold=False), fill="#4B5563")

    # Dateline bar
    d.line((36, 196, W - 36, 196), fill="#111827", width=2)
    ist_str = get_ist_now().strftime("%d-%m-%Y | %I:%M %p IST")
    city_str = news_data.get("lead_city", "पटना / बिहार")
    sector_str = news_data.get("sector", "विशेष रिपोर्ट")
    d.text((36, 204), f"{city_str} | {sector_str} | {ist_str} | पृष्ठ 01", font=get_font(19, bold=False), fill="#1F2937")
    d.line((36, 232, W - 36, 232), fill="#9CA3AF", width=1)

    # 3. Main Headlines
    y_pos = 248
    red_hl = news_data.get("headline_red", "").strip()
    black_hl = news_data.get("headline_black", "").strip()
    y_pos = draw_wrapped_text(d, red_hl, get_font(42, bold=True), "#DC2626", 36, y_pos, W - 72, 52)
    y_pos = draw_wrapped_text(d, black_hl, get_font(38, bold=True), "#111827", 36, y_pos + 4, W - 72, 48)

    # Sub-lead byline
    lead_line = f"{city_str} (विशेष संवाददाता) | {news_data.get('detailed_analysis', '')[:90]}..."
    d.text((36, y_pos + 8), lead_line, font=get_font(21, bold=False), fill="#374151")
    y_pos += 46

    # 4. News Photo
    photo_box_y = y_pos
    photo_h = 490
    if os.path.exists(photo_path):
        try:
            with Image.open(photo_path) as p:
                p_rgb = p.convert("RGB")
                p_resized = p_rgb.resize((W - 72, photo_h), Image.Resampling.LANCZOS)
                im.paste(p_resized, (36, photo_box_y))
        except Exception:
            d.rectangle((36, photo_box_y, W - 36, photo_box_y + photo_h), fill="#374151")
    # Photo caption overlay
    d.rectangle((42, photo_box_y + photo_h - 40, 380, photo_box_y + photo_h - 8), fill="#0B2038")
    d.text((54, photo_box_y + photo_h - 35), "विशेष रिपोर्ट • फोटो: ब्यूरो / AI प्रेस", font=get_font(18, bold=False), fill="#FFFFFF")
    d.text((W - 200, photo_box_y + photo_h - 30), "pollinations.ai", font=get_font(15, bold=False), fill="#FFFFFF")
    y_pos = photo_box_y + photo_h + 16

    # 5. Key Highlights Box (Yellow Box)
    hl_y = y_pos
    hl_h = 320
    d.rounded_rectangle((36, hl_y, W - 36, hl_y + hl_h), radius=16, fill="#FEFCE8", outline="#CA8A04", width=2)
    # Header Pill
    d.rounded_rectangle((66, hl_y - 18, 410, hl_y + 30), radius=14, fill="#DC2626")
    d.text((150, hl_y - 10), "मामले की मुख्य बातें", font=get_font(25, bold=True), fill="#FFFFFF")

    cur_hl_y = hl_y + 44
    for pt in news_data.get("key_highlights", [])[:5]:
        d.ellipse((68, cur_hl_y + 9, 82, cur_hl_y + 23), fill="#DC2626")
        draw_wrapped_text(d, pt, get_font(22, bold=True), "#1E293B", 94, cur_hl_y, W - 150, 28)
        cur_hl_y += 54
    y_pos = hl_y + hl_h + 16

    # 6. Detailed Analysis & Founder Signature
    rep_y = y_pos
    rep_h = 160
    d.rounded_rectangle((36, rep_y, W - 36, rep_y + rep_h), radius=14, fill="#FFFFFF", outline="#E2E8F0", width=2)
    d.text((58, rep_y + 12), "विस्तृत रिपोर्ट एवं मुख्य विश्लेषण", font=get_font(27, bold=True), fill="#1E293B")
    d.line((58, rep_y + 44, 380, rep_y + 44), fill="#DC2626", width=3)
    draw_wrapped_text(d, news_data.get("detailed_analysis", ""), get_font(20, bold=False), "#334155", 58, rep_y + 54, 760, 27)

    # Avatar circle right
    avatar_cx, avatar_cy = 940, rep_y + 70
    d.ellipse((avatar_cx - 48, avatar_cy - 48, avatar_cx + 48, avatar_cy + 48), fill="#0F172A", outline="#0284C7", width=3)
    d.text((avatar_cx - 30, avatar_cy - 22), "Founder", font=get_font(16, bold=True), fill="#38BDF8")
    d.text((avatar_cx - 42, avatar_cy + 4), "@rauth_jee", font=get_font(17, bold=True), fill="#F8FAFC")
    y_pos = rep_y + rep_h + 16

    # 7. Two Commercial Sponsor Advertisements Side-by-Side
    ad_w = (W - 72 - 20) // 2
    ad_y = y_pos
    ad_h = 290

    # --- Ad 1 (BBCC Skill Hub) ---
    ad1_x1 = 36
    ad1_x2 = ad1_x1 + ad_w
    d.rounded_rectangle((ad1_x1, ad_y, ad1_x2, ad_y + ad_h), radius=14, fill="#F0F7FF", outline="#2563EB", width=2)
    d.rounded_rectangle((ad1_x1 + 12, ad_y + 12, ad1_x1 + 230, ad_y + 38), radius=8, fill="#DC2626")
    d.text((ad1_x1 + 20, ad_y + 15), "विशेष विज्ञापन: BBCC SKILL HUB", font=get_font(15, bold=True), fill="#FFFFFF")
    d.text((ad1_x1 + 14, ad_y + 46), "अपने कोचिंग का रजिस्ट्रेशन करें!", font=get_font(20, bold=True), fill="#0F172A")
    d.text((ad1_x1 + 14, ad_y + 72), "अपने कोचिंग को ले जाएं 100% ऑनलाइन", font=get_font(18, bold=True), fill="#DC2626")
    draw_wrapped_text(d, "Google पर सर्च करें 'BBCC SKILL HUB' और तुरंत रजिस्ट्रेशन करें। डिजिटल क्लास, ऑनलाइन टेस्ट और स्टूडेंट मैनेजमेंट।", get_font(15, bold=False), "#334155", ad1_x1 + 14, ad_y + 98, ad_w - 28, 22)
    # Ad 1 Button
    d.rounded_rectangle((ad1_x1 + 14, ad_y + ad_h - 48, ad1_x2 - 14, ad_y + ad_h - 14), radius=8, fill="#FFD700")
    d.text((ad1_x1 + 75, ad_y + ad_h - 41), "Google सर्च: BBCC SKILL HUB", font=get_font(17, bold=True), fill="#000000")

    # --- Ad 2 (PTCC+BBCC Chakdah Chowk) ---
    ad2_x1 = ad1_x2 + 20
    ad2_x2 = W - 36
    d.rounded_rectangle((ad2_x1, ad_y, ad2_x2, ad_y + ad_h), radius=14, fill="#F0FDF4", outline="#16A34A", width=2)
    d.rounded_rectangle((ad2_x1 + 12, ad_y + 12, ad2_x1 + 230, ad_y + 38), radius=8, fill="#15803D")
    d.text((ad2_x1 + 20, ad_y + 15), "शैक्षणिक विज्ञापन: PTCC+BBCC", font=get_font(15, bold=True), fill="#FFFFFF")
    d.text((ad2_x1 + 14, ad_y + 46), "Class 1st to 10th (All Subjects)", font=get_font(20, bold=True), fill="#0F172A")
    d.text((ad2_x1 + 14, ad_y + 72), "चकदाह चौक, मधुबनी (Chakdah Chowk)", font=get_font(18, bold=True), fill="#DC2626")
    draw_wrapped_text(d, "अनुभवी शिक्षकों द्वारा सभी विषयों की संपूर्ण तैयारी। नया सत्र 2026-27 के लिए नए बैच शुरू। कमज़ोर छात्रों पर विशेष ध्यान।", get_font(15, bold=False), "#334155", ad2_x1 + 14, ad_y + 98, ad_w - 28, 22)
    # Ad 2 Button
    d.rounded_rectangle((ad2_x1 + 14, ad_y + ad_h - 48, ad2_x2 - 14, ad_y + ad_h - 14), radius=8, fill="#BBF7D0")
    d.text((ad2_x1 + 55, ad_y + ad_h - 41), "प्रवेश प्रारंभ | चकदाह चौक, मधुबनी", font=get_font(17, bold=True), fill="#166534")

    # 8. Bottom Footer Banner
    d.rectangle((0, H - 76, W, H), fill="#0B2038")
    d.text((36, H - 64), "BBCC SKILL HUB | अपने करियर और ज्ञान की सही दिशा", font=get_font(23, bold=True), fill="#FFFFFF")
    d.text((36, H - 34), "रोज़ाना ताज़ा अपडेट के लिए हमारे पेज राउत जी को फॉलो करें (@rauth_jee)", font=get_font(17, bold=False), fill="#D1D5DB")
    # Follow button
    d.rounded_rectangle((800, H - 64, 1044, H - 18), radius=10, fill="#FFD700")
    d.text((865, H - 52), "पेज राउत जी", font=get_font(21, bold=True), fill="#000000")

    im.save(output_path, quality=95)
    logger.info(f"Authentic Newspaper Poster saved: {output_path}")
    return output_path

def push_image_to_github_cdn(local_path: str, repo_path: str = "output/daily_newspaper.png") -> Optional[str]:
    import base64
    try:
        with open(local_path, "rb") as f:
            content_bytes = f.read()
        encoded = base64.b64encode(content_bytes).decode("utf-8")
        url = f"https://api.github.com/repos/{REPO}/contents/{repo_path}"
        headers = {
            "Authorization": f"token {GH_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "NewspaperBot"
        }
        sha = None
        try:
            req_get = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req_get, timeout=10) as r:
                sha = json.loads(r.read().decode()).get("sha")
        except Exception:
            pass

        payload = {"message": f"Update daily newspaper edition {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", "content": encoded, "branch": "main"}
        if sha:
            payload["sha"] = sha
        req_put = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
        with urllib.request.urlopen(req_put, timeout=25) as resp:
            data = json.loads(resp.read().decode())
            logger.info(f"Newspaper poster uploaded to GitHub CDN: commit {data.get('commit', {}).get('sha')[:8]}")
            # Raw URL with timestamp cache buster
            ts = int(time.time())
            return f"https://raw.githubusercontent.com/{REPO}/main/{repo_path}?v={ts}"
    except Exception as e:
        logger.error(f"GitHub CDN upload failed: {e}")
        return None

def publish_to_facebook_page(image_path: str, caption: str) -> Optional[str]:
    logger.info("Publishing Newspaper Photo directly to Facebook Page...")
    try:
        with open(image_path, "rb") as f:
            res = requests.post(
                f"https://graph.facebook.com/v22.0/{FB_PAGE_ID}/photos",
                data={"access_token": FB_ACCESS_TOKEN, "caption": caption},
                files={"source": f},
                timeout=60
            )
            data = res.json()
            post_id = data.get("post_id") or data.get("id")
            if post_id:
                logger.info(f"Facebook Page Photo published! Post ID: {post_id}")
                return str(post_id)
            else:
                logger.warning(f"Facebook response: {data}")
    except Exception as e:
        logger.error(f"Facebook publishing failed: {e}")
    return None

def publish_to_instagram_feed(image_url: str, caption: str) -> Optional[str]:
    logger.info("Publishing Newspaper Photo to Instagram Feed (@rauth_jee)...")
    try:
        # Step 1: Create Container
        r1 = requests.post(
            f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media",
            data={"image_url": image_url, "caption": caption, "access_token": FB_ACCESS_TOKEN},
            timeout=45
        ).json()
        cid = r1.get("id")
        if not cid:
            logger.warning(f"Instagram media creation failed: {r1}")
            return None

        # Wait 3s
        time.sleep(3)

        # Step 2: Publish
        r2 = requests.post(
            f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish",
            data={"creation_id": cid, "access_token": FB_ACCESS_TOKEN},
            timeout=45
        ).json()
        mid = r2.get("id")
        if mid:
            logger.info(f"Instagram Photo published! Media ID: {mid}")
            return str(mid)
        else:
            logger.warning(f"Instagram publish failed: {r2}")
    except Exception as e:
        logger.error(f"Instagram feed post failed: {e}")
    return None

def publish_to_instagram_story(image_url: str) -> Optional[str]:
    logger.info("Publishing Newspaper Photo to Instagram Story...")
    try:
        r1 = requests.post(
            f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media",
            data={"image_url": image_url, "media_type": "STORIES", "access_token": FB_ACCESS_TOKEN},
            timeout=45
        ).json()
        cid = r1.get("id")
        if not cid:
            return None
        time.sleep(3)
        r2 = requests.post(
            f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish",
            data={"creation_id": cid, "access_token": FB_ACCESS_TOKEN},
            timeout=45
        ).json()
        mid = r2.get("id")
        if mid:
            logger.info(f"Instagram Story published! Media ID: {mid}")
            return str(mid)
    except Exception as e:
        logger.warning(f"Story publish failed: {e}")
    return None

def auto_reply_to_instagram_comments():
    try:
        url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media?fields=id,comments{{id,text,from,timestamp}}&limit=5&access_token={FB_ACCESS_TOKEN}"
        resp = requests.get(url, timeout=20).json()
        for media in resp.get("data", []):
            for c in media.get("comments", {}).get("data", []):
                cid = c.get("id")
                user = c.get("from", {}).get("username", "")
                text = c.get("text", "")
                if user and user != "rauth_jee":
                    # Simple auto acknowledgment
                    rep_url = f"https://graph.facebook.com/v22.0/{cid}/replies"
                    msg = f"नमस्ते @{user}! ताज़ा अपडेट और शिक्षा/रोजगार समाचार के लिए हमारे पेज को फॉलो करें। BBCC SKILL HUB में स्वागत है!"
                    requests.post(rep_url, data={"message": msg, "access_token": FB_ACCESS_TOKEN}, timeout=15)
                    logger.info(f"Auto-replied to comment by @{user}")
    except Exception:
        pass

def run_newspaper_pipeline():
    logger.info("================================================================================")
    logger.info(f"STARTING NEWSPAPER PHOTO PIPELINE (10-MIN CYCLE) FOR {CREATOR_HANDLE}")
    logger.info("================================================================================")

    # 1. Fetch fresh unposted news
    news_item = fetch_unique_live_news()
    if not news_item:
        logger.error("No news found. Aborting cycle.")
        return

    # 2. Structure news with Gemini
    formatted = format_news_with_gemini(news_item)
    save_posted_topic(news_item["title"])
    save_posted_topic(f"{formatted.get('headline_red')} {formatted.get('headline_black')}")

    # 3. Generate 8K press photo
    photo_file = str(OUTPUT_DIR / "temp_press_photo.jpg")
    generate_press_photo(formatted.get("ai_image_prompt", "Bihar news photo"), photo_file)

    # 4. Render 1080x1920 Authentic Newspaper Poster
    poster_file = str(OUTPUT_DIR / "daily_newspaper.png")
    create_newspaper_poster(formatted, photo_file, poster_file)

    # 5. Caption Generation
    caption = f"""📰 दैनिक जागरण & BBCC Skill Hub विशेषांक 📰

🔴 {formatted.get('headline_red')}
⚫ {formatted.get('headline_black')}

📍 {formatted.get('lead_city', 'पटना / बिहार')}

📌 मामले की मुख्य बातें:
• {formatted.get('key_highlights', [''])[0]}
• {formatted.get('key_highlights', ['',''])[1]}
• {formatted.get('key_highlights', ['','',''])[2]}

📢 विशेष विज्ञापन (BBCC SKILL HUB):
अपने कोचिंग का रजिस्ट्रेशन करें और 100% ऑनलाइन ले जाएं! Google पर सर्च करें 'BBCC SKILL HUB' और तुरंत रजिस्टर करें।

🎓 शैक्षणिक विज्ञापन (PTCC+BBCC):
Class 1st to 10th (All Subjects) - चकदाह चौक, मधुबनी (Chakdah Chowk) में नए सत्र के लिए प्रवेश प्रारंभ!

👤 हमारे पेज {CREATOR_HANDLE} को फॉलो करें और रोज़ाना सबसे पहले ताज़ा न्यूज़ अपडेट प्राप्त करें।

#BBCCSkillHub #rauth_jee #DainikJagran #BiharNews #SarkariNaukri #Education #BiharJobs #PatnaNews #Madhubani"""

    # 6. Upload Poster to GitHub CDN for Meta Instagram Access
    public_url = push_image_to_github_cdn(poster_file)

    # 7. Publish to Facebook Page (Direct upload)
    fb_id = publish_to_facebook_page(poster_file, caption)

    # 8. Publish to Instagram Feed
    ig_id = None
    if public_url:
        ig_id = publish_to_instagram_feed(public_url, caption)
    else:
        logger.error("Could not obtain public URL for Instagram feed post.")

    # 9. Story Publish (Max 6 times/24h)
    story_id = None
    if should_publish_story() and public_url:
        story_id = publish_to_instagram_story(public_url)
        if story_id:
            record_story_published()
    else:
        logger.info("Story skipped (respecting 6x daily limit).")

    # 10. Auto-reply to comments
    auto_reply_to_instagram_comments()

    logger.info("================================================================================")
    logger.info("NEWSPAPER PHOTO PIPELINE COMPLETE")
    logger.info(f"Facebook Post:  {'SUCCESS (ID: ' + fb_id + ')' if fb_id else 'FAILED'}")
    logger.info(f"Instagram Post: {'SUCCESS (ID: ' + ig_id + ')' if ig_id else 'FAILED'}")
    logger.info(f"Story Post:     {'SUCCESS (ID: ' + story_id + ')' if story_id else 'SKIPPED/LIMIT'}")
    logger.info("================================================================================")

def main():
    logger.info("================================================================================")
    logger.info("BBCC SKILL HUB - 10-MINUTE CONTINUOUS NEWSPAPER PHOTO BOT STARTED")
    logger.info("Window: 06:00 AM - 06:00 PM IST | Every 10 Minutes | Photo Only Mode")
    logger.info("================================================================================")

    while True:
        ist = get_ist_now()
        time_str = ist.strftime("%I:%M:%S %p IST")

        if is_within_publishing_hours():
            logger.info(f"Publishing hours active ({time_str}). Executing 10-minute newspaper run...")
            try:
                run_newspaper_pipeline()
            except Exception as e:
                logger.error(f"Pipeline error: {e}", exc_info=True)
        else:
            logger.info(f"Outside publishing hours ({time_str}). Sleeping cleanly until morning.")

        logger.info("Sleeping for 10 minutes (600 seconds)...")
        time.sleep(600)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_newspaper_pipeline()
    else:
        main()
