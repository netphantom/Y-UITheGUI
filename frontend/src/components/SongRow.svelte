<script>
  import Icon from './Icon.svelte';
  import { api } from '../lib/api.js';
  import { library } from '../lib/library.svelte.js';
  import { player } from '../lib/player.svelte.js';
  import { STATUS_LABELS, coverGradient } from '../lib/format.js';

  let { song } = $props();

  let menuOpen = $state(false);
  let error = $state('');

  const ready = $derived(song.status === 'succeeded');
  const pending = $derived(song.status === 'queued' || song.status === 'running');

  async function run(action) {
    error = '';
    menuOpen = false;
    try {
      await action();
    } catch (err) {
      error = err.message;
    }
  }

  const toggleFavorite = () => run(() => library.updateSong(song.id, { is_favorite: !song.is_favorite }));
  const moveTo = (projectId) => run(() => library.updateSong(song.id, { project_id: projectId }));
  const remove = () => {
    if (confirm(`Delete "${song.title}"?`)) run(() => library.deleteSong(song.id));
  };
</script>

<article class:active={player.song?.id === song.id}>
  <button class="cover" style:background={coverGradient(song)} disabled={!ready} onclick={() => player.toggle(song)} aria-label="Play">
    {#if pending}
      <span class="spinner"></span>
    {:else if ready}
      <span class="overlay"><Icon name={player.isPlaying(song) ? 'pause' : 'play'} filled size={20} /></span>
    {/if}
  </button>

  <a class="text" href="#/songs/{song.id}">
    <strong>{song.title}</strong>
    <span class="muted style">{song.style}</span>
    {#if !ready}
      <span class="status {song.status}">{STATUS_LABELS[song.status]}</span>
    {/if}
    {#if error}<span class="error">{error}</span>{/if}
  </a>

  <div class="actions">
    <button class="ghost" class:liked={song.is_favorite} onclick={toggleFavorite} title="Favorite">
      <Icon name="heart" filled={song.is_favorite} />
    </button>
    <div class="menu-anchor">
      <button class="ghost" onclick={() => (menuOpen = !menuOpen)} title="More"><Icon name="more" /></button>
      {#if menuOpen}
        <div class="menu card" role="menu">
          {#if ready}
            <a href={api.songs.audioUrl(song.id, true)} download>Download audio</a>
            {#if song.has_score}<a href={api.songs.scoreUrl(song.id)} download="{song.title}.abc">Download score</a>{/if}
          {/if}
          <a href="#/?from={song.id}">Reuse prompt</a>
          <label for="move-{song.id}">Move to project</label>
          <select id="move-{song.id}" value={song.project_id ?? ''} onchange={(e) => moveTo(e.target.value ? Number(e.target.value) : null)}>
            <option value="">— none —</option>
            {#each library.projects as project (project.id)}
              <option value={project.id}>{project.name}</option>
            {/each}
          </select>
          <button class="danger" onclick={remove} disabled={song.status === 'running'}>Delete</button>
        </div>
      {/if}
    </div>
  </div>
</article>

<style>
  article {
    display: flex;
    gap: 0.85rem;
    align-items: center;
    padding: 0.5rem;
    border-radius: var(--radius);
  }
  article:hover, article.active { background: var(--bg-hover); }
  .cover {
    width: 56px;
    height: 56px;
    flex-shrink: 0;
    border-radius: 8px;
    border: none;
    padding: 0;
    display: grid;
    place-items: center;
    position: relative;
  }
  .cover:disabled { opacity: 1; cursor: default; }
  .overlay { opacity: 0; transition: opacity 0.15s; color: #fff; }
  article:hover .overlay, article.active .overlay { opacity: 1; }
  .spinner {
    width: 22px;
    height: 22px;
    border: 3px solid rgb(255 255 255 / 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.15rem; }
  .style { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.85rem; }
  .status { font-size: 0.75rem; }
  .status.failed { color: var(--danger); }
  .status.running { color: var(--accent-2); }
  .actions { display: flex; align-items: center; }
  .liked { color: var(--accent); }
  .menu-anchor { position: relative; }
  .menu {
    position: absolute;
    right: 0;
    top: 100%;
    z-index: 10;
    width: 220px;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    box-shadow: 0 10px 30px rgb(0 0 0 / 0.5);
  }
  .menu a { padding: 0.35rem 0.25rem; border-radius: 6px; }
  .menu a:hover { background: var(--bg-hover); }
  .menu label { margin: 0.25rem 0 0; }
</style>
