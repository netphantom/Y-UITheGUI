<script>
  import Icon from './Icon.svelte';
  import { player } from '../lib/player.svelte.js';
  import { coverGradient, formatTime } from '../lib/format.js';
</script>

{#if player.song}
  <footer>
    <a class="info" href="#/songs/{player.song.id}">
      <span class="cover" style:background={coverGradient(player.song)}></span>
      <span>
        <strong>{player.song.title}</strong>
        <small class="muted">{player.song.style}</small>
      </span>
    </a>

    <div class="controls">
      <button class="play" onclick={() => player.toggle(player.song)} aria-label="Play/pause">
        <Icon name={player.playing ? 'pause' : 'play'} filled />
      </button>
      <div class="timeline">
        <small>{formatTime(player.currentTime)}</small>
        <input
          type="range"
          min="0"
          max={player.duration || 0}
          step="0.1"
          value={player.currentTime}
          oninput={(event) => player.seek(Number(event.target.value))}
        />
        <small>{formatTime(player.duration)}</small>
      </div>
    </div>

    <div class="volume">
      <Icon name="volume" />
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={player.volume}
        oninput={(event) => player.setVolume(Number(event.target.value))}
      />
    </div>
  </footer>
{/if}

<style>
  footer {
    height: var(--player-height);
    border-top: 1px solid var(--border);
    background: var(--bg-elevated);
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    align-items: center;
    gap: 1rem;
    padding: 0 1rem;
  }
  .info { display: flex; gap: 0.75rem; align-items: center; min-width: 0; }
  .info span:last-child { display: flex; flex-direction: column; min-width: 0; }
  .info small, .info strong { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .cover { width: 44px; height: 44px; border-radius: 6px; flex-shrink: 0; }
  .controls { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; }
  .play { background: var(--text); color: var(--bg); border: none; width: 34px; height: 34px; padding: 0; display: grid; place-items: center; }
  .play:hover { background: var(--text) !important; filter: brightness(0.9); }
  .timeline { display: flex; gap: 0.6rem; align-items: center; width: 100%; }
  .volume { display: flex; gap: 0.5rem; align-items: center; justify-self: end; width: 140px; }
  input[type='range'] { padding: 0; border: none; background: none; accent-color: var(--accent); }

  @media (max-width: 760px) {
    footer { grid-template-columns: 1fr 1.5fr; }
    .volume { display: none; }
  }
</style>
