<script>
  import Icon from './Icon.svelte';
  import { auth } from '../lib/auth.svelte.js';

  let { currentPath } = $props();

  const LINKS = [
    { path: '/', label: 'Create', icon: 'create' },
    { path: '/library', label: 'Library', icon: 'library' },
    { path: '/projects', label: 'Projects', icon: 'projects' },
    { path: '/settings', label: 'Settings', icon: 'settings' },
  ];

  const isActive = (path) => (path === '/' ? currentPath === '/' : currentPath.startsWith(path));
</script>

<nav>
  <a class="logo" href="#/"><span>Y</span>-UI</a>

  {#each LINKS as link (link.path)}
    <a href="#{link.path}" class="link" class:active={isActive(link.path)}>
      <Icon name={link.icon} />
      {link.label}
    </a>
  {/each}

  <div class="user">
    <span class="avatar">{auth.user.username[0].toUpperCase()}</span>
    <span class="name">{auth.user.username}</span>
    <button class="ghost" title="Log out" onclick={() => auth.logout()}>
      <Icon name="logout" />
    </button>
  </div>
</nav>

<style>
  nav {
    width: var(--sidebar-width);
    padding: 1.25rem 0.75rem;
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  .logo {
    font-size: 1.5rem;
    font-weight: 800;
    padding: 0 0.75rem 1.25rem;
    letter-spacing: -0.03em;
  }
  .logo span {
    background: var(--gradient);
    background-clip: text;
    color: transparent;
  }
  .link {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    padding: 0.6rem 0.75rem;
    border-radius: 8px;
    color: var(--text-muted);
    font-weight: 500;
  }
  .link:hover { background: var(--bg-hover); color: var(--text); }
  .link.active { background: var(--bg-hover); color: var(--text); }
  .user {
    margin-top: auto;
    display: flex;
    gap: 0.6rem;
    align-items: center;
    padding: 0.5rem 0.5rem 0;
  }
  .avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: var(--gradient);
    font-weight: 700;
  }
  .name { flex: 1; overflow: hidden; text-overflow: ellipsis; }

  @media (max-width: 760px) {
    nav { width: auto; flex-direction: row; border-right: none; border-bottom: 1px solid var(--border); padding: 0.5rem; overflow-x: auto; }
    .logo { padding: 0.5rem; }
    .user { margin: 0 0 0 auto; padding: 0; }
    .name { display: none; }
  }
</style>
