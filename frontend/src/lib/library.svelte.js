import { api } from './api.js';

const POLL_MS = 3000;
const isPending = (song) => song.status === 'queued' || song.status === 'running';

/**
 * The user's songs and projects, loaded once and shared by every page.
 * While any song is generating, the list is polled so statuses update live.
 */
class Library {
  songs = $state([]);
  projects = $state([]);
  loaded = $state(false);

  #timer = null;

  async load() {
    [this.songs, this.projects] = await Promise.all([api.songs.list(), api.projects.list()]);
    this.loaded = true;
    this.#schedulePoll();
  }

  reset() {
    clearTimeout(this.#timer);
    this.songs = [];
    this.projects = [];
    this.loaded = false;
  }

  song = (id) => this.songs.find((song) => song.id === Number(id));
  project = (id) => this.projects.find((project) => project.id === Number(id));

  // --- Songs ------------------------------------------------------------------

  async generate(request) {
    const created = await api.songs.create(request);
    this.songs = [...created.reverse(), ...this.songs];
    this.#schedulePoll();
    return created;
  }

  async updateSong(id, patch) {
    this.#replaceSong(await api.songs.update(id, patch));
  }

  async deleteSong(id) {
    await api.songs.remove(id);
    this.songs = this.songs.filter((song) => song.id !== id);
  }

  // --- Projects ---------------------------------------------------------------

  async createProject(data) {
    const project = await api.projects.create(data);
    this.projects = [project, ...this.projects];
    return project;
  }

  async updateProject(id, patch) {
    const updated = await api.projects.update(id, patch);
    this.projects = this.projects.map((project) => (project.id === id ? updated : project));
  }

  async deleteProject(id) {
    await api.projects.remove(id);
    this.projects = this.projects.filter((project) => project.id !== id);
    // The backend detaches the songs (project_id = NULL): mirror it locally.
    this.songs = this.songs.map((song) => (song.project_id === id ? { ...song, project_id: null } : song));
  }

  // --- Internals --------------------------------------------------------------

  #replaceSong(updated) {
    this.songs = this.songs.map((song) => (song.id === updated.id ? updated : song));
  }

  #schedulePoll() {
    clearTimeout(this.#timer);
    if (!this.songs.some(isPending)) return;
    this.#timer = setTimeout(async () => {
      const pending = this.songs.filter(isPending);
      const fresh = await Promise.all(pending.map((song) => api.songs.get(song.id).catch(() => song)));
      fresh.forEach((song) => this.#replaceSong(song));
      this.#schedulePoll();
    }, POLL_MS);
  }
}

export const library = new Library();
