<script>
  let { mode = null, streak = 0, showGameInfo = false } = $props();
  import { currentScreen } from '../lib/stores/game.js';

  let prevStreak = $state(0);
  let pulseStreak = $state(false);

  $effect(() => {
    if (streak > prevStreak && streak > 0) {
      pulseStreak = true;
      setTimeout(() => pulseStreak = false, 600);
    }
    prevStreak = streak;
  });
</script>

<nav class="top-nav">
  <div class="nav-left">
    <button class="logo" onclick={() => currentScreen.set('home')}>RiskAnalyzer</button>
  </div>
  {#if showGameInfo && mode}
    <div class="nav-center">
      <span class="mode-badge">{mode.toUpperCase()}</span>
    </div>
  {/if}
  <div class="nav-right">
    {#if showGameInfo && streak > 0}
      <span class="streak" class:pulse={pulseStreak}>🔥 {streak}</span>
    {/if}
    <button class="stats-link" onclick={() => currentScreen.set('dashboard')}>Stats</button>
  </div>
</nav>

<style>
  .top-nav {
    position: sticky;
    top: 0;
    z-index: 10;
    background: var(--surface);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .nav-left, .nav-right {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .logo {
    color: var(--primary);
    font-size: 1.25rem;
    font-weight: 700;
    background: none;
    border: none;
    cursor: pointer;
    transition: color 0.2s;
  }

  .logo:hover {
    color: var(--primary-bright);
  }

  .nav-center {
    flex: 1;
    display: flex;
    justify-content: center;
  }

  .mode-badge {
    background: var(--primary);
    color: var(--bg);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  .streak {
    font-size: 1rem;
    font-weight: 600;
    color: var(--warm);
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .pulse {
    animation: pulse 0.6s ease;
  }

  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.3);
    }
  }

  .stats-link {
    background: none;
    border: 1px solid var(--primary);
    color: var(--primary);
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.2s;
  }

  .stats-link:hover {
    background: var(--primary);
    color: var(--bg);
  }
</style>
