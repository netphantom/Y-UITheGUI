# Y-UI — a Suno-style studio for self-hosted YuE2

Web UI for [YuE2](https://github.com/multimodal-art-projection/YuE) (`m-a-p/YuE2-3B`):
multi-user accounts, projects, a library of generated songs, a persistent player, and
YuE2's editable **ABC score**: change melody and chords, then render a new version.

```
┌────────────── frontend ──────────────┐      ┌──────────────── backend ────────────────┐
│ Svelte 5 SPA, served by nginx        │ /api │ FastAPI                                 │
│ Create · Library · Projects · Song   │ ───► │  auth (cookie sessions) · projects      │
│ Settings · bottom player             │      │  songs ─► SQLite queue ─► GPU worker    │
└──────────────────────────────────────┘      │  startup: YuE2 update check → load model│
                                              └─────────────────────────────────────────┘
```

## Quick start (Docker)

Requirements: NVIDIA GPU with BF16 and ~24 GB VRAM, NVIDIA driver and
[container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/).

```bash
cp .env.example .env
docker compose up -d --build
# open http://localhost:8080 — the first account you register becomes admin
```

The first start downloads the model weights (several GB) into `./data/huggingface`.
The UI is usable meanwhile; songs wait in the queue until **Settings → Engine** shows *ready*.

**No GPU?** Set `YUI_ENGINE=mock` and `INSTALL_YUE=false` in `.env` and remove the
`deploy:` block from `docker-compose.yml`: the mock engine writes a short tone and an
example score, enough to work on the UI.

## Development without Docker

```bash
# backend (Python 3.12+)
cd backend
uv venv && uv pip install -e ".[dev]"          # add ",yue" for the real engine
YUI_ENGINE=mock YUI_AUTO_UPDATE=false .venv/bin/uvicorn app.main:app --reload
.venv/bin/pytest

# frontend (Node 22+), proxies /api to :8000
cd frontend
npm install && npm run dev
```

## YuE2 updates

At every backend start, `app/yue/updater.py` reads the latest GitHub release of
`multimodal-art-projection/YuE` (tags such as `yue2-v0.1.6`), compares it with the
installed `yue2-infer` package and runs `pip install` if a newer one exists, **before**
the model is imported. Model weights are refreshed by `from_pretrained` through the
Hugging Face cache. A failed check (offline, rate limit) is logged and the installed version
keeps working. To freeze a version, set `YUI_YUE_PINNED_TAG`; to turn the check off,
`YUI_AUTO_UPDATE=false`.

## Exposing it outside your LAN

1. Put a TLS reverse proxy in front of port 8080 (e.g. Caddy: `yui.example.com { reverse_proxy localhost:8080 }`).
2. Set `YUI_COOKIE_SECURE=true`.
3. After creating your accounts, set `YUI_ALLOW_REGISTRATION=false`.

## Layout

```
backend/app/
  config.py          settings (YUI_* env vars)
  db.py, models.py   SQLite + SQLAlchemy models
  repository.py      generic owner-scoped repository (all per-user data access)
  routers/crud.py    router factory for standard CRUD resources (used by projects)
  routers/           auth, songs, system
  yue/engine.py      MusicEngine protocol, YuE2 + mock implementations
  yue/worker.py      serial GPU queue backed by the songs table
  yue/updater.py     startup release check and upgrade
frontend/src/
  lib/api.js         REST client (resource factory mirrors the backend)
  lib/*.svelte.js    shared state: auth, library (with live polling), player, router
  components/, pages/
```

## License

Y-UI is released under the [MIT License](LICENSE).

This UI does not include YuE2. YuE2's code is Apache-2.0, but its **weights are
CC BY-NC 4.0**: songs generated with them may not be used commercially.
