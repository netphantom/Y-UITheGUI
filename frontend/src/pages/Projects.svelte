<script>
  import { library } from '../lib/library.svelte.js';
  import { coverGradient } from '../lib/format.js';

  let name = $state('');
  let error = $state('');

  const songsOf = (project) => library.songs.filter((song) => song.project_id === project.id);

  async function create(event) {
    event.preventDefault();
    error = '';
    try {
      await library.createProject({ name: name.trim() });
      name = '';
    } catch (err) {
      error = err.message;
    }
  }
</script>

<div class="page">
  <h1>Projects</h1>
  <form class="row new" onsubmit={create}>
    <input bind:value={name} placeholder="New project name" required maxlength="120" />
    <button class="primary">Create</button>
  </form>
  {#if error}<p class="error">{error}</p>{/if}

  <div class="grid">
    {#each library.projects as project (project.id)}
      {@const songs = songsOf(project)}
      <a class="project card" href="#/projects/{project.id}">
        <div class="mosaic">
          {#each songs.slice(0, 4) as song (song.id)}<span style:background={coverGradient(song)}></span>{/each}
        </div>
        <strong>{project.name}</strong>
        <span class="muted">{songs.length} song{songs.length === 1 ? '' : 's'}</span>
      </a>
    {:else}
      <p class="muted">No projects yet: group songs into albums, EPs or ideas.</p>
    {/each}
  </div>
</div>

<style>
  .page { padding: 1.5rem; }
  .new { max-width: 480px; margin-bottom: 1.5rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
  .project { display: flex; flex-direction: column; gap: 0.3rem; }
  .project:hover { background: var(--bg-hover); }
  .mosaic {
    aspect-ratio: 1;
    border-radius: 8px;
    background: var(--bg-hover);
    display: grid;
    grid-template-columns: 1fr 1fr;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }
</style>
