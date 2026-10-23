#!/usr/bin/env python3
"""
================================================================================
Cyber Security Social Media Automation Bot
Automated Daily Content & Visual Generation with Cross-Platform Meta Publishing
Runs 24/7 Serverless on GitHub Actions
================================================================================
"""

import os
import sys
import json
import time
import random
import logging
import warnings
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

# Configure UTF-8 for cross-platform console compatibility (avoids Windows cp1252 emoji crash)
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
CREATOR_HANDLE = os.getenv("CREATOR_HANDLE", "@CyberSecurityIntel").strip()
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

# Built-in fallback database in case of API quota exhaustion
FALLBACK_TIPS = [
    {
        "headline": "Beware of MFA Fatigue Attacks",
        "category": "IDENTITY & ACCESS DEFENSE",
        "tip": "Cybercriminals spam your phone with dozens of MFA prompts late at night, hoping you'll click 'Approve' just to silence the notifications. If you receive an unexpected 2FA prompt, never approve it.",
        "action_step": "Disable SMS 2FA and switch to authenticator apps with number matching or hardware FIDO2 security keys.",
        "caption": "🚨 CRITICAL SECURITY ALERT: MFA Fatigue Attacks are on the rise!\n\nAttackers don't always hack in — sometimes they just push notifications until victims break down and click approve.\n\nKey Defense Rules:\n1. Never approve an unexpected push notice.\n2. Always verify the login location.\n3. Switch to number-matching MFA.\n\nStay protected out there!",
        "hashtags": ["#CyberSecurity", "#InfoSec", "#MFA", "#OnlineSafety", "#TechTips"]
    },
    {
        "headline": "Stop Saving Passwords in Browsers",
        "category": "CREDENTIAL SECURITY",
        "tip": "Web browsers store passwords in predictable local directories that common RedLine and Lumma infostealer malwares extract in seconds. A single compromised download can leak all your saved browser logins.",
        "action_step": "Migrate your logins to a dedicated, encrypted password manager with zero-knowledge architecture.",
        "caption": "⚠️ Are your browser-saved passwords actually safe?\n\nInfostealer malware specifically targets Chrome, Edge, and Firefox credential caches. Once infected, all your saved sessions and logins can be exfiltrated in under 5 seconds.\n\nProtect yourself:\n• Use a dedicated zero-knowledge password vault\n• Clear saved browser logins\n• Enable biometric vault locks",
        "hashtags": ["#PasswordSecurity", "#CyberSafety", "#InfoSec", "#DataPrivacy", "#TechSavvy"]
    },
    {
        "headline": "QR Code Phishing (Quishing) Alert",
        "category": "SOCIAL ENGINEERING",
        "tip": "Attackers now place malicious QR codes over parking meters, restaurant tables, and inside fake email attachments. Scanning them bypasses email spam filters and routes your mobile browser straight to credential harvesting pages.",
        "action_step": "Always preview the full URL before opening any link generated from a scanned QR code.",
        "caption": "📱 Think twice before scanning that QR Code!\n\nQuishing (QR Phishing) is exploding because QR codes cannot be easily inspected by standard email security filters.\n\nHow to stay safe:\n1. Check for physical stickers pasted over legitimate QR codes.\n2. Look at the full domain name before entering credentials.\n3. Never authenticate or pay through unverified QR links.",
        "hashtags": ["#Quishing", "#PhishingAwareness", "#CyberDefense", "#TechTrends", "#SecurityTips"]
    }
]

# ==============================================================================
# 1. AI CONTENT GENERATOR (GEMINI API)
# ==============================================================================

def generate_cyber_content() -> Dict[str, Any]:
    """
    Generates a unique viral cyber security tip, caption, and hashtags
    using the Google Gemini API with smart SDK compatibility & fallback.
    """
    logger.info("🤖 Generating Cyber Security Tip with Google Gemini...")
    
    if not GEMINI_API_KEY or "your_gemini" in GEMINI_API_KEY.lower():
        logger.warning("⚠️ Valid GEMINI_API_KEY not configured. Using curated high-impact fallback tip.")
        return random.choice(FALLBACK_TIPS)

    prompt = """
You are an elite Cyber Security Analyst and viral social media creator.
Generate a high-impact, viral, practical daily Cyber Security tip for tech professionals and everyday users.

You must return ONLY a valid JSON object (no markdown code blocks, no explanation) with the following exact keys:
{
  "headline": "Punchy title under 5 words (e.g., 'Beware of MFA Fatigue')",
  "category": "Security domain in 2-3 words (e.g., 'IDENTITY DEFENSE', 'NETWORK SECURITY', 'DATA PRIVACY', 'PHISHING ALERT')",
  "tip": "The main security insight written for an image graphic. Must be under 50 words, clear, high-impact, and easy to understand.",
  "action_step": "A single actionable sentence telling the reader exactly what to do today.",
  "caption": "An engaging, well-formatted Instagram/Facebook caption with a strong hook, bullet points, and a question to drive comments.",
  "hashtags": ["#CyberSecurity", "#InfoSec", "#OnlineSafety", "#TechTips"]
}
"""

    raw_response_text = ""

    # Strategy A: Use modern google-genai SDK if available
    for model_name in ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            raw_response_text = response.text or ""
            logger.info(f"✅ Generated content using google-genai SDK ({model_name}).")
            break
        except Exception as e_genai:
            logger.info(f"Model {model_name} attempt: {e_genai}")
        logger.info(f"Trying google-generativeai SDK fallback (Reason: {e_genai})")
        # Strategy B: Use google-generativeai SDK
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=GEMINI_API_KEY)
            # Try 1.5-flash or 2.0-flash
            try:
                model = legacy_genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
            except Exception:
                model = legacy_genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)
            raw_response_text = response.text or ""
            logger.info("✅ Generated content using google-generativeai SDK.")
        except Exception as e_legacy:
            logger.error(f"❌ Failed to generate with Gemini API: {e_legacy}")
            logger.warning("🔄 Reverting to curated fallback cyber security tip.")
            return random.choice(FALLBACK_TIPS)

    # Clean and parse JSON from response
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
        # Verify required keys
        required_keys = ["headline", "category", "tip", "action_step", "caption", "hashtags"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key in AI response: {key}")
        
        logger.info(f"🎯 Successfully parsed AI Tip: '{data['headline']}' [{data['category']}]")
        return data

    except Exception as parse_err:
        logger.error(f"⚠️ Error parsing Gemini JSON: {parse_err}. Raw text:\n{raw_response_text}")
        return random.choice(FALLBACK_TIPS)

# ==============================================================================
# 2. IMAGE & VISUAL GENERATOR (PILLOW 1080x1920 9:16)
# ==============================================================================

def get_system_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Finds and loads the best available TrueType font across Windows & Linux environments."""
    font_candidates = (
        ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
        if bold
        else ["segoeui.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    )
    search_dirs = [
        os.path.join("assets", "fonts"),
        "C:/Windows/Fonts",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype/liberation",
        "/usr/share/fonts/truetype"
    ]
    for directory in search_dirs:
        for fname in font_candidates:
            fpath = os.path.join(directory, fname)
            if os.path.exists(fpath):
                try:
                    return ImageFont.truetype(fpath, size)
                except Exception:
                    pass
    return ImageFont.load_default()

def wrap_text_lines(text: str, font: ImageFont.ImageFont, max_width: int) -> list:
    """Wraps text into lines that do not exceed max_width."""
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
    """
    Renders an eye-catching vertical 1080x1920 graphic with cyber tech aesthetics,
    glassmorphism card, glowing neon effects, and optional face branding.
    """
    logger.info("🎨 Rendering 1080x1920 Cyber Security Visual Graphic...")
    width, height = 1080, 1920

    # 1. Base Gradient Canvas (Deep Cyber Midnight)
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

    # 4. Typography Preparation
    font_badge = get_system_font(26, bold=True)
    font_cat = get_system_font(28, bold=True)
    font_headline = get_system_font(52, bold=True)
    font_body = get_system_font(36, bold=False)
    font_action_title = get_system_font(26, bold=True)
    font_action_body = get_system_font(30, bold=False)
    font_handle = get_system_font(32, bold=True)
    font_sub = get_system_font(24, bold=False)
    font_footer = get_system_font(28, bold=True)
    font_footer_sub = get_system_font(24, bold=False)

    # 5. UI Layers
    ui_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    uidraw = ImageDraw.Draw(ui_layer)

    # Top Pill Badge
    badge_w, badge_h = 560, 58
    badge_x = (width - badge_w) // 2
    badge_y = 110
    uidraw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=29,
        fill=(0, 240, 255, 25),
        outline=(0, 240, 255, 190),
        width=2
    )
    uidraw.text(
        (width // 2, badge_y + badge_h // 2),
        "SHIELD PROTOCOL • DAILY TIP",
        font=font_badge,
        fill=(0, 240, 255, 255),
        anchor="mm"
    )

    # Creator Branding / Circular Face Overlay
    profile_y = 220
    avatar_size = 140
    avatar_x = 80

    draw_avatar_placeholder = False
    if os.path.exists(face_path):
        try:
            face_img = Image.open(face_path).convert("RGBA")
            face_img = face_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            m_draw = ImageDraw.Draw(mask)
            m_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            ui_layer.paste(face_img, (avatar_x, profile_y), mask)
            
            # Concentric glowing neon ring
            uidraw.ellipse(
                (avatar_x - 3, profile_y - 3, avatar_x + avatar_size + 3, profile_y + avatar_size + 3),
                outline=(0, 240, 255, 230),
                width=4
            )
        except Exception as e:
            logger.warning(f"Could not load face image ({e}), using default cyber badge.")
            draw_avatar_placeholder = True
    else:
        draw_avatar_placeholder = True

    if draw_avatar_placeholder:
        # Draw high-tech cyber shield avatar icon
        uidraw.ellipse(
            (avatar_x, profile_y, avatar_x + avatar_size, profile_y + avatar_size),
            fill=(15, 23, 42, 240),
            outline=(0, 240, 255, 220),
            width=3
        )
        uidraw.text(
            (avatar_x + avatar_size // 2, profile_y + avatar_size // 2),
            "[SEC]",
            font=font_badge,
            fill=(0, 240, 255, 255),
            anchor="mm"
        )

    # Brand Title and Credential
    text_x = avatar_x + avatar_size + 30
    uidraw.text((text_x, profile_y + 35), CREATOR_HANDLE, font=font_handle, fill=(255, 255, 255, 255))
    uidraw.text((text_x, profile_y + 80), "Certified Threat Intel • Daily Defense", font=font_sub, fill=(148, 163, 184, 255))

    # 6. Main Glassmorphism Content Card
    card_margin = 70
    card_x1 = card_margin
    card_x2 = width - card_margin
    card_y1 = 410
    card_y2 = 1690

    # Translucent card container
    uidraw.rounded_rectangle(
        [card_x1, card_y1, card_x2, card_y2],
        radius=40,
        fill=(13, 20, 36, 230),
        outline=(0, 240, 255, 130),
        width=2
    )

    # Category Tag
    tag_y = card_y1 + 50
    category_text = f"// {content.get('category', 'CYBER DEFENSE').upper()}"
    uidraw.text((card_x1 + 60, tag_y), category_text, font=font_cat, fill=(0, 240, 255, 255))

    # Headline
    headline_y = tag_y + 60
    headline_text = content.get("headline", "Cyber Defense Protocol")
    uidraw.text((card_x1 + 60, headline_y), headline_text, font=font_headline, fill=(255, 255, 255, 255))

    # Neon Divider
    div_y = headline_y + 90
    uidraw.line([(card_x1 + 60, div_y), (card_x2 - 60, div_y)], fill=(30, 41, 59, 255), width=2)
    uidraw.line([(card_x1 + 60, div_y), (card_x1 + 250, div_y)], fill=(0, 240, 255, 255), width=3)

    # Body Tip Content (Text wrapping)
    body_y = div_y + 60
    max_text_w = (card_x2 - card_x1) - 120
    tip_text = content.get("tip", "")
    tip_lines = wrap_text_lines(tip_text, font_body, max_text_w)

    for line in tip_lines:
        uidraw.text((card_x1 + 60, body_y), line, font=font_body, fill=(226, 232, 240, 255))
        body_y += 58

    # Inner Action Box
    action_box_y1 = body_y + 50
    action_box_y2 = min(action_box_y1 + 230, card_y2 - 60)
    uidraw.rounded_rectangle(
        [card_x1 + 50, action_box_y1, card_x2 - 50, action_box_y2],
        radius=25,
        fill=(20, 32, 54, 240),
        outline=(139, 92, 246, 160),
        width=2
    )
    uidraw.text(
        (card_x1 + 80, action_box_y1 + 35),
        "⚡ IMMEDIATE ACTION STEP",
        font=font_action_title,
        fill=(167, 139, 250, 255)
    )

    action_text = content.get("action_step", "Review your active security configurations immediately.")
    action_lines = wrap_text_lines(action_text, font_action_body, max_text_w - 40)
    act_y = action_box_y1 + 80
    for aline in action_lines:
        uidraw.text((card_x1 + 80, act_y), aline, font=font_action_body, fill=(241, 245, 249, 255))
        act_y += 42

    # 7. Bottom CTA Footer
    footer_y = height - 150
    uidraw.line([(card_margin, footer_y - 30), (width - card_margin, footer_y - 30)], fill=(30, 41, 59, 200), width=1)
    uidraw.text(
        (width // 2, footer_y),
        "SAVE THIS POST • SHARE TO PROTECT OTHERS",
        font=font_footer,
        fill=(0, 240, 255, 255),
        anchor="mm"
    )
    uidraw.text(
        (width // 2, footer_y + 45),
        f"Follow {CREATOR_HANDLE} for Daily Cyber Defense Intelligence",
        font=font_footer_sub,
        fill=(148, 163, 184, 255),
        anchor="mm"
    )

    # 8. Save Final Composited Image
    final_img = Image.alpha_composite(base, ui_layer).convert("RGB")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_img.save(output_path, "PNG")
    logger.info(f"✅ Graphic rendered and saved to: {output_path}")
    return output_path

# ==============================================================================
# 3. IMAGE HOSTING (FOR INSTAGRAM GRAPH API)
# ==============================================================================

def upload_image_to_public_host(image_path: str) -> Optional[str]:
    """
    Instagram Content Publishing API requires a public HTTPS URL.
    This function uploads the generated graphic to ImgBB (free API)
    or public fallback so Instagram's servers can download it.
    """
    logger.info("☁️ Uploading image to public host for Instagram API...")

    if not os.path.exists(image_path):
        logger.error(f"Image not found at {image_path}")
        return None

    # Primary Host: ImgBB Free API
    if IMGBB_API_KEY:
        try:
            url = "https://api.imgbb.com/1/upload"
            with open(image_path, "rb") as file_bytes:
                payload = {
                    "key": IMGBB_API_KEY,
                    "expiration": 86400 * 7 # Auto-expire after 7 days
                }
                files = {"image": file_bytes}
                res = requests.post(url, data=payload, files=files, timeout=30)
                res_data = res.json()
                if res.status_code == 200 and res_data.get("success"):
                    direct_url = res_data["data"]["url"]
                    logger.info(f"✅ Image uploaded to ImgBB: {direct_url}")
                    return direct_url
                else:
                    logger.warning(f"ImgBB upload error: {res_data}")
        except Exception as e:
            logger.error(f"ImgBB upload failed: {e}")

    # Fallback Host: Free Anonymous Temporary Host (Litterbox/Catbox)
    try:
        logger.info("Attempting fallback upload to Litterbox...")
        url = "https://litterbox.catbox.moe/resources/internals/api.php"
        with open(image_path, "rb") as file_bytes:
            data = {"reqtype": "fileupload", "time": "24h"}
            files = {"fileToUpload": ("cyber_tip.png", file_bytes, "image/png")}
            res = requests.post(url, data=data, files=files, timeout=30)
            if res.status_code == 200 and res.text.startswith("http"):
                direct_url = res.text.strip()
                logger.info(f"✅ Image uploaded to temporary host: {direct_url}")
                return direct_url
    except Exception as e_fb:
        logger.warning(f"Fallback host upload error: {e_fb}")

    logger.warning("⚠️ No public image URL obtained. Instagram posting will be skipped.")
    return None

# ==============================================================================
# 4. META GRAPH API PUBLISHER (FACEBOOK & INSTAGRAM)
# ==============================================================================

class MetaPublisher:
    def __init__(self, access_token: str, page_id: str, ig_user_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.ig_user_id = ig_user_id
        self.graph_base = "https://graph.facebook.com/v19.0"

    def post_to_facebook(self, image_path: str, message: str) -> Optional[str]:
        """
        Publishes the generated image and caption to Facebook Page.
        Uses direct binary multipart upload (no public hosting required).
        """
        logger.info("🚀 Publishing to Facebook Page...")
        if not self.access_token or not self.page_id:
            logger.warning("⚠️ Missing FB_ACCESS_TOKEN or FB_PAGE_ID. Skipping Facebook post.")
            return None

        url = f"{self.graph_base}/{self.page_id}/photos"
        try:
            with open(image_path, "rb") as img_file:
                payload = {
                    "message": message,
                    "access_token": self.access_token
                }
                files = {"source": img_file}
                res = requests.post(url, data=payload, files=files, timeout=45)
                data = res.json()

                if res.status_code == 200 and "id" in data:
                    post_id = data.get("post_id", data["id"])
                    logger.info(f"🎉 Successfully posted to Facebook! ID: {post_id}")
                    return post_id
                else:
                    logger.error(f"❌ Facebook Graph API Error: {json.dumps(data, indent=2)}")
                    return None
        except Exception as e:
            logger.error(f"❌ Exception posting to Facebook: {e}")
            return None

    def post_to_instagram(self, public_image_url: str, caption: str) -> Optional[str]:
        """
        Publishes the image and caption to Instagram Business Account
        via the official 2-step Meta Instagram Content Publishing API:
        Step 1: Create media container
        Step 2: Publish media container
        """
        logger.info("🚀 Publishing to Instagram Business Account...")
        if not self.access_token or not self.ig_user_id:
            logger.warning("⚠️ Missing FB_ACCESS_TOKEN or IG_USER_ID. Skipping Instagram post.")
            return None

        if not public_image_url:
            logger.warning("⚠️ Instagram requires a public image_url. Skipping Instagram post.")
            return None

        # Step 1: Create Container
        container_url = f"{self.graph_base}/{self.ig_user_id}/media"
        container_payload = {
            "image_url": public_image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        try:
            res_container = requests.post(container_url, data=container_payload, timeout=45)
            cdata = res_container.json()
            if "id" not in cdata:
                logger.error(f"❌ Failed to create Instagram container: {json.dumps(cdata, indent=2)}")
                return None
            creation_id = cdata["id"]
            logger.info(f"📦 Instagram Container Created. ID: {creation_id}")

            # Wait briefly for Meta's media processing pipeline
            time.sleep(6)

            # Step 2: Publish Container
            publish_url = f"{self.graph_base}/{self.ig_user_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            res_publish = requests.post(publish_url, data=publish_payload, timeout=45)
            pdata = res_publish.json()

            if res_publish.status_code == 200 and "id" in pdata:
                ig_media_id = pdata["id"]
                logger.info(f"🎉 Successfully published to Instagram! Media ID: {ig_media_id}")
                return ig_media_id
            else:
                logger.error(f"❌ Instagram Publish Error: {json.dumps(pdata, indent=2)}")
                return None

        except Exception as e:
            logger.error(f"❌ Exception publishing to Instagram: {e}")
            return None

# ==============================================================================
# 5. MAIN ORCHESTRATION PIPELINE
# ==============================================================================

def main():
    logger.info("================================================================================")
    logger.info("🛡️ STARTING CYBER SECURITY SOCIAL MEDIA AUTOMATION PIPELINE")
    logger.info("================================================================================")

    # Step 1: Generate AI Content
    content = generate_cyber_content()
    
    # Format Caption & Hashtags
    hashtags_str = " ".join(content.get("hashtags", ["#CyberSecurity", "#InfoSec", "#OnlineSafety"]))
    full_social_caption = f"{content.get('caption', '')}\n\n.\n.\n{hashtags_str}\n\n🛡️ Follow {CREATOR_HANDLE} for daily protection tips."

    # Step 2: Generate Visual Graphic
    output_image_path = "output/daily_tip.png"
    face_branding_path = "assets/my_face.jpg"
    create_cyber_graphic(content, output_path=output_image_path, face_path=face_branding_path)

    # Dry-Run Check
    if DRY_RUN:
        logger.info("⚡ DRY_RUN is active. Graphic generated successfully. Skipping social API calls.")
        logger.info("================================================================================")
        return

    # Step 3: Host Image (Public URL for Instagram)
    public_img_url = upload_image_to_public_host(output_image_path)

    # Step 4: Publish to Meta Platforms
    publisher = MetaPublisher(
        access_token=FB_ACCESS_TOKEN,
        page_id=FB_PAGE_ID,
        ig_user_id=IG_USER_ID
    )

    # 4A. Publish to Facebook
    fb_result = publisher.post_to_facebook(
        image_path=output_image_path,
        message=full_social_caption
    )

    # 4B. Publish to Instagram
    ig_result = None
    if public_img_url:
        ig_result = publisher.post_to_instagram(
            public_image_url=public_img_url,
            caption=full_social_caption
        )
    else:
        logger.warning("Skipping Instagram posting because public image URL is unavailable.")

    # Execution Summary
    logger.info("================================================================================")
    logger.info("📊 EXECUTION SUMMARY")
    logger.info(f"• Content Generated: '{content.get('headline')}'")
    logger.info(f"• Image Created: {output_image_path}")
    logger.info(f"• Facebook Status: {'✅ SUCCESS (ID: ' + fb_result + ')' if fb_result else '⚠️ SKIPPED/FAILED'}")
    logger.info(f"• Instagram Status: {'✅ SUCCESS (ID: ' + ig_result + ')' if ig_result else '⚠️ SKIPPED/FAILED'}")
    logger.info("================================================================================")

if __name__ == "__main__":
    main()
