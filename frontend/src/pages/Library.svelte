<script>
  import SongList from '../components/SongList.svelte';
  import { library } from '../lib/library.svelte.js';

  const FILTERS = {
    all: () => true,
    favorites: (song) => song.is_favorite,
    generating: (song) => song.status === 'queued' || song.status === 'running',
    failed: (song) => song.status === 'failed',
  };

  let filter = $state('all');
  let search = $state('');

  const visible = $derived(
    library.songs.filter(FILTERS[filter]).filter((song) => `${song.title} ${song.style}`.toLowerCase().includes(search.toLowerCase())),
  );
</script>

<div class="page">
  <h1>Library</h1>
  <div class="row toolbar">
    {#each Object.keys(FILTERS) as name (name)}
      <button class:selected={filter === name} onclick={() => (filter = name)}>{name}</button>
    {/each}
    <input type="search" placeholder="Search title or style" bind:value={search} />
  </div>
  <SongList songs={visible} empty="Nothing here." />
</div>

<style>
  .page { padding: 1.5rem; }
  .toolbar { margin-bottom: 1rem; flex-wrap: wrap; }
  .toolbar button { text-transform: capitalize; }
  .toolbar .selected { background: var(--text); color: var(--bg); }
  input[type='search'] { max-width: 280px; margin-left: auto; }
</style>
