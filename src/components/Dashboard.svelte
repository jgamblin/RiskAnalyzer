<script>
  import { onMount } from 'svelte';
  import { goHome, startGame } from '../lib/stores/game.js';
  import { loadProgress, getWeakCategory, exportProgress, importProgress, storageAvailable } from '../lib/stores/progress.js';
  import BarChart from './BarChart.svelte';

  let progress = $state(null);
  let weakCategory = $state(null);
  let importError = $state('');

  onMount(() => {
    progress = loadProgress();
    weakCategory = getWeakCategory(progress);
  });

  // Compute derived display data
  let overallAccuracy = $derived(
    progress && progress.totalQuestions > 0
      ? Math.round((progress.sessions.reduce((sum, s) => sum + s.correct, 0) / progress.totalQuestions) * 100)
      : 0
  );

  let categoryItems = $derived(
    progress
      ? Object.entries(progress.categoryStats)
          .filter(([_, s]) => s.total > 0)
          .map(([cat, s]) => ({
            label: cat,
            value: Math.round((s.correct / s.total) * 100),
            max: 100
          }))
      : []
  );

  let v3Accuracy = $derived(
    progress && progress.cvssVersionStats.v3.total > 0
      ? Math.round((progress.cvssVersionStats.v3.correct / progress.cvssVersionStats.v3.total) * 100)
      : 0
  );

  let v4Accuracy = $derived(
    progress && progress.cvssVersionStats.v4.total > 0
      ? Math.round((progress.cvssVersionStats.v4.correct / progress.cvssVersionStats.v4.total) * 100)
      : 0
  );

  let bestTier = $derived(
    progress
      ? Object.entries(progress.tierStats)
          .filter(([_, s]) => s.total >= 3 && s.correct / s.total >= 0.7)
          .map(([tier, _]) => parseInt(tier))
          .sort((a, b) => b - a)[0] || 1
      : 1
  );

  let recentSessions = $derived(progress ? progress.sessions.slice(-10).reverse() : []);

  async function handleImport(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await importProgress(file);
      progress = loadProgress();
      weakCategory = getWeakCategory(progress);
      importError = '';
    } catch (err) {
      importError = err.message;
    }
    // Reset file input
    e.target.value = '';
  }

  function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function formatMode(mode) {
    const modeMap = {
      cvss3: 'CVSS 3.x',
      cvss4: 'CVSS 4.0',
      cwe: 'CWE Category',
      mixed: 'Mixed'
    };
    return modeMap[mode] || mode;
  }

  function handlePracticeWeak() {
    if (weakCategory) {
      startGame({ mode: 'cwe', length: 20, category: weakCategory });
    }
  }
</script>

<div class="dashboard">
  <!-- Header -->
  <div class="header">
    <h1>Your Stats</h1>
    <button class="back-btn" onclick={goHome}>Back to Menu</button>
  </div>

  {#if progress}
    <!-- Overall Stats Card -->
    <div class="card">
      <h2>Overall Stats</h2>
      <div class="stats-grid">
        <div class="stat">
          <div class="stat-value">{progress.totalQuestions}</div>
          <div class="stat-label">Total Questions</div>
        </div>
        <div class="stat">
          <div class="stat-value">{overallAccuracy}%</div>
          <div class="stat-label">Overall Accuracy</div>
        </div>
        <div class="stat">
          <div class="stat-value">{progress.bestStreak}</div>
          <div class="stat-label">Best Streak</div>
        </div>
        <div class="stat">
          <div class="stat-value">{progress.currentDailyStreak}</div>
          <div class="stat-label">Daily Streak</div>
        </div>
        <div class="stat">
          <div class="stat-value">Tier {bestTier}</div>
          <div class="stat-label">Best Tier</div>
        </div>
      </div>
    </div>

    <!-- Accuracy by CWE Category -->
    {#if categoryItems.length > 0}
      <div class="card">
        <h2>Accuracy by CWE Category</h2>
        <BarChart items={categoryItems} highlightLowest={true} />
      </div>
    {/if}

    <!-- CVSS Version Comparison -->
    {#if progress.cvssVersionStats.v3.total > 0 || progress.cvssVersionStats.v4.total > 0}
      <div class="card">
        <h2>CVSS Version Comparison</h2>
        <div class="cvss-grid">
          <div class="cvss-stat">
            <div class="cvss-version">CVSS 3.x</div>
            <div class="cvss-accuracy">{v3Accuracy}%</div>
            <div class="cvss-count">{progress.cvssVersionStats.v3.total} questions</div>
          </div>
          <div class="cvss-stat">
            <div class="cvss-version">CVSS 4.0</div>
            <div class="cvss-accuracy">{v4Accuracy}%</div>
            <div class="cvss-count">{progress.cvssVersionStats.v4.total} questions</div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Recent Sessions -->
    {#if recentSessions.length > 0}
      <div class="card">
        <h2>Recent Sessions</h2>
        <div class="sessions-table">
          <div class="session-header">
            <div>Date</div>
            <div>Mode</div>
            <div>Score</div>
            <div>Tier</div>
          </div>
          {#each recentSessions as session}
            <div class="session-row">
              <div>{formatDate(session.date)}</div>
              <div>{formatMode(session.mode)}</div>
              <div>{session.correct}/{session.total} ({session.accuracy}%)</div>
              <div>Tier {session.tierReached}</div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Practice Suggestion -->
    {#if weakCategory}
      <div class="card practice-card">
        <h2>Practice Suggestion</h2>
        <p>Your weakest area is <strong>{weakCategory.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</strong></p>
        <button class="practice-btn" onclick={handlePracticeWeak}>
          Practice {weakCategory.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')} →
        </button>
      </div>
    {/if}

    <!-- Export/Import -->
    <div class="card">
      <h2>Data Portability</h2>
      <div class="portability-actions">
        <button class="export-btn" onclick={exportProgress}>Export Progress</button>
        <label class="import-label">
          <input type="file" accept=".json" onchange={handleImport} />
          <span>Import Progress</span>
        </label>
      </div>
      {#if importError}
        <div class="error-message">{importError}</div>
      {/if}
    </div>

    <!-- Storage Notice -->
    {#if !storageAvailable}
      <div class="card notice-card">
        <p>Progress tracking unavailable in private browsing</p>
      </div>
    {/if}
  {:else}
    <div class="card">
      <p>Loading progress...</p>
    </div>
  {/if}
</div>

<style>
  .dashboard {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  h1 {
    font-size: 32px;
    color: var(--text);
    margin: 0;
  }

  h2 {
    font-size: 20px;
    color: var(--text);
    margin: 0 0 16px 0;
  }

  .back-btn {
    background: var(--surface);
    color: var(--text);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s;
  }

  .back-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .card {
    background: var(--surface);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 20px;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 20px;
  }

  .stat {
    text-align: center;
  }

  .stat-value {
    font-size: 32px;
    font-weight: bold;
    color: var(--primary);
    margin-bottom: 8px;
  }

  .stat-label {
    font-size: 14px;
    color: rgba(215, 215, 217, 0.7);
  }

  .cvss-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
  }

  .cvss-stat {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    padding: 20px;
    text-align: center;
  }

  .cvss-version {
    font-size: 14px;
    color: rgba(215, 215, 217, 0.7);
    margin-bottom: 8px;
  }

  .cvss-accuracy {
    font-size: 28px;
    font-weight: bold;
    color: var(--primary);
    margin-bottom: 4px;
  }

  .cvss-count {
    font-size: 12px;
    color: rgba(215, 215, 217, 0.6);
  }

  .sessions-table {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .session-header,
  .session-row {
    display: grid;
    grid-template-columns: 120px 1fr 140px 80px;
    gap: 16px;
    padding: 10px 12px;
    font-size: 14px;
  }

  .session-header {
    font-weight: 600;
    color: rgba(215, 215, 217, 0.7);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .session-row {
    color: var(--text);
    background: rgba(255, 255, 255, 0.03);
    border-radius: 4px;
  }

  .practice-card {
    background: linear-gradient(135deg, var(--surface) 0%, rgba(242, 183, 5, 0.1) 100%);
  }

  .practice-card p {
    color: var(--text);
    margin: 0 0 16px 0;
  }

  .practice-card strong {
    color: var(--warm);
  }

  .practice-btn {
    background: var(--warm);
    color: var(--bg);
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: opacity 0.2s;
  }

  .practice-btn:hover {
    opacity: 0.9;
  }

  .portability-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .export-btn {
    background: var(--primary);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: opacity 0.2s;
  }

  .export-btn:hover {
    opacity: 0.9;
  }

  .import-label {
    position: relative;
    cursor: pointer;
  }

  .import-label input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
  }

  .import-label span {
    display: inline-block;
    background: var(--surface);
    color: var(--text);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    transition: background 0.2s;
  }

  .import-label:hover span {
    background: rgba(255, 255, 255, 0.1);
  }

  .error-message {
    margin-top: 12px;
    padding: 12px;
    background: rgba(232, 80, 80, 0.1);
    border: 1px solid var(--incorrect);
    border-radius: 4px;
    color: var(--incorrect);
    font-size: 14px;
  }

  .notice-card {
    background: rgba(242, 183, 5, 0.1);
    border-color: var(--warm);
  }

  .notice-card p {
    color: var(--warm);
    margin: 0;
    text-align: center;
  }

  @media (max-width: 600px) {
    .session-header,
    .session-row {
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .session-header div:nth-child(3),
    .session-header div:nth-child(4),
    .session-row div:nth-child(3),
    .session-row div:nth-child(4) {
      display: none;
    }
  }
</style>
