<script>
  import { onMount } from 'svelte';
  import { startGame, currentScreen } from '../lib/stores/game.js';
  import { hasCvss4Mode, categories } from '../lib/data.js';
  import { parseUrlParams } from '../lib/url-params.js';
  import TierIndicator from './TierIndicator.svelte';

  let selectedCategory = $state(null);
  let selectedLength = $state(20);
  let selectedTier = $state(2);
  const cvss4Available = hasCvss4Mode();

  function play(mode) {
    startGame({
      mode,
      length: selectedLength,
      category: selectedCategory,
      tier: selectedTier
    });
  }

  onMount(() => {
    const params = parseUrlParams();
    if (params.mode) {
      startGame({
        mode: params.mode,
        length: params.length || 20,
        category: params.category || null,
        tier: params.tier || null,
      });
    }
  });
</script>

<div class="home-screen">
  <div class="content">
    <h1 class="title">Choose Your Challenge</h1>

    <div class="mode-grid">
      <button class="mode-button" onclick={() => play('cvss3')}>
        <div class="mode-title">CVSS 3.x</div>
        <div class="mode-desc">Guess the severity score</div>
      </button>

      <button
        class="mode-button"
        onclick={() => play('cvss4')}
        disabled={!cvss4Available}
      >
        <div class="mode-title">CVSS 4.0</div>
        <div class="mode-desc">Latest scoring system</div>
        {#if !cvss4Available}
          <div class="mode-unavailable">Coming Soon</div>
        {/if}
      </button>

      <button class="mode-button" onclick={() => play('cwe')}>
        <div class="mode-title">CWE</div>
        <div class="mode-desc">Identify the weakness</div>
      </button>

      <button class="mode-button" onclick={() => play('mixed')}>
        <div class="mode-title">Mixed</div>
        <div class="mode-desc">All question types</div>
      </button>
    </div>

    <div class="options">
      <div class="option-group">
        <label for="category">Category</label>
        <select id="category" bind:value={selectedCategory}>
          <option value={null}>All Categories</option>
          {#each categories as cat}
            <option value={cat}>{cat}</option>
          {/each}
        </select>
      </div>

      <div class="option-group">
        <label>Round Length</label>
        <div class="toggle-group">
          <button
            class="toggle-btn"
            class:active={selectedLength === 10}
            onclick={() => selectedLength = 10}
          >
            10
          </button>
          <button
            class="toggle-btn"
            class:active={selectedLength === 20}
            onclick={() => selectedLength = 20}
          >
            20
          </button>
          <button
            class="toggle-btn"
            class:active={selectedLength === 30}
            onclick={() => selectedLength = 30}
          >
            30
          </button>
        </div>
      </div>

      <div class="option-group">
        <label>Difficulty</label>
        <TierIndicator tier={selectedTier} />
        <input
          type="range"
          min="1"
          max="5"
          bind:value={selectedTier}
          class="tier-slider"
        />
      </div>
    </div>

    <button class="view-stats-btn" onclick={() => currentScreen.set('dashboard')}>
      View Stats
    </button>

    <div class="credit">
      <a href="https://twitter.com/jgamblin" target="_blank" rel="noopener">@jgamblin</a>
    </div>
  </div>
</div>

<style>
  .home-screen {
    min-height: calc(100vh - 60px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
  }

  .content {
    width: 100%;
    max-width: 600px;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .title {
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 1rem;
  }

  .mode-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .mode-button {
    background: var(--surface);
    border: 2px solid transparent;
    color: var(--text);
    padding: 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1.1rem;
    transition: all 0.2s ease;
    text-align: left;
    position: relative;
  }

  .mode-button:hover:not(:disabled) {
    border-color: var(--primary);
    transform: translateY(-2px);
  }

  .mode-button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .mode-title {
    font-weight: 700;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    color: var(--primary);
  }

  .mode-desc {
    font-size: 0.9rem;
    opacity: 0.8;
  }

  .mode-unavailable {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: var(--warm);
    color: var(--bg);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
  }

  .options {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    background: var(--surface);
    padding: 1.5rem;
    border-radius: 8px;
  }

  .option-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .option-group label {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text);
    opacity: 0.9;
  }

  select {
    background: var(--bg);
    color: var(--text);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.6rem;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
  }

  select:focus {
    outline: none;
    border-color: var(--primary);
  }

  .toggle-group {
    display: flex;
    gap: 0.5rem;
  }

  .toggle-btn {
    flex: 1;
    background: var(--bg);
    color: var(--text);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.6rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s ease;
  }

  .toggle-btn:hover {
    border-color: var(--primary);
  }

  .toggle-btn.active {
    background: var(--primary);
    color: var(--bg);
    border-color: var(--primary);
    font-weight: 600;
  }

  .tier-slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: rgba(255, 255, 255, 0.2);
    outline: none;
    -webkit-appearance: none;
  }

  .tier-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--primary);
    cursor: pointer;
  }

  .tier-slider::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--primary);
    cursor: pointer;
    border: none;
  }

  .view-stats-btn {
    background: var(--surface);
    color: var(--text);
    border: 2px solid var(--primary);
    padding: 0.8rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.2s ease;
  }

  .view-stats-btn:hover {
    background: var(--primary);
    color: var(--bg);
    transform: translateY(-2px);
  }

  .credit {
    text-align: center;
    margin-top: 1rem;
  }

  .credit a {
    color: var(--primary);
    text-decoration: none;
    font-size: 0.9rem;
    opacity: 0.8;
    transition: opacity 0.2s;
  }

  .credit a:hover {
    opacity: 1;
  }
</style>
