/**
 * Minimal hash router: `#/songs/12` matches the pattern `/songs/:id` with params { id: '12' }.
 * Hash routing needs no server configuration, which keeps self-hosting trivial.
 */

function compile(pattern) {
  const keys = [];
  const source = pattern.replace(/:(\w+)/g, (_, key) => {
    keys.push(key);
    return '([^/]+)';
  });
  return { regex: new RegExp(`^${source}$`), keys };
}

export function createRouter(routes, fallback) {
  const compiled = Object.entries(routes).map(([pattern, component]) => ({ ...compile(pattern), component }));

  const state = $state({ path: '/', component: fallback, params: {}, query: {} });

  function resolve() {
    const [path, search = ''] = (location.hash.slice(1) || '/').split('?');
    state.path = path;
    state.query = Object.fromEntries(new URLSearchParams(search));
    for (const { regex, keys, component } of compiled) {
      const match = path.match(regex);
      if (match) {
        state.component = component;
        state.params = Object.fromEntries(keys.map((key, i) => [key, decodeURIComponent(match[i + 1])]));
        return;
      }
    }
    state.component = fallback;
    state.params = {};
  }

  window.addEventListener('hashchange', resolve);
  resolve();
  return state;
}

export const navigate = (path) => (location.hash = path);
