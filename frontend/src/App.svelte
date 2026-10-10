<script>
  import PlayerBar from './components/PlayerBar.svelte';
  import Sidebar from './components/Sidebar.svelte';
  import { auth } from './lib/auth.svelte.js';
  import { library } from './lib/library.svelte.js';
  import { player } from './lib/player.svelte.js';
  import { createRouter } from './lib/router.svelte.js';
  import Create from './pages/Create.svelte';
  import Library from './pages/Library.svelte';
  import Login from './pages/Login.svelte';
  import NotFound from './pages/NotFound.svelte';
  import Project from './pages/Project.svelte';
  import Projects from './pages/Projects.svelte';
  import Settings from './pages/Settings.svelte';
  import Song from './pages/Song.svelte';

  const route = createRouter(
    {
      '/': Create,
      '/library': Library,
      '/projects': Projects,
      '/projects/:id': Project,
      '/songs/:id': Song,
      '/settings': Settings,
    },
    NotFound,
  );

  auth.restore();

  // Load the user's data on login, wipe it on logout.
  $effect(() => {
    if (auth.user) {
      library.load();
    } else {
      library.reset();
      player.stop();
    }
  });
</script>

{#if auth.user === undefined}
  <!-- Checking the session cookie -->
{:else if auth.user === null}
  <Login />
{:else}
  <div class="shell">
    <Sidebar currentPath={route.path} />
    <main>
      {#if library.loaded}
        <route.component params={route.params} query={route.query} />
      {/if}
    </main>
  </div>
  <PlayerBar />
{/if}

<style>
  .shell { display: flex; height: calc(100vh - var(--player-height)); }
  main { flex: 1; overflow-y: auto; min-width: 0; }

  @media (max-width: 760px) {
    .shell { flex-direction: column; height: auto; min-height: calc(100vh - var(--player-height)); }
  }
</style>
