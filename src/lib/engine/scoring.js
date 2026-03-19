export function createRoundState(mode, length, category, lockedTier) {
  return {
    mode,
    length,
    category,
    lockedTier,
    questionIndex: 0,
    correctAnswers: 0,
    totalAnswered: 0,
    hintsRemaining: 2,
    currentStreak: 0,
    bestStreak: 0,
    startTime: Date.now(),
    questionStartTime: Date.now(),
    totalQuestionTime: 0,
  };
}

export function recordRoundAnswer(state, correct) {
  state.totalAnswered++;
  if (correct) {
    state.correctAnswers++;
    state.currentStreak++;
    if (state.currentStreak > state.bestStreak) state.bestStreak = state.currentStreak;
  } else {
    state.currentStreak = 0;
  }
  state.totalQuestionTime += Date.now() - state.questionStartTime;
  state.questionStartTime = Date.now();
  state.questionIndex++;
  return state;
}

export function getRoundSummary(state, tierReached) {
  return {
    mode: state.mode,
    category: state.category,
    length: state.length,
    correct: state.correctAnswers,
    total: state.totalAnswered,
    accuracy: state.totalAnswered > 0 ? state.correctAnswers / state.totalAnswered : 0,
    avgTime: state.totalAnswered > 0 ? Math.round(state.totalQuestionTime / state.totalAnswered) : 0,
    bestStreak: state.bestStreak,
    tierReached: tierReached,
    date: new Date().toISOString(),
  };
}
