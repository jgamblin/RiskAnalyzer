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
