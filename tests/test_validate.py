"""Tests for scripts/validate.py.

Run with: python3 -m unittest tests.test_validate
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402

VALID_DECISION = (
    '{"timestamp":"2026-05-19T00:00:00Z","type":"decision","component":"x",'
    '"change":"y","reason":"z","impact":["a"],"author":"test"}'
)
VALID_DRIFT = (
    '{"timestamp":"2026-05-19T00:00:00Z","type":"drift","severity":"low",'
    '"detected":"x","location":"a:1","suggested_action":"fix"}'
)


def write_memory(
    tmp: Path,
    *,
    arch: str | None = "# arch\n",
    progress: str | None = "# progress\n",
    decisions: str | None = "",
    drift: str | None = "",
) -> Path:
    mem = tmp / "memory"
    mem.mkdir()
    if arch is not None:
        (mem / "architecture.md").write_text(arch)
    if progress is not None:
        (mem / "progress.md").write_text(progress)
    if decisions is not None:
        (mem / "decisions.jsonl").write_text(decisions)
    if drift is not None:
        (mem / "drift.jsonl").write_text(drift)
    return mem


class ValidateTests(unittest.TestCase):
    def _run(self, **kw):
        check_freshness_days = kw.pop("check_freshness_days", None)
        today = kw.pop("today", None)
        with TemporaryDirectory() as d:
            mem = write_memory(Path(d), **kw)
            return validate.validate(
                mem,
                check_freshness_days=check_freshness_days,
                today=today,
            )

    def test_empty_memory_is_valid(self):
        code, errors, warnings, decisions, drifts = self._run()
        self.assertEqual(code, 0, errors)
        self.assertEqual((decisions, drifts), (0, 0))
        self.assertEqual(warnings, [])

    def test_one_good_decision_and_drift(self):
        code, errors, _w, d, dr = self._run(decisions=VALID_DECISION + "\n", drift=VALID_DRIFT + "\n")
        self.assertEqual(code, 0, errors)
        self.assertEqual((d, dr), (1, 1))

    def test_missing_architecture(self):
        code, errors, *_ = self._run(arch=None)
        self.assertEqual(code, 1)
        self.assertTrue(any("architecture.md" in e and "missing" in e for e in errors))

    def test_missing_progress(self):
        code, errors, *_ = self._run(progress=None)
        self.assertEqual(code, 1)
        self.assertTrue(any("progress.md" in e and "missing" in e for e in errors))

    def test_architecture_too_long(self):
        code, errors, *_ = self._run(arch="x\n" * 201)
        self.assertEqual(code, 1)
        self.assertTrue(any("exceeds 200" in e for e in errors))

    def test_progress_too_long(self):
        code, errors, *_ = self._run(progress="x\n" * 101)
        self.assertEqual(code, 1)
        self.assertTrue(any("exceeds 100" in e for e in errors))

    def test_invalid_json_in_decisions(self):
        code, errors, *_ = self._run(decisions="{not json}\n")
        self.assertEqual(code, 1)
        self.assertTrue(any("invalid JSON" in e for e in errors))

    def test_bad_decision_type(self):
        bad = VALID_DECISION.replace('"type":"decision"', '"type":"nonsense"')
        code, errors, *_ = self._run(decisions=bad + "\n")
        self.assertEqual(code, 1)
        self.assertTrue(any("type 'nonsense'" in e for e in errors))

    def test_missing_decision_field(self):
        bad = VALID_DECISION.replace(',"author":"test"', "")
        code, errors, *_ = self._run(decisions=bad + "\n")
        self.assertEqual(code, 1)
        self.assertTrue(any("missing fields" in e and "author" in e for e in errors))

    def test_bad_decision_timestamp(self):
        bad = VALID_DECISION.replace("2026-05-19T00:00:00Z", "yesterday")
        code, errors, *_ = self._run(decisions=bad + "\n")
        self.assertEqual(code, 1)
        self.assertTrue(any("not ISO-8601" in e for e in errors))

    def test_decision_impact_must_be_list(self):
        bad = VALID_DECISION.replace('"impact":["a"]', '"impact":"a"')
        code, errors, *_ = self._run(decisions=bad + "\n")
        self.assertEqual(code, 1)
        self.assertTrue(any("impact must be a list" in e for e in errors))

    def test_archive_entry_has_different_required_fields(self):
        archive = (
            '{"timestamp":"2026-05-19T00:00:00Z","type":"archive",'
            '"range":"2026-01..2026-04","summary_file":"decisions-archive-2026-05.md","count":200}'
        )
        code, errors, _w, d, _ = self._run(decisions=archive + "\n")
        self.assertEqual(code, 0, errors)
        self.assertEqual(d, 1)

    def test_drift_bad_severity(self):
        bad = VALID_DRIFT.replace('"severity":"low"', '"severity":"catastrophic"')
        code, errors, *_ = self._run(drift=bad + "\n")
        self.assertEqual(code, 1)
        self.assertTrue(any("severity 'catastrophic'" in e for e in errors))

    def test_drift_wrong_type(self):
        bad = VALID_DRIFT.replace('"type":"drift"', '"type":"decision"')
        code, errors, *_ = self._run(drift=bad + "\n")
        self.assertEqual(code, 1)
        self.assertTrue(any("type must be 'drift'" in e for e in errors))

    def test_blank_lines_are_ignored(self):
        code, errors, _w, d, _ = self._run(decisions=f"\n{VALID_DECISION}\n\n")
        self.assertEqual(code, 0, errors)
        self.assertEqual(d, 1)

    def test_freshness_off_by_default(self):
        # Stale "Last updated" should not produce a warning when check_freshness_days is None.
        stale = "# progress\nLast updated: 2020-01-01\n"
        _, _, warnings, *_ = self._run(progress=stale)
        self.assertEqual(warnings, [])

    def test_freshness_warns_when_stale(self):
        stale_arch = "# arch\nLast updated: 2026-01-01\n"
        stale_prog = "# progress\nLast updated: 2026-01-01\n"
        import datetime as _dt
        code, errors, warnings, *_ = self._run(
            arch=stale_arch,
            progress=stale_prog,
            check_freshness_days=30,
            today=_dt.date(2026, 5, 19),
        )
        self.assertEqual(code, 0, errors)
        self.assertEqual(len(warnings), 2)
        self.assertTrue(all("Last updated" in w for w in warnings))

    def test_freshness_ok_when_recent(self):
        import datetime as _dt
        recent_arch = "# arch\nLast updated: 2026-05-10\n"
        recent_prog = "# progress\nLast updated: 2026-05-10\n"
        _, _, warnings, *_ = self._run(
            arch=recent_arch,
            progress=recent_prog,
            check_freshness_days=30,
            today=_dt.date(2026, 5, 19),
        )
        self.assertEqual(warnings, [])

    def test_freshness_missing_last_updated_warns(self):
        _, _, warnings, *_ = self._run(
            progress="# progress\n(no date line)\n",
            check_freshness_days=30,
        )
        self.assertTrue(any("no 'Last updated" in w for w in warnings))

    def test_cli_help(self):
        with self.assertRaises(SystemExit) as cm:
            validate.main(["--help"])
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
