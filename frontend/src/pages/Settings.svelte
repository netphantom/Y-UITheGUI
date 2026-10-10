<script>
  import { api } from '../lib/api.js';
  import { auth } from '../lib/auth.svelte.js';
  import { formatDate } from '../lib/format.js';

  let status = $state(null);
  let users = $state([]);
  let error = $state('');

  const refresh = async () => {
    try {
      status = await api.system.status();
      if (auth.user.is_admin) users = await api.auth.users();
    } catch (err) {
      error = err.message;
    }
  };
  refresh();

  async function deleteUser(user) {
    if (!confirm(`Delete ${user.username} and all their songs?`)) return;
    await api.auth.deleteUser(user.id).catch((err) => (error = err.message));
    refresh();
  }
</script>

<div class="page">
  <h1>Settings</h1>
  {#if error}<p class="error">{error}</p>{/if}

  {#if status}
    <section class="card">
      <div class="row"><h2>Engine</h2><button class="ghost muted" onclick={refresh}>Refresh</button></div>
      <dl>
        <dt>Engine</dt>
        <dd>
          {status.engine} · {status.engine_ready ? 'ready' : status.engine_error ? 'failed to load' : 'loading…'}
          {#if status.engine_error}<pre class="error">{status.engine_error}</pre>{/if}
        </dd>
        <dt>Model</dt><dd>{status.model_id}</dd>
        <dt>Queue</dt><dd>{status.queue_length} song(s)</dd>
        <dt>Installed YuE2</dt><dd>{status.update.installed_version ?? '—'}</dd>
        <dt>Latest release</dt><dd>{status.update.latest_version ?? '—'}</dd>
        <dt>Update check</dt>
        <dd>
          {status.update.state}
          {#if status.update.message}<span class="muted"> — {status.update.message}</span>{/if}
          {#if status.update.checked_at}<span class="muted"> ({formatDate(status.update.checked_at)})</span>{/if}
        </dd>
      </dl>
    </section>
  {/if}

  {#if auth.user.is_admin}
    <section class="card">
      <h2>Users</h2>
      {#each users as user (user.id)}
        <div class="row user">
          <span>{user.username}{user.is_admin ? ' (admin)' : ''}</span>
          <span class="muted">{formatDate(user.created_at)}</span>
          {#if user.id !== auth.user.id}<button class="danger" onclick={() => deleteUser(user)}>Delete</button>{/if}
        </div>
      {/each}
    </section>
  {/if}
</div>

<style>
  .page { padding: 1.5rem; max-width: 760px; display: flex; flex-direction: column; gap: 1rem; }
  .row { justify-content: space-between; }
  dl { display: grid; grid-template-columns: 140px 1fr; gap: 0.5rem; margin: 0; }
  dt { color: var(--text-muted); }
  dd { margin: 0; }
  pre { white-space: pre-wrap; font-size: 0.8rem; }
  .user { padding: 0.4rem 0; border-bottom: 1px solid var(--border); }
  .user span:first-child { flex: 1; }
</style>
