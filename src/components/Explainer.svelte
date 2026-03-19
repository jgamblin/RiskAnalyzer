<script>
  import { slide } from 'svelte/transition';
  import { nextQuestion } from '../lib/stores/game.js';
  let { cve, mode, playerAnswer, correct } = $props();

  // Extract CWE number for link
  let cweNumber = $derived(cve.cwe ? cve.cwe.replace('CWE-', '') : '');

  // Determine correct answer text
  let correctAnswer = $derived(
    mode === 'cvss3' ? String(cve.cvss3_score) :
    mode === 'cvss4' ? String(cve.cvss4_score) :
    cve.cwe
  );

  // Pick the relevant CVSS vector and rationale
  let cvssVector = $derived(
    mode === 'cvss4' ? cve.cvss4_vector : cve.cvss3_vector
  );
  let cvssRationale = $derived(
    mode === 'cvss4' ? cve.cvss4_rationale : cve.cvss3_rationale
  );
</script>

<div class="explainer" transition:slide={{ duration: 400 }}>
  <div class="result-banner" class:correct class:incorrect={!correct}>
    {correct ? 'Correct!' : 'Incorrect'}
  </div>

  {#if !correct}
    <div class="answer-comparison">
      <span class="your-answer">Your Answer: <strong>{playerAnswer}</strong></span>
      <span class="arrow">→</span>
      <span class="correct-answer">Correct: <strong>{correctAnswer}</strong></span>
    </div>
  {/if}

  <div class="section">
    <h3>Why this is {cve.cwe}</h3>
    <p class="cwe-name">{cve.cwe_name}</p>
    <p>{cve.explanation}</p>
  </div>

  {#if cve.common_confusions && cve.common_confusions.length > 0}
    <div class="section">
      <h3>Common Mixups</h3>
      <ul>
        {#each cve.common_confusions as confusion}
          <li><strong>{confusion.cwe}</strong> ({confusion.name}) — {confusion.differentiator}</li>
        {/each}
      </ul>
    </div>
  {/if}

  {#if cvssRationale}
    <div class="section">
      <h3>CVSS Breakdown</h3>
      {#if cvssVector}
        <code class="vector-string">{cvssVector}</code>
      {/if}
      <p>{cvssRationale}</p>
    </div>
  {/if}

  <div class="links">
    <a href="https://nvd.nist.gov/vuln/detail/{cve.cve}" target="_blank" rel="noopener">NVD Detail</a>
    {#if cweNumber}
      <a href="https://cwe.mitre.org/data/definitions/{cweNumber}.html" target="_blank" rel="noopener">CWE Definition</a>
    {/if}
  </div>

  <button class="next-btn" onclick={nextQuestion}>Next Question →</button>
</div>

<style>
  .explainer {
    background: var(--surface);
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
  }

  .result-banner {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-align: center;
  }

  .result-banner.correct {
    color: var(--correct);
  }

  .result-banner.incorrect {
    color: var(--incorrect);
  }

  .answer-comparison {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    font-size: 0.9rem;
    flex-wrap: wrap;
  }

  .your-answer {
    color: var(--incorrect);
  }

  .arrow {
    color: var(--text);
    opacity: 0.5;
  }

  .correct-answer {
    color: var(--correct);
  }

  .section {
    margin-top: 1.5rem;
  }

  .section h3 {
    color: var(--primary);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
  }

  .cwe-name {
    font-weight: 600;
    color: var(--primary-bright);
    margin-bottom: 0.5rem;
  }

  .vector-string {
    display: block;
    background: rgba(255, 255, 255, 0.08);
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    font-size: 0.85rem;
    color: var(--primary-bright);
    margin-bottom: 0.75rem;
    word-break: break-all;
    font-family: 'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', monospace;
  }

  .section p {
    line-height: 1.6;
    color: var(--text);
  }

  .section ul {
    margin: 0;
    padding-left: 1.5rem;
  }

  .section li {
    margin-bottom: 0.5rem;
    line-height: 1.5;
  }

  .links {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
  }

  .links a {
    color: var(--primary);
    text-decoration: underline;
    font-size: 0.9rem;
  }

  .links a:hover {
    color: var(--primary-bright);
  }

  .next-btn {
    display: block;
    width: 100%;
    margin-top: 1.5rem;
    padding: 1rem;
    background: var(--primary);
    color: var(--bg);
    border: none;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .next-btn:hover {
    background: var(--primary-bright);
  }
</style>
