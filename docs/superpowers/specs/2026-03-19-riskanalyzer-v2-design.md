# RiskAnalyzer v2 — Design Spec

## Overview

RiskAnalyzer is a web-based CVE quiz game that helps security professionals and students sharpen their intuition for vulnerability risk assessment. v2 is a ground-up rebuild: Svelte + Vite replaces vanilla HTML/JS, the data pipeline is enriched with deep explanations, and the game adds adaptive difficulty, progress tracking, and a modern dark UI.

Hosted statically on GitHub Pages. No backend.

## Goals

1. **Learning over quizzing** — every answer teaches something through rich post-answer explanations
2. **Adaptive challenge** — difficulty adjusts to the player so it's never boring or frustrating
3. **Track improvement** — players see their progress, weak areas, and get practice suggestions
4. **Classroom-ready** — instructors can share filtered quiz links; students can export progress
5. **CVSS 4.0 support** — keep up with the current scoring standard alongside 3.x

## Architecture

```
GitHub Action (daily cron)
  ├── download_cves.py   — downloads NVD JSONL data (with retry + validation)
  ├── enrich_cves.py     — fetches CWE definitions from MITRE, generates
  │                         structured explanations, CVSS rationale
  │                         → outputs src/data/enriched_cves.json
  ├── npm run build      — Vite builds the Svelte app
  └── deploy             — uploads dist/ to GitHub Pages

Svelte + Vite App (fully static, client-side only)
  ├── Game Engine        — adaptive difficulty, question generation, scoring
  ├── Explainer          — post-answer deep explanations from pre-baked data
  ├── Progress System    — localStorage-based tracking, weak area detection
  └── UI Layer           — dark theme, animations, progress visualizations
```

**Data flow:** Python enriches CVE data at build time → JSON imported by the Svelte app at build time → all game logic and progress tracking runs client-side with localStorage.

## Data Enrichment Pipeline

### Input

`download_cves.py` downloads the NVD dataset from `https://nvd.handsonhacking.org/nvd.jsonl` (upgrade from HTTP to HTTPS). Bug fix: add retry logic (3 attempts with exponential backoff) and validate the downloaded file parses as valid JSON before proceeding. If HTTPS is unavailable, fall back to HTTP with a warning.

### Enrichment (`enrich_cves.py`)

New script that runs after `download_cves.py`.

Steps:
1. Download the CWE XML dictionary from MITRE (cached locally, updated weekly). If download fails, fall back to the last cached copy. If no cache exists, fail the build.
2. Load the NVD JSONL and filter (post-2022, non-rejected, valid CWE, valid CVSS score)
3. For each CVE:
   - Extract CVSS 3.0/3.1 score and vector string from `cve.metrics.cvssMetricV31[0].cvssData.baseScore` and `.vectorString` (fall back to `cvssMetricV30` path)
   - Extract CVSS 4.0 score and vector string from `cve.metrics.cvssMetricV40[0].cvssData.baseScore` and `.vectorString` (null when unavailable)
   - Look up CWE name, description, and map to a simplified category
   - Parse CVSS vector components into plain-English rationale using template-based generation (see Explanation Generation below)
   - Generate an explanation connecting the CVE description to its CWE classification (see Explanation Generation below)
   - Identify common confusion CWEs from MITRE CWE taxonomy relationships (`<Related_Weaknesses>` — PeerOf, CanPrecede, ChildOf) plus a curated static mapping for the most common CWE pairs
   - Assign a difficulty tier (1-5) based on CWE ambiguity and CVSS score clustering (see Difficulty Tier Assignment below)
4. Sample ~1000 CVEs using stratified sampling: target ~200 per tier. If a tier has fewer than 200 candidates, take all available and redistribute remaining slots to adjacent tiers.
5. Output `src/data/enriched_cves.json`

### Explanation Generation

Explanations are generated using **template-based generation** at build time — no LLM API calls.

**CWE explanations** use templates that combine:
- The CWE's official name and description from MITRE
- Keyword matching between the CVE description and CWE-associated terms (see keyword lists below)
- Template: `"This CVE is classified as {CWE_ID} ({CWE_NAME}) because the description references {MATCHED_KEYWORDS}. {CWE_SHORT_DESCRIPTION}"`

**CVSS rationale** uses vector string parsing:
- Each CVSS metric component (AV, AC, PR, UI, S, C, I, A for v3.x; expanded set for v4.0) is mapped to a plain-English phrase via a static lookup table
- Template: `"Score of {SCORE}: {AV_TEXT}, {AC_TEXT}, {PR_TEXT}. Impact: {C_TEXT}, {I_TEXT}, {A_TEXT}."`

**Common mixup explanations** use CWE definition comparison:
- Template: `"{CONFUSION_CWE} ({CONFUSION_NAME}) — {KEY_DIFFERENTIATOR}"` where `KEY_DIFFERENTIATOR` is derived from comparing the CWE descriptions (e.g., "targets database queries, not HTML output")
- A curated differentiator table covers the ~50 most common CWE confusion pairs. For pairs not in the table, fall back to showing just the confusion CWE's name and description.

**Keyword lists for CWE matching** (examples, full lists defined in code):
- CWE-79 (XSS): `["script", "XSS", "cross-site", "reflected", "stored", "DOM", "sanitiz", "escap", "HTML", "JavaScript"]`
- CWE-89 (SQLi): `["SQL", "query", "injection", "database", "parameteriz"]`
- CWE-787 (Out-of-bounds Write): `["buffer", "overflow", "out-of-bounds", "write", "memory", "heap", "stack"]`
- etc. (~30-40 CWE keyword lists covering the most common CWEs)

### Per-CVE Data Structure

```json
{
  "cve": "CVE-2024-1234",
  "description": "...",
  "cvss3_score": 7.5,
  "cvss3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
  "cvss3_rationale": "High score due to network-accessible attack vector with no authentication required, but limited to confidentiality impact only.",
  "cvss4_score": 8.2,
  "cvss4_vector": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N",
  "cvss4_rationale": "...",
  "cwe": "CWE-79",
  "cwe_name": "Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
  "cwe_description": "The product does not neutralize or incorrectly neutralizes user-controllable input before it is placed in output...",
  "cwe_category": "injection",
  "explanation": "This CVE is classified as CWE-79 because the description indicates user-supplied input is reflected in web output without sanitization.",
  "common_confusions": ["CWE-89", "CWE-94"],
  "difficulty_tier": 2
}
```

Fields `cvss4_score`, `cvss4_vector`, and `cvss4_rationale` are null when CVSS 4.0 data is not available for a CVE.

### CWE Categories

Simplified mapping for filtering and progress tracking:
- **injection** — CWE-79, CWE-89, CWE-94, etc.
- **memory** — CWE-119, CWE-120, CWE-125, CWE-787, etc.
- **auth** — CWE-287, CWE-306, CWE-862, etc.
- **crypto** — CWE-327, CWE-330, CWE-338, etc.
- **config** — CWE-732, CWE-269, CWE-276, etc.
- **info-disclosure** — CWE-200, CWE-209, CWE-532, etc.
- **other** — anything not in the above

### Difficulty Tier Assignment

Tiers 1-5. Each CVE gets a composite score (0-100) from three weighted factors:

1. **CWE ambiguity (40%):** Number of related CWEs in the MITRE taxonomy (PeerOf, ChildOf). More relations = higher difficulty. Normalized to 0-100.
2. **CVSS score clustering (30%):** Distance from the nearest "round number" boundary (x.0, x.5). Closer = harder to guess = higher difficulty. E.g., 7.1 is harder than 9.8.
3. **Description clarity (30%):** Keyword match strength. If the CVE description contains exact CWE-associated keywords (from the keyword lists above), it scores lower difficulty. Score = `100 - (matched_keywords / total_keywords_for_cwe * 100)`.

Composite score mapped to tiers: 0-20 = tier 1, 21-40 = tier 2, 41-60 = tier 3, 61-80 = tier 4, 81-100 = tier 5.

If tiers are heavily skewed after scoring, adjust tier boundaries to achieve roughly 200 CVEs per tier from the candidate pool.

## Game Engine

### Game Modes

| Mode | Question | Answer choices |
|---|---|---|
| CVSS 3.x | "What is this CVE's CVSS 3.x Base Score?" | 4 numeric options |
| CVSS 4.0 | "What is this CVE's CVSS 4.0 Base Score?" | 4 numeric options (only CVEs with v4 data; mode hidden if <50 CVEs have v4 data) |
| CWE | "What is this CVE's CWE?" | 4 CWE options |
| Mixed | Alternates between all three types | 4 options per question |

### Round Configuration

- Round length: 10, 20, or 30 questions (default 20)
- Optional CWE category filter (e.g., "injection only")
- Category filter can be set via URL query param for classroom link sharing

**Supported URL query params:**
- `mode` — `cvss3`, `cvss4`, `cwe`, `mixed` (default: show mode select screen)
- `category` — any valid CWE category slug: `injection`, `memory`, `auth`, `crypto`, `config`, `info-disclosure`
- `length` — `10`, `20`, `30` (default: 20)
- `tier` — `1`-`5` to lock difficulty (disables adaptive; useful for classrooms)
- Invalid params are silently ignored, falling back to defaults

### Adaptive Difficulty

Tracks a rolling window of the last 10 answers. Player starts at tier 2.

| Rolling accuracy (last 10) | Action |
|---|---|
| 80%+ correct | Move up one tier (max 5) |
| 40-80% correct | Stay at current tier |
| Below 40% correct | Move down one tier (min 1) |

**Wrong answer generation scales with tier:**
- Tier 1-2: Random wrong answers from different CWE categories / distant CVSS scores
- Tier 3-4: Wrong answers from the same CWE category / closer CVSS scores
- Tier 5: Wrong answers are the `common_confusions` / very close CVSS scores

**Mixed mode bias:** When selecting questions, tier takes priority (driven by adaptive difficulty). Within the selected tier, prefer questions from the player's weakest CWE category if available. If no questions exist at the intersection of the desired tier and weak category, fall back to any question at the target tier.

### Hints

2 hints per round. A hint removes 2 of the 3 wrong answers, leaving 2 choices (1 correct + 1 wrong).

### Skip

Skipping counts as a wrong answer (current behavior). Shows the explainer with the correct answer.

## Post-Answer Explainer

Appears in-place after every answer. Player must click "Next Question" to advance.

### Layout

```
┌─────────────────────────────────────────────┐
│  Correct! / Incorrect                       │
├─────────────────────────────────────────────┤
│  YOUR ANSWER: CWE-89    CORRECT: CWE-79    │
├─────────────────────────────────────────────┤
│  WHY THIS IS [CWE ID]                       │
│  [CWE name]                                 │
│  [Explanation connecting description → CWE] │
├─────────────────────────────────────────────┤
│  COMMON MIXUPS                              │
│  • [Confusion CWE] — [why it doesn't fit]  │
│  • [Confusion CWE] — [why it doesn't fit]  │
├─────────────────────────────────────────────┤
│  CVSS BREAKDOWN                             │
│  [Vector string components in plain English]│
├─────────────────────────────────────────────┤
│  Links: NVD Detail | CWE Definition         │
│                                             │
│            [ Next Question → ]              │
└─────────────────────────────────────────────┘
```

### Behavior

- Shows full explanation on both correct and incorrect answers
- On wrong answers: additionally highlights the key differentiator between the guess and correct answer
- For CVSS mode: highlights which vector component(s) the player likely misjudged based on answer distance
- External links (NVD, MITRE CWE) open in new tabs

## Progress Tracking System

All data stored in localStorage.

**Storage limits and retention:**
- Retain the last 100 sessions. Older sessions are pruned on each new session save.
- Cumulative stats (accuracy by category, streaks) are stored as aggregates, not raw answer history, keeping storage small.
- Estimated total storage: ~50-100KB, well within the ~5MB localStorage limit.
- If localStorage is unavailable (private browsing, full storage), the game still works — progress tracking is gracefully disabled with a notice to the player.
- No migration needed from v1 (v1 has no persistent state).

### Data Tracked

**Per session:**
- Mode, category filter, round length
- Score, accuracy percentage
- Average time per question
- Difficulty tier reached
- Date/time

**Cumulative:**
- Total questions answered
- Accuracy by CWE category
- Accuracy by CVSS version (3.x vs 4.0)
- Accuracy by difficulty tier
- Current streak, best streak, daily play streak

### Progress Dashboard

Accessible from the main menu. Displays:
- Overall stats (total questions, accuracy, current/best tier)
- Accuracy by CWE category as horizontal bar chart (highlights weakest)
- CVSS version comparison
- Recent session history
- Practice suggestion based on weakest category, with a direct "Practice [category]" button

### Weak Area Detection

Identifies the CWE category with the lowest accuracy (minimum 10 questions answered in that category to qualify). Suggests focused practice and biases Mixed mode toward it.

### Data Portability

- **Export:** downloads all localStorage progress as a JSON file
- **Import:** uploads a JSON file to restore progress
- Use case: students back up their data, or share with an instructor for review

## UI Design

### Tech

Svelte + Vite. Single-page app. Responsive (mobile-friendly).

### Color Palette

| Role | Color | Hex |
|---|---|---|
| Background | Dark charcoal | `#0d1117` |
| Cards/surfaces | Dark surface | `#161b22` |
| Text | Soft silver | `#D7D7D9` |
| Primary accent | Cyan | `#3BACD9` |
| Secondary accent | Bright cyan | `#23B7D9` |
| Correct/positive | Gold | `#F2CB05` |
| Incorrect/errors | Muted red | `#e85050` (supplementary, test and adjust) |
| Warm accent | Amber | `#F2B705` |

### Animations (Svelte transitions)

- Questions: slide/fade in
- Explainer panel: slides up from below after answering
- Choice buttons: hover states, "lock in" animation on click
- Progress bars: animate on dashboard
- Streak counter: pulse on increment
- Difficulty tier indicator: smooth transition between levels

### Screens

1. **Home / Mode Select** — choose mode (CVSS 3.x, CVSS 4.0, CWE, Mixed), optional category filter, round length selector, link to progress dashboard
2. **Game** — question area, 4 choice buttons, skip/hint buttons, score display, difficulty tier indicator, streak counter
3. **Explainer** — appears in-place after each answer (not a separate screen, part of the game flow)
4. **End of Round** — summary stats, comparison to previous rounds, suggested next action, play again buttons
5. **Progress Dashboard** — full stats, bar charts, session history, weak area suggestion, export/import buttons

### Layout

- Centered content area, max-width ~700px
- Top nav: logo/title, current mode, streak counter, progress link
- Responsive: stacks vertically on mobile

## Deployment

### GitHub Action

Updated workflow:
1. Checkout (upgrade to `actions/checkout@v4`)
2. Setup Python (upgrade to `actions/setup-python@v5`)
3. Setup Node.js (`actions/setup-node@v4`)
4. Install Python dependencies, run `download_cves.py` (with retry/validation)
5. Run `enrich_cves.py`
6. Install npm dependencies, run `npm run build`
7. Deploy `dist/` to GitHub Pages via `actions/upload-pages-artifact` + `actions/deploy-pages`

### Deployment Transition

- The current setup serves files directly from the repo root on the `main` branch. The new setup deploys build artifacts via Actions.
- **Required:** Change the GitHub Pages source setting from "Deploy from a branch" to "GitHub Actions" in repository settings.
- **CNAME:** The custom domain file (`CNAME` with `game.cve.icu`) must be placed in `public/CNAME` so Vite copies it to `dist/` during build.
- **CSV no longer committed:** The enriched JSON is generated and consumed during the build. Neither `cves.csv` nor `enriched_cves.json` need to be committed to the repo. Add both to `.gitignore`.

### Bug Fixes

- `download_cves.py`: add 3 retries with exponential backoff, validate JSON integrity before proceeding
- Upgrade all GitHub Actions from v2 to v4/v5

### Pipeline Failure Handling

- If `download_cves.py` fails after all retries: Action fails, no deploy. The previous deployment remains live.
- If `enrich_cves.py` fails (e.g., MITRE CWE download fails with no cache): Action fails, no deploy.
- If enrichment produces fewer than 500 viable CVEs: Action fails with a clear error message. Threshold is 500 minimum (below this, adaptive difficulty can't function well).

## Accessibility

- Color contrast: verify all text/background combinations meet WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text). The muted red on dark charcoal and gold on dark charcoal must be tested.
- Keyboard navigation: all interactive elements (buttons, choices, nav) must be reachable via Tab and activatable via Enter/Space
- Screen reader: semantic HTML, ARIA labels on game state changes (correct/incorrect announcements)

## Out of Scope

- Server-side leaderboards or user accounts
- Real-time multiplayer
- AI-powered explanations at runtime
- Mobile native apps
- Automated testing (deferred to a follow-up iteration)
- Bundle size budget (the ~1MB JSON payload is acceptable for a daily-refreshed educational tool; optimize later if needed)
