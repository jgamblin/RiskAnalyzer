<script>
  import { onMount } from 'svelte';
  import { startGame, goHome, currentScreen } from '../lib/stores/game.js';
  import { recordSession, loadProgress, getWeakCategory, storageAvailable } from '../lib/stores/progress.js';

  let { summary, gameConfig } = $props();

  let previousAccuracy = $state(null);
  let weakCategory = $state(null);
  let recorded = $state(false);

  onMount(() => {
    if (!recorded) {
      // Get previous session for comparison before recording new one
      const progress = loadProgress();
      if (progress.sessions.length > 0) {
        const lastSession = progress.sessions[progress.sessions.length - 1];
        previousAccuracy = lastSession.accuracy;
      }
      // Record this session
      const updated = recordSession(summary);
      weakCategory = getWeakCategory(updated);
      recorded = true;
    }
  });

  let accuracyPct = $derived(Math.round(summary.accuracy * 100));
  let avgTimeSec = $derived((summary.avgTime / 1000).toFixed(1));

  let comparison = $derived(() => {
    if (previousAccuracy === null) return 'First session!';
    const diff = Math.round((summary.accuracy - previousAccuracy) * 100);
    if (diff > 0) return `↑ ${diff}% better than last round`;
    if (diff < 0) return `↓ ${Math.abs(diff)}% worse than last round`;
    return 'Same as last round';
  });

  let comparisonColor = $derived(() => {
    if (previousAccuracy === null) return 'var(--text)';
    const diff = Math.round((summary.accuracy - previousAccuracy) * 100);
    if (diff > 0) return 'var(--correct)';
    if (diff < 0) return 'var(--incorrect)';
    return 'var(--text)';
  });

  function playAgain() {
    startGame(gameConfig);
  }

  function changeMode() {
    goHome();
  }

  function viewStats() {
    currentScreen.set('dashboard');
  }

  function practiceWeak() {
    if (weakCategory) {
      startGame({ mode: gameConfig.mode, length: gameConfig.length, category: weakCategory });
    }
  }
</script>

<div class="end-round">
  <h1 class="title">Round Complete!</h1>

  <div class="stats-card">
    <div class="stat-row">
      <span class="stat-label">Score</span>
      <span class="stat-value">{summary.correct} / {summary.total} ({accuracyPct}%)</span>
    </div>

    <div class="stat-row">
      <span class="stat-label">Best Streak</span>
      <span class="stat-value">{summary.bestStreak}</span>
    </div>

    <div class="stat-row">
      <span class="stat-label">Average Time</span>
      <span class="stat-value">{avgTimeSec}s per question</span>
    </div>

    {#if summary.tierReached !== undefined && summary.tierReached !== null}
      <div class="stat-row">
        <span class="stat-label">Difficulty Tier</span>
        <span class="stat-value">Tier {summary.tierReached}</span>
      </div>
    {/if}
  </div>

  {#if storageAvailable}
    <div class="comparison-card">
      <span class="comparison-text" style="color: {comparisonColor()}">{comparison()}</span>
    </div>

    {#if weakCategory}
      <div class="suggestion-card">
        <p class="suggestion-text">
          Consider practicing <strong>{weakCategory}</strong> — it's your weakest category.
        </p>
        <button class="practice-weak-btn" onclick={practiceWeak}>
          Practice {weakCategory}
        </button>
      </div>
    {/if}
  {/if}

  <div class="actions">
    <button class="action-btn primary" onclick={playAgain}>
      Play Again
    </button>
    <button class="action-btn outline" onclick={changeMode}>
      Change Mode
    </button>
    <button class="action-btn outline" onclick={viewStats}>
      View Stats
    </button>
  </div>
</div>

<style>
  .end-round {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    padding: 2rem 1rem;
    max-width: 500px;
    margin: 0 auto;
  }

  .title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
    margin: 0;
    text-align: center;
  }

  .stats-card,
  .comparison-card,
  .suggestion-card {
    background: var(--surface);
    border-radius: 12px;
    padding: 1.5rem;
    width: 100%;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }

  .stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .stat-row:last-child {
    border-bottom: none;
  }

  .stat-label {
    font-size: 0.95rem;
    color: var(--text);
    opacity: 0.8;
  }

  .stat-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text);
  }

  .comparison-card {
    text-align: center;
  }

  .comparison-text {
    font-size: 1rem;
    font-weight: 600;
  }

  .suggestion-card {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .suggestion-text {
    margin: 0;
    font-size: 0.95rem;
    color: var(--text);
    opacity: 0.9;
    line-height: 1.5;
  }

  .suggestion-text strong {
    color: var(--primary);
    font-weight: 600;
  }

  .practice-weak-btn {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: 2px solid var(--warm);
    background: transparent;
    color: var(--warm);
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 600;
    transition: all 0.2s;
  }

  .practice-weak-btn:hover {
    background: var(--warm);
    color: var(--bg);
  }

  .actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
  }

  .action-btn {
    padding: 1rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
  }

  .action-btn.primary {
    background: var(--primary);
    color: var(--bg);
  }

  .action-btn.primary:hover {
    background: #2a8fb0;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 172, 217, 0.3);
  }

  .action-btn.outline {
    background: transparent;
    border: 2px solid var(--primary);
    color: var(--primary);
  }

  .action-btn.outline:hover {
    background: rgba(59, 172, 217, 0.1);
    border-color: var(--primary);
  }

  @media (max-width: 640px) {
    .title {
      font-size: 1.75rem;
    }

    .end-round {
      padding: 1rem 0.5rem;
    }
  }
</style>
