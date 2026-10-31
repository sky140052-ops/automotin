# BBCC Social Media Automation (Approval Queue)

This folder contains a separate, approval-first social media workflow. It does not change the existing newspaper automation.

## Daily schedule (India Standard Time)

- 08:00
- 12:00
- 16:00
- 20:00

GitHub Actions creates an approval-request issue at each scheduled time. The issue is a reminder/queue item only.

## Important current limitation

GitHub Actions cannot start a ChatGPT conversation or ask ChatGPT to generate an image by itself. The image must first be created in ChatGPT and uploaded to the repository (or supplied through a connected image-generation API).

No Facebook or Instagram publishing is enabled yet. Before publishing can be implemented, the account owner must configure Meta's official API access and repository secrets. Never put access tokens in source code.

## Approval rule

The workflow is intentionally approval-only. A human must review the final image and caption and explicitly approve each post. Scheduled issue creation does not publish anything.

## Planned Meta integration

After Meta API credentials and permissions are configured, a separate publish workflow can publish only approved assets. It should validate the image URL, caption, platform account IDs, and approval state before calling Meta Graph API.
