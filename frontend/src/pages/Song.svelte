<script>
  import Icon from '../components/Icon.svelte';
  import { api } from '../lib/api.js';
  import { library } from '../lib/library.svelte.js';
  import { player } from '../lib/player.svelte.js';
  import { navigate } from '../lib/router.svelte.js';
  import { STATUS_LABELS, coverGradient, formatDate } from '../lib/format.js';

  let { params } = $props();

  const song = $derived(library.song(params.id));
  const ready = $derived(song?.status === 'succeeded');
  const parent = $derived(song?.parent_id && library.song(song.parent_id));

  let score = $state('');
  let originalScore = $state('');
  let error = $state('');
  let busy = $state(false);

  // Load the ABC score once the song is ready, or when another song is opened. Keyed on the id
  // only, so renaming or favoriting the song does not discard an in-progress score edit.
  const scoreSongId = $derived(ready && song.has_score ? song.id : null);
  $effect(() => {
    const id = scoreSongId;
    score = originalScore = '';
    if (id !== null) {
      api.songs.score(id).then((text) => (score = originalScore = text)).catch((err) => (error = err.message));
    }
  });

  async function act(action) {
    busy = true;
    error = '';
    try {
      await action();
    } catch (err) {
      error = err.message;
    } finally {
      busy = false;
    }
  }

  function rename() {
    const title = prompt('Title', song.title)?.trim();
    if (title) act(() => library.updateSong(song.id, { title }));
  }

  /** YuE2's signature feature: re-render the song from a hand-edited melody/chord score. */
  const regenerateFromScore = () =>
    act(async () => {
      const [created] = await library.generate({
        title: `${song.title} (edit)`,
        style: song.style,
        lyrics: song.lyrics,
        plan_mode: song.plan_mode === 'off' ? 'full' : song.plan_mode,
        abc: score,
        seed: song.seed,
        cfg_scale: song.cfg_scale,
        project_id: song.project_id,
        parent_id: song.id,
      });
      navigate(`/songs/${created.id}`);
    });
</script>

<div class="page">
  {#if !song}
    <p class="muted">Song not found.</p>
  {:else}
    <header>
      <button class="cover" style:background={coverGradient(song)} disabled={!ready} onclick={() => player.toggle(song)} aria-label="Play">
        {#if ready}<Icon name={player.isPlaying(song) ? 'pause' : 'play'} filled size={48} />{/if}
      </button>
      <div class="meta">
        <h1>{song.title} <button class="ghost" onclick={rename} title="Rename"><Icon name="edit" /></button></h1>
        <p>{song.style}</p>
        <p class="muted small">
          {STATUS_LABELS[song.status]} · seed {song.seed} · plan {song.plan_mode}
          {#if song.cfg_scale} · cfg {song.cfg_scale}{/if}
          · {formatDate(song.created_at)}
          {#if song.engine_version} · YuE2 {song.engine_version}{/if}
        </p>
        {#if parent}<p class="small">Edited from <a href="#/songs/{parent.id}">{parent.title}</a></p>{/if}
        {#if song.truncated}<p class="small warn">The model hit its length limit: the song may end abruptly.</p>{/if}
        {#if song.error}<pre class="error">{song.error}</pre>{/if}
        <div class="row">
          {#if ready}<a class="button" href={api.songs.audioUrl(song.id, true)} download><Icon name="download" /> Audio</a>{/if}
          <a class="button" href="#/?from={song.id}"><Icon name="refresh" /> Reuse prompt</a>
        </div>
      </div>
    </header>

    {#if error}<p class="error">{error}</p>{/if}

    <div class="columns">
      <section>
        <h2>Lyrics</h2>
        <pre class="card lyrics">{song.lyrics || 'Instrumental / no lyrics'}</pre>
      </section>
      {#if song.has_score}
        <section>
          <div class="row">
            <h2>Score (ABC)</h2>
          </div>
          <p class="muted small">Edit melody and chords, then render a new version that follows your changes.</p>
          <textarea class="score" rows="18" spellcheck="false" bind:value={score}></textarea>
          <div class="row">
            <button class="primary" disabled={busy || score === originalScore} onclick={regenerateFromScore}>Regenerate from score</button>
            <button disabled={score === originalScore} onclick={() => (score = originalScore)}>Reset</button>
          </div>
        </section>
      {/if}
    </div>
  {/if}
</div>

<style>
  .page { padding: 1.5rem; max-width: 1200px; }
  header { display: flex; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap; }
  .cover { width: 200px; height: 200px; border: none; border-radius: 12px; display: grid; place-items: center; color: #fff; }
  .cover:disabled { opacity: 1; }
  .meta { flex: 1; min-width: 260px; display: flex; flex-direction: column; gap: 0.4rem; }
  .meta h1 { display: flex; align-items: center; gap: 0.25rem; margin: 0; }
  .meta p { margin: 0; }
  .small { font-size: 0.85rem; }
  .warn { color: var(--accent-2); }
  .button { display: inline-flex; gap: 0.4rem; align-items: center; padding: 0.45rem 0.9rem; border: 1px solid var(--border); border-radius: 999px; }
  .button:hover { background: var(--bg-hover); }
  .columns { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; }
  .lyrics { white-space: pre-wrap; font-family: inherit; line-height: 1.6; margin: 0; }
  .score { font-family: ui-monospace, 'JetBrains Mono', monospace; font-size: 0.85rem; margin-bottom: 0.75rem; }
  pre.error { white-space: pre-wrap; font-size: 0.8rem; }
</style>
