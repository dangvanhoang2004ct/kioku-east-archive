# KIOKU — AGENTS.md (canonical repository instructions)

Scope: KIOKU only (dangvanhoang2004ct/kioku-east-archive), website at kioku-v4/. Never apply Momo Matcha rules or alter that repo.

## Before any change
- Read kioku-v4/dang-lam.md and kioku-v4/ghi-chu/muc-luc.md first, then only relevant notes and source. Read kioku-v4/chatgpt.md and kioku-v4/design-rule.md when task-relevant, respecting approved brand decisions.
- Identify actual HEAD, base branch, open PRs, worktrees and active build path. KIOKU V7 is currently on Draft PR #10, commit f558ee561d8a9ce44a704637a6eef11612145156; main is NOT V7. Preserve V7 and its parent branch history.
- BEFORE WRITING ANYTHING NEW, CHECK IF IT ALREADY EXISTS. Reuse existing page markup, components, data adapters and feature logic. Do not rebuild the app or add framework/dependencies without demonstrated need.

## Beginner-readable clean architecture
- Keep this app organized so a beginner can read it. ONE JOB PER FILE, explicit names, small interfaces, no duplicate logic or unnecessary abstraction.
- Screens go in kioku-v4/pages/: one source entry per existing screen: Home (index.html), Collection (collection.html), Finder (finder.html), Reference Detail (work.html), Condition Guide (condition-guide.html), Journal (journal.html), About (about.html). These public HTML routes already exist in kioku-v4/; first determine their source/build ownership. Extract source to pages/ incrementally only if useful while retaining the exact existing public URLs and deep links in built output.
- Shared UI pieces go in kioku-v4/components/: only genuinely reused header, footer, navigation, search dialog, cards, viewer etc. Preserve accessibility, focus, keyboard operation and CSS behavior. No templating framework required.
- Loading/saving/reading data goes in kioku-v4/data/ when it has a real job. First reuse existing modules in features/catalog/, features/storefront/, features/condition/ and features/inventory/. Data adapters should own catalogue loading, browser persistence/favorites, condition notes and export where already implemented. Do NOT invent a new DB/backend or move privileged operations into browser code.
- Domain behavior stays in existing features/ modules; pages compose views, components own reusable presentation, data owns persistence and I/O.
- MAX 300 LINES per new or modified HANDWRITTEN SOURCE FILE. Split by coherent responsibility, not arbitrary size or minification. Existing untouched legacy code above 300 lines is a reported debt, not a reason to rewrite it blindly. Binary GLB, Blender .blend, vendor files, generated bundles and machine exports are exempt. Handwritten Blender generators and WebGL renderer are not exempt when edited, but do not change the mesh, rig or generated assets for this housekeeping task.
- Code should be visibly readable: single-line compressed HTML, CSS or JS is not considered clean merely because the line count is low. Keep simple build tools and static output; preserve exact paths.

## Nonregression and brand constraints
- Keep all seven English pages and working search, maker/line filters, sort, saved references, comparison (max 3), Finder, detail zoom, local condition notes/copy/export, mobile navigation and shareable URL state.
- Keep reference catalogue separate from real physical stock. Never invent products, prices, authentication, ratings, inventory, policies, checkout or transaction outcomes.
- Preserve approved Shelf Echo assets and ONE authentic volumetric River Guardian V7: no replacement GLB, geometry/armature/animation edits or extra decorative dragon. Retain 10 bones, six materials, six-second swim, Pause/Play, pointer/keyboard orbit, reduced-motion and no-WebGL fallback. Protect user-approved layout and mobile CTA. Do not assert GPU render passes based only on mocks/build.
- Respect current Cloudflare Pages build conventions; NO merge, Production deployment, or force-push without owner's approval. Do not modify KIOKU bridge or Momo bridge outside explicitly approved scope.

## Implementation and Codex acceptance gates
P0 — AUDIT. Map seven public routes to sources, shared code, data/state, build output and dependencies. Inventory existing modules and handwritten files above 300 lines, duplication, existing QA and V7 stacked-PR ancestry. Compare to rules before deciding file creation.
P1 — PAGES. On an isolated V7-based KIOKU branch/worktree, extract page source incrementally; start with low-risk static pages, then commerce-independent collector features, leaving the GLB alone.
P2 — SHARED/DATA/READABILITY. Extract only justified shared UI and I/O adapters, retaining one responsibility per file and <=300 lines for new/touched handwritten source. Keep output behavior and URLs equivalent.
P3 — FUNCTION & SAFETY. Run applicable npm test/build, link, import, navigation, favorites, compare, filters, Finder, zoom, notes, accessibility and security regression checks; no fabricated stock or external transactions.
P4 — INDEPENDENT QA. Antigravity returns commits and Draft PR. Codex Web independently reviews diff and test evidence, including real Safari/WebKit and Chromium GPU QA at 390x844 and 1440px for impacted 3D work, Pause/Play, orbit, reduced-motion and fallback. Record PASS/FAIL/NOT RUN per check and exact SHA.
P5 — RELEASE. Cloudflare Preview only when authorized; verify URL and deploy SHA, owner visual approval, then require explicit permission before merge or Production deployment.

Bridge safety: KIOKU Bridge currently operates READ_ONLY. It may receive GitHub Issue audit tasks, NOT direct source editing until owner AND local operator explicitly authorize feature_edit with isolated worktree and validated restrictions. Never broaden its permissions silently. No change to Momo.

Final Codex report: each P0-P5 = DONE / IN PROGRESS / BLOCKED / NOT STARTED, with commit/PR, files, actual test result PASS/FAIL/NOT RUN, blocking defects, corrective next action. Say COMPLETE only when every required condition is verified, else INCOMPLETE. Update existing status/notes after verified changes; do not duplicate documentation. Never expose tokens, secrets or personal data.
