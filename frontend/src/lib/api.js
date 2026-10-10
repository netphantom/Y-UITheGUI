/**
 * Thin client for the backend REST API. Authentication is an httpOnly cookie,
 * so requests only need `credentials: 'include'` and no token handling.
 */

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

/** Listeners notified on 401, so the app can drop back to the login page. */
const unauthorizedListeners = new Set();
export const onUnauthorized = (listener) => unauthorizedListeners.add(listener);

function errorMessage(body) {
  if (typeof body?.detail === 'string') return body.detail;
  // FastAPI validation errors: [{ loc, msg }, ...]
  if (Array.isArray(body?.detail)) return body.detail.map((e) => `${e.loc.at(-1)}: ${e.msg}`).join(', ');
  return 'Unexpected error';
}

export async function request(method, path, body) {
  const response = await fetch(`/api${path}`, {
    method,
    credentials: 'include',
    headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (response.status === 401) unauthorizedListeners.forEach((listener) => listener());
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new ApiError(response.status, errorMessage(payload));
  }
  if (response.status === 204) return null;
  const type = response.headers.get('Content-Type') ?? '';
  return type.includes('application/json') ? response.json() : response.text();
}

const query = (params = {}) => {
  const defined = Object.entries(params).filter(([, value]) => value !== undefined && value !== null);
  return defined.length ? `?${new URLSearchParams(defined)}` : '';
};

/** Standard CRUD client for a REST collection (mirrors the backend router factory). */
function resource(path) {
  return {
    list: (params) => request('GET', `${path}${query(params)}`),
    get: (id) => request('GET', `${path}/${id}`),
    create: (data) => request('POST', path, data),
    update: (id, patch) => request('PATCH', `${path}/${id}`, patch),
    remove: (id) => request('DELETE', `${path}/${id}`),
  };
}

export const api = {
  auth: {
    me: () => request('GET', '/auth/me'),
    login: (credentials) => request('POST', '/auth/login', credentials),
    register: (credentials) => request('POST', '/auth/register', credentials),
    logout: () => request('POST', '/auth/logout'),
    users: () => request('GET', '/auth/users'),
    deleteUser: (id) => request('DELETE', `/auth/users/${id}`),
  },
  projects: resource('/projects'),
  songs: {
    ...resource('/songs'),
    score: (id) => request('GET', `/songs/${id}/score`),
    audioUrl: (id, download = false) => `/api/songs/${id}/audio${download ? '?download=true' : ''}`,
    scoreUrl: (id) => `/api/songs/${id}/score`,
  },
  system: {
    status: () => request('GET', '/system/status'),
  },
};
