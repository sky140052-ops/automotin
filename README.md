# BBCC Skill Hub — Daily AI News Automation

Daily Hindi news poster/reel automation for **BBCC SKILL HUB** and **PTCC + BBCC**. The active workflow entry point on this branch is `bbcc_news_bot.py`.

## What it does
- Collects recent candidate headlines from Google News RSS (Bihar education/jobs and national education).
- Rejects items without a parseable timestamp or older than 48 hours.
- Uses Gemini to create a Hindi summary while preserving the source link and source title.
- Fails closed when no recent RSS item or Gemini API key is available; it does not publish hardcoded fallback news.
- Generates a 1080×1350 original BBCC-branded poster, Hindi narration, and an MP4 reel.
- Can publish a Facebook Page photo post; Instagram image posting is attempted only when IG_USER_ID and IMGBB_API_KEY are configured.
- Keeps processed source IDs in output/state.json and uses GitHub Actions cache to restore/save the state between scheduled runs.

## GitHub Actions setup
In repository **Settings → Secrets and variables → Actions**, add:
- `GEMINI_API_KEY` — required.
- `FB_ACCESS_TOKEN` and `FB_PAGE_ID` — required for scheduled live publication.
- `IG_USER_ID` and `IMGBB_API_KEY` — optional for Instagram image posts.
- Optional repository variable `GEMINI_MODEL` (default `gemini-2.5-flash`).

Workflow runs daily at 08:00 IST. Use **Actions → BBCC Skill Hub Daily AI News Automation → Run workflow**. Manual runs default to `dry_run=true`; generated files are uploaded as a workflow artifact. Set `dry_run=false` only after verifying the generated output and credentials.

## Local run
```bash
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env with your own credentials
python bbcc_news_bot.py
```

## Important limitations
- RSS headline and timestamp are the discovery source, not proof that every underlying claim is independently confirmed. Review the source article before public posting.
- Instagram publishing depends on Meta account permissions, account linkage, Graph API availability, and a reachable image host.
- Generated output needs visual review for Hindi font availability and line wrapping.
- The legacy `main.py` is retained on this branch for comparison, but the updated workflow does not execute it.
