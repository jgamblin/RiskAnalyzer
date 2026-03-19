const STORAGE_KEY = 'riskanalyzer_progress';
const MAX_SESSIONS = 100;

function isStorageAvailable() {
  try {
    const test = '__storage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}

export const storageAvailable = isStorageAvailable();

function defaultProgress() {
  return {
    totalQuestions: 0,
    categoryStats: {},
    cvssVersionStats: { v3: { correct: 0, total: 0 }, v4: { correct: 0, total: 0 } },
    tierStats: {},
    bestStreak: 0,
    currentDailyStreak: 0,
    lastPlayDate: null,
    sessions: [],
  };
}

export function loadProgress() {
  if (!storageAvailable) return defaultProgress();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultProgress();
    return JSON.parse(raw);
  } catch {
    return defaultProgress();
  }
}

export function saveProgress(progress) {
  if (!storageAvailable) return;
  try {
    // Prune old sessions
    if (progress.sessions.length > MAX_SESSIONS) {
      progress.sessions = progress.sessions.slice(-MAX_SESSIONS);
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch {
    // Storage full or unavailable — silently fail
  }
}

export function recordSession(summary) {
  const progress = loadProgress();

  // Update total questions
  progress.totalQuestions += summary.total;

  // Update CVSS version stats
  if (summary.mode === 'cvss3' || summary.mode === 'mixed') {
    progress.cvssVersionStats.v3.correct += summary.correct;
    progress.cvssVersionStats.v3.total += summary.total;
  }
  if (summary.mode === 'cvss4' || summary.mode === 'mixed') {
    progress.cvssVersionStats.v4.correct += summary.correct;
    progress.cvssVersionStats.v4.total += summary.total;
  }

  // Update best streak
  if (summary.bestStreak > progress.bestStreak) {
    progress.bestStreak = summary.bestStreak;
  }

  // Update daily streak
  const today = new Date().toISOString().split('T')[0];
  if (progress.lastPlayDate !== today) {
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
    if (progress.lastPlayDate === yesterday) {
      progress.currentDailyStreak++;
    } else {
      progress.currentDailyStreak = 1;
    }
    progress.lastPlayDate = today;
  }

  // Add session
  progress.sessions.push(summary);

  saveProgress(progress);
  return progress;
}

export function recordCategoryAnswer(category, correct) {
  const progress = loadProgress();
  if (!progress.categoryStats[category]) {
    progress.categoryStats[category] = { correct: 0, total: 0 };
  }
  progress.categoryStats[category].total++;
  if (correct) progress.categoryStats[category].correct++;
  saveProgress(progress);
}

export function recordTierAnswer(tier, correct) {
  const progress = loadProgress();
  const key = String(tier);
  if (!progress.tierStats[key]) {
    progress.tierStats[key] = { correct: 0, total: 0 };
  }
  progress.tierStats[key].total++;
  if (correct) progress.tierStats[key].correct++;
  saveProgress(progress);
}

export function getWeakCategory(progress) {
  if (!progress) progress = loadProgress();
  let weakest = null;
  let lowestAccuracy = Infinity;

  for (const [cat, stats] of Object.entries(progress.categoryStats)) {
    if (stats.total >= 10) {
      const accuracy = stats.correct / stats.total;
      if (accuracy < lowestAccuracy) {
        lowestAccuracy = accuracy;
        weakest = cat;
      }
    }
  }

  return weakest;
}

export function exportProgress() {
  const progress = loadProgress();
  const blob = new Blob([JSON.stringify(progress, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `riskanalyzer-progress-${new Date().toISOString().split('T')[0]}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

export function importProgress(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        // Basic validation
        if (typeof data.totalQuestions !== 'number' || !Array.isArray(data.sessions)) {
          reject(new Error('Invalid progress file format'));
          return;
        }
        saveProgress(data);
        resolve(data);
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}
