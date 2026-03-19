<script>
  let { items = [], highlightLowest = false } = $props();

  // Find the item with lowest value if highlighting is enabled
  let lowestValue = $derived(
    highlightLowest && items.length > 0
      ? Math.min(...items.map(item => item.value))
      : null
  );

  function formatLabel(label) {
    // Capitalize and replace hyphens with spaces
    return label
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
</script>

<div class="bar-chart">
  {#each items as item}
    {@const isLowest = highlightLowest && item.value === lowestValue}
    <div class="bar-row">
      <div class="label">{formatLabel(item.label)}</div>
      <div class="bar-container">
        <div
          class="bar-fill"
          class:highlight={isLowest}
          style="width: {(item.value / item.max) * 100}%"
        ></div>
      </div>
      <div class="percentage">
        {item.value}%
        {#if isLowest}
          <span class="weak-spot">← weak spot</span>
        {/if}
      </div>
    </div>
  {/each}
</div>

<style>
  .bar-chart {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .bar-row {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .label {
    min-width: 160px;
    font-size: 14px;
    color: var(--text);
  }

  .bar-container {
    flex: 1;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    height: 24px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    background: var(--primary);
    border-radius: 4px;
    transition: width 0.6s ease;
  }

  .bar-fill.highlight {
    background: var(--warm);
  }

  .percentage {
    min-width: 120px;
    text-align: right;
    font-size: 14px;
    color: var(--text);
  }

  .weak-spot {
    color: var(--warm);
    font-size: 12px;
    margin-left: 6px;
  }
</style>
