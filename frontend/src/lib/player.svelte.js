import { api } from './api.js';

/** The single, app-wide audio player shown in the bottom bar. */
class Player {
  song = $state(null);
  playing = $state(false);
  currentTime = $state(0);
  duration = $state(0);
  volume = $state(0.9);

  #audio = new Audio();

  constructor() {
    const audio = this.#audio;
    audio.addEventListener('timeupdate', () => (this.currentTime = audio.currentTime));
    audio.addEventListener('durationchange', () => (this.duration = audio.duration || 0));
    audio.addEventListener('play', () => (this.playing = true));
    audio.addEventListener('pause', () => (this.playing = false));
    audio.addEventListener('ended', () => (this.playing = false));
  }

  /** Play a song, or toggle pause if it is the current one. */
  toggle(song) {
    if (this.song?.id === song.id) {
      this.#audio.paused ? this.#audio.play() : this.#audio.pause();
      return;
    }
    this.song = song;
    this.#audio.src = api.songs.audioUrl(song.id);
    this.#audio.volume = this.volume;
    this.#audio.play();
  }

  isPlaying = (song) => this.playing && this.song?.id === song.id;

  seek(seconds) {
    this.#audio.currentTime = seconds;
  }

  setVolume(volume) {
    this.volume = volume;
    this.#audio.volume = volume;
  }

  stop() {
    this.#audio.pause();
    this.#audio.removeAttribute('src');
    this.song = null;
  }
}

export const player = new Player();
