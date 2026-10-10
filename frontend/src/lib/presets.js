/** Suggestions for the Create page. YuE2 reads style as comma-separated descriptors. */

export const STYLE_TAGS = {
  Genre: ['pop', 'rock', 'jazz-funk', 'hip hop', 'r&b', 'edm', 'lo-fi', 'metal', 'folk', 'cantautorato', 'synthwave', 'reggaeton'],
  Mood: ['uplifting', 'melancholic', 'dreamy', 'energetic', 'dark', 'romantic', 'chill'],
  Instruments: ['acoustic piano', 'Rhodes', 'electric guitar', 'acoustic guitar', 'strings', 'synth pads', '808 bass', 'light drums'],
  Voice: ['expressive female voice', 'warm male voice', 'raspy vocals', 'choir', 'duet'],
  Language: ['English', 'Italian', 'Spanish', 'Japanese', 'Chinese'],
  Tempo: ['70 BPM', '90 BPM', '110 BPM', '128 BPM', '150 BPM'],
};

export const SECTION_TAGS = ['[Intro]', '[Verse]', '[Pre-Chorus]', '[Chorus]', '[Bridge]', '[Outro]'];

export const PLAN_MODES = [
  { value: 'full', label: 'Full plan', hint: 'Melody + chords score, editable afterwards (default)' },
  { value: 'melody', label: 'Melody only', hint: 'Melody score with free accompaniment' },
  { value: 'off', label: 'No plan', hint: 'Straight from lyrics and style, no editable score' },
];
