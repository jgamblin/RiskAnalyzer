<script>
  import TopNav from './components/TopNav.svelte';
  import HomeScreen from './components/HomeScreen.svelte';
  import GameScreen from './components/GameScreen.svelte';
  import { currentScreen, gameState } from './lib/stores/game.js';
</script>

<TopNav
  mode={$gameState.round?.mode}
  streak={$gameState.round?.currentStreak ?? 0}
  showGameInfo={$currentScreen === 'game'}
/>
<main>
  {#if $currentScreen === 'home'}
    <HomeScreen />
  {:else if $currentScreen === 'game'}
    <GameScreen />
  {:else if $currentScreen === 'dashboard'}
    <p>Dashboard coming soon</p>
  {/if}
</main>
