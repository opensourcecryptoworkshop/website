import csv
import io
from pathlib import Path

import pytest

import sheet_to_yaml as s2y

REPO = Path(__file__).resolve().parents[2]
DATA_2026 = REPO / "data" / "2026" / "sessions.yaml"

HEADERS = [
    "Timestamp",
    s2y.COL_ID,
    s2y.COL_TITLE,
    s2y.COL_ABSTRACT,
    s2y.COL_CONSENT,
] + [h.format(n=n) for n in (1, 2) for h in s2y.SPEAKER_FIELDS.values()]


def write_csv(path: Path, rows: list[dict]) -> Path:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def response(sub_id, title="A Talk", **extra):
    row = {
        "Timestamp": "2027/01/15 10:00:00",
        s2y.COL_ID: sub_id,
        s2y.COL_TITLE: title,
        s2y.COL_ABSTRACT: "First paragraph.\n\nSecond paragraph.",
        s2y.COL_CONSENT: "Yes, under CC BY-NC-ND 4.0",
        "Speaker 1 name": "Ada Example",
        "Speaker 1 pronouns": "she/her",
        "Speaker 1 affiliation": "Example Org",
        "Speaker 1 bio": "Ada maintains libexample.",
    }
    row.update(extra)
    return row


def dump(sessions) -> str:
    out = io.StringIO()
    s2y.make_yaml().dump(sessions, out)
    return out.getvalue()


def load(text: str):
    return s2y.make_yaml().load(text)


def test_new_session_is_appended_without_time(tmp_path):
    sessions = load("- time: '9:00'\n  break: Breakfast\n")
    rows = s2y.read_rows(write_csv(tmp_path / "r.csv", [response("2027-01")]))
    assert s2y.upsert(sessions, rows) == (1, 0)
    new = sessions[-1]
    assert new["id"] == "2027-01"
    assert new["time"] == ""
    assert new["speakers"][0]["name"] == "Ada Example"
    assert "Second paragraph." in new["abstract"]
    assert "abstract: |" in dump(sessions)


def test_update_preserves_organizer_fields(tmp_path):
    sessions = load(
        "- id: 2027-01\n"
        "  time: 10:00 - 10:30\n"
        "  title: Old Title\n"
        "  video: https://archive.org/details/x\n"
        "  speakers: []\n"
        "  abstract: old\n"
    )
    rows = s2y.read_rows(write_csv(tmp_path / "r.csv", [response("2027-01", title="New Title")]))
    assert s2y.upsert(sessions, rows) == (0, 1)
    session = sessions[0]
    assert session["title"] == "New Title"
    assert session["time"] == "10:00 - 10:30"
    assert session["video"] == "https://archive.org/details/x"
    assert list(session.keys())[:2] == ["id", "time"]


def test_latest_response_wins(tmp_path):
    rows = s2y.read_rows(
        write_csv(
            tmp_path / "r.csv",
            [response("2027-01", title="First"), response("2027-01", title="Corrected")],
        )
    )
    assert rows["2027-01"][s2y.COL_TITLE] == "Corrected"


def test_multiple_speakers(tmp_path):
    row = response(
        "2027-02",
        **{"Speaker 2 name": "Bo Example", "Speaker 2 bio": "Bo also maintains it."},
    )
    session = s2y.row_to_session(row)
    assert [sp["name"] for sp in session["speakers"]] == ["Ada Example", "Bo Example"]


def test_check_flags_missing_details(tmp_path):
    sessions = s2y.CommentedSeq()
    rows = s2y.read_rows(
        write_csv(
            tmp_path / "r.csv",
            [response("2027-03", **{"Speaker 1 bio": "", s2y.COL_CONSENT: "No"})],
        )
    )
    s2y.upsert(sessions, rows)
    problems = s2y.check(sessions)
    assert "2027-03: missing time" in problems
    assert "2027-03: Ada Example missing bio" in problems
    assert "2027-03: no recording consent" in problems


def test_check_2026_reports_only_missing_bios():
    # Past years have no submission IDs, so only time/title/abstract/bio apply,
    # and 2026 is complete apart from a couple of speakers without bios.
    sessions = s2y.load_sessions(s2y.make_yaml(), DATA_2026)
    assert all(p.endswith("missing bio") for p in s2y.check(sessions))


def test_2026_round_trips_unchanged():
    original = DATA_2026.read_text()
    assert dump(load(original)) == original


def test_requires_an_action(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["sheet_to_yaml.py", str(DATA_2026)])
    with pytest.raises(SystemExit):
        s2y.main()
