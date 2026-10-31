# BBCC Social Media Automation (Approval Queue)

This is a separate approval-first queue. Existing newspaper generation remains scheduled independently.

## Daily approval reminders (India Standard Time)

- 08:00
- 12:00
- 16:00
- 20:00

GitHub Actions creates an approval-request issue at each slot. The issue is a reminder only; it does not publish.

## Current repository integration

The repository already has secrets named `FB_ACCESS_TOKEN`, `FB_PAGE_ID`, `IG_USER_ID`, `GEMINI_API_KEY`, `IMGBB_API_KEY`, `CREATOR_HANDLE`, and `ELEVENLABS_API_KEY`. Secret names being present does not prove that tokens are valid or have the required Meta permissions. Secret values are not read or printed by this workflow.

The existing `main.py` contains Instagram publishing calls. To honour the approval-first requirement, both scheduled newspaper workflows now set `DRY_RUN: 'true'`. They can continue generating newspaper/reel assets, but their Instagram publishing functions must not publish live content. The newspaper automation files and schedules remain in place.

## Approval rule

A human must review the final image and caption and explicitly approve each post. No live publish workflow is connected yet. Do not add a live publishing step until an approved asset, caption, platform target, and explicit approval can be validated together.

## Important limitation

GitHub Actions cannot start a ChatGPT conversation or invoke ChatGPT's built-in image generation. Image creation must happen in ChatGPT or through a separately configured image-generation API. The current queue creates approval reminders only; it does not yet create image previews or upload images automatically.

## Meta integration checklist

Before enabling live publishing, validate the Page and Instagram account relationship, token validity, required permissions, and media URL accessibility using Meta's official API. Keep all credentials in GitHub Actions secrets; never commit or paste token values into source files or issues.
