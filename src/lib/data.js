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
