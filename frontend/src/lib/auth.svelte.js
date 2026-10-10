import { api, onUnauthorized } from './api.js';

/** Logged-in user state. `user === undefined` means "still checking the session". */
class Auth {
  user = $state(undefined);

  constructor() {
    onUnauthorized(() => (this.user = null));
  }

  async restore() {
    this.user = await api.auth.me().catch(() => null);
  }

  async login(credentials) {
    this.user = await api.auth.login(credentials);
  }

  async register(credentials) {
    this.user = await api.auth.register(credentials);
  }

  async logout() {
    await api.auth.logout().catch(() => {});
    this.user = null;
  }
}

export const auth = new Auth();
