<script>
  import { gameState, submitAnswer, skipQuestion, useHint } from '../lib/stores/game.js';
  import TierIndicator from './TierIndicator.svelte';
  import QuestionCard from './QuestionCard.svelte';
  import ChoiceButton from './ChoiceButton.svelte';
  import Explainer from './Explainer.svelte';
  import EndRound from './EndRound.svelte';
  import { getRoundSummary } from '../lib/engine/scoring.js';
  import { recordCategoryAnswer, recordTierAnswer } from '../lib/stores/progress.js';

  let questionTexts = {
    cvss3: "What is this CVE's CVSS 3.x Base Score?",
    cvss4: "What is this CVE's CVSS 4.0 Base Score?",
    cwe: "What is this CVE's CWE?",
  };

  // Derive correct answer for highlighting
  function getCorrectAnswer(cve, mode) {
    if (mode === 'cvss3') return String(cve.cvss3_score);
    if (mode === 'cvss4') return String(cve.cvss4_score);
    return cve.cwe;
  }

  function getChoiceState(choice, state) {
    if (choice === null) return 'hidden';
    if (!state.showExplainer) return 'default';
    const correct = getCorrectAnswer(state.currentCve, state.currentMode);
    if (choice === correct) return 'correct';
    if (choice === state.selectedAnswer) return 'incorrect';
    return 'default';
  }

  function handleSelect(choice) {
    const state = $gameState;
    if (state.showExplainer) return;
    submitAnswer(choice);
    // Record category/tier stats
    const cve = state.currentCve;
    const correct = choice === getCorrectAnswer(cve, state.currentMode);
    if (cve.cwe_category) recordCategoryAnswer(cve.cwe_category, correct);
    if (state.adaptive) recordTierAnswer(state.adaptive.tier, correct);
  }

  let score = $derived(
    $gameState.round
      ? `Score: ${$gameState.round.correctAnswers} / ${$gameState.round.totalAnswered} (${$gameState.round.totalAnswered > 0 ? Math.round(($gameState.round.correctAnswers / $gameState.round.totalAnswered) * 100) : 100}%)`
      : ''
  );

  let questionNumber = $derived(
    $gameState.round
      ? `Question ${$gameState.round.questionIndex + ($gameState.showExplainer ? 0 : 1)} of ${$gameState.round.length}`
      : ''
  );

  let isRoundOver = $derived($gameState.round && $gameState.round.questionIndex >= $gameState.round.length);
  let roundSummary = $derived(isRoundOver ? getRoundSummary($gameState.round, $gameState.adaptive?.tier) : null);
  let gameConfig = $derived($gameState.round ? { mode: $gameState.round.mode, length: $gameState.round.length, category: $gameState.round.category, tier: $gameState.round.lockedTier } : null);
</script>

<div class="game-screen">
  {#if !isRoundOver}
    <div class="game-header">
      <div class="game-info">
        <span class="question-number">{questionNumber}</span>
        <span class="score-display">{score}</span>
      </div>
      {#if $gameState.adaptive}
        <TierIndicator tier={$gameState.adaptive.tier} />
      {/if}
    </div>

    {#if $gameState.currentCve}
      <QuestionCard
        cve={$gameState.currentCve}
        questionText={questionTexts[$gameState.currentMode] || ''}
      />

      {#if !$gameState.showExplainer}
        <div class="choices-grid">
          {#each $gameState.choices as choice}
            <ChoiceButton
              text={choice}
              onSelect={handleSelect}
              state={getChoiceState(choice, $gameState)}
              disabled={$gameState.showExplainer}
            />
          {/each}
        </div>

        <div class="action-buttons">
          <button class="action-btn skip-btn" onclick={skipQuestion}>
            Skip
          </button>
          <button
            class="action-btn hint-btn"
            onclick={useHint}
            disabled={$gameState.round?.hintsRemaining <= 0}
          >
            Hint ({$gameState.round?.hintsRemaining ?? 0})
          </button>
        </div>
      {:else}
        <!-- Show choices in resolved state -->
        <div class="choices-grid resolved">
          {#each $gameState.choices as choice}
            <ChoiceButton
              text={choice}
              onSelect={() => {}}
              state={getChoiceState(choice, $gameState)}
              disabled={true}
            />
          {/each}
        </div>
      {/if}

      {#if $gameState.showExplainer}
        <Explainer
          cve={$gameState.currentCve}
          mode={$gameState.currentMode}
          playerAnswer={$gameState.selectedAnswer}
          correct={$gameState.isCorrect}
        />
      {/if}
    {/if}
  {:else}
    <EndRound summary={roundSummary} gameConfig={gameConfig} />
  {/if}
</div>

<style>
  .game-screen {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .game-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .game-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .question-number {
    font-size: 0.9rem;
    color: var(--text);
    opacity: 0.8;
  }

  .score-display {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary);
  }

  .choices-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .action-buttons {
    display: flex;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }

  .action-btn {
    flex: 1;
    padding: 0.75rem;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: transparent;
    color: var(--text);
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .action-btn:hover:not(:disabled) {
    border-color: var(--primary);
    background: rgba(59, 172, 217, 0.1);
  }

  .action-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  @media (max-width: 640px) {
    .choices-grid {
      grid-template-columns: 1fr;
    }
  }
</style>