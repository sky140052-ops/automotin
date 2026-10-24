#!/usr/bin/env python3
"""
================================================================================
Dainik Jagran / BBCC Skill Hub Style Hindi News Automation Engine
Creator: @rauth_jee (RAUTH JEE NEWS & SKILL HUB)
Automated 3x Daily Multi-Format Engine:
1. Live Google News Ingestion (Bihar, Education, Jobs, National, International)
2. Newspaper Clipping Poster (1080x1920, Exact Dainik Jagran / BBCC Hub Style)
   - Top Navy Bar: RAUTH JEE SKILL & NEWS HUB + Latest News Today
   - Masthead: Dainik Jagran + Date/Place + Slogan
   - Big Red & Black Breaking Headline
   - The Famous Yellow Highlight Box ("मामले की मुख्य बातें")
   - Detailed Story Box & Circular Founder Avatar (@rauth_jee)
   - Bottom Navy Footer: Follow @rauth_jee
3. Viral 3D Breaking News Reel (News Anchor Voiceover + Kinetic Subtitles + Beat)
4. Instagram Multi-Format Publisher (Feed Post + Story + Reel)
5. Facebook Page Auto-Publisher (Direct Graph API + Make.com Mirror)
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
import shutil
import datetime
import subprocess
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
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
logger = logging.getLogger("HindiNewsBot")

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
CREATOR_HANDLE = os.getenv("CREATOR_HANDLE", "@rauth_jee").strip()
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

VIRAL_HASHTAGS = [
    "#rauth_jee", "#BiharNews", "#BPSCTRE4", "#BiharEducation", "#DainikJagran",
    "#SarkariNaukri", "#HindiNews", "#BreakingNewsHindi", "#DigitalIndia",
    "#TrendingReels", "#NewsReels", "#ViralNews"
]

FALLBACK_NEWS_DATABASE = [
    {
        "newspaper_title": "दैनिक जागरण",
        "tagline": "सत्य के साथ हर कदम",
        "dateline": "पटना / बिहार | ताज़ा अपडेट / पृष्ठ 01",
        "headline_red": "टीआरआई-4: बिहार में 32,388 शिक्षक पदों की",
        "headline_black": "बड़ी भर्ती का नोटिफिकेशन जारी, आवेदन जल्द शुरू",
        "lead_city": "पटना",
        "lead_summary": "बिहार लोक सेवा आयोग (BPSC) ने चौथे चरण की बहुप्रतीक्षित शिक्षक नियुक्ति प्रक्रिया (TRE-4) के लिए आधिकारिक अधिसूचना जारी कर दी है, जिससे लाखों शिक्षक अभ्यर्थियों में खुशी का माहौल है।",
        "key_highlights": [
            "प्राथमिक और माध्यमिक स्कूलों में कुल 32,388 पदों पर होगी बंपर बहाली।",
            "सीटेट (CTET) और बीटेट (BTET) उत्तीर्ण अभ्यर्थियों को ही मिलेगा आवेदन का मौका।",
            "सामान्य वर्ग के लिए अधिकतम आयु सीमा 37 वर्ष निर्धारित की गई है।",
            "परीक्षा में पारदर्शिता हेतु आधुनिक बायोमेट्रिक व AI तकनीक का होगा उपयोग।",
            "अभ्यर्थी आधिकारिक वेबसाइट bpsc.bih.nic.in से कर सकेंगे ऑनलाइन आवेदन।"
        ],
        "detailed_report": [
            "शिक्षा विभाग के अनुसार चौथे चरण की इस बहाली में आरक्षण नियमों का पूरी तरह",
            "पालन किया जाएगा। सभी जिलों से रिक्तियों का रोस्टर क्लियरेंस पूरा हो चुका है।",
            "",
            "गौरतलब है कि पिछले तीन चरणों (TRE-1, TRE-2 और TRE-3) में रिकॉर्ड संख्या में",
            "शिक्षकों की नियुक्ति हुई है। नए दिशा-निर्देशों से योग्य अभ्यर्थियों को सीधा लाभ मिलेगा।",
            "",
            "आयोग ने अभ्यर्थियों से अपील की है कि वे आवेदन से पूर्व सभी शैक्षणिक प्रमाण पत्रों",
            "को तैयार रखें तथा केवल आधिकारिक वेबसाइट की सूचना पर ही विश्वास करें।"
        ],
        "reel_script": "ब्रेकिंग न्यूज़! बिहार में चौथे चरण की शिक्षक भर्ती का आधिकारिक नोटिफिकेशन जारी हो चुका है! कुल 32,388 पदों पर प्राथमिक और माध्यमिक शिक्षकों की बंपर बहाली होगी। पूरी रिपोर्ट और मुख्य बातें जानने के लिए पोस्ट पढ़ें और रोज़ाना ताज़ा न्यूज़ के लिए अभी फॉलो करें @rauth_jee को!",
        "reel_phrases": [
            {"hook": "🚨 ब्रेकिंग न्यूज़!", "white": "बिहार शिक्षक भर्ती (TRE-4)", "punch": "32,388 पदों पर बंपर बहाली!"},
            {"hook": "📢 BPSC का बड़ा फैसला", "white": "प्राथमिक व माध्यमिक स्तर पर", "punch": "नोटिफिकेशन जारी!"},
            {"hook": "📌 मुख्य पात्रता", "white": "CTET / BTET पास अभ्यर्थी", "punch": "ही होंगे योग्य!"},
            {"hook": "⚡ ज़रूरी जानकारी", "white": "अधिकतम आयु सीमा 37 साल", "punch": "आवेदन जल्द शुरू!"},
            {"hook": "📰 हर दिन ताज़ा न्यूज़ के लिए", "white": "अभी फॉलो करें", "punch": "@rauth_jee"}
        ],
        "caption": "📢 दैनिक जागरण ब्रेकिंग: बिहार शिक्षक बहाली (TRE-4) पर बड़ा फैसला!\n\nशिक्षा विभाग और BPSC ने 32,388 पदों पर भर्ती का रास्ता साफ़ कर दिया है।\n\n📌 मुख्य बातें:\n• CTET / BTET उत्तीर्ण अभ्यर्थियों को अवसर\n• सामान्य वर्ग आयु सीमा: 37 वर्ष\n• ऑनलाइन आवेदन जल्द शुरू होंगे\n\nअपने दोस्तों के साथ शेयर करें और रोज़ाना ताज़ा अख़बार अपडेट्स के लिए फॉलो करें: @rauth_jee"
    },
    {
        "newspaper_title": "दैनिक भास्कर",
        "tagline": "सत्यमेव जयते",
        "dateline": "नई दिल्ली / भारत | ताज़ा अपडेट / राष्ट्रीय संस्करण",
        "headline_red": "डिजिटल अरेस्ट और साइबर फ्रॉड पर केंद्र सख्त",
        "headline_black": "गृह मंत्रालय ने जारी की नई गाइडलाइन, तुरंत ब्लॉक होंगे खाते",
        "lead_city": "नई दिल्ली",
        "lead_summary": "देश भर में बढ़ते डिजिटल अरेस्ट और ऑनलाइन फ्रॉड के मामलों को देखते हुए गृह मंत्रालय (MHA) और साइबर विंग ने कड़ा रुख अपनाया है और संदिग्ध नंबरों और खातों पर तुरंत कार्रवाई के आदेश दिए हैं।",
        "key_highlights": [
            "कोई भी पुलिस, CBI या कोर्ट वीडियो कॉल पर कभी 'डिजिटल अरेस्ट' नहीं करती।",
            "गृह मंत्रालय की नेशनल साइबर हेल्पलाइन 1930 को 24 घंटे एक्टिव किया गया।",
            "संदिग्ध बैंक खातों को शिकायत मिलते ही 15 मिनट में फ्रीज़ करने के निर्देश।",
            "फर्जी पार्सल या मनी लॉन्ड्रिंग के नाम पर आए किसी भी अनजान कॉल पर पैसे न भेजें।",
            "नागरिक तुरंत cybercrime.gov.in पर रिपोर्ट दर्ज करा सकते हैं।"
        ],
        "detailed_report": [
            "केंद्रीय गृह मंत्रालय ने स्पष्ट किया है कि भारत के कानून में 'डिजिटल अरेस्ट' नाम का",
            "कोई प्रावधान नहीं है। अपराधी पुलिस या जज बनकर लोगों को डरा रहे हैं।",
            "",
            "बैंकिंग एजेंसियों और टेलीकॉम कंपनियों के साथ मिलकर 3 लाख से अधिक सिम कार्ड",
            "और संदिग्ध खातों को अब तक ब्लॉक किया जा चुका है।",
            "",
            "साइबर एक्सपर्ट्स की सलाह है कि घबराने की बजाय तुरंत 1930 पर कॉल करें।"
        ],
        "reel_script": "सावधान! गृह मंत्रालय ने डिजिटल अरेस्ट और ऑनलाइन फ्रॉड पर बड़ी चेतावनी जारी की है! पुलिस या जज कभी भी वीडियो कॉल पर डिजिटल अरेस्ट नहीं करते। फ्रॉड होने पर तुरंत 1930 पर कॉल करें। सुरक्षित रहने के लिए अभी फॉलो करें @rauth_jee को!",
        "reel_phrases": [
            {"hook": "🚨 सावधान इंडिया!", "white": "डिजिटल अरेस्ट के नाम पर", "punch": "हैकर्स का नया जाल!"},
            {"hook": "❌ बड़ा सच", "white": "कानून में डिजिटल अरेस्ट", "punch": "जैसा कुछ भी नहीं होता!"},
            {"hook": "⚠️ तुरंत क्या करें?", "white": "साइबर फ्रॉड होते ही", "punch": "तुरंत 1930 पर कॉल करें!"},
            {"hook": "⚡ शेयर करें", "white": "अपने सभी दोस्तों और", "punch": "परिवार को बचाएं!"},
            {"hook": "📰 सुरक्षित रहने के लिए", "white": "अभी फॉलो करें", "punch": "@rauth_jee"}
        ],
        "caption": "⚠️ सावधान: गृह मंत्रालय का बड़ा अलर्ट — 'डिजिटल अरेस्ट' से बचें!\n\nठग पुलिस या कस्टम अधिकारी बनकर लोगों को लाखों का चूना लगा रहे हैं।\n\nयाद रखें:\n1. कोई भी कानून वीडियो कॉल पर अरेस्ट नहीं करता\n2. अनजान कॉल पर पैसे कभी न भेजें\n3. तुरंत 1930 पर रिपोर्ट करें\n\n🛡️ रोज़ाना ज़रूरी जानकारियों के लिए फॉलो करें: @rauth_jee"
    }
]

# ==============================================================================
# 1. LIVE GOOGLE NEWS RSS FETCHER
# ==============================================================================

def fetch_live_google_news() -> Optional[Dict[str, str]]:
    """Fetches real-time trending Hindi news from Google News RSS."""
    logger.info("📡 Fetching real-time breaking news from Google News RSS...")
    
    # Select topics based on time of day
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        # Morning: Bihar Education, Jobs, BPSC
        query = urllib.parse.quote("बिहार शिक्षक भर्ती परीक्षा नौकरी")
        url = f"https://news.google.com/rss/search?q={query}&hl=hi&gl=IN&ceid=IN:hi"
        domain_label = "बिहार शिक्षा व भर्ती"
    elif 12 <= hour < 18:
        # Afternoon: National India Headlines
        url = "https://news.google.com/rss/headlines/section/topic/NATION?hl=hi&gl=IN&ceid=IN:hi"
        domain_label = "राष्ट्रीय समाचार"
    else:
        # Evening: National & International
        url = "https://news.google.com/rss/headlines/section/topic/WORLD?hl=hi&gl=IN&ceid=IN:hi"
        domain_label = "देश-विदेश ब्रेकिंग"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = root.findall(".//item")
        if items:
            top_item = items[0]
            title = top_item.find("title").text or ""
            desc = top_item.find("description").text if top_item.find("description") is not None else ""
            pub_date = top_item.find("pubDate").text if top_item.find("pubDate") is not None else ""
            logger.info(f"✅ Live News Fetched ({domain_label}): {title}")
            return {
                "title": title,
                "desc": desc,
                "pub_date": pub_date,
                "domain": domain_label
            }
    except Exception as e:
        logger.warning(f"Google News RSS notice: {e}")
    return None

def format_news_with_gemini(raw_news: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """Formats live news into authentic Dainik Jagran / BBCC Skill Hub layout using Gemini."""
    logger.info("🤖 Formatting News into Dainik Jagran Newspaper Layout...")
    
    if not GEMINI_API_KEY or "your_gemini" in GEMINI_API_KEY.lower():
        return random.choice(FALLBACK_NEWS_DATABASE)

    news_context = ""
    if raw_news:
        news_context = f"Live Headline: {raw_news.get('title')}\nDetails: {raw_news.get('desc')}\nCategory: {raw_news.get('domain')}"
    else:
        news_context = "Top Breaking News about Bihar Education, Jobs, or National Policy."

    prompt = f"""
You are an expert Chief Editor at a leading Hindi Daily Newspaper (Dainik Jagran / Bhaskar).
Transform this news story into an authentic, highly engaging Hindi Newspaper Clipping infographic (like BBCC SKILL HUB format):

{news_context}

Return ONLY a valid JSON object with these EXACT keys:
{{
  "newspaper_title": "दैनिक जागरण",
  "tagline": "सत्य के साथ हर कदम",
  "dateline": "पटना / बिहार | ताज़ा अपडेट / पृष्ठ 01",
  "headline_red": "Catchy Red Headline Line 1 under 6 words in pure Devanagari Hindi (e.g. 'टीआरआई-4: बिहार में शिक्षक पदों पर')",
  "headline_black": "Black Headline Line 2 under 6 words in pure Devanagari Hindi (e.g. 'बड़ी भर्ती का नोटिफिकेशन जारी')",
  "lead_city": "पटना",
  "lead_summary": "1 to 2 clear, formal sentences summarizing the news in Hindi newspaper tone.",
  "key_highlights": [
    "First crucial fact or decision in 10-15 Hindi words.",
    "Second crucial rule or eligibility detail.",
    "Third crucial date, quota, or government provision.",
    "Fourth crucial point for students or public.",
    "Fifth crucial point regarding official website or procedure."
  ],
  "detailed_report": [
    "Paragraph 1 providing full background context and official statement (under 25 words).",
    "",
    "Paragraph 2 highlighting the impact and future steps (under 25 words).",
    "",
    "Paragraph 3 giving advisory to candidates or readers (under 25 words)."
  ],
  "reel_script": "High-energy, authoritative News Anchor voiceover in pure Hindi under 30 words (takes 9-11 seconds of speech). Must start with 'ब्रेकिंग न्यूज़!' and end with 'रोज़ाना ताज़ा न्यूज़ के लिए फॉलो करें @rauth_jee को!'",
  "reel_phrases": [
    {{"hook": "🚨 ब्रेकिंग न्यूज़!", "white": "यहाँ खबर का मुख्य विषय", "punch": "बड़ा फैसला जारी!"}},
    {{"hook": "📢 नया अपडेट", "white": "यहाँ नियम या भर्ती की बात", "punch": "लाखों लोगों को फायदा!"}},
    {{"hook": "📌 मुख्य बातें", "white": "यहाँ मुख्य शर्त या तारीख", "punch": "आधिकारिक आदेश जारी!"}},
    {{"hook": "⚡ ज़रूरी जानकारी", "white": "यहाँ कार्रवाई या पात्रता", "punch": "तुरंत चेक करें!"}},
    {{"hook": "📰 हर दिन ताज़ा न्यूज़ के लिए", "white": "अभी फॉलो करें", "punch": "@rauth_jee"}}
  ],
  "caption": "Detailed Instagram caption in Hindi with newspaper style headlines, bullet points, hashtags, and call to action."
}}
"""
    raw_text = ""
    for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            res = client.models.generate_content(model=model_name, contents=prompt)
            raw_text = res.text or ""
            if raw_text:
                logger.info(f"✅ Formatted news with {model_name}.")
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
        return random.choice(FALLBACK_NEWS_DATABASE)

    try:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"): cleaned = cleaned[7:]
        if cleaned.startswith("```"): cleaned = cleaned[3:]
        if cleaned.endswith("```"): cleaned = cleaned[:-3]
        data = json.loads(cleaned.strip())
        data["hashtags"] = VIRAL_HASHTAGS
        return data
    except Exception as e:
        logger.warning(f"JSON parse error: {e}. Using fallback database.")
        return random.choice(FALLBACK_NEWS_DATABASE)

# ==============================================================================
# 2. NEWSPAPER CLIPPING POSTER ENGINE (BBCC SKILL HUB / DAINIK JAGRAN STYLE)
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

def wrap_text_lines(text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
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

def create_newspaper_graphic(
    news_data: Dict[str, Any],
    output_path: str = "output/daily_tip.png",
    face_path: str = "assets/my_face.jpg"
) -> str:
    """
    Renders 1080x1920 Full HD Hindi Newspaper Infographic:
    - Top Navy Blue Banner: RAUTH JEE SKILL & NEWS HUB + Latest News Today
    - Masthead: Dainik Jagran + Date/Place + Slogan
    - Big Bold Red & Black Headline
    - Signature Yellow Highlights Box ("मामले की मुख्य बातें") with Red Bullets
    - Detailed Story Card + Founder Avatar (@rauth_jee)
    - Bottom Navy Footer
    """
    logger.info("🎨 Rendering 1080x1920 Dainik Jagran / BBCC Hub Style Newspaper Poster...")
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), (248, 249, 250)) # warm off-white newsprint background
    draw = ImageDraw.Draw(img)

    # Fonts
    font_masthead = get_devanagari_font(62, bold=True)
    font_bold_xl = get_devanagari_font(44, bold=True)
    font_bold_lg = get_devanagari_font(34, bold=True)
    font_bold_md = get_devanagari_font(26, bold=True)
    font_reg_md = get_devanagari_font(24, bold=False)
    font_reg_sm = get_devanagari_font(20, bold=False)

    # 1. TOP NAVY BLUE BAR (BBCC SKILL HUB STYLE)
    draw.rectangle([(0, 0), (w, 110)], fill=(10, 37, 64))
    draw.text((40, 22), "RAUTH JEE", font=get_devanagari_font(38, bold=True), fill=(255, 222, 3))
    draw.text((250, 30), "SKILL & NEWS HUB", font=font_bold_md, fill=(255, 255, 255))
    draw.text((40, 72), "Learn • Grow • Build Your Future", font=font_reg_sm, fill=(203, 213, 225))
    # Right Yellow Badge
    draw.rounded_rectangle([w - 290, 22, w - 40, 85], radius=15, fill=(255, 222, 3))
    draw.text((w - 165, 53), "Latest News Today", font=font_bold_md, fill=(10, 37, 64), anchor="mm")

    # 2. NEWSPAPER MASTHEAD (DAINIK JAGRAN STYLE)
    paper_title = news_data.get("newspaper_title", "दैनिक जागरण")
    tagline = news_data.get("tagline", "सत्य के साथ हर कदम")
    # Sun rays icon
    draw.ellipse([45, 140, 105, 200], fill=(245, 158, 11))
    draw.text((120, 130), paper_title, font=font_masthead, fill=(15, 23, 42))
    draw.text((w - 270, 155), tagline, font=font_reg_sm, fill=(100, 116, 139))
    draw.line([(40, 210), (w - 40, 210)], fill=(203, 213, 225), width=2)

    # Dateline divider
    dateline = news_data.get("dateline", "पटना / बिहार | ताज़ा अपडेट / पृष्ठ 01")
    draw.text((50, 222), dateline, font=font_reg_sm, fill=(71, 85, 105))
    draw.line([(40, 255), (w - 40, 255)], fill=(203, 213, 225), width=2)

    # 3. BREAKING HEADLINE (Line 1 Red, Line 2 Black)
    hl_red = news_data.get("headline_red", "बड़ी खबर: शिक्षा विभाग का नया फैसला")
    hl_black = news_data.get("headline_black", "अभ्यर्थियों को मिला बड़ा अवसर, आदेश जारी")
    draw.text((40, 280), hl_red, font=font_bold_xl, fill=(220, 38, 38))
    draw.text((40, 345), hl_black, font=font_bold_xl, fill=(15, 23, 42))

    # 4. LEAD SUBTITLE
    lead_city = news_data.get("lead_city", "पटना")
    lead_summary = news_data.get("lead_summary", "शिक्षा विभाग ने आगामी भर्ती को लेकर विस्तृत दिशा-निर्देश जारी किए हैं।")
    draw.text((40, 425), f"{lead_city} | ", font=font_bold_md, fill=(15, 23, 42))
    lead_lines = wrap_text_lines(lead_summary, font_reg_md, w - 180)
    if lead_lines:
        draw.text((130, 425), lead_lines[0], font=font_reg_md, fill=(51, 65, 85))
        if len(lead_lines) > 1:
            draw.text((40, 465), lead_lines[1], font=font_reg_md, fill=(51, 65, 85))

    # 5. THE SIGNATURE YELLOW HIGHLIGHTS BOX ("मामले की मुख्य बातें")
    box_y = 530
    box_h = 440
    draw.rounded_rectangle([40, box_y, w - 40, box_y + box_h], radius=20, fill=(254, 249, 195), outline=(234, 179, 8), width=3)
    # Red Pill
    draw.rounded_rectangle([70, box_y + 20, 400, box_y + 75], radius=25, fill=(220, 38, 38))
    draw.text((235, box_y + 47), "📌 मामले की मुख्य बातें", font=font_bold_md, fill=(255, 255, 255), anchor="mm")

    points = news_data.get("key_highlights", [
        "विभाग ने सभी प्रक्रियाओं को पूरी तरह स्पष्ट किया।",
        "योग्य अभ्यर्थियों को निर्धारित पोर्टल से आवेदन करने का अवसर।",
        "सभी आवश्यक दिशा-निर्देश आधिकारिक वेबसाइट पर अपलोड।",
        "नियमों के तहत पारदर्शिता बनाए रखने के कड़े प्रबंध।",
        "रोज़ाना नई जानकारी के लिए जुड़े रहें।"
    ])
    py = box_y + 105
    for pt in points[:5]:
        draw.ellipse([(75, py + 8), (89, py + 22)], fill=(220, 38, 38))
        draw.text((105, py), pt, font=font_bold_md, fill=(15, 23, 42))
        py += 62

    # 6. DETAILED STORY CARD & FOUNDER AVATAR
    card_y = 1010
    card_h = 730
    draw.rounded_rectangle([40, card_y, w - 40, card_y + card_h], radius=20, fill=(255, 255, 255), outline=(226, 232, 240), width=2)
    draw.text((70, card_y + 30), "विस्तृत रिपोर्ट और विश्लेषण", font=font_bold_lg, fill=(15, 23, 42))
    draw.line([(70, card_y + 85), (370, card_y + 85)], fill=(220, 38, 38), width=4)

    # Embed Founder Face
    if os.path.exists(face_path):
        try:
            fimg = Image.open(face_path).convert("RGBA").resize((130, 130), Image.Resampling.LANCZOS)
            mask = Image.new("L", (130, 130), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 130, 130), fill=255)
            img.paste(fimg, (w - 220, card_y + 30), mask)
            draw.ellipse((w - 224, card_y + 26, w - 86, card_y + 164), outline=(10, 37, 64), width=3)
            draw.text((w - 155, card_y + 175), CREATOR_HANDLE, font=font_bold_md, fill=(10, 37, 64), anchor="mm")
        except Exception:
            pass

    body_list = news_data.get("detailed_report", [
        "संबंधित विभाग ने आगामी चरणों के लिए पूरी रूपरेखा तैयार कर ली है।",
        "सभी जिलों से रोस्टर और पदों की गणना पूरी होने के बाद आगे की कार्रवाई शुरू होगी।",
        "",
        "अभ्यर्थियों को सलाह दी गई है कि वे किसी भी अनाधिकृत स्रोत पर विश्वास न करें",
        "और समय-समय पर विभागीय पोर्टल को चेक करते रहें।"
    ])
    by = card_y + 115
    for line in body_list:
        if line:
            wrapped = wrap_text_lines(line, font_reg_md, w - 320)
            for wl in wrapped:
                draw.text((70, by), wl, font=font_reg_md, fill=(51, 65, 85))
                by += 44
        else:
            by += 20

    # 7. BOTTOM NAVY FOOTER
    draw.rectangle([(0, h - 120), (w, h)], fill=(10, 37, 64))
    draw.text((40, h - 85), f"RAUTH JEE HUB | अपने करियर की सही दिशा", font=font_bold_md, fill=(255, 255, 255))
    draw.text((40, h - 45), f"रोज़ाना ताज़ा अपडेट के लिए फॉलो करें: {CREATOR_HANDLE}", font=font_reg_sm, fill=(203, 213, 225))
    draw.rounded_rectangle([w - 320, h - 95, w - 40, h - 35], radius=15, fill=(255, 222, 3))
    draw.text((w - 180, h - 65), f"Follow {CREATOR_HANDLE}", font=get_devanagari_font(22, bold=True), fill=(10, 37, 64), anchor="mm")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    logger.info(f"✅ Dainik Jagran style newspaper poster saved: {output_path}")
    return output_path

# ==============================================================================
# 3. VIRAL 3D NEWS REEL ENGINE (BREAKING NEWS ANCHOR VOICEOVER + MUSIC)
# ==============================================================================

def get_ffmpeg_binary() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def generate_voiceover_audio(text: str, output_path: str = "output/voiceover.mp3") -> tuple[str, float]:
    """Generates realistic Hindi news anchor voiceover."""
    logger.info("🎙️ Generating Hindi News Anchor Neural Voiceover...")
    from gtts import gTTS
    raw_tts = "output/raw_tts.mp3"
    tts = gTTS(text=text, lang="hi", slow=False)
    tts.save(raw_tts)

    ffmpeg = get_ffmpeg_binary()
    is_male = random.choice([True, False])
    gender_label = "Male" if is_male else "Female"
    logger.info(f"🎭 News Anchor Voice: {gender_label} Hindi Neural")

    if is_male:
        pitch_filter = "asetrate=44100*0.88,aresample=44100,atempo=1.14"
    else:
        pitch_filter = "asetrate=44100*1.12,aresample=44100,atempo=0.90"

    cmd = [ffmpeg, "-y", "-i", raw_tts, "-af", pitch_filter, output_path]
    subprocess.run(cmd, capture_output=True)

    probe = subprocess.run([ffmpeg, "-i", output_path], capture_output=True, text=True)
    duration = 10.0
    for line in probe.stderr.splitlines():
        if "Duration" in line:
            try:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
            except Exception:
                pass
    duration = max(8.0, min(duration, 15.0))
    logger.info(f"🎙️ News Voiceover duration: {duration:.2f}s")
    return output_path, duration

def generate_news_synth_music(music_path: str = "assets/music.wav", duration: float = 12.0) -> str:
    if os.path.exists(music_path) and os.path.getsize(music_path) > 10000:
        return music_path
    os.makedirs(os.path.dirname(music_path), exist_ok=True)
    sr = 44100
    ns = int(sr * duration)
    bpm = 126
    bl = sr * 60 / bpm
    notes = [130.81, 155.56, 174.61, 196.00, 233.08, 261.63, 293.66, 349.23]
    with wave.open(music_path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = bytearray()
        for i in range(ns):
            t = i / sr
            bp = (i % int(bl)) / bl
            kick = math.sin(2 * math.pi * (160 * math.exp(-bp * 16) + 42) * t) * math.exp(-bp * 9) if bp < 0.5 else 0
            bass = 0.5 * math.sin(2 * math.pi * 65.41 * t)
            step = int(i // (bl / 4)) % len(notes)
            arp = math.sin(2 * math.pi * notes[step] * t) * math.exp(-((i % int(bl / 4)) / (bl / 4)) * 6) * 0.35
            s = max(-32767, min(32767, int((kick * 0.7 + bass * 0.5 + arp * 0.4) * 22000)))
            frames.extend(struct.pack("<hh", s, s))
        wf.writeframes(frames)
    return music_path

def create_news_reel_video(
    news_data: Dict[str, Any],
    newspaper_img_path: str = "output/daily_tip.png",
    face_path: str = "assets/my_face.jpg",
    output_video_path: str = "output/daily_reel.mp4"
) -> Optional[str]:
    """
    Renders breaking news video reel with Ken Burns zoom over the newspaper graphic,
    pop-up highlighted subtitle cards (Bold Yellow & White), news ticker, and anchor audio.
    """
    logger.info("🎬 Rendering Breaking News Video Reel MP4...")
    ffmpeg = get_ffmpeg_binary()

    # 1. Voiceover
    voice_script = news_data.get("reel_script")
    if not voice_script:
        voice_script = f"ब्रेकिंग न्यूज़! {news_data.get('headline_red', '')} {news_data.get('headline_black', '')}। पूरी जानकारी के लिए पोस्ट पढ़ें और फॉलो करें {CREATOR_HANDLE} को।"
    voice_path, duration = generate_voiceover_audio(voice_script, "output/voiceover.mp3")

    # 2. Mix Voiceover + News Synth Music
    music_path = generate_news_synth_music("assets/music.wav", duration=float(duration + 2.0))
    mixed_audio = "output/final_audio.aac"
    mix_cmd = [
        ffmpeg, "-y",
        "-i", voice_path,
        "-i", music_path,
        "-filter_complex", "[0:a]volume=2.4[a0];[1:a]volume=0.18[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[outa]",
        "-map", "[outa]",
        "-c:a", "aac",
        mixed_audio
    ]
    subprocess.run(mix_cmd, capture_output=True)

    # 3. Subtitles
    phrases = news_data.get("reel_phrases")
    if not phrases or not isinstance(phrases, list):
        phrases = [
            {"hook": "🚨 ब्रेकिंग न्यूज़!", "white": news_data.get("headline_red", "बड़ा फैसला"), "punch": news_data.get("headline_black", "आधिकारिक आदेश जारी!")},
            {"hook": "📢 नया अपडेट", "white": news_data.get("lead_summary", "लाखों अभ्यर्थियों को राहत"), "punch": "पूरी रिपोर्ट जारी!"},
            {"hook": "📌 मुख्य बातें", "white": "पात्रता और आवेदन की शर्तें", "punch": "विभागीय पोर्टल पर उपलब्ध!"},
            {"hook": "📰 हर दिन ताज़ा न्यूज़ के लिए", "white": "अभी फॉलो करें", "punch": CREATOR_HANDLE}
        ]

    # 4. Generate Animated Video Frames (24 FPS)
    fps = 24
    total_frames = int(duration * fps)
    w, h = 1080, 1920

    base_paper = Image.open(newspaper_img_path).convert("RGB")
    font_bold_lg = get_devanagari_font(52, bold=True)
    font_bold_md = get_devanagari_font(42, bold=True)
    font_sub = get_devanagari_font(24, bold=False)

    frames_dir = "output/reel_frames"
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    logger.info(f"🎞️ Rendering {total_frames} news reel frames ({duration:.1f}s @ {fps}fps)...")
    t_start = time.time()

    for idx in range(total_frames):
        t = idx / fps
        progress = t / duration
        phrase_idx = min(int(progress * len(phrases)), len(phrases) - 1)
        p_data = phrases[phrase_idx]

        # Subtle Ken Burns zoom effect on newspaper
        zoom = 1.0 + 0.05 * progress
        zw, zh = int(w * zoom), int(h * zoom)
        crop_x = (zw - w) // 2
        crop_y = int((zh - h) * 0.3 * progress)
        resized = base_paper.resize((zw, zh), Image.Resampling.BILINEAR)
        frame = resized.crop((crop_x, crop_y, crop_x + w, crop_y + h))
        draw = ImageDraw.Draw(frame)

        # Top Neon Red/Yellow Progress Bar
        draw.rectangle([(0, 0), (int(w * progress), 12)], fill=(220, 38, 38))

        # Breaking News Pop-Up Subtitle Card (Yellow & White Highlight)
        card_y = 750
        draw.rounded_rectangle([60, card_y, w - 60, card_y + 350], radius=30, fill=(10, 37, 64), outline=(255, 222, 3), width=4)

        # Line 1: Hook (Yellow #FFE600)
        draw.text((w // 2 + 2, card_y + 68), p_data.get("hook", "🚨 ब्रेकिंग न्यूज़!"), font=font_bold_lg, fill=(0, 0, 0), anchor="mm")
        draw.text((w // 2, card_y + 66), p_data.get("hook", "🚨 ब्रेकिंग न्यूज़!"), font=font_bold_lg, fill=(255, 222, 3), anchor="mm")

        # Line 2: White Text
        draw.text((w // 2 + 2, card_y + 168), p_data.get("white", "दैनिक समाचार"), font=font_bold_md, fill=(0, 0, 0), anchor="mm")
        draw.text((w // 2, card_y + 166), p_data.get("white", "दैनिक समाचार"), font=font_bold_md, fill=(255, 255, 255), anchor="mm")

        # Line 3: Punch (Yellow #FFE600)
        draw.text((w // 2 + 2, card_y + 268), p_data.get("punch", f"फॉलो करें {CREATOR_HANDLE}"), font=font_bold_md, fill=(0, 0, 0), anchor="mm")
        draw.text((w // 2, card_y + 266), p_data.get("punch", f"फॉलो करें {CREATOR_HANDLE}"), font=font_bold_md, fill=(255, 222, 3), anchor="mm")

        # Bottom News Ticker Bar
        ticker_y = h - 180
        draw.rectangle([(0, ticker_y), (w, ticker_y + 60)], fill=(220, 38, 38))
        draw.text((w // 2, ticker_y + 30), f"⚡ ताज़ा अपडेट्स और सरकारी योजनाओं के लिए फॉलो करें: {CREATOR_HANDLE}", font=font_sub, fill=(255, 255, 255), anchor="mm")

        frame.save(f"{frames_dir}/f_{idx:04d}.jpg", quality=85)

    logger.info(f"✅ Rendered {total_frames} frames in {time.time() - t_start:.2f}s.")

    # 5. Assemble Video + Mixed Audio
    logger.info("🎥 Encoding breaking news MP4 with FFmpeg...")
    cmd_assemble = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-i", f"{frames_dir}/f_%04d.jpg",
        "-i", mixed_audio,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video_path
    ]
    subprocess.run(cmd_assemble, check=True)
    shutil.rmtree(frames_dir, ignore_errors=True)

    if os.path.exists(output_video_path):
        logger.info(f"✅ Breaking News Reel rendered: {output_video_path} (Duration: {duration:.1f}s)")
        return output_video_path
    return None

# ==============================================================================
# 4. MEDIA HOSTING & GITHUB RAW CDN
# ==============================================================================

def upload_image_to_imgbb(image_path: str) -> Optional[str]:
    if not IMGBB_API_KEY: return None
    try:
        with open(image_path, "rb") as f:
            res = requests.post(
                "https://api.imgbb.com/1/upload",
                data={"key": IMGBB_API_KEY},
                files={"image": f},
                timeout=30
            )
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                url = data["data"]["url"]
                logger.info(f"✅ Newspaper poster uploaded to ImgBB: {url}")
                return url
    except Exception as e:
        logger.error(f"ImgBB upload error: {e}")
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
        payload = {"message": "Update breaking news reel MP4", "content": v_b64, "branch": "main"}
        if check.status_code == 200:
            payload["sha"] = check.json()["sha"]
        res = requests.put(api_url, headers=headers, json=payload, timeout=60)
        if res.status_code in (200, 201):
            logger.info(f"✅ News reel video pushed to GitHub CDN: {raw_url}")
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
        logger.info("🚀 1/3 Publishing Newspaper Feed Post to Instagram...")
        try:
            r1 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media", data={
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" not in r1:
                logger.error(f"Feed post container creation failed: {r1}")
                return None
            time.sleep(6)
            r2 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media_publish", data={
                "creation_id": r1["id"],
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" in r2:
                logger.info(f"🎉 Newspaper Feed Post Published! Media ID: {r2['id']}")
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
                logger.info(f"🎉 News Story Published! ID: {r2['id']}")
                return r2["id"]
        except Exception as e:
            logger.error(f"Story post error: {e}")
        return None

    def publish_reel(self, video_url: str, caption: str) -> Optional[str]:
        logger.info("🚀 3/3 Publishing Breaking News Reel to Instagram...")
        try:
            r1 = requests.post(f"{self.graph_base}/{self.ig_user_id}/media", data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": "true",
                "access_token": self.access_token
            }, timeout=45).json()
            if "id" not in r1:
                logger.error(f"Reel container creation failed: {r1}")
                return None
            creation_id = r1["id"]

            logger.info("⏳ Waiting for Meta video processing...")
            for _ in range(18):
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
                logger.info(f"🎉 Breaking News Reel Published! Media ID: {r2['id']}")
                return r2["id"]
        except Exception as e:
            logger.error(f"Reel publish error: {e}")
        return None

# ==============================================================================
# 6. FACEBOOK PAGE AUTO-PUBLISHER
# ==============================================================================

class FacebookPublisher:
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.graph_base = "https://graph.facebook.com/v19.0"

    def publish_page_photo(self, image_url: str, caption: str) -> Optional[str]:
        if not self.page_id or not self.access_token: return None
        try:
            res = requests.post(
                f"{self.graph_base}/{self.page_id}/photos",
                data={"url": image_url, "caption": caption, "access_token": self.access_token},
                timeout=45
            ).json()
            if "id" in res:
                logger.info(f"🎉 Facebook Page News Published! ID: {res['id']}")
                return res["id"]
        except Exception:
            pass
        return None

# ==============================================================================
# 7. MAIN EXECUTION PIPELINE
# ==============================================================================

def main():
    logger.info("================================================================================")
    logger.info(f"📰 STARTING DAINIK JAGRAN HINDI NEWS AUTOMATION FOR {CREATOR_HANDLE}")
    logger.info("================================================================================")

    # 1. Fetch Live Breaking News from Google News RSS
    raw_news = fetch_live_google_news()

    # 2. Format with Gemini AI into Dainik Jagran / BBCC Hub layout
    news_data = format_news_with_gemini(raw_news)
    hashtags_str = " ".join(news_data.get("hashtags", VIRAL_HASHTAGS))
    full_caption = f"{news_data.get('caption', '')}\n\n.\n.\n{hashtags_str}\n\n📰 रोज़ाना अख़बार की ताज़ा खबरों के लिए फॉलो करें: {CREATOR_HANDLE}"

    # 3. Render 1080x1920 Newspaper Graphic (Dainik Jagran / BBCC Hub Style)
    poster_path = "output/daily_tip.png"
    face_path = "assets/my_face.jpg"
    create_newspaper_graphic(news_data, output_path=poster_path, face_path=face_path)

    # 4. Render Breaking News Video Reel
    reel_path = "output/daily_reel.mp4"
    create_news_reel_video(news_data, newspaper_img_path=poster_path, face_path=face_path, output_video_path=reel_path)

    if DRY_RUN:
        logger.info("⚡ DRY_RUN active. Media created successfully. Skipping publishing.")
        return

    # 5. Host Media
    public_img_url = upload_image_to_imgbb(poster_path)
    public_video_url = host_video_on_github(reel_path)

    if not public_img_url:
        logger.error("❌ Public image URL not available. Aborting.")
        return

    # 6. Publish Multi-Format to Instagram
    ig_publisher = InstagramMultiPublisher(
        access_token=FB_ACCESS_TOKEN,
        ig_user_id=IG_USER_ID
    )

    # 6A. Feed Post
    post_id = ig_publisher.publish_feed_post(public_img_url, full_caption)
    # 6B. Story
    story_id = ig_publisher.publish_story(public_img_url)
    # 6C. 3D Reel
    reel_id = None
    if public_video_url:
        reel_id = ig_publisher.publish_reel(public_video_url, full_caption)

    # 7. Facebook Page Direct Attempt (In addition to Make.com auto-mirror)
    fb_publisher = FacebookPublisher(access_token=FB_ACCESS_TOKEN, page_id=FB_PAGE_ID)
    fb_post_id = fb_publisher.publish_page_photo(public_img_url, full_caption)

    logger.info("================================================================================")
    logger.info("📊 MULTI-FORMAT NEWS EXECUTION SUMMARY")
    logger.info(f"• Creator:          {CREATOR_HANDLE}")
    logger.info(f"• News Headline:    '{news_data.get('headline_red')} {news_data.get('headline_black')}'")
    logger.info(f"• Newspaper Post:   {'✅ SUCCESS (ID: ' + post_id + ')' if post_id else '❌ FAILED'}")
    logger.info(f"• News Story:       {'✅ SUCCESS (ID: ' + story_id + ')' if story_id else '❌ FAILED'}")
    logger.info(f"• News Reel:        {'✅ SUCCESS (ID: ' + reel_id + ')' if reel_id else '❌ FAILED'}")
    logger.info(f"• FB Page Post:     {'✅ SUCCESS (ID: ' + fb_post_id + ')' if fb_post_id else 'ℹ️ Auto-Mirror via Make.com'}")
    logger.info("================================================================================")

if __name__ == "__main__":
    main()
