#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# "rich", "ruamel.yaml"
# ]
# ///
"""Sync accepted-session details from the acceptance form into data/<year>/sessions.yaml.

Reads the CSV export of the phase-2 (acceptance) Google Form and upserts each
session into the schedule data file by submission ID. Fields organizers own in
the YAML (time, video, slot order, breaks) are preserved; fields speakers own
(title, abstract, speakers, recording consent) are replaced from the CSV.

With --check, reports sessions that are missing details needed for the site.
"""

import argparse
import csv
import logging
import sys
from pathlib import Path

from rich.console import Console
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.scalarstring import LiteralScalarString

PARSER = argparse.ArgumentParser(description=__doc__)

PARSER.add_argument(
    "--log-level",
    default=logging.INFO,
    type=lambda x: getattr(logging, x.upper()),
    help="Configure the logging level.",
)
PARSER.add_argument("yaml", type=Path, help="Path to data/<year>/sessions.yaml")
PARSER.add_argument("--csv", type=Path, help="CSV export of the acceptance form")
PARSER.add_argument(
    "--check",
    action="store_true",
    help="Report sessions missing details; exit non-zero if any are found.",
)

LOG = logging.getLogger("sheet_to_yaml")

# Column headers of the acceptance form; keep in sync with tools/cfp/README.md.
COL_ID = "Submission ID"
COL_TITLE = "Final title"
COL_ABSTRACT = "Final abstract"
COL_CONSENT = "Recording consent"
MAX_SPEAKERS = 4
SPEAKER_FIELDS = {
    "name": "Speaker {n} name",
    "pronouns": "Speaker {n} pronouns",
    "affiliation": "Speaker {n} affiliation",
    "link": "Speaker {n} link",
    "bio": "Speaker {n} bio",
    "headshot": "Speaker {n} headshot URL",
}


def text_value(value: str) -> str | LiteralScalarString:
    """Normalize form text, using a YAML block scalar for multi-line values."""
    value = "\n".join(line.rstrip() for line in value.strip().splitlines())
    if "\n" in value:
        return LiteralScalarString(value + "\n")
    return value


def read_rows(csv_path: Path) -> dict[str, dict[str, str]]:
    """Read the form export, keeping the latest response for each submission ID."""
    rows = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sub_id = (row.get(COL_ID) or "").strip()
            if not sub_id:
                LOG.warning("Skipping response with no %r", COL_ID)
                continue
            if sub_id in rows:
                LOG.info("%s: using later response", sub_id)
            rows[sub_id] = row
    return rows


def row_to_session(row: dict[str, str]) -> dict:
    """Convert one form response into the speaker-owned session fields."""
    speakers = []
    for n in range(1, MAX_SPEAKERS + 1):
        name = (row.get(SPEAKER_FIELDS["name"].format(n=n)) or "").strip()
        if not name:
            continue
        speaker = CommentedMap()
        for key, header in SPEAKER_FIELDS.items():
            speaker[key] = text_value(row.get(header.format(n=n)) or "")
        speakers.append(speaker)
    return {
        "title": text_value(row.get(COL_TITLE) or ""),
        "abstract": text_value(row.get(COL_ABSTRACT) or ""),
        "speakers": CommentedSeq(speakers),
        "recording_consent": text_value(row.get(COL_CONSENT) or ""),
    }


def upsert(sessions: CommentedSeq, rows: dict[str, dict[str, str]]) -> tuple[int, int]:
    """Update sessions in place from form rows; returns (added, updated)."""
    by_id = {s["id"]: s for s in sessions if "id" in s}
    added = updated = 0
    for sub_id, row in rows.items():
        fields = row_to_session(row)
        if sub_id in by_id:
            by_id[sub_id].update(fields)
            updated += 1
        else:
            session = CommentedMap(id=sub_id, time="")
            session.update(fields)
            sessions.append(session)
            added += 1
    return added, updated


def check(sessions: CommentedSeq) -> list[str]:
    """Return a description of each missing detail."""
    problems = []
    for session in sessions:
        if "break" in session:
            continue
        label = session.get("id") or session.get("title") or "<untitled>"
        for key in ("time", "title", "abstract"):
            if not session.get(key):
                problems.append(f"{label}: missing {key}")
        if not session.get("speakers"):
            problems.append(f"{label}: no speakers")
        for speaker in session.get("speakers") or []:
            name = speaker.get("name") or "<unnamed>"
            if not speaker.get("bio"):
                problems.append(f"{label}: {name} missing bio")
            # Sessions that came through the CFP forms carry an ID and the
            # fields the acceptance form collects.
            if "id" in session and not speaker.get("affiliation"):
                problems.append(f"{label}: {name} missing affiliation")
        if "id" in session and not str(session.get("recording_consent", "")).lower().startswith("yes"):
            problems.append(f"{label}: no recording consent")
    return problems


def make_yaml() -> YAML:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=2, offset=0)
    return yaml


def load_sessions(yaml: YAML, path: Path) -> CommentedSeq:
    if not path.exists():
        return CommentedSeq()
    return yaml.load(path) or CommentedSeq()


def main():
    args = PARSER.parse_args()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=args.log_level, format=log_format)
    console = Console()

    if not args.csv and not args.check:
        PARSER.error("nothing to do; pass --csv and/or --check")

    yaml = make_yaml()
    sessions = load_sessions(yaml, args.yaml)

    if args.csv:
        added, updated = upsert(sessions, read_rows(args.csv))
        args.yaml.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(sessions, args.yaml)
        console.print(f"[green]{args.yaml}[/]: {added} added, {updated} updated")
        if added:
            console.print("[yellow]New sessions have no time; set it and reorder them in the file.[/]")

    if args.check:
        problems = check(sessions)
        for problem in problems:
            console.print(f"[red]✗[/] {problem}")
        if problems:
            sys.exit(1)
        console.print("[green]All sessions complete.[/]")


if __name__ == "__main__":
    main()
