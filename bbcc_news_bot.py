#!/usr/bin/env python3
"""BBCC Skill Hub verified Hindi news poster/reel automation.

Only recent RSS items are eligible. Gemini may summarize a source but cannot invent
facts; the source URL and timestamp are preserved in the output. No news fallback.
"""
from __future__ import annotations
import os, re, json, hashlib, logging, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.utils import parsedate_to_datetime
import requests
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET

OUT = Path("output")
OUT.mkdir(exist_ok=True)
STATE = OUT / "state.json"
LOG = logging.getLogger("bbcc-news")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
TIMEOUT = 20
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Bihar+teacher+recruitment+OR+BPSC+OR+STET+when%3A2d&hl=hi&gl=IN&ceid=IN%3Ahi",
    "https://news.google.com/rss/search?q=Bihar+news+education+government+when%3A2d&hl=hi&gl=IN&ceid=IN%3Ahi",
    "https://news.google.com/rss/search?q=India+education+government+exam+when%3A2d&hl=hi&gl=IN&ceid=IN%3Ahi",
]
HEADERS = {"User-Agent": "BBCC-Skill-Hub-NewsBot/1.0 (source-verifying educational news)"}

def load_state():
    try:
        data = json.loads(STATE.read_text("utf-8"))
        return data if isinstance(data, dict) else {"published": []}
    except (OSError, ValueError):
        return {"published": []}

def fetch_candidates():
    candidates, seen = [], set()
    now = datetime.now(timezone.utc)
    for feed in RSS_FEEDS:
        try:
            response = requests.get(feed, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                url = (item.findtext("link") or "").strip()
                source = (item.findtext("source") or "").strip()
                pub = (item.findtext("pubDate") or "").strip()
                if not title or not url or url in seen:
                    continue
                try:
                    published = parsedate_to_datetime(pub)
                    if published.tzinfo is None: published = published.replace(tzinfo=timezone.utc)
                    published = published.astimezone(timezone.utc)
                except (TypeError, ValueError, OverflowError):
                    continue
                if published > now + timedelta(hours=2) or now - published > timedelta(hours=48):
                    continue
                seen.add(url)
                candidates.append({"title": title, "url": url, "source": source or "Google News RSS",
                                   "published_at": published.isoformat()})
        except (requests.RequestException, ET.ParseError) as exc:
            LOG.warning("RSS feed unavailable: %s", exc)
    candidates.sort(key=lambda x: x["published_at"], reverse=True)
    return candidates

def generate_story(candidate):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is required; refusing to create unverified/fallback news.")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    base = "https://generativelanguage.googleapis.com/v1beta"
    prompt = f"""आप BBCC Skill Hub के हिंदी न्यूज़ संपादक हैं। नीचे दिए गए स्रोत शीर्षक के आधार पर पोस्ट तैयार करें।
तथ्य, संख्या, तारीख, भर्ती पद, आवेदन शुरू होने की बात या सरकारी आदेश खुद से न जोड़ें।
अगर शीर्षक से कोई दावा सत्यापित नहीं होता, उसे निश्चित तथ्य की तरह न लिखें; स्रोत-आधारित सीमित भाषा रखें।
स्रोत शीर्षक: {candidate['title']}
प्रकाशन समय: {candidate['published_at']}
स्रोत: {candidate['source']}
लिंक: {candidate['url']}
केवल valid JSON लौटाएँ, keys: headline (अधिकतम 90 अक्षर), summary (60-90 शब्द, हिंदी), bullets (3 छोटे बिंदु), narration (लगभग 70-100 हिंदी शब्द), caption (हिंदी, स्रोत लिंक शामिल), category (छोटा हिंदी शब्द)."""

    def request_model(name):
        return requests.post(
            f"{base}/models/{name}:generateContent",
            params={"key": key},
            json={"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}},
            timeout=45,
        )

    resp = request_model(model)
    if resp.status_code == 404:
        # Model availability differs by API project; discover models for this key.
        catalog = requests.get(f"{base}/models", params={"key": key}, timeout=20)
        if catalog.ok:
            available = [
                item.get("name", "").removeprefix("models/")
                for item in catalog.json().get("models", [])
                if "generateContent" in item.get("supportedGenerationMethods", [])
                and "gemini" in item.get("name", "").lower()
            ]
            available.sort(key=lambda n: (0 if n == "gemini-2.5-flash" else
                                          1 if "2.5-flash" in n else
                                          2 if "flash" in n.lower() else 3, n))
            alternate = next((name for name in available if name and name != model), None)
            if alternate:
                LOG.warning("Configured Gemini model returned 404; retrying discovered model %s", alternate)
                model = alternate
                resp = request_model(model)
        else:
            LOG.error("Gemini model list request failed with HTTP %s", catalog.status_code)
    if not resp.ok:
        try:
            detail = resp.json().get("error", {}).get("message", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"Gemini API HTTP {resp.status_code} for model {model}: {detail[:1200]}")
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    story = json.loads(text)
    required = ("headline", "summary", "bullets", "narration", "caption", "category")
    if any(not story.get(k) for k in required) or not isinstance(story["bullets"], list):
        raise ValueError("Gemini returned an incomplete news object.")
    story["bullets"] = [str(x)[:180] for x in story["bullets"][:3]]
    story["source_url"] = candidate["url"]
    story["source_title"] = candidate["title"]
    story["source_name"] = candidate["source"]
    story["published_at"] = candidate["published_at"]
    story["id"] = hashlib.sha256(candidate["url"].encode()).hexdigest()
    return story

def font(size, bold=False):
    paths = (["/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
              "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"] if bold else
             ["/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for p in paths:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except OSError: pass
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    words, lines, line = str(text).split(), [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0), test, font=fnt)[2] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def draw_wrapped(draw, text, xy, fnt, fill, max_width, line_gap=10, max_lines=8):
    x, y = xy
    for line in wrap(draw, text, fnt, max_width)[:max_lines]:
        draw.text((x,y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap
    return y

def make_poster(story):
    im = Image.new("RGB", (1080, 1350), "#f8f7f2")
    d = ImageDraw.Draw(im)
    d.rectangle((0,0,1080,14), fill="#c62828")
    d.rectangle((0,14,1080,156), fill="#12233f")
    d.text((52,38), "BBCC SKILL HUB", font=font(48, True), fill="white")
    d.text((55,98), "PTCC + BBCC  |  सफलता का नया ठिकाना", font=font(26), fill="#ffd36a")
    d.text((52,184), "आज की प्रमुख खबर", font=font(30, True), fill="#b71c1c")
    y = draw_wrapped(d, story["headline"], (52,235), font(48, True), "#172033", 970, 12, 3)
    d.line((52,y+10,1028,y+10), fill="#d6b25e", width=4)
    y = draw_wrapped(d, story["summary"], (52,y+34), font(29), "#252525", 970, 12, 5)
    y += 20
    d.rounded_rectangle((45,y,1035,min(1200,y+255)), radius=22, fill="#fff0c2", outline="#e2b64d", width=3)
    d.text((72,y+20), "मुख्य बातें", font=font(32, True), fill="#7b1b1b")
    by = y+70
    for bullet in story["bullets"]:
        d.ellipse((76,by+9,91,by+24), fill="#b71c1c")
        by = draw_wrapped(d, bullet, (108,by), font(24), "#202020", 875, 7, 2) + 7
    d.rectangle((0,1240,1080,1350), fill="#12233f")
    d.text((52,1260), "BBCC SKILL HUB  •  हिंदी में भरोसेमंद जानकारी", font=font(26, True), fill="white")
    d.text((52,1304), "स्रोत लिंक कैप्शन में देखें | पोस्ट करने से पहले खबर जाँचें", font=font(20), fill="#ffd36a")
    path = OUT / "daily_tip.png"
    im.save(path, quality=95)
    return path

def make_reel(story, poster):
    try:
        from gtts import gTTS
        from imageio_ffmpeg import get_ffmpeg_exe
    except ImportError as exc:
        raise RuntimeError("gTTS and imageio-ffmpeg dependencies are required for reels") from exc
    audio = OUT / "narration.mp3"
    gTTS(text=story["narration"], lang="hi", slow=False).save(str(audio))
    # A 9:16 canvas is made from the poster; audio duration determines reel length.
    ffmpeg = get_ffmpeg_exe()
    temp = OUT / "reel_visual.mp4"
    reel = OUT / "daily_reel.mp4"
    subprocess.run([ffmpeg, "-y", "-loop", "1", "-i", str(poster), "-i", str(audio),
                    "-vf", "scale=607:1080:force_original_aspect_ratio=decrease,pad=607:1080:(ow-iw)/2:(oh-ih)/2,scale=608:1080,setsar=1",
                    "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(reel)],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    audio.unlink(missing_ok=True)
    return reel

def publish(story, poster, reel):
    token, page_id = os.getenv("FB_ACCESS_TOKEN","").strip(), os.getenv("FB_PAGE_ID","").strip()
    ig_id = os.getenv("IG_USER_ID","").strip()
    if not token:
        raise RuntimeError("FB_ACCESS_TOKEN is required for live publishing.")
    # Publish Facebook image post directly; do not claim Instagram publication without public media hosting.
    with open(poster, "rb") as f:
        r = requests.post(f"https://graph.facebook.com/v22.0/{page_id}/photos",
            data={"access_token": token, "caption": story["caption"]}, files={"source": f}, timeout=60)
    r.raise_for_status()
    LOG.info("Facebook post published: %s", r.json().get("id", "confirmed"))
    if ig_id:
        imgbb = os.getenv("IMGBB_API_KEY","").strip()
        if not imgbb:
            LOG.warning("Instagram skipped: IMGBB_API_KEY missing; Facebook publication succeeded.")
            return
        with open(poster,"rb") as f:
            up = requests.post("https://api.imgbb.com/1/upload", data={"key":imgbb},
                              files={"image":f}, timeout=60)
        up.raise_for_status()
        public_url = up.json()["data"]["url"]
        container = requests.post(f"https://graph.facebook.com/v22.0/{ig_id}/media",
            data={"image_url":public_url,"caption":story["caption"],"access_token":token}, timeout=60)
        container.raise_for_status()
        creation_id = container.json()["id"]
        status = requests.post(f"https://graph.facebook.com/v22.0/{ig_id}/media_publish",
            data={"creation_id":creation_id,"access_token":token}, timeout=60)
        status.raise_for_status()
        LOG.info("Instagram image post published: %s", status.json().get("id","confirmed"))

def main():
    dry = os.getenv("DRY_RUN","true").lower() in ("1","true","yes")
    state = load_state()
    published = state.get("published", [])
    candidates = fetch_candidates()
    if not candidates:
        raise RuntimeError("No fresh news found in RSS sources (last 48 hours); no fallback will be published.")
    candidate = next((c for c in candidates if hashlib.sha256(c["url"].encode()).hexdigest() not in published), None)
    if not candidate:
        LOG.info("No unseen source items among the fresh headlines; successful no-op, no duplicate will be published.")
        return
    story = generate_story(candidate)
    poster = make_poster(story)
    reel = make_reel(story, poster)
    (OUT / "daily_story.json").write_text(json.dumps(story, ensure_ascii=False, indent=2), "utf-8")
    LOG.info("Generated poster and reel from source: %s", candidate["url"])
    if dry:
        LOG.info("DRY_RUN enabled: media generated; nothing published.")
    else:
        publish(story, poster, reel)
        published.append(story["id"])
        state["published"] = published[-500:]
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), "utf-8")

if __name__ == "__main__":
    main()
