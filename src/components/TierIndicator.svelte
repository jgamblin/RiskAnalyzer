<script>
  let { tier = 2 } = $props();
  const labels = ['Beginner', 'Easy', 'Medium', 'Hard', 'Expert'];
</script>

<div class="tier-indicator">
  <div class="tier-dots">
    {#each [1, 2, 3, 4, 5] as t}
      <span class="dot" class:filled={t <= tier}></span>
    {/each}
  </div>
  <span class="tier-label">Tier {tier} — {labels[tier - 1]}</span>
</div>

<style>
  .tier-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .tier-dots {
    display: flex;
    gap: 0.5rem;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    transition: background-color 0.3s ease;
  }

  .dot.filled {
    background: var(--primary);
  }

  .tier-label {
    color: var(--text);
    font-size: 0.8rem;
    opacity: 0.8;
  }
</style>
