const WINDOW_SIZE = 10;

export function createAdaptiveState(startTier = 2) {
  return { tier: startTier, history: [] };
}

export function recordAnswer(state, correct) {
  state.history.push(correct);
  if (state.history.length > WINDOW_SIZE) {
    state.history.shift();
  }
  if (state.history.length >= WINDOW_SIZE) {
    const accuracy = state.history.filter(Boolean).length / WINDOW_SIZE;
    if (accuracy >= 0.8 && state.tier < 5) state.tier++;
    else if (accuracy < 0.4 && state.tier > 1) state.tier--;
  }
  return state;
}
