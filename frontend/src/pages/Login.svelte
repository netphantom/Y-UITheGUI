<script>
  import { api } from '../lib/api.js';
  import { auth } from '../lib/auth.svelte.js';

  let mode = $state('login');
  let username = $state('');
  let password = $state('');
  let error = $state('');
  let busy = $state(false);
  let allowRegistration = $state(true);

  api.system.status().then((status) => (allowRegistration = status.allow_registration)).catch(() => {});

  async function submit(event) {
    event.preventDefault();
    busy = true;
    error = '';
    try {
      await auth[mode]({ username, password });
    } catch (err) {
      error = err.message;
    } finally {
      busy = false;
    }
  }
</script>

<main>
  <form class="card" onsubmit={submit}>
    <img class="logo" src="/logo.png" alt="Y-UI" />
    <p class="muted tagline">Make a song with YuE2, on your own hardware.</p>

    <div class="field">
      <label for="username">Username</label>
      <input id="username" bind:value={username} autocomplete="username" required />
    </div>
    <div class="field">
      <label for="password">Password</label>
      <input
        id="password"
        type="password"
        bind:value={password}
        autocomplete={mode === 'login' ? 'current-password' : 'new-password'}
        minlength={mode === 'register' ? 8 : undefined}
        required
      />
    </div>
    {#if error}<p class="error">{error}</p>{/if}

    <button class="primary" disabled={busy}>{mode === 'login' ? 'Log in' : 'Create account'}</button>

    {#if allowRegistration}
      <button type="button" class="ghost switch" onclick={() => (mode = mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? 'No account? Sign up' : 'Have an account? Log in'}
      </button>
    {/if}
  </form>
</main>

<style>
  main {
    min-height: 100vh;
    display: grid;
    place-items: center;
    background:
      radial-gradient(circle at 25% 20%, rgb(0 212 255 / 0.18), transparent 45%),
      radial-gradient(circle at 75% 80%, rgb(232 60 240 / 0.18), transparent 45%),
      var(--bg);
  }
  form { width: min(380px, 92vw); padding: 2rem; display: flex; flex-direction: column; }
  .logo { width: 120px; height: 120px; align-self: center; filter: drop-shadow(0 10px 30px rgb(168 85 247 / 0.35)); }
  .tagline { text-align: center; margin-bottom: 1.5rem; }
  .primary { padding: 0.7rem; }
  .switch { margin-top: 0.75rem; color: var(--text-muted); }
</style>
