<script>
  import SongList from '../components/SongList.svelte';
  import { library } from '../lib/library.svelte.js';
  import { navigate } from '../lib/router.svelte.js';

  let { params } = $props();

  const project = $derived(library.project(params.id));
  const songs = $derived(library.songs.filter((song) => song.project_id === project?.id));
  let error = $state('');

  async function act(action) {
    error = '';
    try {
      await action();
    } catch (err) {
      error = err.message;
    }
  }

  function rename() {
    const name = prompt('Project name', project.name)?.trim();
    if (name) act(() => library.updateProject(project.id, { name }));
  }

  function remove() {
    if (confirm(`Delete "${project.name}"? Its songs stay in your library.`)) {
      act(async () => {
        await library.deleteProject(project.id);
        navigate('/projects');
      });
    }
  }

  const saveDescription = (event) => act(() => library.updateProject(project.id, { description: event.target.value }));
</script>

<div class="page">
  {#if project}
    <div class="row header">
      <h1>{project.name}</h1>
      <button onclick={rename}>Rename</button>
      <button class="danger" onclick={remove}>Delete</button>
      <a class="primary-link" href="#/">+ New song</a>
    </div>
    <textarea rows="2" placeholder="Description, notes, concept…" value={project.description} onchange={saveDescription}></textarea>
    {#if error}<p class="error">{error}</p>{/if}
    <h2>Songs</h2>
    <SongList {songs} empty="No songs in this project. Use “Move to project” from a song's menu." />
  {:else}
    <p class="muted">Project not found.</p>
  {/if}
</div>

<style>
  .page { padding: 1.5rem; }
  .header { flex-wrap: wrap; margin-bottom: 0.75rem; }
  .header h1 { margin: 0 auto 0 0; }
  textarea { margin-bottom: 1.5rem; }
  .primary-link { background: var(--gradient); padding: 0.5rem 1rem; border-radius: 999px; font-weight: 600; }
</style>
