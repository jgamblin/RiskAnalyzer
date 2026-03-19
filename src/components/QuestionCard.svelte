<script>
  import { fly } from 'svelte/transition';
  let { cve, questionText } = $props();
</script>

{#key cve.cve}
  <div class="question-card" in:fly={{ x: 50, duration: 300 }}>
    <div class="cve-badge">{cve.cve}</div>
    <p class="cve-description">{cve.description}</p>
    <p class="question-text">{questionText}</p>
  </div>
{/key}

<style>
  .question-card {
    background: var(--surface);
    border-radius: 12px;
    padding: 1.5rem;
  }

  .cve-badge {
    display: inline-block;
    background: var(--primary);
    color: var(--bg);
    padding: 0.25rem 0.75rem;
    border-radius: 16px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }

  .cve-description {
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--text);
    margin: 0;
  }

  .question-text {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary);
    margin-top: 1rem;
    margin-bottom: 0;
  }
</style>
