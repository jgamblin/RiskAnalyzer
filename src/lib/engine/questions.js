import { allCves, getCvesByTier, getCvesByCategory } from '../data.js';

/**
 * Select a question CVE matching tier/category constraints.
 * In mixed mode with no category filter, prefers weakCategory questions.
 * Falls back to adjacent tiers if needed.
 */
export function selectQuestion(cves, mode, tier, category, usedIds, weakCategory = null) {
  let candidates = cves.filter(c => !usedIds.has(c.cve));

  // Filter by category if specified
  if (category) {
    candidates = candidates.filter(c => c.cwe_category === category);
  }

  // Filter by mode (CVSS 4.0 needs cvss4_score)
  if (mode === 'cvss4') {
    candidates = candidates.filter(c => c.cvss4_score != null);
  }

  // Try exact tier first
  let tierCandidates = candidates.filter(c => c.difficulty_tier === tier);

  // Mixed mode bias: prefer weak category within tier
  if (mode === 'mixed' && !category && weakCategory) {
    const weakCandidates = tierCandidates.filter(c => c.cwe_category === weakCategory);
    if (weakCandidates.length > 0) {
      tierCandidates = weakCandidates;
    }
  }

  if (tierCandidates.length > 0) {
    return tierCandidates[Math.floor(Math.random() * tierCandidates.length)];
  }

  // Fall back to adjacent tiers
  for (let offset = 1; offset <= 4; offset++) {
    const nearby = candidates.filter(c =>
      c.difficulty_tier === tier + offset || c.difficulty_tier === tier - offset
    );
    if (nearby.length > 0) {
      return nearby[Math.floor(Math.random() * nearby.length)];
    }
  }

  // Last resort: any unused candidate
  if (candidates.length > 0) {
    return candidates[Math.floor(Math.random() * candidates.length)];
  }

  return null;
}

/**
 * Generate 4 choices (1 correct + 3 wrong). Wrong answer quality scales with tier.
 */
export function generateChoices(cve, mode, tier, cves) {
  if (mode === 'cvss3' || mode === 'cvss4') {
    return generateCvssChoices(cve, mode, tier);
  } else {
    return generateCweChoices(cve, tier, cves);
  }
}

function generateCvssChoices(cve, mode, tier) {
  const correctScore = mode === 'cvss4' ? cve.cvss4_score : cve.cvss3_score;
  const choices = [String(correctScore)];

  // Range narrows with tier: tier 1 = ±2.6, tier 5 = ±1.0
  const range = 3.0 - tier * 0.4;

  while (choices.length < 4) {
    const offset = (Math.random() * range * 2 - range);
    let wrong = Math.round((correctScore + offset) * 10) / 10;
    wrong = Math.max(1.0, Math.min(10.0, wrong));
    const wrongStr = String(wrong);
    if (!choices.includes(wrongStr) && wrong !== correctScore) {
      choices.push(wrongStr);
    }
  }

  return shuffle(choices);
}

function generateCweChoices(cve, tier, cves) {
  const correctCwe = cve.cwe;
  const choices = [correctCwe];

  if (tier >= 5 && cve.common_confusions && cve.common_confusions.length > 0) {
    // Tier 5: use common confusions
    for (const conf of cve.common_confusions) {
      if (choices.length < 4 && !choices.includes(conf.cwe)) {
        choices.push(conf.cwe);
      }
    }
  }

  if (tier >= 3 && choices.length < 4) {
    // Tier 3-4: same category
    const sameCategory = cves.filter(c => c.cwe_category === cve.cwe_category && c.cwe !== correctCwe);
    const uniqueCwes = [...new Set(sameCategory.map(c => c.cwe))];
    while (choices.length < 4 && uniqueCwes.length > 0) {
      const idx = Math.floor(Math.random() * uniqueCwes.length);
      const wrong = uniqueCwes.splice(idx, 1)[0];
      if (!choices.includes(wrong)) {
        choices.push(wrong);
      }
    }
  }

  // Fill remaining with random CWEs from different categories
  const otherCwes = [...new Set(cves.filter(c => c.cwe !== correctCwe).map(c => c.cwe))];
  while (choices.length < 4 && otherCwes.length > 0) {
    const idx = Math.floor(Math.random() * otherCwes.length);
    const wrong = otherCwes.splice(idx, 1)[0];
    if (!choices.includes(wrong)) {
      choices.push(wrong);
    }
  }

  return shuffle(choices);
}

/**
 * For mixed mode: pick which question type to ask for a given CVE.
 */
export function pickQuestionType(cve, hasCvss4) {
  const types = ['cvss3', 'cwe'];
  if (hasCvss4 && cve.cvss4_score != null) {
    types.push('cvss4');
  }
  return types[Math.floor(Math.random() * types.length)];
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
