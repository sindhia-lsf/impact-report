# Editable Impact Report Dashboard

This directory contains the repo-native Black Tech Week 2026 impact dashboard. It is intentionally dependency-light: Node serves the editable HTML/CSS/JS client and exposes the aggregate-only JSON already tracked in `../source-data/impact-summary.json`.

## Run locally

```bash
cd dashboard
npm start
# open http://localhost:3000
```

Set `PORT` when a host provides one:

```bash
PORT=8080 npm start
```

The client calls `GET /api/report`; no Manus hosting, build service, database, authentication, or external runtime is required. This makes the app suitable for OpenClaw on the OVH VPS and later routing through a Railway SSH proxy.

## Edit the report

Update aggregate values in `../source-data/impact-summary.json` and refresh the page. Sponsor-facing presentation choices live in `public/index.html`, `public/styles.css`, and `public/app.js`. The “In-Person Attendees” headline intentionally presents the approved 5,249 combined in-room reach, while the source remains aggregate-only.

## Data guardrails

Do not add personal identifiers, row-level exports, names, emails, phone numbers, private notes, or credentials. Economic impact is labeled as modeled and is not presented as audited results. Bootcamp and paid/unpaid details are intentionally excluded from the sponsor-facing UI.


## Manus design snapshot

The current Manus-edited blackdash design, including the updated **12,000+** footprint value and its current text/content, is preserved under `dashboard/public/manus-import/`. Run the local server and open `/manus-import/index.html` to view that snapshot. The existing repo-native dashboard source remains at the dashboard root and is not deleted.
