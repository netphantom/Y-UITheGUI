<script>
  import SongRow from './SongRow.svelte';

  let { songs, empty = 'No songs yet.' } = $props();
</script>

{#if songs.length}
  <div class="list">
    {#each songs as song (song.id)}
      <SongRow {song} />
    {/each}
  </div>
{:else}
  <p class="muted">{empty}</p>
{/if}

<style>
  .list { display: flex; flex-direction: column; gap: 0.15rem; }
</style>
