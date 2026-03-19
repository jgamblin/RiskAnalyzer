import { writable, get } from 'svelte/store';
import { allCves, hasCvss4Mode } from '../data.js';
import { createAdaptiveState, recordAnswer as adaptiveRecord } from '../engine/adaptive.js';
import { selectQuestion, generateChoices, pickQuestionType } from '../engine/questions.js';
import { createRoundState, recordRoundAnswer, getRoundSummary } from '../engine/scoring.js';
import { loadProgress, getWeakCategory } from './progress.js';

export const currentScreen = writable('home');

export const gameState = writable({
  round: null,
  adaptive: null,
  currentCve: null,
  currentMode: null,   // for mixed mode: the specific type for this question
  choices: [],
  selectedAnswer: null,
  isCorrect: null,
  showExplainer: false,
  usedIds: new Set(),
});

export function startGame(config) {
  const { mode, length = 20, category = null, tier = null } = config;
  const round = createRoundState(mode, length, category, tier);
  const adaptive = createAdaptiveState(tier || 2);
  const usedIds = new Set();

  const state = {
    round,
    adaptive,
    currentCve: null,
    currentMode: null,
    choices: [],
    selectedAnswer: null,
    isCorrect: null,
    showExplainer: false,
    usedIds,
  };

  // Select first question
  const progress = loadProgress();
  const weakCat = getWeakCategory(progress);
  const effectiveTier = tier || adaptive.tier;
  const cve = selectQuestion(allCves, mode, effectiveTier, category, usedIds, weakCat);

  if (!cve) {
    console.error('No questions available');
    return;
  }

  usedIds.add(cve.cve);
  let questionMode = mode;
  if (mode === 'mixed') {
    questionMode = pickQuestionType(cve, hasCvss4Mode());
  }

  state.currentCve = cve;
  state.currentMode = questionMode;
  state.choices = generateChoices(cve, questionMode, effectiveTier, allCves);

  gameState.set(state);
  currentScreen.set('game');
}

export function submitAnswer(choice) {
  gameState.update(state => {
    const cve = state.currentCve;
    const mode = state.currentMode;

    let correctAnswer;
    if (mode === 'cvss3') correctAnswer = String(cve.cvss3_score);
    else if (mode === 'cvss4') correctAnswer = String(cve.cvss4_score);
    else correctAnswer = cve.cwe;

    const isCorrect = choice === correctAnswer;

    recordRoundAnswer(state.round, isCorrect);
    if (!state.round.lockedTier) {
      adaptiveRecord(state.adaptive, isCorrect);
    }

    state.selectedAnswer = choice;
    state.isCorrect = isCorrect;
    state.showExplainer = true;

    return state;
  });
}

export function skipQuestion() {
  gameState.update(state => {
    const cve = state.currentCve;
    const mode = state.currentMode;

    let correctAnswer;
    if (mode === 'cvss3') correctAnswer = String(cve.cvss3_score);
    else if (mode === 'cvss4') correctAnswer = String(cve.cvss4_score);
    else correctAnswer = cve.cwe;

    recordRoundAnswer(state.round, false);
    if (!state.round.lockedTier) {
      adaptiveRecord(state.adaptive, false);
    }

    state.selectedAnswer = correctAnswer;
    state.isCorrect = false;
    state.showExplainer = true;

    return state;
  });
}

export function useHint() {
  gameState.update(state => {
    if (state.round.hintsRemaining <= 0) return state;
    state.round.hintsRemaining--;

    const cve = state.currentCve;
    const mode = state.currentMode;
    let correctAnswer;
    if (mode === 'cvss3') correctAnswer = String(cve.cvss3_score);
    else if (mode === 'cvss4') correctAnswer = String(cve.cvss4_score);
    else correctAnswer = cve.cwe;

    // Remove 2 wrong answers, keep correct + 1 wrong
    const wrong = state.choices.filter(c => c !== correctAnswer);
    const keepWrong = wrong[Math.floor(Math.random() * wrong.length)];
    state.choices = state.choices.map(c => {
      if (c === correctAnswer || c === keepWrong) return c;
      return null; // hidden
    });

    return state;
  });
}

export function nextQuestion() {
  gameState.update(state => {
    // Check if round is over
    if (state.round.questionIndex >= state.round.length) {
      return state; // GameScreen will detect this and show EndRound
    }

    const progress = loadProgress();
    const weakCat = getWeakCategory(progress);
    const effectiveTier = state.round.lockedTier || state.adaptive.tier;
    const mode = state.round.mode;

    const cve = selectQuestion(allCves, mode, effectiveTier, state.round.category, state.usedIds, weakCat);
    if (!cve) {
      // No more questions available
      state.round.questionIndex = state.round.length; // force end
      return state;
    }

    state.usedIds.add(cve.cve);
    let questionMode = mode;
    if (mode === 'mixed') {
      questionMode = pickQuestionType(cve, hasCvss4Mode());
    }

    state.currentCve = cve;
    state.currentMode = questionMode;
    state.choices = generateChoices(cve, questionMode, effectiveTier, allCves);
    state.selectedAnswer = null;
    state.isCorrect = null;
    state.showExplainer = false;

    return state;
  });
}

export function goHome() {
  currentScreen.set('home');
  gameState.set({
    round: null,
    adaptive: null,
    currentCve: null,
    currentMode: null,
    choices: [],
    selectedAnswer: null,
    isCorrect: null,
    showExplainer: false,
    usedIds: new Set(),
  });
}
