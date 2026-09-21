# Neptun calendar feeds

This repository fetches the private Neptun iCalendar feed on a schedule and
publishes three filtered feeds through GitHub Pages:

- `lectures.ics` — lesson codes `E01`, `E02`, …
- `seminars.ics` — lesson codes `G01`, `G02`, …
- `other.ics` — events without an `E…` or `G…` lesson code

The source subscription URL is stored only as the `NEPTUN_ICS_URL` GitHub
Actions secret. It is never committed to this repository or printed by the
workflow.
