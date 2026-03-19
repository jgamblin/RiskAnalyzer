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

`download_cves.py` downloads the NVD dataset from `http://nvd.handsonhacking.org/nvd.jsonl`. Bug fix: add retry logic (3 attempts with exponential backoff) and validate the downloaded file parses as valid JSON before proceeding.

### Enrichment (`enrich_cves.py`)

New script that runs after `download_cves.py`.

Steps:
1. Download the CWE XML dictionary from MITRE (cached locally, updated weekly)
2. Load the NVD JSONL and filter (post-2022, non-rejected, valid CWE, valid CVSS score)
3. For each CVE:
   - Extract CVSS 3.0/3.1 score and vector string
   - Extract CVSS 4.0 score and vector string (when available)
   - Look up CWE name, description, and map to a simplified category
   - Parse CVSS vector components into plain-English rationale
   - Generate an explanation connecting the CVE description to its CWE classification
   - Identify common confusion CWEs (CWEs frequently mistaken for this one)
   - Assign a difficulty tier (1-5) based on CWE ambiguity and CVSS score clustering
4. Sample ~1000 CVEs (up from 500) to support adaptive difficulty having enough per tier
5. Output `src/data/enriched_cves.json`

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

Tiers 1-5, based on:
- **CWE ambiguity:** CWEs with many common confusions score higher difficulty
- **CVSS score clustering:** CVEs with scores near decision boundaries (e.g., 6.9 vs 7.0) score higher
- **Description clarity:** Descriptions with obvious keywords (e.g., "SQL injection") score lower

Distribution target: roughly equal across tiers to ensure enough questions at each level.

## Game Engine

### Game Modes

| Mode | Question | Answer choices |
|---|---|---|
| CVSS 3.x | "What is this CVE's CVSS 3.x Base Score?" | 4 numeric options |
| CVSS 4.0 | "What is this CVE's CVSS 4.0 Base Score?" | 4 numeric options (only CVEs with v4 data) |
| CWE | "What is this CVE's CWE?" | 4 CWE options |
| Mixed | Alternates between all three types | 4 options per question |

### Round Configuration

- Round length: 10, 20, or 30 questions (default 20)
- Optional CWE category filter (e.g., "injection only")
- Category filter can be set via URL query param: `?category=injection&mode=cwe` for classroom link sharing

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

**Mixed mode bias:** Slightly favors the player's weakest CWE category when selecting questions (based on progress data).

### Hints

2 hints per round. A hint removes 2 of the 4 wrong answers, leaving 2 choices.

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

### Bug Fixes

- `download_cves.py`: add 3 retries with exponential backoff, validate JSON integrity before proceeding
- Upgrade all GitHub Actions from v2 to v4/v5

## Out of Scope

- Server-side leaderboards or user accounts
- Real-time multiplayer
- AI-powered explanations at runtime
- Mobile native apps
