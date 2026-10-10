/** Small presentation helpers shared by components. */

/** Deterministic cover art: two hues derived from the seed, so variants look different. */
export function coverGradient(song) {
  const hue = (song.seed * 47) % 360;
  return `linear-gradient(135deg, hsl(${hue} 70% 45%), hsl(${(hue + 60) % 360} 80% 30%))`;
}

export function formatTime(seconds) {
  if (!Number.isFinite(seconds)) return '0:00';
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
}

export const formatDate = (iso) => new Date(iso).toLocaleString();

export const STATUS_LABELS = {
  queued: 'In queue',
  running: 'Generating…',
  succeeded: 'Ready',
  failed: 'Failed',
};
