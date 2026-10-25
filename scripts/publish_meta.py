import os, sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import requests
IST=timezone(timedelta(hours=5,minutes=30)); now=datetime.now(IST)
if now.strftime("%H:%M")!="06:00" and os.getenv("FORCE_SOCIAL_PUBLISH")!="true":
    print("Social posting skipped: only the 06:00 IST edition is eligible."); sys.exit(0)
page_id=os.getenv("FB_PAGE_ID","").strip(); token=os.getenv("FB_PAGE_ACCESS_TOKEN","").strip(); ig_id=os.getenv("IG_USER_ID","").strip()
version=os.getenv("META_GRAPH_VERSION","v23.0").strip(); public=os.getenv("PUBLIC_SITE_URL","").strip().rstrip("/")
if not (page_id and token and public): print("Social posting skipped: configure FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN and PUBLIC_SITE_URL."); sys.exit(0)
day=now.strftime("%Y-%m-%d"); directory=Path("newpepar")/day; pngs=sorted(directory.glob("*.png"))
if not pngs: print("No poster found; skip publishing."); sys.exit(0)
poster=pngs[0]; poster_url=f"{public}/{poster.as_posix()}"; edition_url=f"{public}/latest.html"
caption=f"📰 BBCC Skill Hub — दैनिक समाचारपत्र | {day}\n\nबिहार की खबरें • सरकारी नौकरी • शिक्षा\nभर्ती और आवेदन की जानकारी आधिकारिक अधिसूचना से जाँचें।\nपूरी खबरें: {edition_url}\n\n#BBCCSkillHub #BiharNews #BiharJobs #Education #SarkariNaukri"
base=f"https://graph.facebook.com/{version}"
with poster.open("rb") as image:
    res=requests.post(f"{base}/{page_id}/photos",data={"access_token":token,"caption":caption},files={"source":(poster.name,image,"image/png")},timeout=60)
if not res.ok: raise SystemExit(f"Facebook publishing failed: {res.status_code} {res.text[:800]}")
print("Facebook Page post created.")
if ig_id:
    create=requests.post(f"{base}/{ig_id}/media",data={"image_url":poster_url,"caption":caption,"access_token":token},timeout=60)
    if not create.ok: raise SystemExit(f"Instagram media creation failed: {create.status_code} {create.text[:800]}")
    pub=requests.post(f"{base}/{ig_id}/media_publish",data={"creation_id":create.json().get("id"),"access_token":token},timeout=60)
    if not pub.ok: raise SystemExit(f"Instagram publishing failed: {pub.status_code} {pub.text[:800]}")
    print("Instagram post published.")
else: print("Instagram skipped: IG_USER_ID not configured.")
