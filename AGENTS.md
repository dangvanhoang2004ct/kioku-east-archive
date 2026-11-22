# KIOKU shared workspace — Codex Mac + Google Antigravity

Scope: this repository only. KIOKU's website lives in `kioku-v4/`. Do not mix this project with Momo Matcha or RoleFit.

## Startup (both agents)
1. Read `kioku-v4/dang-lam.md` and `kioku-v4/ghi-chu/muc-luc.md`; open only relevant additional notes.
2. Follow `kioku-v4/chatgpt.md` and `kioku-v4/design-rule.md`. These are the existing authoritative project rules; this file only shares them with IDE agents.
3. Inspect the current Git branch and the target PR before changing any source. Historical progress notes are not proof of a successful test or deployment.

## Collaboration
- **Antigravity:** local source inspection, Blender/GLB iteration, focused implementation and technical QA in an isolated feature branch or worktree.
- **Codex Mac:** release-oriented review, merge only when authorized, and verify GitHub Actions / Cloudflare deploy. Do not redo design or sculpt without a new explicit assignment.
- Never let two agents edit the same working tree concurrently. Use a separate worktree/branch for concurrent tasks, and exchange changes via commits/PRs, not by copying files between editors.
- Use English for all prompts intended for Codex.
- Preserve approved KIOKU identity, seven collector pages, existing Search/Filter/Saved/Compare/Finder functionality and mobile-first UX.
- For the dragon, use **one rigged 3D model**, owner artwork as reference, and static art only as a fallback. V4 and the linked PRs are **review work, not approved production**.
- Never auto-merge or publish to Production. Require owner approval and real Safari/Chromium GPU QA for animation changes.
- Do not add dependencies, dashboards, or duplicate documents without a concrete need. Never commit secrets.

## Reports
Keep reports short: Changed / Tested / Blocked / Owner action.
Include branch, commit, PR, Preview URL when verified. Never claim the Mac app is connected or GPU QA passed without direct evidence.

## Local setup
Open **the same local Git repository** in Codex Mac and Antigravity. Git and this file provide the shared context; this is not a real-time remote-control integration between the two apps.
