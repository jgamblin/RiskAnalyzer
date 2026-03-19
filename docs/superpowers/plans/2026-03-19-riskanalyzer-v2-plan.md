# RiskAnalyzer v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild RiskAnalyzer as a Svelte+Vite app with enriched CVE data, adaptive difficulty, post-answer explainers, progress tracking, and a modern dark UI — deployed statically on GitHub Pages.

**Architecture:** Python pipeline enriches NVD CVE data at build time (template-based explanations, CVSS vector parsing, CWE taxonomy lookups). Svelte+Vite SPA consumes the JSON, runs all game logic client-side. localStorage for progress. GitHub Action builds and deploys daily.

**Tech Stack:** Svelte 5, Vite, Python 3, GitHub Actions, GitHub Pages

**Spec:** `docs/superpowers/specs/2026-03-19-riskanalyzer-v2-design.md`

---

## File Structure

```
RiskAnalyzer/
├── .github/workflows/
│   └── deploy.yml                  # NEW — replaces download_cves.yml
├── pipeline/
│   ├── download_cves.py            # NEW — rewritten with retry/validation
│   ├── enrich_cves.py              # NEW — main enrichment script
│   ├── cwe_keywords.py             # NEW — keyword lists + category mapping
│   ├── cvss_templates.py           # NEW — CVSS vector→English lookup tables
│   ├── cwe_confusions.py           # NEW — curated confusion pairs + differentiators
│   └── requirements.txt            # NEW — Python deps for pipeline
├── public/
│   └── CNAME                       # MOVED from root
├── src/
│   ├── App.svelte                  # NEW — main app, screen routing
│   ├── main.js                     # NEW — Svelte entry point
│   ├── app.css                     # NEW — global styles, CSS variables, color palette
│   ├── lib/
│   │   ├── stores/
│   │   │   ├── game.js             # NEW — game state (Svelte stores)
│   │   │   └── progress.js         # NEW — localStorage progress tracking
│   │   ├── engine/
│   │   │   ├── adaptive.js         # NEW — adaptive difficulty logic
│   │   │   ├── questions.js        # NEW — question selection + wrong answer generation
│   │   │   └── scoring.js          # NEW — scoring, streaks, round management
│   │   ├── data.js                 # NEW — load/access enriched CVE data
│   │   └── url-params.js           # NEW — parse URL query params for classroom links
│   ├── components/
│   │   ├── HomeScreen.svelte       # NEW — mode select, category filter, round length
│   │   ├── GameScreen.svelte       # NEW — main game loop container
│   │   ├── QuestionCard.svelte     # NEW — CVE description + question display
│   │   ├── ChoiceButton.svelte     # NEW — individual answer button with animations
│   │   ├── Explainer.svelte        # NEW — post-answer explanation panel
│   │   ├── EndRound.svelte         # NEW — end-of-round summary + play again
│   │   ├── Dashboard.svelte        # NEW — progress dashboard with charts
│   │   ├── BarChart.svelte         # NEW — horizontal bar chart component
│   │   ├── TopNav.svelte           # NEW — navigation bar
│   │   └── TierIndicator.svelte    # NEW — difficulty tier visual indicator
│   └── data/
│       └── enriched_cves.json      # GENERATED at build time, gitignored
├── package.json                    # NEW
├── vite.config.js                  # NEW
├── svelte.config.js                # NEW
├── index.html                      # REWRITTEN — Vite entry point
├── .gitignore                      # MODIFIED — add node_modules, enriched_cves.json, cves.csv
├── requirements.txt                # KEEP (root) for backward compat during transition
├── download_cves.py                # KEEP for now, remove after deploy.yml is live
├── script.js                       # DELETE after Svelte app is working
├── styles.css                      # DELETE after Svelte app is working
```

---

## Task 1: Project Scaffold — Svelte + Vite Setup

**Files:**
- Create: `package.json`, `vite.config.js`, `src/main.js`, `src/App.svelte`, `src/app.css`, `public/CNAME`
- Rewrite: `index.html`
- Modify: `.gitignore`

- [ ] **Step 1: Initialize npm project and install dependencies**

```bash
cd /Users/gamblin/Documents/Github/RiskAnalyzer
npm init -y
npm install svelte@^5
npm install -D vite @sveltejs/vite-plugin-svelte
```

Then add scripts to `package.json`:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

- [ ] **Step 2: Create `vite.config.js`**

```js
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: 'dist',
  },
});
```

- [ ] **Step 3: Create `svelte.config.js`**

```js
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
};
```

- [ ] **Step 4: Create `src/main.js`**

Note: Svelte 5 uses `mount()` instead of constructor instantiation.

```js
import { mount } from 'svelte';
import App from './App.svelte';
import './app.css';

const app = mount(App, {
  target: document.getElementById('app'),
});

export default app;
```

- [ ] **Step 5: Create `src/app.css` with color palette and global styles**

Define CSS custom properties for the full color palette from the spec:
- `--bg: #0d1117`, `--surface: #161b22`, `--text: #D7D7D9`
- `--primary: #3BACD9`, `--primary-bright: #23B7D9`
- `--correct: #F2CB05`, `--incorrect: #e85050`, `--warm: #F2B705`

Global reset, body background, font stack (system monospace or Inter), box-sizing.

Add `main { max-width: 700px; margin: 0 auto; padding: 1rem; }` for centered content layout per spec.

- [ ] **Step 6: Create `src/App.svelte` with placeholder**

Simple component that renders "RiskAnalyzer v2" text. This will be expanded later with screen routing.

- [ ] **Step 7: Rewrite `index.html` as Vite entry point**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RiskAnalyzer</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 8: Move CNAME to `public/CNAME`**

```bash
mkdir -p public
cp CNAME public/CNAME
```

- [ ] **Step 9: Update `.gitignore`**

Add: `node_modules/`, `dist/`, `src/data/enriched_cves.json`, `cves.csv`

- [ ] **Step 10: Verify dev server starts**

```bash
npx vite dev
```

Expected: Browser opens with "RiskAnalyzer v2" text on dark background.

- [ ] **Step 11: Commit**

```bash
git add package.json package-lock.json vite.config.js svelte.config.js src/ public/CNAME index.html .gitignore
git commit -m "feat: scaffold Svelte + Vite project"
```

---

## Task 2: Python Pipeline — Download with Retry + Validation

**Files:**
- Create: `pipeline/download_cves.py`, `pipeline/requirements.txt`

- [ ] **Step 1: Create `pipeline/requirements.txt`**

```
requests
pandas
numpy
lxml
```

(`lxml` is needed for CWE XML parsing in Task 3)

- [ ] **Step 2: Create `pipeline/download_cves.py`**

Rewrite of the root `download_cves.py` with these changes:
- URL upgraded to `https://nvd.handsonhacking.org/nvd.jsonl` with HTTP fallback
- 3 retry attempts with exponential backoff (2s, 4s, 8s)
- After download, validate JSON integrity by parsing the file
- On validation failure, retry the download
- **Note on format:** Despite the `.jsonl` extension, the upstream file is actually a JSON array (not JSON Lines). The current `download_cves.py` loads it with `json.load()` which confirms this. Validation uses `json.load()` accordingly.
- **Path resolution:** All pipeline scripts resolve paths relative to the **project root**, not the script's directory. Each script computes `PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` and uses it for all file paths. This means scripts can be run from any directory.
- Output: `nvd.jsonl` in the **project root**
- Script should be importable (wrap main logic in `if __name__ == "__main__"` and also expose a `download()` function that returns the path)

Key logic:
```python
import requests
import json
import time
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS = [
    "https://nvd.handsonhacking.org/nvd.jsonl",
    "http://nvd.handsonhacking.org/nvd.jsonl",
]
LOCAL_FILE = os.path.join(PROJECT_ROOT, "nvd.jsonl")
MAX_RETRIES = 3

def download():
    for url in URLS:
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Downloading from {url} (attempt {attempt + 1})...")
                response = requests.get(url, timeout=300)
                response.raise_for_status()
                with open(LOCAL_FILE, 'wb') as f:
                    f.write(response.content)
                # Validate JSON (file is a JSON array despite .jsonl extension)
                with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
                    json.load(f)
                print("Download and validation successful.")
                return LOCAL_FILE
            except (requests.RequestException, json.JSONDecodeError) as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    wait = 2 ** (attempt + 1)
                    print(f"Retrying in {wait}s...")
                    time.sleep(wait)
        print(f"All retries failed for {url}, trying next URL...")
    print("ERROR: All download attempts failed.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    download()
```

- [ ] **Step 3: Test locally**

```bash
cd /Users/gamblin/Documents/Github/RiskAnalyzer
python pipeline/download_cves.py
```

Expected: Downloads `nvd.jsonl` successfully with validation message.

- [ ] **Step 4: Commit**

```bash
git add pipeline/download_cves.py pipeline/requirements.txt
git commit -m "feat: add download pipeline with retry and validation"
```

---

## Task 3: Python Pipeline — CWE Data + Keywords + Confusions

**Files:**
- Create: `pipeline/cwe_keywords.py`, `pipeline/cwe_confusions.py`, `pipeline/cvss_templates.py`

- [ ] **Step 1: Create `pipeline/cwe_keywords.py`**

Contains two data structures:

1. `CWE_CATEGORY_MAP` — dict mapping CWE IDs (as strings like "79") to category slugs:
   - `injection`: 77, 78, 79, 80, 89, 90, 91, 94, 95, 96, 943
   - `memory`: 119, 120, 121, 122, 124, 125, 126, 127, 131, 170, 415, 416, 476, 680, 787, 788, 805, 806, 822, 823, 824, 825
   - `auth`: 250, 280, 284, 285, 287, 288, 290, 294, 306, 307, 352, 384, 522, 613, 620, 639, 640, 798, 862, 863
   - Note: CWE-269 (Improper Privilege Management) and CWE-276 (Incorrect Default Permissions) are placed in `config` per spec, not `auth`
   - `crypto`: 295, 310, 320, 326, 327, 328, 330, 331, 338, 347
   - `config`: 16, 269, 276, 434, 502, 611, 668, 732, 829, 918
   - `info-disclosure`: 200, 201, 203, 209, 215, 312, 319, 359, 532, 538, 548
   - Anything else: `other`

2. `CWE_KEYWORDS` — dict mapping CWE IDs to lists of keyword strings used for explanation generation and difficulty scoring. Cover the ~35 most common CWEs. Examples in spec.

- [ ] **Step 2: Create `pipeline/cvss_templates.py`**

Contains lookup tables that map CVSS vector metric values to plain-English phrases.

**CVSS 3.x metrics:**
```python
CVSS3_LABELS = {
    "AV": {
        "N": "attack is network-accessible",
        "A": "attack requires adjacent network access",
        "L": "attack requires local access",
        "P": "attack requires physical access",
    },
    "AC": {
        "L": "low attack complexity",
        "H": "high attack complexity",
    },
    # ... PR, UI, S, C, I, A
}
```

**CVSS 4.0 metrics:** Same pattern for AV, AC, AT, PR, UI, VC, VI, VA, SC, SI, SA.

Functions:
- `parse_cvss3_vector(vector_string) -> dict` — parse "CVSS:3.1/AV:N/AC:L/..." into component dict
- `cvss3_rationale(score, vector_string) -> str` — returns English rationale
- `parse_cvss4_vector(vector_string) -> dict`
- `cvss4_rationale(score, vector_string) -> str`

- [ ] **Step 3: Create `pipeline/cwe_confusions.py`**

Contains:

1. `CURATED_CONFUSIONS` — dict mapping CWE IDs to lists of `(confused_cwe_id, differentiator_text)` tuples. Cover ~50 most common pairs:
   ```python
   CURATED_CONFUSIONS = {
       "79": [
           ("89", "SQL Injection targets database queries, not HTML output"),
           ("94", "Code Injection executes arbitrary server-side code, not client-side scripts"),
       ],
       "89": [
           ("79", "XSS targets browser-rendered HTML, not database queries"),
           ("78", "OS Command Injection targets system commands, not SQL"),
       ],
       # ... ~50 pairs
   }
   ```

2. `get_confusions(cwe_id, cwe_taxonomy) -> list` — function that combines curated confusions with MITRE taxonomy relationships (PeerOf, ChildOf) for CWEs not in the curated list. Returns list of `{"cwe": "CWE-XX", "name": "...", "differentiator": "..."}`.

**Note:** The spec shows `common_confusions` as a simple string array `["CWE-89"]`, but the enriched JSON will use the richer format with name and differentiator included. This is an intentional enhancement — the Explainer component needs this data to render meaningful confusion explanations without additional lookups.

- [ ] **Step 4: Commit**

```bash
git add pipeline/cwe_keywords.py pipeline/cvss_templates.py pipeline/cwe_confusions.py
git commit -m "feat: add CWE keywords, CVSS templates, and confusion data"
```

---

## Task 4: Python Pipeline — Enrichment Script

**Files:**
- Create: `pipeline/enrich_cves.py`

- [ ] **Step 1: Create `pipeline/enrich_cves.py`**

Main enrichment script. High-level flow:

**Path resolution:** Like `download_cves.py`, uses `PROJECT_ROOT` for all paths. Adds the `pipeline/` directory to `sys.path` for sibling imports.

```python
import json, os, sys, time
import requests
import numpy as np
import pandas as pd
from lxml import etree

# Resolve paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPELINE_DIR)

from cwe_keywords import CWE_CATEGORY_MAP, CWE_KEYWORDS
from cvss_templates import cvss3_rationale, cvss4_rationale
from cwe_confusions import CURATED_CONFUSIONS, get_confusions

CWE_XML_URL = "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip"
CWE_CACHE = os.path.join(PIPELINE_DIR, "cwe_cache.xml")
NVD_FILE = os.path.join(PROJECT_ROOT, "nvd.jsonl")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "src", "data", "enriched_cves.json")
MIN_CVES = 500
TARGET_PER_TIER = 200
```

Key sections:

**a) Download/cache CWE XML from MITRE:**
- Download ZIP, extract XML. Cache locally in `pipeline/` with timestamp.
- If download fails and cache exists (< 7 days old), use cache.
- If no cache, fail with clear error.
- Parse XML with lxml. The CWE XML uses namespace `http://cwe.mitre.org/cwe-6`:
  ```python
  NS = {'ns': 'http://cwe.mitre.org/cwe-6'}
  tree = etree.parse(cache_path)
  for weakness in tree.xpath('//ns:Weakness', namespaces=NS):
      cwe_id = weakness.get('ID')
      name = weakness.get('Name')
      description = weakness.findtext('ns:Description', default='', namespaces=NS)
      related = weakness.xpath('ns:Related_Weaknesses/ns:Related_Weakness', namespaces=NS)
      # Each related has attrs: Nature (e.g. "ChildOf", "PeerOf"), CWE_ID, View_ID
  ```

**b) Load and filter NVD data:**
- Same filtering as current `download_cves.py`: post-2022, non-rejected, valid CWE, valid CVSS
- Extract new fields: `cvssMetricV31[0].cvssData.vectorString`, `cvssMetricV40[0].cvssData.baseScore` and `.vectorString`

**c) Enrich each CVE:**
- Look up CWE in parsed XML → get name, description
- Map CWE to category via `CWE_CATEGORY_MAP`
- Generate explanation using template + keyword matching
- Generate CVSS rationale via `cvss3_rationale()` / `cvss4_rationale()`
- Get confusions via `get_confusions()`
- Calculate difficulty tier:
  - CWE ambiguity (40%): count related CWEs in taxonomy, normalize
  - CVSS clustering (30%): distance to nearest x.0 or x.5, normalize
  - Description clarity (30%): keyword match ratio, invert

**d) Stratified sampling:**
- Assign tiers based on composite score (0-20=T1, 21-40=T2, etc.)
- If skewed, adjust boundaries
- Sample ~200 per tier, total ~1000
- If total < 500, fail with error

**e) Output:**
- Write to `src/data/enriched_cves.json`
- Also write a metadata object at the top: `{"generated": "ISO date", "total": N, "cvss4_count": N, "tiers": {1: N, 2: N, ...}}`

The output JSON structure:
```json
{
  "meta": {"generated": "...", "total": 1000, "cvss4_count": 45, "tiers": {"1": 200, "2": 200, ...}},
  "cves": [
    { ... per-CVE structure from spec ... }
  ]
}
```

- [ ] **Step 2: Create `src/data/` directory with `.gitkeep`**

```bash
mkdir -p src/data
touch src/data/.gitkeep
```

- [ ] **Step 3: Test the pipeline end-to-end locally**

```bash
cd /Users/gamblin/Documents/Github/RiskAnalyzer
python pipeline/download_cves.py
python pipeline/enrich_cves.py
```

Expected: `src/data/enriched_cves.json` is created with ~1000 CVEs. Check the output:
```bash
python -c "import json; d=json.load(open('src/data/enriched_cves.json')); print(d['meta']); print(json.dumps(d['cves'][0], indent=2))"
```

Verify: meta shows tier distribution, first CVE has all expected fields populated.

- [ ] **Step 4: Commit**

```bash
git add pipeline/enrich_cves.py src/data/.gitkeep
git commit -m "feat: add CVE enrichment pipeline with explanations and difficulty tiers"
```

---

## Task 5: Data Layer — Load Enriched CVEs in Svelte

**Files:**
- Create: `src/lib/data.js`, `src/lib/url-params.js`

- [ ] **Step 1: Create `src/lib/data.js`**

```js
import cveData from '../data/enriched_cves.json';

export const meta = cveData.meta;
export const allCves = cveData.cves;

export function getCvesByTier(tier) {
  return allCves.filter(c => c.difficulty_tier === tier);
}

export function getCvesByCategory(category) {
  return allCves.filter(c => c.cwe_category === category);
}

export function getCvesWithCvss4() {
  return allCves.filter(c => c.cvss4_score != null);
}

export function hasCvss4Mode() {
  return getCvesWithCvss4().length >= 50;
}

export const categories = [...new Set(allCves.map(c => c.cwe_category))].sort();
```

- [ ] **Step 2: Create `src/lib/url-params.js`**

```js
const VALID_MODES = ['cvss3', 'cvss4', 'cwe', 'mixed'];
const VALID_CATEGORIES = ['injection', 'memory', 'auth', 'crypto', 'config', 'info-disclosure'];
const VALID_LENGTHS = [10, 20, 30];
const VALID_TIERS = [1, 2, 3, 4, 5];

export function parseUrlParams() {
  const params = new URLSearchParams(window.location.search);
  const mode = VALID_MODES.includes(params.get('mode')) ? params.get('mode') : null;
  const category = VALID_CATEGORIES.includes(params.get('category')) ? params.get('category') : null;
  const length = VALID_LENGTHS.includes(Number(params.get('length'))) ? Number(params.get('length')) : null;
  const tier = VALID_TIERS.includes(Number(params.get('tier'))) ? Number(params.get('tier')) : null;
  return { mode, category, length, tier };
}
```

- [ ] **Step 3: Commit**

```bash
git add src/lib/data.js src/lib/url-params.js
git commit -m "feat: add data layer and URL param parsing"
```

---

## Task 6: Game Engine — Stores, Adaptive Difficulty, Question Generation

**Files:**
- Create: `src/lib/stores/game.js`, `src/lib/stores/progress.js`, `src/lib/engine/adaptive.js`, `src/lib/engine/questions.js`, `src/lib/engine/scoring.js`

- [ ] **Step 1: Create `src/lib/engine/adaptive.js`**

```js
const WINDOW_SIZE = 10;

export function createAdaptiveState(startTier = 2) {
  return { tier: startTier, history: [] };
}

export function recordAnswer(state, correct) {
  state.history.push(correct);
  if (state.history.length > WINDOW_SIZE) {
    state.history.shift();
  }
  if (state.history.length >= WINDOW_SIZE) {
    const accuracy = state.history.filter(Boolean).length / WINDOW_SIZE;
    if (accuracy >= 0.8 && state.tier < 5) state.tier++;
    else if (accuracy < 0.4 && state.tier > 1) state.tier--;
  }
  return state;
}
```

- [ ] **Step 2: Create `src/lib/engine/questions.js`**

Functions:
- `selectQuestion(cves, mode, tier, category, usedIds, weakCategory)` — picks a CVE matching tier/category constraints, avoiding repeats. Falls back to adjacent tiers if needed. **Mixed mode bias:** when `mode === 'mixed'` and no category filter is set, pass the player's `weakCategory` (from progress store). The function prefers questions from `weakCategory` within the target tier. If none available, falls back to any question at the target tier.
- `generateChoices(cve, mode, tier, allCves)` — generates 4 choices (1 correct + 3 wrong). Wrong answer quality scales with tier:
  - Tier 1-2: random from different categories / distant scores
  - Tier 3-4: same category / closer scores
  - Tier 5: use `common_confusions` / very close scores
- For CVSS modes: wrong scores generated within `±(3 - tier * 0.4)` range of correct score, clamped to 0.1-10.0
- For CWE mode: wrong CWEs from same/different category depending on tier

- [ ] **Step 3: Create `src/lib/engine/scoring.js`**

```js
export function createRoundState(mode, length, category, lockedTier) {
  return {
    mode,
    length,
    category,
    lockedTier,
    questionIndex: 0,
    correctAnswers: 0,
    totalAnswered: 0,
    hintsRemaining: 2,
    currentStreak: 0,
    bestStreak: 0,
    startTime: Date.now(),
    questionStartTime: Date.now(),
    totalQuestionTime: 0,
  };
}

export function recordRoundAnswer(state, correct) {
  state.totalAnswered++;
  if (correct) {
    state.correctAnswers++;
    state.currentStreak++;
    if (state.currentStreak > state.bestStreak) state.bestStreak = state.currentStreak;
  } else {
    state.currentStreak = 0;
  }
  state.totalQuestionTime += Date.now() - state.questionStartTime;
  state.questionStartTime = Date.now();
  state.questionIndex++;
  return state;
}

export function getRoundSummary(state) {
  return {
    mode: state.mode,
    category: state.category,
    length: state.length,
    correct: state.correctAnswers,
    total: state.totalAnswered,
    accuracy: state.totalAnswered > 0 ? state.correctAnswers / state.totalAnswered : 0,
    avgTime: state.totalAnswered > 0 ? state.totalQuestionTime / state.totalAnswered : 0,
    bestStreak: state.bestStreak,
    date: new Date().toISOString(),
  };
}
```

- [ ] **Step 4: Create `src/lib/stores/game.js`**

Svelte writable stores for:
- `currentScreen` — `'home' | 'game' | 'dashboard'`
- `gameState` — holds round state, adaptive state, current question, choices, selected answer, showExplainer flag
- Actions: `startGame(config)`, `submitAnswer(choice)`, `skipQuestion()`, `useHint()`, `nextQuestion()`, `endRound()`

This store orchestrates the game loop by composing `adaptive.js`, `questions.js`, and `scoring.js`.

- [ ] **Step 5: Create `src/lib/stores/progress.js`**

localStorage-backed store with graceful degradation:
- `isStorageAvailable()` — checks if localStorage is accessible (try/catch a test write). Returns boolean. Exported as `storageAvailable` flag.
- If storage is unavailable (private browsing, full), all read functions return defaults and write functions are no-ops. The game still works — components check `storageAvailable` and show a notice ("Progress tracking unavailable in private browsing") when false.
- `loadProgress()` — reads from localStorage, returns default state if unavailable
- `saveProgress(progress)` — writes to localStorage, prunes to 100 sessions
- `recordSession(summary)` — appends session, updates cumulative stats
- `getWeakCategory()` — returns category with lowest accuracy (min 10 questions)
- `exportProgress()` — downloads JSON file
- `importProgress(file)` — reads uploaded JSON, validates, replaces localStorage

Cumulative stats structure:
```js
{
  totalQuestions: 0,
  categoryStats: { injection: { correct: 0, total: 0 }, ... },
  cvssVersionStats: { v3: { correct: 0, total: 0 }, v4: { correct: 0, total: 0 } },
  tierStats: { 1: { correct: 0, total: 0 }, ... },
  bestStreak: 0,
  currentDailyStreak: 0,
  lastPlayDate: null,
  sessions: [],
}
```

- [ ] **Step 6: Commit**

```bash
git add src/lib/engine/ src/lib/stores/
git commit -m "feat: add game engine with adaptive difficulty, scoring, and progress tracking"
```

---

## Task 7: UI Components — TopNav, HomeScreen, TierIndicator

**Files:**
- Create: `src/components/TopNav.svelte`, `src/components/HomeScreen.svelte`, `src/components/TierIndicator.svelte`
- Modify: `src/App.svelte`

- [ ] **Step 1: Create `src/components/TopNav.svelte`**

Sticky top bar with:
- "RiskAnalyzer" title/logo (left)
- Current mode indicator (center, only shown during game)
- Streak counter with pulse animation (right, only during game)
- "Stats" link to dashboard (right)
- Uses CSS variables from `app.css`
- Props: `mode`, `streak`, `showGameInfo`

- [ ] **Step 2: Create `src/components/TierIndicator.svelte`**

Small visual component showing current difficulty tier (1-5):
- 5 small dots/bars, filled up to current tier
- Color transitions smoothly using Svelte `tweened`
- Tier label text: "Tier {n}" with descriptive word (Beginner/Easy/Medium/Hard/Expert)
- Props: `tier`

- [ ] **Step 3: Create `src/components/HomeScreen.svelte`**

Mode selection screen:
- Title: "Choose Your Challenge"
- 4 mode buttons (CVSS 3.x, CVSS 4.0, CWE, Mixed) — CVSS 4.0 button disabled/hidden if `hasCvss4Mode()` is false
- Category filter dropdown (optional, "All Categories" default)
- Round length toggle: 10 / 20 / 30
- "View Stats" button linking to dashboard
- Credit: "@jgamblin"
- On mode select: dispatches `startGame()` with config
- If URL params are present, auto-start the game with those params

- [ ] **Step 4: Update `src/App.svelte` with screen routing**

```svelte
<script>
  import TopNav from './components/TopNav.svelte';
  import HomeScreen from './components/HomeScreen.svelte';
  import { currentScreen } from './lib/stores/game.js';
  // GameScreen, Dashboard imported later
</script>

<TopNav ... />
<main>
  {#if $currentScreen === 'home'}
    <HomeScreen />
  {:else if $currentScreen === 'game'}
    <!-- GameScreen placeholder -->
    <p>Game coming soon</p>
  {:else if $currentScreen === 'dashboard'}
    <!-- Dashboard placeholder -->
    <p>Dashboard coming soon</p>
  {/if}
</main>
```

- [ ] **Step 5: Verify home screen renders**

```bash
npx vite dev
```

Expected: Dark background, mode selection buttons visible, category filter and round length options work. CVSS 4.0 button state depends on data.

- [ ] **Step 6: Commit**

```bash
git add src/components/TopNav.svelte src/components/HomeScreen.svelte src/components/TierIndicator.svelte src/App.svelte
git commit -m "feat: add TopNav, HomeScreen, and TierIndicator components"
```

---

## Task 8: UI Components — Game Screen (Question, Choices, Explainer)

**Files:**
- Create: `src/components/GameScreen.svelte`, `src/components/QuestionCard.svelte`, `src/components/ChoiceButton.svelte`, `src/components/Explainer.svelte`
- Modify: `src/App.svelte`

- [ ] **Step 1: Create `src/components/QuestionCard.svelte`**

Card displaying:
- CVE ID (e.g., "CVE-2024-1234")
- CVE Description text
- Question text (varies by mode: "What is this CVE's CVSS 3.x Base Score?" etc.)
- Slides/fades in using Svelte `fly` transition
- Props: `cve`, `questionText`

- [ ] **Step 2: Create `src/components/ChoiceButton.svelte`**

Individual answer button:
- Displays choice text
- Hover: scale up slightly, border color to `--primary`
- On click: "lock in" animation (brief scale pulse), then calls `onSelect`
- After answer: shows correct (gold border) or incorrect (red border) state
- Can be hidden (for hint functionality)
- Props: `text`, `onSelect`, `state` (default/correct/incorrect/hidden), `disabled`

- [ ] **Step 3: Create `src/components/Explainer.svelte`**

Post-answer explanation panel. Slides up using Svelte `slide` transition.

Sections:
- Result banner: "Correct!" (gold) or "Incorrect" (red)
- Your Answer vs Correct Answer (only if wrong)
- "Why this is [CWE]" section: CWE name, explanation text
- "Common Mixups" section: list of confusion CWEs with differentiators
- "CVSS Breakdown" section: vector components in plain English
- Links: NVD Detail, CWE Definition (open in new tab)
- "Next Question →" button

Props: `cve`, `mode`, `playerAnswer`, `correct`

For CWE mode: shows CWE explanation + common mixups prominently, CVSS breakdown secondary.
For CVSS mode: shows CVSS breakdown prominently, CWE info secondary. **On wrong CVSS answers:** compare the player's guessed score to the correct score and highlight which CVSS vector component(s) most likely account for the difference. For example, if the player guessed 5.0 but the correct answer is 8.1, highlight "Attack Vector: Network" and "Privileges Required: None" as the components driving the high score. This uses the pre-baked `cvss3_rationale`/`cvss4_rationale` text from the enriched data.

- [ ] **Step 4: Create `src/components/GameScreen.svelte`**

Main game container that orchestrates the game loop:
- Subscribes to `gameState` store
- Renders: TopNav game info, TierIndicator, QuestionCard, 4x ChoiceButton, Skip/Hint buttons, Score display
- After answer: shows Explainer, hides choices
- After "Next Question": advances to next question or EndRound
- Score display: `"Score: X / Y (Z%)"` — updates live
- Hint button: grayed out when 0 remaining, shows count
- Skip button: always available

Layout:
- QuestionCard at top
- Choices in a 2x2 grid (or 1-column on mobile)
- Skip/Hint row below choices
- Explainer below everything when visible
- Score and TierIndicator in the game header area

- [ ] **Step 5: Wire GameScreen into App.svelte**

Replace the game placeholder with the actual GameScreen component import.

- [ ] **Step 6: Generate test data and verify game loop**

If `enriched_cves.json` exists from Task 4, start the dev server and play through a few questions. Verify:
- Question renders with CVE description
- 4 choices appear
- Clicking a choice shows correct/incorrect state
- Explainer slides in
- "Next Question" advances
- Score updates
- Hint removes 2 wrong answers
- Skip counts as wrong

- [ ] **Step 7: Commit**

```bash
git add src/components/GameScreen.svelte src/components/QuestionCard.svelte src/components/ChoiceButton.svelte src/components/Explainer.svelte src/App.svelte
git commit -m "feat: add game screen with questions, choices, and explainer"
```

---

## Task 9: UI Components — End of Round

**Files:**
- Create: `src/components/EndRound.svelte`
- Modify: `src/components/GameScreen.svelte`

- [ ] **Step 1: Create `src/components/EndRound.svelte`**

End-of-round summary screen:
- "Round Complete!" header
- Score: X / Y (Z%)
- Best streak this round
- Average time per question
- Difficulty tier reached
- Comparison to last session (if available from progress store): "↑ 5% better" or "↓ 3% worse"
- Weak area suggestion: "Your weakest area is Auth — try a focused round?"
- Action buttons:
  - "Play Again (same mode)" — restarts with same config
  - "Change Mode" — goes to HomeScreen
  - "View Stats" — goes to Dashboard
- Records session to progress store

Props: `summary` (from `getRoundSummary()`), `previousSession` (from progress store)

- [ ] **Step 2: Wire EndRound into GameScreen**

When `questionIndex >= length`, show EndRound instead of the question loop.

- [ ] **Step 3: Verify end-of-round flow**

Play a 10-question round to completion. Verify summary shows correct stats, comparison works (or shows "First session!" if no history), and all buttons navigate correctly.

- [ ] **Step 4: Commit**

```bash
git add src/components/EndRound.svelte src/components/GameScreen.svelte
git commit -m "feat: add end-of-round summary with comparison and suggestions"
```

---

## Task 10: UI Components — Progress Dashboard

**Files:**
- Create: `src/components/Dashboard.svelte`, `src/components/BarChart.svelte`
- Modify: `src/App.svelte`

- [ ] **Step 1: Create `src/components/BarChart.svelte`**

Reusable horizontal bar chart component:
- Props: `items` (array of `{label, value, max}`), `color` (CSS variable), `highlightLowest`
- Each bar: label on left, filled bar proportional to value/max, percentage on right
- If `highlightLowest`: lowest bar gets a distinct style (warm amber) and "← weak spot" label
- Bars animate in using Svelte `tweened` values
- Responsive: bars stack cleanly on mobile

- [ ] **Step 2: Create `src/components/Dashboard.svelte`**

Full progress dashboard:
- "Your Stats" header
- Overall stats card: total questions, overall accuracy, current/best tier, best streak
- Accuracy by CWE category: BarChart with `highlightLowest`
- CVSS version comparison: two stat cards side-by-side (v3.x accuracy, v4.0 accuracy)
- Recent sessions list: last 10 sessions, each showing date, mode, score, tier
- Practice suggestion: "Your weakest area is [X] — [Practice X →]" button that starts a filtered round
- Export/Import buttons at the bottom
- "Back to Menu" button

- [ ] **Step 3: Wire Dashboard into App.svelte**

Replace the dashboard placeholder with the actual Dashboard component import.

- [ ] **Step 4: Verify dashboard renders**

Start dev server, play a round, then navigate to dashboard. Verify:
- Stats display correctly
- Bar chart renders and animates
- Session history shows the round just played
- Export downloads a JSON file
- Import loads a JSON file (test with the exported file)
- Practice suggestion links to a filtered game

- [ ] **Step 5: Commit**

```bash
git add src/components/Dashboard.svelte src/components/BarChart.svelte src/App.svelte
git commit -m "feat: add progress dashboard with bar charts and data portability"
```

---

## Task 11: Animations and Polish

**Files:**
- Modify: `src/components/ChoiceButton.svelte`, `src/components/QuestionCard.svelte`, `src/components/Explainer.svelte`, `src/components/TopNav.svelte`, `src/components/TierIndicator.svelte`, `src/app.css`

- [ ] **Step 1: Add question transitions**

In `QuestionCard.svelte`: wrap the card in a `{#key}` block keyed on CVE ID, with `fly` transition (slide in from right, fade).

- [ ] **Step 2: Add choice button animations**

In `ChoiceButton.svelte`:
- Hover: `transform: scale(1.02)`, border color transition
- Click "lock in": brief `scale(0.95)` then `scale(1.0)` with border flash
- Correct state: gold border and subtle glow
- Incorrect state: red border
- Hidden (post-hint): `display: none` with `fade` out

- [ ] **Step 3: Add explainer slide-in**

In `Explainer.svelte`: use Svelte `slide` transition with `duration: 400`. Result banner uses `fly` from top.

- [ ] **Step 4: Add streak counter pulse**

In `TopNav.svelte`: when streak increments, add a CSS animation class `pulse` that scales up briefly. Use Svelte reactive statement to detect streak changes.

- [ ] **Step 5: Add tier indicator transitions**

In `TierIndicator.svelte`: use Svelte `tweened` for the tier value so dots/bars fill smoothly.

- [ ] **Step 6: Add responsive styles**

In `src/app.css`:
- `@media (max-width: 600px)`: choices stack to 1 column, card padding reduces, nav collapses
- Ensure touch targets are ≥ 44px
- Test on mobile viewport in dev tools

- [ ] **Step 7: Verify accessibility basics**

- Tab through all interactive elements — verify focus order makes sense
- Check color contrast for text on dark backgrounds (use browser dev tools)
- Add `aria-live="polite"` to the result/score region for screen readers

- [ ] **Step 8: Commit**

```bash
git add src/components/ src/app.css
git commit -m "feat: add animations, transitions, responsive layout, and accessibility"
```

---

## Task 12: GitHub Action — Build and Deploy

**Files:**
- Create: `.github/workflows/deploy.yml`
- Modify: `.gitignore`

- [ ] **Step 1: Create `.github/workflows/deploy.yml`**

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  schedule:
    - cron: '5 0 * * *'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install Python dependencies
        run: pip install -r pipeline/requirements.txt

      - name: Download CVE data
        run: python pipeline/download_cves.py

      - name: Enrich CVE data
        run: python pipeline/enrich_cves.py

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install npm dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'dist'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Verify npm scripts exist in `package.json`**

Confirm `dev`, `build`, and `preview` scripts are present (added in Task 1 Step 1). If missing, add them.

- [ ] **Step 3: Verify build works locally**

```bash
npm run build
ls dist/
```

Expected: `dist/` contains `index.html`, `assets/`, and `CNAME`.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/deploy.yml package.json
git commit -m "feat: add GitHub Actions workflow for build and deploy to Pages"
```

---

## Task 13: Cleanup and Final Integration

**Files:**
- Delete: `download_cves.py` (root), `script.js`, `styles.css`, `.github/workflows/download_cves.yml`
- Modify: `.gitignore`, `requirements.txt` (root — can be deleted)

- [ ] **Step 1: Remove old files**

```bash
git rm download_cves.py script.js styles.css .github/workflows/download_cves.yml requirements.txt
```

- [ ] **Step 2: Update `.gitignore` final check**

Ensure these are in `.gitignore`:
- `node_modules/`
- `dist/`
- `src/data/enriched_cves.json`
- `cves.csv`
- `nvd.jsonl`
- `pipeline/cwe_cache.xml`

- [ ] **Step 3: Verify full build pipeline locally**

```bash
python pipeline/download_cves.py
python pipeline/enrich_cves.py
npm run build
npx vite preview
```

Expected: Preview server shows the complete working game with all features.

- [ ] **Step 4: Manual smoke test**

Verify all screens and features:
- [ ] Home screen: all 4 mode buttons visible (CVSS 4.0 may be hidden)
- [ ] Category filter works
- [ ] Round length selector works
- [ ] Game plays through with questions, choices, scoring
- [ ] Hint removes 2 wrong answers
- [ ] Skip counts as wrong, shows explainer
- [ ] Explainer shows CWE explanation, common mixups, CVSS breakdown, links
- [ ] Adaptive difficulty tier changes visible in TierIndicator
- [ ] End-of-round summary shows stats
- [ ] Dashboard shows cumulative stats and bar charts
- [ ] Export/import works
- [ ] URL params work: `?mode=cwe&category=injection&length=10`
- [ ] Mobile responsive (use browser dev tools)
- [ ] Keyboard navigation (Tab through buttons)

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: remove legacy files, finalize v2 migration"
```

---

## Task 14: Deploy

- [ ] **Step 1: Remind user to update GitHub Pages settings**

The user must change the GitHub Pages source in repository settings from "Deploy from a branch" to "GitHub Actions". This is a manual step in the GitHub UI:
1. Go to repo Settings → Pages
2. Under "Build and deployment", change Source to "GitHub Actions"

- [ ] **Step 2: Push to main**

```bash
git push origin main
```

- [ ] **Step 3: Monitor the GitHub Action**

```bash
gh run watch
```

Expected: Action runs successfully — downloads CVEs, enriches data, builds Svelte app, deploys to Pages.

- [ ] **Step 4: Verify live site**

Visit `https://game.cve.icu` and run the same smoke test from Task 13 Step 4.

- [ ] **Step 5: Final commit — remove old CNAME from root if still present**

```bash
git rm CNAME 2>/dev/null; git commit -m "chore: remove root CNAME (now in public/)" || echo "already removed"
```
