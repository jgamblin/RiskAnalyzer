"""
CVE Enrichment Pipeline — enriches NVD data with explanations,
CVSS rationale, CWE taxonomy data, and difficulty tiers.

Usage:
    python pipeline/enrich_cves.py
"""

import json, os, sys, time, zipfile, io
import requests
import numpy as np
import pandas as pd
from lxml import etree

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPELINE_DIR)

from cwe_keywords import CWE_CATEGORY_MAP, CWE_KEYWORDS, get_category
from cvss_templates import cvss3_rationale, cvss4_rationale
from cwe_confusions import get_confusions

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CWE_XML_URL = "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip"
CWE_CACHE = os.path.join(PIPELINE_DIR, "cwe_cache.xml")
NVD_FILE = os.path.join(PROJECT_ROOT, "nvd.jsonl")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "src", "data", "enriched_cves.json")
MIN_CVES = 500
TARGET_PER_TIER = 200
CWE_NS = {"ns": "http://cwe.mitre.org/cwe-6"}

# ---------------------------------------------------------------------------
# Section A: Download / Cache CWE XML from MITRE
# ---------------------------------------------------------------------------


def download_cwe_xml():
    """Download CWE XML from MITRE, cache locally. Returns parsed taxonomy dict."""
    # Check cache freshness (< 7 days)
    if os.path.exists(CWE_CACHE):
        cache_age = time.time() - os.path.getmtime(CWE_CACHE)
        if cache_age < 7 * 86400:
            print("Using cached CWE XML.")
            return parse_cwe_xml(CWE_CACHE)

    # Download
    try:
        print("Downloading CWE XML from MITRE...")
        response = requests.get(CWE_XML_URL, timeout=120)
        response.raise_for_status()
        # Extract XML from ZIP
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            xml_names = [n for n in zf.namelist() if n.endswith('.xml')]
            if not xml_names:
                raise ValueError("No XML file found in CWE ZIP")
            with zf.open(xml_names[0]) as xml_file:
                with open(CWE_CACHE, 'wb') as f:
                    f.write(xml_file.read())
        print("CWE XML downloaded and cached.")
        return parse_cwe_xml(CWE_CACHE)
    except Exception as e:
        print(f"CWE download failed: {e}")
        if os.path.exists(CWE_CACHE):
            print("Falling back to cached CWE XML.")
            return parse_cwe_xml(CWE_CACHE)
        print("ERROR: No CWE cache available.", file=sys.stderr)
        sys.exit(1)


def parse_cwe_xml(path):
    """Parse CWE XML into taxonomy dict: {cwe_id: {name, description, related}}"""
    print("Parsing CWE XML...")
    tree = etree.parse(path)
    taxonomy = {}
    for weakness in tree.xpath("//ns:Weakness", namespaces=CWE_NS):
        cwe_id = weakness.get("ID")
        name = weakness.get("Name", "")
        desc_el = weakness.find("ns:Description", namespaces=CWE_NS)
        description = desc_el.text if desc_el is not None and desc_el.text else ""

        related = []
        for rel in weakness.xpath("ns:Related_Weaknesses/ns:Related_Weakness", namespaces=CWE_NS):
            related.append({
                "nature": rel.get("Nature", ""),
                "cwe_id": rel.get("CWE_ID", ""),
            })

        taxonomy[cwe_id] = {
            "name": name,
            "description": description,
            "related": related,
        }
    print(f"Parsed {len(taxonomy)} CWE entries.")
    return taxonomy


# ---------------------------------------------------------------------------
# Section B: Load and Filter NVD Data
# ---------------------------------------------------------------------------


def get_nested(entry, keys, default=None):
    """Safely get a nested value from a dict."""
    try:
        for key in keys:
            entry = entry[key]
        return entry
    except (KeyError, IndexError, TypeError):
        return default


def load_nvd_data():
    """Load NVD JSON, filter, and return list of raw CVE dicts."""
    print("Loading NVD data...")
    with open(NVD_FILE, 'r', encoding='utf-8') as f:
        nvd_data = json.load(f)

    print(f"Total entries: {len(nvd_data)}")
    filtered = []
    for entry in nvd_data:
        cve_id = get_nested(entry, ['cve', 'id'])
        status = get_nested(entry, ['cve', 'vulnStatus'], '')
        if 'Rejected' in status:
            continue

        published = get_nested(entry, ['cve', 'published'], '')
        if published < '2022-01-01':
            continue

        cwe_value = get_nested(entry, ['cve', 'weaknesses', 0, 'description', 0, 'value'], '')
        if not cwe_value or cwe_value.startswith('NVD') or cwe_value == 'Missing_Data':
            continue

        description = get_nested(entry, ['cve', 'descriptions', 0, 'value'], '')
        if not description or len(description.split()) > 200:
            continue

        # CVSS 3.x: prefer v31 over v30
        cvss3_score = get_nested(entry, ['cve', 'metrics', 'cvssMetricV31', 0, 'cvssData', 'baseScore'])
        cvss3_vector = get_nested(entry, ['cve', 'metrics', 'cvssMetricV31', 0, 'cvssData', 'vectorString'])
        if cvss3_score is None:
            cvss3_score = get_nested(entry, ['cve', 'metrics', 'cvssMetricV30', 0, 'cvssData', 'baseScore'])
            cvss3_vector = get_nested(entry, ['cve', 'metrics', 'cvssMetricV30', 0, 'cvssData', 'vectorString'])

        if cvss3_score is None or float(cvss3_score) < 1.0:
            continue

        # CVSS 4.0 (optional)
        cvss4_score = get_nested(entry, ['cve', 'metrics', 'cvssMetricV40', 0, 'cvssData', 'baseScore'])
        cvss4_vector = get_nested(entry, ['cve', 'metrics', 'cvssMetricV40', 0, 'cvssData', 'vectorString'])

        filtered.append({
            'cve': cve_id,
            'description': description.replace(',', ' ').replace('\n', ' ').replace('\r', ' ').replace('"', ''),
            'cvss3_score': float(cvss3_score),
            'cvss3_vector': cvss3_vector,
            'cvss4_score': float(cvss4_score) if cvss4_score else None,
            'cvss4_vector': cvss4_vector,
            'cwe_raw': cwe_value,
            'published': published,
        })

    print(f"Filtered to {len(filtered)} CVEs.")
    return filtered


# ---------------------------------------------------------------------------
# Section C: Enrich Each CVE
# ---------------------------------------------------------------------------


def generate_explanation(cve, cwe_id, cwe_name):
    """Generate template-based explanation for a CVE's CWE classification."""
    clean_id = cwe_id.replace("CWE-", "")
    keywords = CWE_KEYWORDS.get(clean_id, [])
    desc_lower = cve['description'].lower()
    matched = [kw for kw in keywords if kw.lower() in desc_lower]

    if matched:
        kw_text = ", ".join(f'"{kw}"' for kw in matched[:3])
        return f"This CVE is classified as {cwe_id} ({cwe_name}) because the description references {kw_text}. {cwe_name} vulnerabilities involve situations where {cwe_name.lower()}."
    else:
        return f"This CVE is classified as {cwe_id} ({cwe_name}). {cwe_name} vulnerabilities involve situations where {cwe_name.lower()}."


def calculate_difficulty(cve, cwe_id, taxonomy):
    """Calculate difficulty tier composite score (0-100)."""
    clean_id = cwe_id.replace("CWE-", "")

    # Factor 1: CWE ambiguity (40%) — number of related CWEs
    related_count = len(taxonomy.get(clean_id, {}).get("related", []))
    ambiguity = min(related_count / 10.0, 1.0) * 100  # normalize: 10+ relations = max

    # Factor 2: CVSS clustering (30%) — distance from nearest .0 or .5
    score = cve['cvss3_score']
    dist_to_half = min(abs(score % 0.5), abs(0.5 - (score % 0.5)))
    clustering = (1.0 - dist_to_half / 0.25) * 100  # closer to .0/.5 = easier, farther = harder

    # Factor 3: Description clarity (30%) — keyword match ratio
    keywords = CWE_KEYWORDS.get(clean_id, [])
    if keywords:
        desc_lower = cve['description'].lower()
        matched = sum(1 for kw in keywords if kw.lower() in desc_lower)
        clarity = (1.0 - matched / len(keywords)) * 100  # more matches = easier
    else:
        clarity = 100  # no keywords = hardest

    composite = ambiguity * 0.4 + clustering * 0.3 + clarity * 0.3
    return composite


def enrich_cves(raw_cves, taxonomy):
    """Enrich each CVE with explanations, rationale, confusions, and difficulty."""
    print("Enriching CVEs...")
    enriched = []
    cvss4_count = 0

    for cve in raw_cves:
        cwe_raw = cve['cwe_raw']
        clean_id = cwe_raw.replace("CWE-", "")

        # Look up CWE in taxonomy
        cwe_info = taxonomy.get(clean_id, {})
        cwe_name = cwe_info.get("name", cwe_raw)
        cwe_description = cwe_info.get("description", "")
        if len(cwe_description) > 300:
            cwe_description = cwe_description[:297] + "..."

        category = get_category(cwe_raw)
        explanation = generate_explanation(cve, cwe_raw, cwe_name)

        # CVSS rationale
        cvss3_rat = cvss3_rationale(cve['cvss3_score'], cve['cvss3_vector']) if cve['cvss3_vector'] else f"Score of {cve['cvss3_score']}."
        cvss4_rat = None
        if cve['cvss4_score'] is not None:
            cvss4_rat = cvss4_rationale(cve['cvss4_score'], cve['cvss4_vector']) if cve['cvss4_vector'] else f"Score of {cve['cvss4_score']}."
            cvss4_count += 1

        # Confusions
        confusions = get_confusions(clean_id, taxonomy)

        # Difficulty
        difficulty_score = calculate_difficulty(cve, cwe_raw, taxonomy)

        enriched.append({
            "cve": cve['cve'],
            "description": cve['description'],
            "cvss3_score": cve['cvss3_score'],
            "cvss3_vector": cve['cvss3_vector'],
            "cvss3_rationale": cvss3_rat,
            "cvss4_score": cve['cvss4_score'],
            "cvss4_vector": cve['cvss4_vector'],
            "cvss4_rationale": cvss4_rat,
            "cwe": cwe_raw,
            "cwe_name": cwe_name,
            "cwe_description": cwe_description,
            "cwe_category": category,
            "explanation": explanation,
            "common_confusions": confusions,
            "difficulty_score": difficulty_score,
            "difficulty_tier": 0,  # assigned after scoring all CVEs
        })

    print(f"Enriched {len(enriched)} CVEs ({cvss4_count} with CVSS 4.0).")
    return enriched, cvss4_count


# ---------------------------------------------------------------------------
# Section D: Stratified Sampling
# ---------------------------------------------------------------------------


def assign_tiers_and_sample(enriched):
    """Assign difficulty tiers and perform stratified sampling."""
    # Sort by difficulty score to assign tiers
    scores = [c['difficulty_score'] for c in enriched]

    # Try default boundaries first
    boundaries = [20, 40, 60, 80, 100]

    for cve in enriched:
        score = cve['difficulty_score']
        if score <= boundaries[0]:
            cve['difficulty_tier'] = 1
        elif score <= boundaries[1]:
            cve['difficulty_tier'] = 2
        elif score <= boundaries[2]:
            cve['difficulty_tier'] = 3
        elif score <= boundaries[3]:
            cve['difficulty_tier'] = 4
        else:
            cve['difficulty_tier'] = 5

    # Count per tier
    tier_counts = {}
    tier_cves = {}
    for t in range(1, 6):
        tier_cves[t] = [c for c in enriched if c['difficulty_tier'] == t]
        tier_counts[t] = len(tier_cves[t])

    print(f"Tier distribution: {tier_counts}")

    # If heavily skewed, use quantile-based boundaries instead
    min_tier = min(tier_counts.values())
    if min_tier < 50:
        print("Tiers heavily skewed, using quantile-based boundaries...")
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        boundaries = [sorted_scores[int(n * i / 5)] for i in range(1, 5)] + [100]

        for cve in enriched:
            score = cve['difficulty_score']
            if score <= boundaries[0]:
                cve['difficulty_tier'] = 1
            elif score <= boundaries[1]:
                cve['difficulty_tier'] = 2
            elif score <= boundaries[2]:
                cve['difficulty_tier'] = 3
            elif score <= boundaries[3]:
                cve['difficulty_tier'] = 4
            else:
                cve['difficulty_tier'] = 5

        tier_cves = {}
        tier_counts = {}
        for t in range(1, 6):
            tier_cves[t] = [c for c in enriched if c['difficulty_tier'] == t]
            tier_counts[t] = len(tier_cves[t])
        print(f"Adjusted tier distribution: {tier_counts}")

    # Stratified sampling: ~200 per tier
    import random
    random.seed(42)
    sampled = []
    for t in range(1, 6):
        available = tier_cves[t]
        n_sample = min(TARGET_PER_TIER, len(available))
        sampled.extend(random.sample(available, n_sample))

    # Remove temporary difficulty_score field
    for cve in sampled:
        del cve['difficulty_score']

    total = len(sampled)
    if total < MIN_CVES:
        print(f"ERROR: Only {total} CVEs after sampling (minimum {MIN_CVES}).", file=sys.stderr)
        sys.exit(1)

    # Recount
    final_tiers = {}
    for t in range(1, 6):
        final_tiers[str(t)] = len([c for c in sampled if c['difficulty_tier'] == t])

    return sampled, final_tiers


# ---------------------------------------------------------------------------
# Section E: Main
# ---------------------------------------------------------------------------


def main():
    taxonomy = download_cwe_xml()
    raw_cves = load_nvd_data()
    enriched, cvss4_count = enrich_cves(raw_cves, taxonomy)
    sampled, tier_distribution = assign_tiers_and_sample(enriched)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    output = {
        "meta": {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total": len(sampled),
            "cvss4_count": cvss4_count,
            "tiers": tier_distribution,
        },
        "cves": sampled,
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"Output: {OUTPUT_PATH}")
    print(f"Total CVEs: {len(sampled)}, CVSS 4.0: {cvss4_count}")
    print(f"Tiers: {tier_distribution}")
    print("Enrichment complete.")


if __name__ == "__main__":
    main()
