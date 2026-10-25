from __future__ import annotations
import html, json, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
import feedparser
from PIL import Image, ImageDraw, ImageFont
IST=timezone(timedelta(hours=5,minutes=30)); NOW=datetime.now(IST)
DAY=NOW.strftime("%Y-%m-%d"); STAMP=NOW.strftime("%H-%M-%S")
DISPLAY_DATE=NOW.strftime("%d-%m-%Y"); DISPLAY_TIME=NOW.strftime("%H:%M IST")
ROOT=Path("newpepar"); EDITION_DIR=ROOT/DAY; EDITION_DIR.mkdir(parents=True,exist_ok=True)
CATEGORIES=[("बिहार की ताज़ा खबरें","Bihar news","bihar"),("सरकारी नौकरी","Bihar government recruitment vacancy official notification","jobs"),("शिक्षा","Bihar education school university exam result","education")]
OFFICIAL_LINKS=[("BPSC","https://bpsc.bihar.gov.in/"),("BSSC","https://bssc.bihar.gov.in/"),("बिहार सरकार","https://state.bihar.gov.in/"),("बिहार शिक्षा विभाग","https://state.bihar.gov.in/educationbihar/")]
def clean(v): return re.sub(r"\s+"," ",html.unescape(v or "")).strip()
def feed_url(q): return "https://news.google.com/rss/search?q="+quote(q+" when:1d")+"&hl=hi&gl=IN&ceid=IN:hi"
def published_at(e):
    try: return datetime(*e.published_parsed[:6],tzinfo=timezone.utc).astimezone(IST).strftime("%d-%m-%Y %H:%M IST")
    except Exception: return "प्रकाशन समय उपलब्ध नहीं"
def official_domain(u):
    u=(u or "").lower()
    return any(d in u for d in (".gov.in",".nic.in","bpsc.bihar.gov.in","bssc.bihar.gov.in"))
def collect():
    items=[]; seen=set()
    for section,q,cat in CATEGORIES:
        try:
            feed=feedparser.parse(feed_url(q))
            for e in feed.entries[:15]:
                title,link=clean(e.get("title","")),e.get("link","")
                if not title or not link or title.casefold() in seen: continue
                seen.add(title.casefold()); source=clean((e.get("source") or {}).get("title","")) or "Google News feed"
                items.append({"section":section,"category":cat,"title":title,"url":link,"source":source,"published":published_at(e),"summary":clean(re.sub(r"<[^>]*>"," ",e.get("summary","")))[:500],"official_domain":official_domain(link)})
        except Exception as exc: print(f"RSS error ({section}): {exc}")
    return items
def make_page(items):
    parts=[]
    for section,_,cat in CATEGORIES:
        cards=[]
        for x in [z for z in items if z["category"]==cat][:10]:
            warning=""
            if cat=="jobs": warning=("<b class='official'>सरकारी डोमेन का लिंक; नोटिस स्वयं पढ़ें।</b>" if x["official_domain"] else "<b class='warning'>मीडिया रिपोर्ट: आवेदन से पहले आधिकारिक नोटिस की पुष्टि करें।</b>")
            summary=f"<p>{html.escape(x['summary'])}</p>" if x["summary"] else ""
            cards.append("<article><h3><a target='_blank' rel='noopener' href='"+html.escape(x["url"],quote=True)+"'>"+html.escape(x["title"])+"</a></h3>"+summary+"<small>स्रोत: "+html.escape(x["source"])+" · प्रकाशित: "+html.escape(x["published"])+"</small><p>"+warning+"</p></article>")
        if not cards: cards=["<p>इस रन में कोई खबर प्राप्त नहीं हुई। संबंधित आधिकारिक वेबसाइट देखें।</p>"]
        parts.append(f"<section><h2>{html.escape(section)}</h2>{''.join(cards)}</section>")
    links="".join(f"<li><a target='_blank' rel='noopener' href='{u}'>{label}</a></li>" for label,u in OFFICIAL_LINKS)
    return f"""<!doctype html><html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BBCC Skill Hub Newspaper — {DAY} {DISPLAY_TIME}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f2ec;color:#182335;font-family:Arial,'Noto Sans Devanagari',sans-serif;line-height:1.65}}header{{background:#092c54;color:white;padding:28px max(20px,calc((100% - 1000px)/2));border-bottom:7px solid #f0b323}}header h1{{font-size:clamp(32px,5vw,54px);margin:0}}header p{{margin:3px 0}}main{{max-width:1000px;margin:auto;padding:18px}}.notice{{background:#fff1c9;padding:14px;border-left:5px solid #d49b16;border-radius:4px}}section{{background:white;padding:20px;margin:18px 0;border-radius:10px;box-shadow:0 2px 10px #0001}}h2{{margin-top:0;border-bottom:2px solid #e1ad27;padding-bottom:8px}}article{{padding:14px 0;border-bottom:1px solid #e3e6ea}}h3{{margin:0 0 7px;font-size:20px}}a{{color:#07559a;overflow-wrap:anywhere}}small{{color:#5f6978}}.warning{{color:#8b4b00}}.official{{color:#176b42}}footer{{text-align:center;padding:22px;color:#5f6978}}</style></head><body><header><h1>BBCC Skill Hub</h1><p>दैनिक डिजिटल समाचारपत्र</p><p>बिहार · सरकारी नौकरी · शिक्षा</p><p>दिनांक: {DISPLAY_DATE} | संस्करण समय: {DISPLAY_TIME}</p></header><main><p class="notice"><b>संपादकीय सूचना:</b> यह स्वचालित समाचार संकलन है। खबरों के साथ स्रोत लिंक और उपलब्ध प्रकाशन समय दिया गया है। नौकरी, परिणाम, पात्रता, शुल्क और अंतिम तिथि केवल विभाग की मूल अधिसूचना से सत्यापित करें।</p>{''.join(parts)}<section><h2>आधिकारिक वेबसाइटें</h2><ul>{links}</ul></section></main><footer>BBCC Skill Hub · {DAY} {DISPLAY_TIME} · मूल स्रोत से पुष्टि करें।</footer></body></html>"""
def get_font(size):
    for p in ["/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf","/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Regular.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if Path(p).exists():
            try: return ImageFont.truetype(p,size)
            except Exception: pass
    return ImageFont.load_default()
def make_poster(items,path):
    im=Image.new("RGB",(1080,1350),"#f5f1e7"); d=ImageDraw.Draw(im)
    d.rectangle((0,0,1080,230),fill="#092c54"); d.rectangle((0,220,1080,235),fill="#f0b323")
    d.text((48,34),"BBCC SKILL HUB",font=get_font(52),fill="white"); d.text((50,106),"दैनिक डिजिटल समाचारपत्र",font=get_font(32),fill="#ffcf58"); d.text((50,172),f"{DISPLAY_DATE} | {DISPLAY_TIME}",font=get_font(25),fill="white")
    y=270
    for section,_,cat in CATEGORIES:
        d.rounded_rectangle((40,y,1040,y+56),radius=10,fill="#e3e8ee"); d.text((60,y+8),section,font=get_font(29),fill="#092c54"); y+=72
        selected=[x for x in items if x["category"]==cat][:2] or [{"title":"ताज़ा अपडेट के लिए वेबसाइट देखें"}]
        for x in selected:
            lines=[]; line=""
            for word in x["title"].split():
                candidate=(line+" "+word).strip()
                if d.textbbox((0,0),candidate,font=get_font(22))[2]>960 and line: lines.append(line); line=word
                else: line=candidate
            if line: lines.append(line)
            for part in lines[:2]: d.text((62,y),part,font=get_font(22),fill="#182335"); y+=32
            y+=8
        y+=16
        if y>1110: break
    d.line((42,1205,1038,1205),fill="#c6bca8",width=2); d.text((48,1230),"पूरी खबरें और स्रोत लिंक: HTML संस्करण देखें",font=get_font(22),fill="#092c54"); d.text((48,1275),"नौकरी की पुष्टि आधिकारिक नोटिस से करें",font=get_font(20),fill="#555555"); im.save(path,format="PNG")
def main():
    items=collect(); page=make_page(items); hp=EDITION_DIR/f"{STAMP}.html"; pp=EDITION_DIR/f"{STAMP}.png"
    hp.write_text(page,encoding="utf-8"); make_poster(items,pp); Path("latest.html").write_text(page,encoding="utf-8")
    meta={"date":DAY,"time_ist":DISPLAY_TIME,"edition":str(hp),"poster":str(pp),"story_count":len(items),"stories":items}
    (EDITION_DIR/f"{STAMP}.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Generated {hp}; stories={len(items)}")
    if not items: print("WARNING: no RSS items fetched; inspect feed/network availability.")
if __name__=="__main__": main()
