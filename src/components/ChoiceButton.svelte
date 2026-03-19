<script>
  let { text, onSelect, state = 'default', disabled = false } = $props();
</script>

{#if state !== 'hidden'}
  <button
    class="choice-btn {state}"
    onclick={() => onSelect(text)}
    {disabled}
  >
    {text}
  </button>
{/if}

<style>
  .choice-btn {
    background: var(--surface);
    border: 2px solid rgba(255, 255, 255, 0.15);
    color: var(--text);
    padding: 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s;
    text-align: center;
  }

  .choice-btn:hover:not(:disabled) {
    border-color: var(--primary);
    transform: scale(1.02);
  }

  .choice-btn.correct {
    border-color: var(--correct);
    background: rgba(242, 203, 5, 0.1);
  }

  .choice-btn.incorrect {
    border-color: var(--incorrect);
    background: rgba(232, 80, 80, 0.1);
  }

  .choice-btn:disabled {
    opacity: 0.6;
    cursor: default;
  }
</style>
