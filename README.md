# BBCC Skill Hub — Hindi Digital Newspaper

Automatically generates timestamped Hindi editions about Bihar news, government jobs, and education.

## Schedule
GitHub Actions is scheduled every 5 minutes from 06:00 through 18:00 India Standard Time. GitHub uses UTC: 06:00 IST = 00:30 UTC and 18:00 IST = 12:30 UTC. Scheduled runs can be delayed by GitHub; this is not a guaranteed real-time scheduler.

## Output
Each run saves files in the exact folder newpepar/YYYY-MM-DD/:
- HH-MM-SS.html: responsive Hindi newspaper with linked headlines, source labels, and available publication times.
- HH-MM-SS.png: social media poster.
- HH-MM-SS.json: edition metadata and links.
- latest.html: most recent edition at repository root.

## Accuracy
Stories are discovered using Google News RSS. This is a discovery feed, not proof that every claim is true. Headlines link to publishers; job items from non-government domains are labelled as media reports. Always verify vacancies, eligibility, deadlines and fees from the original recruiting department notice.

## Manual test
GitHub → Actions → BBCC Skill Hub Newspaper → Run workflow. This generates an edition. Social posting is not attempted on manual runs.

## Optional Facebook / Instagram publishing
To avoid spamming followers every five minutes, social posting is limited to the 06:00 IST scheduled run. Configure repository secrets FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN, and optionally IG_USER_ID (linked Instagram Professional account). Configure repository variables PUBLIC_SITE_URL (public HTTPS base URL serving generated files) and optionally META_GRAPH_VERSION (a currently supported Meta Graph API version).

Meta publishing requires a configured Meta app, the right Page/Instagram permissions, a valid token and public hosting for Instagram image URLs. Credentials are never stored in source code. Missing credentials cause publishing to be skipped.

## Public hosting
For public clickable editions, enable GitHub Pages in Settings → Pages and choose the main branch/root. Set PUBLIC_SITE_URL to the published site URL. Public Pages makes committed editions publicly reachable.

## Operational notes
The workflow must run successfully in GitHub Actions; check the Actions tab after the first run. Scheduled workflows require Actions to be enabled. GitHub can delay cron runs during load.
