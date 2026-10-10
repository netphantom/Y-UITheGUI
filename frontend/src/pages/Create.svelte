<script>
  import { untrack } from 'svelte';
  import SongList from '../components/SongList.svelte';
  import TagPicker from '../components/TagPicker.svelte';
  import { library } from '../lib/library.svelte.js';
  import { PLAN_MODES, SECTION_TAGS, STYLE_TAGS } from '../lib/presets.js';

  let { query } = $props();

  const EMPTY_FORM = { title: '', style: '', lyrics: '', plan_mode: 'full', seed: '', cfg_scale: '', variants: 1, project_id: '' };
  let form = $state({ ...EMPTY_FORM });
  let showTags = $state(true);
  let showAdvanced = $state(false);
  let busy = $state(false);
  let error = $state('');
  let lyricsField;

  // "Reuse prompt" links open this page with ?from=<song id>.
  // Only the query is tracked: live status polling must not overwrite what the user is typing.
  $effect(() => {
    const from = query.from;
    const source = from && untrack(() => library.song(from));
    if (source) {
      form = { ...EMPTY_FORM, title: source.title, style: source.style, lyrics: source.lyrics, plan_mode: source.plan_mode, project_id: source.project_id ?? '' };
    }
  });

  function insertSection(tag) {
    const { selectionStart: start, selectionEnd: end } = lyricsField;
    const prefix = start > 0 && form.lyrics[start - 1] !== '\n' ? '\n\n' : '';
    form.lyrics = `${form.lyrics.slice(0, start)}${prefix}${tag}\n${form.lyrics.slice(end)}`;
    lyricsField.focus();
  }

  const optionalNumber = (value) => (value === '' || value === null ? null : Number(value));

  async function submit(event) {
    event.preventDefault();
    busy = true;
    error = '';
    try {
      await library.generate({
        ...form,
        title: form.title.trim() || 'Untitled',
        seed: optionalNumber(form.seed),
        cfg_scale: optionalNumber(form.cfg_scale),
        project_id: optionalNumber(form.project_id),
        variants: Number(form.variants),
      });
    } catch (err) {
      error = err.message;
    } finally {
      busy = false;
    }
  }
</script>

<div class="layout">
  <form class="composer" onsubmit={submit}>
    <h1>Create</h1>

    <div class="field">
      <div class="row label-row">
        <label for="lyrics">Lyrics</label>
        <span class="sections">
          {#each SECTION_TAGS as tag (tag)}
            <button type="button" class="chip" onclick={() => insertSection(tag)}>{tag}</button>
          {/each}
        </span>
      </div>
      <textarea id="lyrics" rows="12" bind:this={lyricsField} bind:value={form.lyrics} placeholder={'[Verse]\nWrite your lyrics here…\n\n[Chorus]\n…'}></textarea>
    </div>

    <div class="field">
      <div class="row label-row">
        <label for="style">Style of music</label>
        <button type="button" class="ghost muted" onclick={() => (showTags = !showTags)}>{showTags ? 'Hide' : 'Show'} suggestions</button>
      </div>
      <textarea id="style" rows="3" bind:value={form.style} required maxlength="1000" placeholder="English, warm piano pop, expressive female voice, 88 BPM"></textarea>
      {#if showTags}<TagPicker bind:value={form.style} groups={STYLE_TAGS} />{/if}
    </div>

    <div class="field">
      <label for="title">Title</label>
      <input id="title" bind:value={form.title} maxlength="120" placeholder="Untitled" />
    </div>

    <button type="button" class="ghost muted" onclick={() => (showAdvanced = !showAdvanced)}>
      {showAdvanced ? '▾' : '▸'} Advanced options
    </button>
    {#if showAdvanced}
      <div class="advanced">
        <div class="field">
          <label for="plan">Symbolic plan</label>
          <select id="plan" bind:value={form.plan_mode}>
            {#each PLAN_MODES as mode (mode.value)}<option value={mode.value}>{mode.label}</option>{/each}
          </select>
          <small class="muted">{PLAN_MODES.find((mode) => mode.value === form.plan_mode).hint}</small>
        </div>
        <div class="field">
          <label for="project">Project</label>
          <select id="project" bind:value={form.project_id}>
            <option value="">— none —</option>
            {#each library.projects as project (project.id)}<option value={project.id}>{project.name}</option>{/each}
          </select>
        </div>
        <div class="field">
          <label for="seed">Seed</label>
          <input id="seed" type="number" min="0" bind:value={form.seed} placeholder="Random" />
        </div>
        <div class="field">
          <label for="cfg">Guidance (cfg scale)</label>
          <input id="cfg" type="number" step="0.1" min="0.1" max="20" bind:value={form.cfg_scale} placeholder="Model default" />
        </div>
        <div class="field">
          <label for="variants">Variants</label>
          <select id="variants" bind:value={form.variants}><option value={1}>1</option><option value={2}>2</option></select>
        </div>
      </div>
    {/if}

    {#if error}<p class="error">{error}</p>{/if}
    <button class="primary create" disabled={busy || !form.style.trim()}>
      {busy ? 'Queueing…' : 'Create ♪'}
    </button>
  </form>

  <section class="workspace">
    <h2>Recent</h2>
    <SongList songs={library.songs.slice(0, 30)} empty="Your songs will appear here." />
  </section>
</div>

<style>
  .layout { display: grid; grid-template-columns: minmax(340px, 480px) 1fr; height: 100%; }
  .composer { padding: 1.5rem; border-right: 1px solid var(--border); overflow-y: auto; }
  .workspace { padding: 1.5rem; overflow-y: auto; }
  .label-row { justify-content: space-between; flex-wrap: wrap; }
  .sections { display: flex; gap: 0.25rem; flex-wrap: wrap; margin-bottom: 0.35rem; }
  .chip { padding: 0.15rem 0.5rem; font-size: 0.75rem; }
  .advanced { display: grid; grid-template-columns: 1fr 1fr; gap: 0 1rem; margin-top: 0.75rem; }
  .advanced .field:first-child { grid-column: 1 / -1; }
  .create { width: 100%; padding: 0.85rem; font-size: 1rem; margin-top: 1rem; }

  @media (max-width: 900px) {
    .layout { grid-template-columns: 1fr; height: auto; }
    .composer { border-right: none; border-bottom: 1px solid var(--border); }
  }
</style>
