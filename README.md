# 🛡️ 24/7 Cloud Automated Cyber Security Social Media Bot

An enterprise-grade, serverless social media automation engine running 24/7 on **GitHub Actions**. It automatically leverages Google Gemini AI to craft viral daily Cyber Security insights, renders high-DPI vertical graphics (1080x1920) with personal face branding using Pillow, and publishes them cross-platform to **Instagram Business** and **Facebook Pages** via the Meta Graph API.

---

## 🚀 Key Features

- **24/7 Serverless Automation**: Zero local machine dependency — runs automatically on GitHub Actions using cron scheduling (`schedule: 30 4 * * *`).
- **Google Gemini AI Engine**: Generates unique, viral, educational cybersecurity tips under 50 words with engaging captions and 3-5 curated hashtags.
- **Glassmorphism Visual Studio**: Generates 1080x1920 high-resolution vertical graphics (9:16) with deep cyber gradients, glowing neon halos, matrix overlays, and structured actionable steps.
- **Dynamic Face Branding**: Automatically overlays your face (`assets/my_face.jpg`) with circular anti-aliased cropping and electric glowing cyan borders, with a clean shield badge fallback.
- **Meta Graph API Auto-Publishing**:
  - Direct binary upload to **Facebook Pages**.
  - Two-stage containerized publishing to **Instagram Business Accounts** via fast cloud image hosting.
- **Resilient Fallback Architecture**: Includes built-in curated threat intelligence fallback data to ensure your daily post **never fails** even during upstream API outages.

---

## 📁 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── automation.yml         # GitHub Actions 24/7 Cron Runner
├── assets/
│   ├── my_face.jpg                # (Optional) Your face photo for branding
│   └── fonts/                     # (Optional) Custom TrueType fonts
├── output/
│   └── daily_tip.png              # Auto-generated daily 1080x1920 graphic
├── .env.example                   # Local development environment template
├── .gitignore                     # Git ignore rules for secrets and temp files
├── main.py                        # Production orchestration engine
├── requirements.txt               # Python package dependencies
└── README.md                      # Documentation & Hindi Deployment Guide
```

---

## ⚙️ Environment Variables & GitHub Secrets

| Secret Name | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | **Yes** | Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `FB_ACCESS_TOKEN` | **Yes** | Long-Lived Meta User / Page Access Token with posting permissions |
| `FB_PAGE_ID` | **Yes** | Facebook Page ID (Numeric ID from Page About / Meta Business Suite) |
| `IG_USER_ID` | **Yes** | Instagram Business Account ID (Numeric ID linked to FB Page) |
| `IMGBB_API_KEY` | Recommended | Free API key from [ImgBB](https://api.imgbb.com/) for public image hosting (Required for Instagram API) |
| `CREATOR_HANDLE` | Optional | Custom handle for branding (e.g. `@CyberSecurityIntel`) |
| `DRY_RUN` | Optional | Set to `true` to test graphic generation without publishing |
