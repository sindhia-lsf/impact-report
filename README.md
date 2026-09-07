# Black Tech Week 2026 Impact Report Dashboard

This repository contains the code and supporting aggregate data for the Black Tech Week 2026 impact report dashboard.

The current branch imports the public dashboard baseline that was built through Manus and published at:

https://blackdash-kq75eadu.manus.space

## Contents

- `public/` - static dashboard capture from the Manus-published site.
- `source-data/` - aggregate-only JSON snapshots used to shape the report and dashboard.
- `docs/` - Manus dashboard build and revision briefs.
- `manuscript/` - OpenClaw-generated HTML/report builder artifacts used during the impact report work.

## Data Handling

This project should use aggregate-only reporting data. Do not commit personal identifiers, row-level attendee exports, names, emails, phone numbers, private notes, or raw operational credentials.

## Workflow

All feature work should happen on feature branches first. Merge into `master` only after review and testing.
