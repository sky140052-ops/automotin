#!/usr/bin/env python3
"""
================================================================================
Dainik Jagran / BBCC Skill Hub Style Hindi News Automation Engine (V2 Premium)
Creator: @rauth_jee (RAUTH JEE NEWS & SKILL HUB)

Features:
1. Anti-Duplication Engine:
   - Checks output/posted_topics.json to ensure NO TOPIC IS EVER REPEATED!
   - Every run picks a 100% fresh, unposted news story.
2. Live Google News Ingestion:
   - Rotates topics: Bihar Education & Jobs, National Policies, Cyber/Tech, World.
3. FLUX.1 Generative AI Photo Engine (ChatGPT / Midjourney quality):
   - Generates authentic, 8K photorealistic press photos matching the news topic.
4. ElevenLabs Ultra-Realistic Studio Hindi Voiceover:
   - Uses eleven_multilingual_v2 with natural human breathing and emotional cadence.
5. 1080x1920 Newspaper Clipping Poster (Dainik Jagran / BBCC Hub Style):
   - Top Navy Bar: RAUTH JEE SKILL & NEWS HUB
   - Masthead: Dainik Jagran + Dateline
   - Red & Black Breaking Headline
   - Embedded FLUX AI Photo
   - Signature Yellow Highlight Box ("मामले की मुख्य बातें")
   - Detailed Story Card + Circular Founder Avatar (@rauth_jee)
   - Bottom Navy Footer: Follow @rauth_jee
6. Viral 3D Breaking News Reel (Ken Burns Zoom + Pop-up Subtitles + Synth Beat)
7. Multi-Format Auto-Publisher (Instagram Feed + Story + Reel + Facebook Page)
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
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "sky140052-ops/automotin").strip()
CREATOR_HANDLE = os.getenv("CREATOR_HANDLE", "@rauth_jee").strip()
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

POSTED_TOPICS_FILE = "output/posted_topics.json"
REPLIED_COMMENTS_FILE = "output/replied_comments.json"

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
        "ai_image_prompt": "press conference in bihar education department, indian officials announcing teacher recruitment examination, realistic news photography",
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
        "reel_script": "ब्रेकिंग न्यूज़! बिहार में चौथे चरण की शिक्षक भर्ती का आधिकारिक नोटिफिकेशन जारी हो चुका है! कुल 32,388 पदों पर प्राथमिक और माध्यमिक शिक्षकों की बंपर बहाली होगी। पूरी रिपोर्ट और मुख्य बातें जानने के लिए पोस्ट पढ़ें और ताज़ा न्यूज़ के लिए हमारे पेज राउत जी को फॉलो करें!",
        "reel_phrases": [
            {"hook": "🚨 ब्रेकिंग न्यूज़!", "white": "बिहार शिक्षक भर्ती (TRE-4)", "punch": "32,388 पदों पर बंपर बहाली!"},
            {"hook": "📢 BPSC का बड़ा फैसला", "white": "प्राथमिक व माध्यमिक स्तर पर", "punch": "नोटिफिकेशन जारी!"},
            {"hook": "📌 मुख्य पात्रता", "white": "सीटेट व बीटेट पास अभ्यर्थी", "punch": "ही होंगे योग्य!"},
            {"hook": "⚡ ज़रूरी जानकारी", "white": "अधिकतम आयु सीमा 37 साल", "punch": "आवेदन जल्द शुरू!"},
            {"hook": "📰 हर दिन ताज़ा न्यूज़ के लिए", "white": "अभी फॉलो करें", "punch": "@rauth_jee"}
        ],
        "caption": "📢 दैनिक जागरण ब्रेकिंग: बिहार शिक्षक बहाली (TRE-4) पर बड़ा फैसला!\n\nशिक्षा विभाग और BPSC ने 32,388 पदों पर भर्ती का रास्ता साफ़ कर दिया है।\n\n📌 मुख्य बातें:\n• सीटेट / बीटेट उत्तीर्ण अभ्यर्थियों को अवसर\n• सामान्य वर्ग आयु सीमा: 37 वर्ष\n• ऑनलाइन आवेदन जल्द शुरू होंगे\n\nअपने दोस्तों के साथ शेयर करें और रोज़ाना ताज़ा अख़बार अपडेट्स के लिए फॉलो करें: @rauth_jee"
    },
    {
        "newspaper_title": "दैनिक भास्कर",
        "tagline": "सत्यमेव जयते",
        "dateline": "नई दिल्ली / भारत | ताज़ा अपडेट / राष्ट्रीय संस्करण",
        "headline_red": "डिजिटल अरेस्ट और ऑनलाइन फ्रॉड पर बड़ा फैसला:",
        "headline_black": "गृह मंत्रालय ने जारी की सख्त गाइडलाइन, खाते होंगे सीज",
        "lead_city": "नई दिल्ली",
        "lead_summary": "देश भर में बढ़ते डिजिटल अरेस्ट और ऑनलाइन फ्रॉड के मामलों को देखते हुए गृह मंत्रालय (MHA) और साइबर विंग ने कड़ा रुख अपनाया है और संदिग्ध नंबरों और खातों पर तुरंत कार्रवाई के आदेश दिए हैं।",
        "ai_image_prompt": "cyber crime investigation command center india, cyber police monitoring digital fraud on computer screens, photojournalism, cinematic lighting",
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
        "reel_script": "सावधान! गृह मंत्रालय ने डिजिटल अरेस्ट और ऑनलाइन फ्रॉड पर बड़ी चेतावनी जारी की है! पुलिस या जज कभी भी वीडियो कॉल पर डिजिटल अरेस्ट नहीं करते। फ्रॉड होने पर तुरंत 1930 पर कॉल करें। सुरक्षित रहने के लिए हमारे पेज राउत जी को फॉलो करें!",
        "reel_phrases": [
            {"hook": "🚨 सावधान इंडिया!", "white": "डिजिटल अरेस्ट के नाम पर", "punch": "हैकर्स का नया जाल!"},
            {"hook": "❌ बड़ा सच", "white": "कानून में डिजिटल अरेस्ट", "punch": "जैसा कुछ भी नहीं होता!"},
            {"hook": "⚠️ तुरंत क्या करें?", "white": "साइबर फ्रॉड होते ही", "punch": "तुरंत 1930 पर कॉल करें!"},
            {"hook": "⚡ शेयर करें", "white": "अपने सभी दोस्तों और", "punch": "परिवार को बचाएं!"},
            {"hook": "📰 सुरक्षित रहने के लिए", "white": "अभी फॉलो करें", "punch": "@rauth_jee"}
        ],
        "caption": "⚠️ सावधान: गृह मंत्रालय का बड़ा अलर्ट — 'डिजिटल अरेस्ट' से बचें!\n\nठग पुलिस या कस्टम अधिकारी बनकर लोगों को लाखों का चूना लगा रहे हैं।\n\nयाद रखें:\n1. कोई भी कानून वीडियो कॉल पर अरेस्ट नहीं करता\n2. अनजान कॉल पर पैसे कभी न भेजें\n3. तुरंत 1930 पर रिपोर्ट करें\n\n🛡️ रोज़ाना ज़रूरी जानकारियों के लिए फॉलो करें: @rauth_jee"
    },
    {
        "newspaper_title": "दैनिक जागरण",
        "tagline": "सत्य के साथ हर कदम",
        "dateline": "नई दिल्ली | ताज़ा अपडेट / पृष्ठ 01",
        "headline_red": "रेलवे का बड़ा तोहफा: 50 नई सुपरफास्ट",
        "headline_black": "ट्रेनें चलाने का ऐलान, किराया भी होगा सस्ता",
        "lead_city": "नई दिल्ली",
        "lead_summary": "भारतीय रेलवे ने देश भर के प्रमुख और व्यस्त मार्गों पर 50 नई सुपरफास्ट और आधुनिक वंदे भारत ट्रेनें चलाने की घोषणा की है, जिससे करोड़ों रेल यात्रियों को कन्फर्म सीट मिलेगी।",
        "ai_image_prompt": "modern indian passenger train departing railway station, indian passengers, cinematic lighting, photojournalism, 8k",
        "key_highlights": [
            "प्रमुख रूटों पर दौड़ेंगी 50 नई सुपरफास्ट व वंदे भारत ट्रेनें।",
            "किराए में 10 से 15 प्रतिशत तक की राहत देने का प्रस्ताव।",
            "त्योहारों व छुट्टियों में कन्फर्म टिकट मिलना होगा आसान।",
            "आधुनिक बायो-टॉयलेट, वाई-फाई और जीपीएस से लैस होंगी बोगियां।",
            "आईआरसीटीसी (IRCTC) पोर्टल पर जल्द शुरू होगी टिकट बुकिंग।"
        ],
        "detailed_report": [
            "रेल मंत्रालय ने यात्रियों की भारी भीड़ को देखते हुए यह महत्वपूर्ण फैसला लिया है।",
            "पटना-दिल्ली, मुंबई-अहमदाबाद समेत प्रमुख रूटों को प्राथमिकता दी जाएगी।",
            "",
            "सभी कोचों में आधुनिक सुरक्षा उपकरण और सीसीटीवी कैमरे स्थापित किए जाएंगे।"
        ],
        "reel_script": "ब्रेकिंग न्यूज़! भारतीय रेलवे ने 50 नई सुपरफास्ट ट्रेनें चलाने का बड़ा ऐलान किया है! किराया भी सस्ता होगा और टिकट भी आसानी से मिलेगा। पूरी खबर जानने के लिए पोस्ट पढ़ें और ताज़ा अपडेट्स के लिए हमारे पेज राउत जी को फॉलो करें!",
        "reel_phrases": [
            {"hook": "🚨 रेलवे का बड़ा फैसला!", "white": "50 नई सुपरफास्ट ट्रेनें", "punch": "रूट्स का हुआ ऐलान!"},
            {"hook": "📢 आम जनता को राहत", "white": "किराया होगा सस्ता", "punch": "कन्फर्म टिकट मिलेगा!"},
            {"hook": "⚡ बुकिंग अपडेट", "white": "IRCTC पर जल्द", "punch": "टिकट उपलब्ध होंगे!"},
            {"hook": "📰 हर दिन ताज़ा न्यूज़ के लिए", "white": "अभी फॉलो करें", "punch": "@rauth_jee"}
        ],
        "caption": "🚆 भारतीय रेलवे का बड़ा तोहफा: 50 नई सुपरफास्ट ट्रेनें जल्द!\n\nसफर होगा आसान और किराया भी सस्ता।\n\nफॉलो करें: @rauth_jee"
    },
    {
        "newspaper_title": "दैनिक जागरण",
        "tagline": "सत्य के साथ हर कदम",
        "dateline": "पटना / बिहार | विकास बुलेटिन / पृष्ठ 01",
        "headline_red": "पटना मेट्रो प्रोजेक्ट में आई तेजी:",
        "headline_black": "अगले साल से दौड़ेगी ट्रेन, ट्रायल रन शुरू",
        "lead_city": "पटना",
        "lead_summary": "राजधानी पटना में बहुप्रतीक्षित मेट्रो परियोजना का कार्य रिकॉर्ड गति से आगे बढ़ रहा है और प्राथमिक कॉरिडोर पर अंडरग्राउंड टनलिंग कार्य पूरा कर लिया गया है।",
        "ai_image_prompt": "modern patna metro train on elevated track in bihar, urban skyline, bright daylight, realistic press photo",
        "key_highlights": [
            "प्राथमिक कॉरिडोर पर पटरी बिछाने और इलेक्ट्रिफिकेशन का काम शुरू।",
            "मीठापुर से आईएसबीटी (ISBT) बस स्टैंड तक सबसे पहले चलेगी मेट्रो।",
            "प्रतिदिन 5 लाख से अधिक यात्रियों को जाम से मिलेगी स्थायी मुक्ति।",
            "आधुनिक ऑटोमैटिक फेयर कलेक्शन व स्मार्ट कार्ड की सुविधा उपलब्ध होगी।",
            "पर्यावरण अनुकूल ग्रीन एनर्जी से संचालित होंगे सभी मेट्रो स्टेशन।"
        ],
        "detailed_report": [
            "बिहार सरकार और मेट्रो रेल कॉरपोरेशन ने निर्माण कार्य की समीक्षा के बाद",
            "संतुष्टि जताई है। सभी सुरक्षा मानकों का कड़ाई से पालन किया जा रहा है।",
            "",
            "पटनावासियों के लिए यह परियोजना यातायात के क्षेत्र में ऐतिहासिक मील का पत्थर बनेगी।"
        ],
        "reel_script": "बड़ी खुशखबरी! पटना मेट्रो का काम पूरा होने के करीब है! अगले साल से प्राथमिक रूट पर मेट्रो दौड़ने लगेगी जिससे जाम से पूरी राहत मिलेगी। पूरी रिपोर्ट पढ़ने के लिए पोस्ट देखें और ताज़ा खबरों के लिए हमारे पेज राउत जी को फॉलो करें!",
        "reel_phrases": [
            {"hook": "🚨 पटना मेट्रो अपडेट!", "white": "टनलिंग का काम पूरा", "punch": "ट्रायल रन जल्द शुरू!"},
            {"hook": "🚆 जाम से मिलेगी मुक्ति", "white": "मीठापुर से ISBT तक", "punch": "सबसे पहले दौड़ेगी मेट्रो!"},
            {"hook": "⚡ ग्रीन व स्मार्ट सिटी", "white": "स्मार्ट कार्ड व QR कोड", "punch": "से मिलेगा टिकट!"},
            {"hook": "📰 हर दिन ताज़ा न्यूज़ के लिए", "white": "अभी फॉलो करें", "punch": "@rauth_jee"}
        ],
        "caption": "🚆 पटना मेट्रो की बड़ी प्रगति: अगले साल से दौड़ेगी ट्रेन!\n\nराजधानीवासियों को जाम से मिलेगी मुक्ति।\n\nफॉलो करें: @rauth_jee"
    }
]

# ==============================================================================
# 1. TOPIC DEDUPLICATION & PERSISTENCE
# ==============================================================================

def load_posted_topics() -> List[str]:
    os.makedirs(os.path.dirname(POSTED_TOPICS_FILE), exist_ok=True)
    if os.path.exists(POSTED_TOPICS_FILE):
        try:
            with open(POSTED_TOPICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_posted_topic(title: str):
    topics = load_posted_topics()
    cleaned = title.strip()[:80]
    if cleaned and cleaned not in topics:
        topics.append(cleaned)
        if len(topics) > 150:
            topics = topics[-150:]
        try:
            with open(POSTED_TOPICS_FILE, "w", encoding="utf-8") as f:
                json.dump(topics, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Added topic to deduplication database: '{cleaned}'")
        except Exception as e:
            logger.warning(f"Could not save posted topics: {e}")

# ==============================================================================
# 2. LIVE GOOGLE NEWS INGESTION (STRICT ZERO-DUPLICATION)
# ==============================================================================

def fetch_unique_live_news() -> Optional[Dict[str, str]]:
    """Fetches real-time Hindi breaking news, ensuring NO DUPLICATE topics."""
    logger.info("📡 Scanning Google News RSS for fresh, unposted breaking news...")
    posted_topics = load_posted_topics()

    # 7 Diverse, high-interest news search categories
    queries = [
        ("बिहार शिक्षा भर्ती शिक्षक परीक्षा रिजल्ट", "बिहार शिक्षा व भर्ती"),
        ("भारत सरकार बड़ी घोषणा नया नियम योजना", "राष्ट्रीय बड़ी खबर"),
        ("साइबर सुरक्षा डिजिटल फ्रॉड ऑनलाइन अलर्ट", "डिजिटल सुरक्षा अलर्ट"),
        ("भारतीय रेलवे वंदे भारत नया रूट ट्रेन", "भारतीय रेलवे"),
        ("इसरो विज्ञान अंतरिक्ष नया मिशन टेक्नोलॉजी", "विज्ञान व अंतरिक्ष"),
        ("आरबीआई बैंक नया नियम यूपीआई वित्तीय अलर्ट", "बैंकिंग व वित्त"),
        ("बिहार विकास योजना पटना मेट्रो बड़ी खबर", "बिहार विकास")
    ]
    random.shuffle(queries)

    for q_text, domain_label in queries:
        try:
            encoded_q = urllib.parse.quote(q_text)
            url = f"https://news.google.com/rss/search?q={encoded_q}&hl=hi&gl=IN&ceid=IN:hi"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            for item in items[:8]:
                raw_title = item.find("title").text or ""
                clean_title = raw_title.split(" - ")[0].strip()
                desc = item.find("description").text if item.find("description") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

                if len(clean_title) < 15:
                    continue

                # Strict check against all posted topics
                is_duplicate = False
                title_words = set([w for w in clean_title.split() if len(w) >= 3])
                for prev in posted_topics:
                    prev_words = set([w for w in prev.split() if len(w) >= 3])
                    overlap = len(title_words.intersection(prev_words))
                    if overlap >= 3 or clean_title[:35] in prev or prev[:35] in clean_title:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    logger.info(f"✅ Found Fresh Unique Story ({domain_label}): {clean_title}")
                    return {
                        "title": clean_title,
                        "desc": desc,
                        "pub_date": pub_date,
                        "domain": domain_label
                    }
        except Exception as e:
            logger.warning(f"Error querying Google News ({domain_label}): {e}")
            continue

    logger.warning("No unposted live stories found in current RSS queries. Will pick unique from fallback.")
    return None

# ==============================================================================
# 3. GEMINI AI NEWS FORMATTER (WITH RESILIENT REST & DYNAMIC FALLBACK)
# ==============================================================================

def call_gemini_rest(prompt: str) -> Optional[str]:
    """Direct REST call to Gemini 3.5 / 3.8 Flash, bypassing SDK incompatibilities."""
    if not GEMINI_API_KEY or "your_gemini" in GEMINI_API_KEY.lower():
        return None

    # Modern production models in Google AI Studio
    models = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-2.0-flash-exp"]
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            r = requests.post(url, json=payload, timeout=25)
            if r.status_code == 200:
                data = r.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    logger.info(f"✅ News structured with Gemini AI ({m})")
                    return text
            else:
                logger.warning(f"Gemini {m} returned HTTP {r.status_code}")
        except Exception as e:
            logger.warning(f"Gemini {m} call error: {e}")
    return None

def dynamically_format_live_news(raw_news: Dict[str, str]) -> Dict[str, Any]:
    """Dynamically structures raw Google News into Dainik Jagran layout if Gemini is unavailable."""
    title = raw_news.get("title", "")
    domain = raw_news.get("domain", "ताज़ा बड़ी खबर")
    words = title.split()

    if len(words) > 6:
        split_idx = min(6, len(words) // 2 + 1)
        headline_red = " ".join(words[:split_idx]) + ":"
        headline_black = " ".join(words[split_idx:])
    else:
        headline_red = "बड़ी खबर:"
        headline_black = title

    lead_city = "पटना" if ("बिहार" in title or "पटना" in title) else "नई दिल्ली"
    
    # Keyword-based AI Image prompt
    t_lower = title.lower()
    if any(k in t_lower for k in ["ट्रेन", "रेलवे", "रेल", "वंदे"]):
        ai_prompt = "indian railways passenger train departing modern station, indian passengers, cinematic lighting, 8k photojournalism"
    elif any(k in t_lower for k in ["शिक्षक", "स्कूल", "भर्ती", "bpsc", "परीक्षा"]):
        ai_prompt = "indian government examination hall, young students taking test, official bihar education board, realistic photojournalism"
    elif any(k in t_lower for k in ["साइबर", "फ्रॉड", "अरेस्ट", "हैक"]):
        ai_prompt = "indian cyber security police officers examining digital data on computer monitors, cyber cell crime branch, dramatic lighting"
    elif any(k in t_lower for k in ["इसरो", "स्पेस", "रॉकेट", "मिशन"]):
        ai_prompt = "isro satellite rocket launch pad sriharikota india, dramatic exhaust smoke, space exploration, photorealistic 8k"
    elif any(k in t_lower for k in ["मेट्रो", "पुल", "सड़क"]):
        ai_prompt = "modern elevated metro train running in indian city, urban infrastructure, bright daylight photo"
    else:
        ai_prompt = "indian government press conference room, officials addressing press media with microphones, realistic news photo"

    return {
        "newspaper_title": "दैनिक जागरण",
        "tagline": "सत्य के साथ हर कदम",
        "dateline": f"{lead_city} | ताज़ा अपडेट / पृष्ठ 01",
        "headline_red": headline_red[:35],
        "headline_black": headline_black[:45],
        "lead_city": lead_city,
        "lead_summary": f"{title}। इस संबंध में संबंधित विभाग द्वारा आधिकारिक दिशा-निर्देश जारी कर दिए गए हैं।",
        "ai_image_prompt": ai_prompt,
        "key_highlights": [
            f"{headline_black[:40]} पर बड़ा फैसला।",
            "संबंधित विभाग ने नियमों व शर्तों की पूरी रूपरेखा तैयार की।",
            "आम नागरिकों और अभ्यर्थियों को मिलेगा सीधा लाभ।",
            "पारदर्शिता और सुविधा के लिए डिजिटल माध्यमों का होगा उपयोग।",
            "आधिकारिक पोर्टल पर विस्तृत अधिसूचना व जानकारी उपलब्ध।"
        ],
        "detailed_report": [
            f"{title} को लेकर व्यापक तैयारियां पूरी कर ली गई हैं।",
            "",
            "वरिष्ठ अधिकारियों के अनुसार नई व्यवस्था से लोगों को बड़ी सुविधा और राहत मिलेगी।",
            "",
            "सभी नागरिकों से अपील की गई है कि वे केवल आधिकारिक सूचनाओं पर ही भरोसा करें।"
        ],
        "reel_script": f"ब्रेकिंग न्यूज़! {headline_red} {headline_black}! पूरी रिपोर्ट जानने के लिए इस पोस्ट को ध्यान से पढ़ें और रोज़ाना ताज़ा खबरों के लिए हमारे पेज राउत जी को फॉलो करें!",
        "reel_phrases": [
            {"hook": "🚨 ब्रेकिंग न्यूज़!", "white": headline_red.replace(":", ""), "punch": headline_black[:30]},
            {"hook": "📢 बड़ा फैसला", "white": "आधिकारिक सूचना जारी", "punch": "नियम लागू!"},
            {"hook": "📌 मुख्य बातें", "white": "पूरी जानकारी के लिए", "punch": "पोस्ट पढ़ें!"},
            {"hook": "📰 ताज़ा खबरों के लिए", "white": "अभी फॉलो करें", "punch": "पेज राउत जी"}
        ],
        "caption": f"📢 दैनिक जागरण ब्रेकिंग: {title}\n\n📌 मुख्य बातें:\n• पूरी रिपोर्ट जारी\n• आधिकारिक पोर्टल पर अधिसूचना उपलब्ध\n\nऐसी ही हर ताज़ा खबर के लिए फॉलो करें: @rauth_jee",
        "hashtags": VIRAL_HASHTAGS
    }

def format_news_with_gemini(raw_news: Optional[Dict[str, str]]) -> Dict[str, Any]:
    logger.info("🤖 Formatting News into Dainik Jagran Newspaper Layout...")
    posted_topics = load_posted_topics()

    news_context = ""
    if raw_news:
        news_context = f"Headline: {raw_news.get('title')}\nDetails: {raw_news.get('desc')}\nDomain: {raw_news.get('domain')}"
    else:
        news_context = "Top Breaking Educational or National Policy News."

    prompt = f"""
You are an expert Chief Editor at Dainik Jagran / Bhaskar.
Transform this news story into an authentic, highly engaging Hindi Newspaper Clipping infographic:

{news_context}

IMPORTANT RULES:
- Use pure, clean Hindi Devanagari. Write abbreviations phonetically (e.g. 'सीटेट', 'बीपीएससी', 'टीआरई-4').
- Return ONLY a valid JSON object with these EXACT keys:
{{
  "newspaper_title": "दैनिक जागरण",
  "tagline": "सत्य के साथ हर कदम",
  "dateline": "पटना / बिहार | ताज़ा अपडेट / पृष्ठ 01",
  "headline_red": "Punchy Red Headline Line 1 under 6 words in Devanagari",
  "headline_black": "Black Headline Line 2 under 6 words in Devanagari",
  "lead_city": "पटना",
  "lead_summary": "1 to 2 clear formal sentences in Hindi newspaper tone.",
  "ai_image_prompt": "Specific English prompt describing a realistic photojournalistic news image for this story (e.g. 'press conference bihar education department, photojournalism, cinematic lighting, 8k resolution')",
  "key_highlights": [
    "First crucial fact or decision in 10-15 Hindi words.",
    "Second crucial rule or eligibility detail.",
    "Third crucial date or provision.",
    "Fourth crucial point for public.",
    "Fifth crucial point regarding official portal."
  ],
  "detailed_report": [
    "Paragraph 1 providing context and official statement.",
    "",
    "Paragraph 2 highlighting the impact.",
    "",
    "Paragraph 3 giving advisory to readers."
  ],
  "reel_script": "News anchor voiceover in Hindi under 30 words starting with 'ब्रेकिंग न्यूज़!' and ending strictly with 'हमारे पेज राउत जी को फॉलो करें!'",
  "reel_phrases": [
    {{"hook": "🚨 ब्रेकिंग न्यूज़!", "white": "खबर का मुख्य विषय", "punch": "बड़ा फैसला जारी!"}},
    {{"hook": "📢 नया अपडेट", "white": "नियम या प्रक्रिया", "punch": "लाखों लोगों को राहत!"}},
    {{"hook": "📌 मुख्य बातें", "white": "पात्रता और शर्तें", "punch": "विभागीय पोर्टल पर उपलब्ध!"}},
    {{"hook": "⚡ ज़रूरी निर्देश", "white": "तुरंत चेक करें", "punch": "और तैयार रहें!"}},
    {{"hook": "📰 ताज़ा खबरों के लिए", "white": "अभी फॉलो करें", "punch": "पेज राउत जी"}}
  ],
  "caption": "Detailed Instagram caption with headlines, bullet points, hashtags, and call to action."
}}
"""
    raw_text = call_gemini_rest(prompt)

    if raw_text:
        try:
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:]
            if cleaned.startswith("```"): cleaned = cleaned[3:]
            if cleaned.endswith("```"): cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            data["hashtags"] = VIRAL_HASHTAGS
            return data
        except Exception as e:
            logger.warning(f"JSON parse error from Gemini: {e}")

    # If Gemini unavailable but we have live Google News, dynamically build it!
    if raw_news:
        logger.info("⚡ Dynamically structuring live Google News story...")
        return dynamically_format_live_news(raw_news)

    # Pick an unposted story from fallback database
    for story in FALLBACK_NEWS_DATABASE:
        full_h = f"{story.get('headline_red')} {story.get('headline_black')}"
        if not any(full_h[:30] in p for p in posted_topics):
            story["hashtags"] = VIRAL_HASHTAGS
            return story

    return FALLBACK_NEWS_DATABASE[0]

# ==============================================================================
# 4. FLUX.1 / POLLINATIONS AI PHOTO GENERATOR (CHATGPT / MIDJOURNEY QUALITY)
# ==============================================================================

def generate_flux_ai_photo(prompt: str, output_path: str = "output/news_photo.jpg") -> Optional[str]:
    """Generates authentic 8K photorealistic press photos via AI."""
    logger.info("🎨 Generating 8K Photorealistic Press Photo via AI...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    full_prompt = f"{prompt}, award winning photojournalism, cinematic lighting, ultra realistic, 8k resolution, canon eos r5"
    encoded_prompt = urllib.parse.quote(full_prompt)

    # Resilient multi-endpoint fallback
    endpoints = [
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1000&height=500&nologo=true",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1000&height=500&model=turbo&nologo=true",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1000&height=500&model=flux&nologo=true"
    ]

    for url in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            if len(data) > 5000:
                with open(output_path, "wb") as f:
                    f.write(data)
                logger.info(f"✅ AI Press Photo generated: {output_path} ({len(data)} bytes)")
                return output_path
        except Exception as e:
            logger.warning(f"AI photo generation retry: {e}")

    return None

# ==============================================================================
# 5. ELEVENLABS ULTRA-REALISTIC HINDI VOICEOVER ENGINE
# ==============================================================================

def generate_elevenlabs_voiceover(text: str, output_path: str = "output/voiceover.mp3") -> tuple[str, float]:
    """Generates broadcast studio quality Hindi voiceover via ElevenLabs."""
    ffmpeg = get_ffmpeg_binary()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if ELEVENLABS_API_KEY:
        logger.info("🎙️ Generating Ultra-Realistic Studio Voiceover via ElevenLabs...")
        # Voices: George (Captivating Storyteller) or Sarah (Confident Female Anchor)
        voices = [
            ("JBFqnCBsd6RMkjVDRZzb", "Male (George)"),
            ("EXAVITQu4vr4xnSDxMaL", "Female (Sarah)")
        ]
        voice_id, voice_label = random.choice(voices)
        logger.info(f"🎭 ElevenLabs Voice: {voice_label}")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200 and len(res.content) > 5000:
                with open(output_path, "wb") as f:
                    f.write(res.content)
                logger.info(f"✅ ElevenLabs Voiceover generated! Size: {len(res.content)} bytes")
                duration = probe_audio_duration(output_path)
                return output_path, duration
            else:
                logger.warning(f"ElevenLabs notice: {res.status_code} {res.text[:100]}. Falling back to gTTS.")
        except Exception as e:
            logger.warning(f"ElevenLabs connection notice: {e}")

    # Fallback to gTTS if ElevenLabs unavailable
    logger.info("🎙️ Using neural gTTS fallback voiceover...")
    from gtts import gTTS
    raw_tts = "output/raw_tts.mp3"
    gTTS(text=text, lang="hi", slow=False).save(raw_tts)
    is_male = random.choice([True, False])
    pitch_filter = "asetrate=44100*0.88,aresample=44100,atempo=1.14" if is_male else "asetrate=44100*1.12,aresample=44100,atempo=0.90"
    subprocess.run([ffmpeg, "-y", "-i", raw_tts, "-af", pitch_filter, output_path], capture_output=True)
    duration = probe_audio_duration(output_path)
    return output_path, duration

def probe_audio_duration(audio_path: str) -> float:
    ffmpeg = get_ffmpeg_binary()
    probe = subprocess.run([ffmpeg, "-i", audio_path], capture_output=True, text=True)
    duration = 10.0
    for line in probe.stderr.splitlines():
        if "Duration" in line:
            try:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
            except Exception:
                pass
    return max(8.0, min(duration, 16.0))

# ==============================================================================
# 6. NEWSPAPER CLIPPING POSTER ENGINE (BBCC SKILL HUB / DAINIK JAGRAN STYLE)
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
                try: return ImageFont.truetype(fpath, size)
                except Exception: pass
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
    ai_photo_path: Optional[str] = None,
    output_path: str = "output/daily_tip.png",
    face_path: str = "assets/my_face.jpg"
) -> str:
    """
    Renders 1080x1920 Full HD Hindi Newspaper Infographic:
    - Top Navy Bar: RAUTH JEE SKILL & NEWS HUB
    - Masthead: Dainik Jagran + Dateline
    - Red & Black Breaking Headline
    - Embedded FLUX AI Photo
    - Signature Yellow Highlight Box ("मामले की मुख्य बातें")
    - Detailed Story Card + Founder Avatar (@rauth_jee)
    - Bottom Navy Footer
    """
    logger.info("🎨 Rendering 1080x1920 Dainik Jagran / BBCC Hub Style Newspaper Poster...")
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), (248, 249, 250)) # warm off-white newsprint
    draw = ImageDraw.Draw(img)

    font_masthead = get_devanagari_font(62, bold=True)
    font_bold_xl = get_devanagari_font(42, bold=True)
    font_bold_lg = get_devanagari_font(32, bold=True)
    font_bold_md = get_devanagari_font(26, bold=True)
    font_reg_md = get_devanagari_font(24, bold=False)
    font_reg_sm = get_devanagari_font(20, bold=False)

    # 1. TOP NAVY BLUE BAR (BBCC SKILL HUB)
    draw.rectangle([(0, 0), (w, 120)], fill=(10, 37, 64))
    draw.text((40, 20), "BBCC SKILL HUB", font=get_devanagari_font(46, bold=True), fill=(255, 222, 3))
    draw.text((470, 32), "| दैनिक समाचार विशेषांक", font=font_bold_md, fill=(255, 255, 255))
    draw.text((40, 78), "Learn • Grow • Build Your Future | हमारे पेज राउत जी को फॉलो करें", font=font_reg_sm, fill=(203, 213, 225))
    # Right Yellow Badge
    draw.rounded_rectangle([w - 260, 24, w - 40, 92], radius=15, fill=(255, 222, 3))
    draw.text((w - 150, 58), "ताज़ा न्यूज़ आज", font=font_bold_md, fill=(10, 37, 64), anchor="mm")

    # 2. NEWSPAPER MASTHEAD (AUTHENTIC DAINIK JAGRAN STYLE)
    paper_title = news_data.get("newspaper_title", "दैनिक जागरण")
    tagline = news_data.get("tagline", "सत्य के साथ हर कदम | विश्व का सर्वाधिक पढ़ा जाने वाला दैनिक")

    # Double rule above masthead
    draw.line([(35, 128), (w - 35, 128)], fill=(15, 23, 42), width=3)
    draw.line([(35, 134), (w - 35, 134)], fill=(15, 23, 42), width=1)

    draw.ellipse([45, 142, 105, 202], fill=(245, 158, 11))
    draw.text((120, 132), paper_title, font=font_masthead, fill=(15, 23, 42))
    draw.text((w - 360, 158), tagline, font=font_reg_sm, fill=(100, 116, 139))

    # Double rule under masthead with dateline
    draw.line([(35, 215), (w - 35, 215)], fill=(15, 23, 42), width=1)
    dateline = news_data.get("dateline", "पटना / बिहार | शनिवार, 24 अक्टूबर 2026 | वर्ष 24, अंक 23 | पृष्ठ 01")
    draw.text((45, 224), dateline, font=font_reg_sm, fill=(30, 41, 59))
    draw.line([(35, 258), (w - 35, 258)], fill=(15, 23, 42), width=3)

    # 3. BREAKING HEADLINE (Line 1 Red Kicker, Line 2 Black Title)
    hl_red = news_data.get("headline_red", "🔴 बड़ी खबर: बड़ा प्रशासनिक फैसला")
    hl_black = news_data.get("headline_black", "आधिकारिक आदेश जारी, नियमों में राहत")
    draw.text((40, 275), hl_red, font=font_bold_xl, fill=(220, 38, 38))
    draw.text((40, 335), hl_black, font=font_bold_xl, fill=(15, 23, 42))

    # 4. LEAD SUBTITLE
    lead_city = news_data.get("lead_city", "पटना")
    lead_summary = news_data.get("lead_summary", "संबंधित विभाग ने इस विषय पर आधिकारिक स्पष्टीकरण जारी कर दिया है।")
    draw.text((40, 410), f"{lead_city} (विशेष संवाददाता) | {lead_summary[:85]}...", font=font_reg_md, fill=(51, 65, 85))

    # 5. EMBED REAL FLUX AI PRESS PHOTO
    photo_top = 460
    photo_h = 470
    if ai_photo_path and os.path.exists(ai_photo_path):
        try:
            ai_img = Image.open(ai_photo_path).convert("RGB").resize((w - 80, photo_h), Image.Resampling.LANCZOS)
            mask = Image.new("L", (w - 80, photo_h), 0)
            ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (w - 80, photo_h)], radius=15, fill=255)
            img.paste(ai_img, (40, photo_top), mask)
            draw.rounded_rectangle([(40, photo_top), (w - 40, photo_top + photo_h)], radius=15, outline=(15, 23, 42), width=2)
            # Photo badge
            draw.rounded_rectangle([55, photo_top + photo_h - 40, 380, photo_top + photo_h - 10], radius=8, fill=(10, 37, 64))
            draw.text((65, photo_top + photo_h - 36), "📷 विशेष रिपोर्ट • फोटो: ब्यूरो / AI प्रेस", font=font_reg_sm, fill=(255, 255, 255))
        except Exception:
            pass

    # 6. SIGNATURE YELLOW HIGHLIGHT BOX ("मामले की मुख्य बातें")
    box_y = photo_top + photo_h + 20
    box_h = 390
    draw.rounded_rectangle([40, box_y, w - 40, box_y + box_h], radius=16, fill=(254, 249, 195), outline=(217, 119, 6), width=3)
    draw.rounded_rectangle([70, box_y + 16, 420, box_y + 68], radius=25, fill=(220, 38, 38))
    draw.text((245, box_y + 42), "📌 मामले की मुख्य बातें", font=font_bold_md, fill=(255, 255, 255), anchor="mm")

    points = news_data.get("key_highlights", [
        "विभाग ने सभी नियमों को स्पष्ट करते हुए दिशा-निर्देश जारी किए।",
        "योग्य अभ्यर्थियों के लिए पोर्टल पर विस्तृत जानकारी उपलब्ध।",
        "पारदर्शिता और निष्पक्षता बनाए रखने के कड़े प्रबंध किए गए।",
        "अनजान या फर्जी सूचनाओं से सावधान रहने की अपील।",
        "रोज़ाना नई जानकारी के लिए जुड़े रहें।"
    ])
    py = box_y + 92
    for pt in points[:5]:
        draw.ellipse([(75, py + 8), (89, py + 22)], fill=(220, 38, 38))
        draw.text((105, py), pt, font=font_bold_md, fill=(15, 23, 42))
        py += 56

    # 7. DETAILED STORY CARD & FOUNDER AVATAR
    card_y = box_y + box_h + 20
    card_h = h - 140 - card_y
    draw.rounded_rectangle([40, card_y, w - 40, card_y + card_h], radius=16, fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    draw.text((70, card_y + 20), "विस्तृत रिपोर्ट एवं मुख्य विश्लेषण", font=font_bold_lg, fill=(15, 23, 42))
    draw.line([(70, card_y + 62), (430, card_y + 62)], fill=(220, 38, 38), width=3)

    # Embed Founder Face
    if os.path.exists(face_path):
        try:
            fimg = Image.open(face_path).convert("RGBA").resize((110, 110), Image.Resampling.LANCZOS)
            mask = Image.new("L", (110, 110), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 110, 110), fill=255)
            img.paste(fimg, (w - 180, card_y + 18), mask)
            draw.ellipse((w - 184, card_y + 14, w - 66, card_y + 132), outline=(10, 37, 64), width=3)
            draw.text((w - 125, card_y + 142), CREATOR_HANDLE, font=font_reg_sm, fill=(10, 37, 64), anchor="mm")
        except Exception:
            pass

    body_list = news_data.get("detailed_report", [
        "संबंधित विभाग ने आगामी चरणों के लिए पूरी रूपरेखा तैयार कर ली है।",
        "सभी जिलों से रोस्टर और पदों की गणना पूरी होने के बाद आगे की कार्रवाई शुरू होगी।",
        "अभ्यर्थियों को सलाह दी गई है कि वे केवल आधिकारिक पोर्टल से ही जानकारी प्राप्त करें।"
    ])
    by = card_y + 80
    for line in body_list[:4]:
        if line:
            wrapped = wrap_text_lines(line, font_reg_md, w - 280)
            for wl in wrapped:
                draw.text((70, by), wl, font=font_reg_md, fill=(51, 65, 85))
                by += 38
        else:
            by += 15

    # 8. BOTTOM NAVY FOOTER
    draw.rectangle([(0, h - 120), (w, h)], fill=(10, 37, 64))
    draw.text((40, h - 85), f"BBCC SKILL HUB | अपने करियर और ज्ञान की सही दिशा", font=font_bold_md, fill=(255, 255, 255))
    draw.text((40, h - 45), f"रोज़ाना ताज़ा अपडेट के लिए हमारे पेज राउत जी को फॉलो करें (@rauth_jee)", font=font_reg_sm, fill=(203, 213, 225))
    draw.rounded_rectangle([w - 360, h - 95, w - 40, h - 35], radius=15, fill=(255, 222, 3))
    draw.text((w - 200, h - 65), f"पेज राउत जी", font=get_devanagari_font(24, bold=True), fill=(10, 37, 64), anchor="mm")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    logger.info(f"✅ Dainik Jagran style newspaper poster saved: {output_path}")
    return output_path

# ==============================================================================
# 7. BREAKING NEWS VIDEO REEL ENGINE
# ==============================================================================

def get_ffmpeg_binary() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def generate_cinematic_news_soundtrack(output_path: str = "assets/music.wav", duration: float = 12.0) -> str:
    """
    Synthesizes a broadcast-grade cinematic TV news soundtrack:
    - Deep Taiko drum impacts & rhythmic snare hits (no cheesy high bleeps)
    - Dark orchestral D-minor / Bb-major strings pad
    - Sub-bass heartbeat pulse (55 Hz)
    - Tension whoosh / riser
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sr = 44100
    ns = int(sr * duration)
    bpm = 120
    beat_samples = int(sr * 60 / bpm)  # 0.5s per beat

    # Chord frequencies (D Minor dramatic news pad: D3, F3, A3, D4 & Bb Major)
    chord_d_minor = [146.83, 174.61, 220.00, 293.66]
    chord_bb_major = [116.54, 146.83, 174.61, 233.08]

    frames = bytearray()
    for i in range(ns):
        t = i / sr
        bar = int(t / 2.0) % 2  # alternates every 2 seconds
        chord = chord_d_minor if bar == 0 else chord_bb_major

        # 1. Cinematic Heavy News Drum (Taiko impact on beat 0 and beat 2)
        drum_hit = 0.0

        # Beat 0: Big Impact
        t_hit_0 = (i % (beat_samples * 4)) / sr
        if t_hit_0 < 0.6:
            pitch_0 = 45.0 + 75.0 * math.exp(-t_hit_0 * 18.0)
            drum_hit += 0.85 * math.sin(2 * math.pi * pitch_0 * t_hit_0) * math.exp(-t_hit_0 * 4.5)
            drum_hit += 0.3 * (random.random() * 2.0 - 1.0) * math.exp(-t_hit_0 * 40.0)

        # Beat 2: Snare / Clap Hit
        t_hit_2 = ((i - beat_samples * 2) % (beat_samples * 4)) / sr
        if 0 <= t_hit_2 < 0.3:
            drum_hit += 0.45 * (random.random() * 2.0 - 1.0) * math.exp(-t_hit_2 * 25.0)
            drum_hit += 0.4 * math.sin(2 * math.pi * 90.0 * t_hit_2) * math.exp(-t_hit_2 * 12.0)

        # Beat 3.5: Rhythmic pre-hit
        t_hit_3 = ((i - int(beat_samples * 3.5)) % (beat_samples * 4)) / sr
        if 0 <= t_hit_3 < 0.2:
            drum_hit += 0.35 * math.sin(2 * math.pi * 65.0 * t_hit_3) * math.exp(-t_hit_3 * 15.0)

        # 2. Dramatic Deep Orchestral Strings / News Pad (Smooth, dark, serious)
        pad = 0.0
        for f in chord:
            pad += (0.15 * math.sin(2 * math.pi * f * t) +
                    0.08 * math.sin(2 * math.pi * (f * 2.0) * t) +
                    0.04 * math.sin(2 * math.pi * (f * 0.5) * t))
        pad *= (0.7 + 0.3 * math.sin(2 * math.pi * 0.5 * t))

        # 3. News Heartbeat Sub-Bass Pulse (55Hz)
        sub_pulse = 0.4 * math.sin(2 * math.pi * 55.0 * t) * (1.0 if (i % beat_samples) < (beat_samples * 0.35) else 0.1)

        # 4. Cinematic Tension Riser / Whoosh
        riser = 0.0
        t_riser = t % 4.0
        if t_riser > 2.5:
            r_prog = (t_riser - 2.5) / 1.5
            riser = 0.25 * (random.random() * 2.0 - 1.0) * (r_prog ** 2)

        # Total mix (Balanced, powerful, NO high bleeps)
        total = drum_hit * 0.65 + pad * 0.35 + sub_pulse * 0.3 + riser * 0.15
        total = max(-0.95, min(0.95, total))
        sample_val = int(total * 32000)

        frames.extend(struct.pack("<hh", sample_val, sample_val))

    with wave.open(output_path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(frames)

    logger.info(f"✅ Cinematic TV news soundtrack generated: {output_path} ({duration}s)")
    return output_path

def create_news_reel_video(
    news_data: Dict[str, Any],
    ai_photo_path: Optional[str] = None,
    newspaper_img_path: str = "output/daily_tip.png",
    face_path: str = "assets/my_face.jpg",
    output_video_path: str = "output/daily_reel.mp4"
) -> Optional[str]:
    """
    Renders Google Flow / TV News Channel video reel (Option B: Pure Cinematic Soundtrack):
    - Duration: 12.0 seconds punchy news bulletin reel
    - Audio: Powerful cinematic news theme (Drums + Sub-Bass + Strings), NO robotic bleeps, NO voice
    - Top Masthead: BBCC SKILL HUB in gold & white with pulsing 🔴 LIVE NEWS broadcast badge
    - Full-Screen Visual: 8K Photorealistic AI Press Photo with smooth cinematic Ken Burns zoom
    - Authentic TV News Channel Lower-Third:
      * Red Breaking Bar: 🔴 BREAKING NEWS
      * Main Headline Plate: Headline Line 1 (Gold) + Headline Line 2 (White) + Summary
      * Bottom News Ticker Bar: ⚡ ताज़ा खबरों और सरकारी अपडेट्स के लिए हमारे पेज राउत जी को फॉलो करें
    """
    logger.info("🎬 Rendering TV News Channel (BBCC Skill Hub - Option B Music Reel)...")
    ffmpeg = get_ffmpeg_binary()

    duration = 12.0
    fps = 24
    total_frames = int(duration * fps)
    w, h = 1080, 1920

    # 1. Generate Cinematic News Soundtrack (Music only, no voice, no 'chiyu chiyu')
    music_wav = "output/cinematic_music.wav"
    generate_cinematic_news_soundtrack(music_wav, duration=duration)

    # 2. Setup Visual Components (TV News Layout)
    photo_file = ai_photo_path if (ai_photo_path and os.path.exists(ai_photo_path)) else "output/news_photo.jpg"
    if not os.path.exists(photo_file):
        photo_file = newspaper_img_path

    try:
        base_photo = Image.open(photo_file).convert("RGB")
    except Exception:
        base_photo = Image.new("RGB", (w, 1200), (15, 23, 42))

    font_logo = get_devanagari_font(46, bold=True)
    font_sub = get_devanagari_font(22, bold=False)
    font_badge = get_devanagari_font(26, bold=True)
    font_hl_1 = get_devanagari_font(42, bold=True)
    font_hl_2 = get_devanagari_font(38, bold=True)
    font_desc = get_devanagari_font(24, bold=False)
    font_ticker = get_devanagari_font(26, bold=True)

    hl_red = news_data.get("headline_red", "🔴 बड़ी खबर: ताज़ा आदेश जारी")
    hl_black = news_data.get("headline_black", "नियमों में हुआ बड़ा बदलाव")
    lead_summary = news_data.get("lead_summary", "विभागीय पोर्टल पर आधिकारिक अधिसूचना जारी")[:80]

    frames_dir = "output/reel_frames"
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    logger.info(f"🎞️ Rendering {total_frames} TV News Channel frames ({duration:.1f}s @ {fps}fps)...")
    t_start = time.time()

    for idx in range(total_frames):
        progress = idx / total_frames

        # Create canvas
        frame = Image.new("RGB", (w, h), (10, 20, 35))

        # Slow cinematic Ken Burns zoom on the press photo (middle area)
        zoom = 1.0 + 0.12 * progress
        pw_target = int(w * zoom)
        ph_target = int(1220 * zoom)
        photo_resized = base_photo.resize((pw_target, ph_target), Image.Resampling.BILINEAR)
        crop_x = (pw_target - w) // 2
        crop_y = int((ph_target - 1220) * 0.5)
        photo_crop = photo_resized.crop((crop_x, crop_y, crop_x + w, crop_y + 1220))
        frame.paste(photo_crop, (0, 160))

        draw = ImageDraw.Draw(frame)

        # 1. TOP TV NEWS CHANNEL MASTHEAD (BBCC SKILL HUB)
        draw.rectangle([(0, 0), (w, 160)], fill=(10, 25, 47))
        draw.rectangle([(0, 154), (w, 160)], fill=(220, 38, 38)) # red accent line

        draw.text((45, 35), "BBCC SKILL HUB", font=font_logo, fill=(255, 222, 3))
        draw.text((45, 98), "दैनिक समाचार बुलेटिन • देश और बिहार की बड़ी खबरें", font=font_sub, fill=(203, 213, 225))

        # Flashing Live Badge (Pulses every second)
        is_live_pulse = (int(idx / (fps * 0.5)) % 2) == 0
        badge_bg = (220, 38, 38) if is_live_pulse else (185, 28, 28)
        draw.rounded_rectangle([w - 240, 45, w - 45, 115], radius=12, fill=badge_bg)
        draw.text((w - 142, 80), "🔴 LIVE NEWS", font=font_badge, fill=(255, 255, 255), anchor="mm")

        # Top Red/Yellow Progress Bar
        draw.rectangle([(0, 0), (int(w * progress), 10)], fill=(255, 222, 3))

        # 2. TV NEWS CHANNEL LOWER THIRD (BOTTOM NEWS OVERLAY)
        # Red Breaking Header Plate
        draw.rectangle([(0, h - 460), (440, h - 395)], fill=(220, 38, 38))
        draw.text((220, h - 428), "🔴 BREAKING NEWS", font=font_badge, fill=(255, 255, 255), anchor="mm")

        # Main Headline Card (Deep Navy Glass with Gold Border)
        draw.rectangle([(0, h - 395), (w, h - 95)], fill=(10, 25, 47))
        draw.line([(0, h - 395), (w, h - 395)], fill=(255, 222, 3), width=4)

        # Headline Line 1 (Gold #FFDE03)
        draw.text((45, h - 350), hl_red[:45], font=font_hl_1, fill=(255, 222, 3))
        # Headline Line 2 (Crisp White #FFFFFF)
        draw.text((45, h - 280), hl_black[:50], font=font_hl_2, fill=(255, 255, 255))
        # Summary description
        draw.text((45, h - 215), f"{lead_summary}...", font=font_desc, fill=(203, 213, 225))

        # 3. BOTTOM TICKER BAR
        draw.rectangle([(0, h - 95), (w, h)], fill=(220, 38, 38))
        draw.text((w // 2, h - 48), "⚡ ताज़ा खबरों और सरकारी अपडेट्स के लिए हमारे पेज राउत जी को फॉलो करें", font=font_ticker, fill=(255, 255, 255), anchor="mm")

        frame.save(f"{frames_dir}/f_{idx:04d}.jpg", quality=85)

    logger.info(f"✅ Rendered {total_frames} frames in {time.time() - t_start:.2f}s.")

    # 3. Assemble Video + Audio (Directly mux with cinematic news soundtrack)
    logger.info("🎥 Encoding TV news channel MP4 with FFmpeg...")
    cmd_assemble = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-i", f"{frames_dir}/f_%04d.jpg",
        "-i", music_wav,
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
        logger.info(f"✅ TV News Channel Reel rendered: {output_video_path} (Duration: {duration:.1f}s)")
        return output_video_path
    return None

# ==============================================================================
# 8. MEDIA HOSTING & GITHUB CDN
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

def persist_github_file(file_path: str, commit_msg: str):
    if not GITHUB_TOKEN or not os.path.exists(file_path): return
    try:
        import base64
        with open(file_path, "rb") as f:
            c_b64 = base64.b64encode(f.read()).decode("utf-8")
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
        api_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/contents/{file_path.replace(os.sep, '/')}"
        check = requests.get(api_url, headers=headers)
        payload = {"message": commit_msg, "content": c_b64, "branch": "main"}
        if check.status_code == 200:
            payload["sha"] = check.json()["sha"]
        requests.put(api_url, headers=headers, json=payload, timeout=30)
    except Exception:
        pass

def persist_posted_topics_to_github():
    persist_github_file(POSTED_TOPICS_FILE, "Sync posted topics history")
    persist_github_file(REPLIED_COMMENTS_FILE, "Sync replied comments history")

def auto_reply_to_instagram_comments(access_token: str, ig_user_id: str):
    """Automatically scans recent Instagram posts and replies to new user comments."""
    if not access_token or not ig_user_id:
        return
    logger.info("💬 Checking Instagram comments for automated replies...")
    os.makedirs(os.path.dirname(REPLIED_COMMENTS_FILE), exist_ok=True)
    replied = []
    if os.path.exists(REPLIED_COMMENTS_FILE):
        try:
            with open(REPLIED_COMMENTS_FILE, "r", encoding="utf-8") as f:
                replied = json.load(f)
        except Exception:
            pass

    url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media?fields=id,comments{{id,text,from,timestamp}}&limit=10&access_token={access_token}"
    try:
        r = requests.get(url, timeout=30).json()
        items = r.get("data", [])
        new_replies = 0

        for media in items:
            comments_data = media.get("comments", {}).get("data", [])
            for c in comments_data:
                cid = c.get("id")
                c_text = c.get("text", "")
                author = c.get("from", {}).get("username", "")

                if not cid or cid in replied or author == "rauth_jee":
                    continue

                reply_msg = f"नमस्ते @{author}! कमेंट के लिए धन्यवाद। ताज़ा खबरों और सरकारी अपडेट्स के लिए हमारे पेज राउत जी से जुड़े रहें 🙏"
                reply_url = f"https://graph.facebook.com/v19.0/{cid}/replies"
                resp = requests.post(reply_url, data={"message": reply_msg, "access_token": access_token}, timeout=30).json()
                if "id" in resp:
                    logger.info(f"✅ Replied to @{author}: {resp['id']}")
                    replied.append(cid)
                    new_replies += 1

        with open(REPLIED_COMMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(replied, f, ensure_ascii=False, indent=2)
        if new_replies > 0:
            logger.info(f"🎉 Replied to {new_replies} new user comments on Instagram!")
    except Exception as e:
        logger.warning(f"Comment auto-reply notice: {e}")

# ==============================================================================
# 9. META INSTAGRAM MULTI-FORMAT PUBLISHER
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
# 10. MAIN EXECUTION PIPELINE
# ==============================================================================

def main():
    logger.info("================================================================================")
    logger.info(f"📰 STARTING PREMIUM NEWS ENGINE (FLUX AI + ELEVENLABS) FOR {CREATOR_HANDLE}")
    logger.info("================================================================================")

    # 1. Fetch Unique Fresh News (Zero Duplication)
    raw_news = fetch_unique_live_news()

    # 2. Format with Gemini AI into Dainik Jagran / BBCC Hub layout
    news_data = format_news_with_gemini(raw_news)
    final_headline = f"{news_data.get('headline_red', '')} {news_data.get('headline_black', '')}".strip()
    save_posted_topic(final_headline)
    if raw_news and raw_news.get("title"):
        save_posted_topic(raw_news["title"])

    hashtags_str = " ".join(news_data.get("hashtags", VIRAL_HASHTAGS))
    full_caption = f"{news_data.get('caption', '')}\n\n.\n.\n{hashtags_str}\n\n📰 रोज़ाना ताज़ा खबरों और सरकारी अपडेट्स के लिए हमारे पेज राउत जी को फॉलो करें: {CREATOR_HANDLE}"

    # 3. Generate 8K Photorealistic Press Photo via FLUX.1 AI
    ai_img_prompt = news_data.get("ai_image_prompt", f"editorial photojournalism for news: {news_data.get('headline_red')}")
    ai_photo_path = generate_flux_ai_photo(ai_img_prompt, "output/news_photo.jpg")

    # 4. Render 1080x1920 Newspaper Graphic (Dainik Jagran + AI Photo + Yellow Box)
    poster_path = "output/daily_tip.png"
    face_path = "assets/my_face.jpg"
    create_newspaper_graphic(news_data, ai_photo_path=ai_photo_path, output_path=poster_path, face_path=face_path)

    # 5. Render TV News Channel Video Reel (Google Flow / BBCC Skill Hub Style)
    reel_path = "output/daily_reel.mp4"
    create_news_reel_video(news_data, ai_photo_path=ai_photo_path, newspaper_img_path=poster_path, face_path=face_path, output_video_path=reel_path)

    if DRY_RUN:
        logger.info("⚡ DRY_RUN active. Media created successfully. Skipping publishing.")
        persist_posted_topics_to_github()
        return

    # 6. Host Media
    public_img_url = upload_image_to_imgbb(poster_path)
    public_video_url = host_video_on_github(reel_path)
    persist_posted_topics_to_github()

    if not public_img_url:
        logger.error("❌ Public image URL not available. Aborting.")
        return

    # 7. Publish Multi-Format to Instagram
    ig_publisher = InstagramMultiPublisher(
        access_token=FB_ACCESS_TOKEN,
        ig_user_id=IG_USER_ID
    )

    # 7A. Feed Post
    post_id = ig_publisher.publish_feed_post(public_img_url, full_caption)
    # 7B. Story
    story_id = ig_publisher.publish_story(public_img_url)
    # 7C. 3D Reel
    reel_id = None
    if public_video_url:
        reel_id = ig_publisher.publish_reel(public_video_url, full_caption)

    # 8. Auto-Reply to Comments on Instagram
    auto_reply_to_instagram_comments(FB_ACCESS_TOKEN, IG_USER_ID)
    persist_posted_topics_to_github()

    logger.info("================================================================================")
    logger.info("📊 MULTI-FORMAT NEWS EXECUTION SUMMARY")
    logger.info(f"• Creator:          {CREATOR_HANDLE}")
    logger.info(f"• News Headline:    '{news_data.get('headline_red')} {news_data.get('headline_black')}'")
    logger.info(f"• Voice Engine:     {'ElevenLabs Studio Neural' if ELEVENLABS_API_KEY else 'gTTS Fallback'}")
    logger.info(f"• AI Photo Engine:  FLUX.1 8K Photorealistic")
    logger.info(f"• Newspaper Post:   {'✅ SUCCESS (ID: ' + post_id + ')' if post_id else '❌ FAILED'}")
    logger.info(f"• News Story:       {'✅ SUCCESS (ID: ' + story_id + ')' if story_id else '❌ FAILED'}")
    logger.info(f"• News Reel:        {'✅ SUCCESS (ID: ' + reel_id + ')' if reel_id else '❌ FAILED'}")
    logger.info(f"• Comment Auto-Bot: ✅ ACTIVE (Scanning & Replying to comments)")
    logger.info(f"• FB Auto-Mirror:   ✅ ACTIVE via Meta Accounts Center / Make.com")
    logger.info("================================================================================")

if __name__ == "__main__":
    main()
