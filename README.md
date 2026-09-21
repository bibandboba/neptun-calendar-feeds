# Neptun calendar feeds

This repository fetches the private Neptun iCalendar feed on a schedule and
publishes three filtered feeds through token-protected, unguessable GitHub Pages
paths:

- `lectures.ics` — lesson codes `E01`, `E02`, …
- `seminars.ics` — lesson codes `G01`, `G02`, …
- `other.ics` — events without an `E…` or `G…` lesson code

The source subscription URL and feed token are stored only as GitHub Actions
secrets. They are never committed to this repository or printed by the workflow.
The Pages build intentionally contains no unprotected `*.ics` files at the
site root. The token is a bearer secret: anyone who obtains a full feed URL can
read that feed, so the URLs must not be published or shared.
