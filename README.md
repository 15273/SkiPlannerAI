# skiMate

Monorepo for the **skiMate** MVP (GitHub repo: `SkiPlannerAI`): curated resort and map data, a FastAPI backend, flight search (Amadeus when configured) with ranking and deep-link fallback, and an Expo (React Native) app for iOS and Android.

## Repository layout

| Path | Purpose |
|------|---------|
| [apps/mobile](apps/mobile) | Expo app (iOS + Android) |
| [services/api](services/api) | REST API (FastAPI) |
| [data/seed](data/seed) | Curated resort seeds and GeoJSON map snippets |
| [docs](docs) | ADRs, data ingest spec, map API contract, booking hooks, QA |

## Secrets

Copy [.env.example](.env.example) to `.env` at the repo root for local development. Never commit real credentials. For Amadeus, create keys in the Amadeus for Developers portal (test environment).

## Run the API

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn skiplanner_api.main:app --reload --host 0.0.0.0 --port 8040
```

Or from repo root: `./scripts/run_api.sh` (default port **8040**; override: `API_PORT=9000 ./scripts/run_api.sh`).

Open `http://localhost:8040/docs` for OpenAPI.

## Run the mobile app

```bash
cd apps/mobile
npm install
npx expo start
```

Use a simulator or device. For a physical device, set `expo.extra.apiBaseUrl` in [apps/mobile/app.json](apps/mobile/app.json) to your machine LAN IP (e.g. `http://192.168.1.10:8040`).

## GitHub milestones and issues

To bootstrap milestones and MVP issues on GitHub (requires [`gh`](https://cli.github.com/) and auth):

```bash
./scripts/gh_bootstrap_mvp.sh 15273/SkiPlannerAI
```

### Link open issues to a GitHub Project (skiMate)

The **skiMate** board is user project **#5**: [project settings](https://github.com/users/15273/projects/5/settings).

Issues are **milestones**, not the same as a **Project** board. The CLI needs extra OAuth scopes (`read:project`, `project`):

```bash
gh auth refresh -h github.com -s read:project -s project
```

Then link all open issues in this repo (script defaults to project `5`, owner `15273`):

```bash
chmod +x ./scripts/gh_link_issues_to_project.sh
./scripts/gh_link_issues_to_project.sh
```

To use a different project: `export GITHUB_PROJECT_NUMBER=...` or run `gh project list --owner 15273`.

Alternatively, in the GitHub web UI: open the **skiMate** project → **Add item** → search issues from `SkiPlannerAI`, or enable workflow automation in project settings to auto-add issues from this repository.

## Legacy entry

The top-level [main.py](main.py) is kept as a minimal stub; the product API lives under `services/api/`.
