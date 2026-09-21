#!/usr/bin/env python3
"""Fetch the Neptun iCalendar feed and publish filtered calendars."""
from __future__ import annotations

import os
import re
import ssl
import urllib.request
from pathlib import Path


CODE_RE = re.compile(r"\(\s*-\s*[EG]\d+\s*\)", re.IGNORECASE)
LECTURE_RE = re.compile(r"\(\s*-\s*E\d+\s*\)", re.IGNORECASE)
SEMINAR_RE = re.compile(r"\(\s*-\s*G\d+\s*\)", re.IGNORECASE)


def unfold(lines: list[str]) -> list[str]:
    result: list[str] = []
    for line in lines:
        if line.startswith((" ", "\t")) and result:
            result[-1] += line[1:]
        else:
            result.append(line)
    return result


def summary_from_event(event_lines: list[str]) -> str:
    for line in unfold(event_lines):
        if line.startswith("SUMMARY:"):
            return line[len("SUMMARY:") :]
    return ""


def matches(kind: str, summary: str) -> bool:
    if kind == "lecture":
        return bool(LECTURE_RE.search(summary))
    if kind == "seminar":
        return bool(SEMINAR_RE.search(summary))
    if kind == "other":
        return not bool(CODE_RE.search(summary))
    raise ValueError(f"Unknown feed kind: {kind}")


def filter_calendar(source: str, kind: str, name: str) -> tuple[str, int]:
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    output: list[str] = []
    event: list[str] = []
    inside_event = False
    selected = 0

    for line in lines:
        if line == "BEGIN:VEVENT":
            inside_event = True
            event = [line]
            continue

        if not inside_event:
            output.append(line)
            continue

        event.append(line)
        if line == "END:VEVENT":
            if matches(kind, summary_from_event(event)):
                output.extend(event)
                selected += 1
            inside_event = False

    for index, line in enumerate(output):
        if line.startswith("X-WR-CALNAME:"):
            output[index] = "X-WR-CALNAME:" + name

    result = "\r\n".join(output).rstrip("\r\n") + "\r\n"
    return result, selected


def fetch_source() -> str:
    url = os.environ["NEPTUN_ICS_URL"].strip()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "neptun-calendar-feeds/1.0"},
    )
    # The Neptun endpoint currently serves a valid feed with an incomplete
    # certificate chain. GitHub's runner can reach it only with this flag.
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, timeout=120, context=context) as response:
        body = response.read().decode("utf-8-sig")

    if "BEGIN:VCALENDAR" not in body or "END:VCALENDAR" not in body:
        raise RuntimeError("Neptun response is not an iCalendar feed")
    return body


def main() -> None:
    source = fetch_source()
    public = Path("public")
    public.mkdir(parents=True, exist_ok=True)

    specs = {
        "lecture": ("lectures.ics", "Neptun - Lectures"),
        "seminar": ("seminars.ics", "Neptun - Seminars"),
        "other": ("other.ics", "Neptun - Other events"),
    }

    total = 0
    for kind, (filename, name) in specs.items():
        filtered, count = filter_calendar(source, kind, name)
        (public / filename).write_text(filtered, encoding="utf-8", newline="")
        print(f"{filename}: {count} events")
        total += count

    # A simple landing page makes accidental browser visits understandable.
    (public / "index.html").write_text(
        "<!doctype html><meta charset=\"utf-8\"><title>Neptun calendar feeds</title>"
        "<p>Calendar feeds: <a href=\"lectures.ics\">lectures</a>, "
        "<a href=\"seminars.ics\">seminars</a>, "
        "<a href=\"other.ics\">other events</a>.</p>\n",
        encoding="utf-8",
    )
    print(f"total published events: {total}")


if __name__ == "__main__":
    main()
