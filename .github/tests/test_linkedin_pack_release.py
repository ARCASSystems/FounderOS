from __future__ import annotations

import csv
import datetime
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO / "skills" / "linkedin-power-audit"
SCAN_DIR = REPO / "skills" / "linkedin-network-scan"
RUNNER = REPO / "skills" / "linkedin-start" / "run.py"
SENTINEL = "MESSAGE-CONTENT-MUST-NOT-SURVIVE"
AS_OF = "2026-06-07"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


audit_mod = load_module("linkedin_power_audit_release", AUDIT_DIR / "power_audit.py")
scan_mod = load_module("linkedin_network_scan_release", SCAN_DIR / "scan.py")


PROFILE = (
    "First Name,Last Name,Headline,Summary,Industry,Geo Location\r\n"
    "Synthetic,Person,Founder building operations systems,Practical systems for operators.,Software,Test City\r\n"
)

CONNECTIONS = (
    "\ufeffNotes:,This export belongs to the account holder\r\n"
    '"A multiline note\r\nwith an escaped ""quote"" before the real header"\r\n'
    "\r\n"
    "First Name,Last Name,URL,Email Address,Company,Position,Connected On\r\n"
    "Avery,Reply,https://example.invalid/avery,,Acme Systems,Founder and CEO,1 Mar 2026\r\n"
    "Bailey,Outbound,https://example.invalid/bailey,,Beta Works,Head of Operations,2 Mar 2026\r\n"
    "Casey,Dormant,https://example.invalid/casey,,Gamma Group,Managing Director,3 Mar 2024\r\n"
)

MESSAGES = (
    "\ufeffCONVERSATION ID,FROM,TO,DATE,SUBJECT,CONTENT,FOLDER,ATTACHMENTS\r\n"
    f'c1,Avery Reply,Synthetic Person,2026-06-01 09:00 UTC,,{SENTINEL},INBOX,\r\n'
    f'c1,Synthetic Person,Avery Reply,2026-06-01 10:00 UTC,,{SENTINEL},SENT,\r\n'
    f'c1,Avery Reply,Synthetic Person,2026-06-02 09:00 UTC,,{SENTINEL},INBOX,\r\n'
    f'c2,Synthetic Person,Bailey Outbound,2026-06-03 09:00 UTC,,{SENTINEL},SENT,\r\n'
    f'c2,Synthetic Person,Bailey Outbound,2026-06-04 09:00 UTC,,{SENTINEL},SENT,\r\n'
    f'c2,Synthetic Person,Bailey Outbound,2026-06-05 09:00 UTC,,{SENTINEL},SENT,\r\n'
    f'c2,Synthetic Person,Bailey Outbound,2026-06-06 09:00 UTC,,{SENTINEL},SENT,\r\n'
    f'c3,Casey Dormant,Synthetic Person,2024-01-01 09:00:00 UTC,,{SENTINEL},INBOX,\r\n'
)

INVITATIONS = (
    "From,To,Sent At,Message,Direction,inviterProfileUrl,inviteeProfileUrl\r\n"
    "Inbound Example,Synthetic Person,2026-06-01 08:00 UTC,,INCOMING,https://example.invalid/inbound,\r\n"
)

SHARES = (
    "Date,ShareCommentary,ShareLink,SharedUrl,MediaUrl,Visibility\r\n"
    '2026-05-01 09:00 UTC,"A systems lesson with an escaped ""quote""\r\nand a second line.",https://example.invalid/share,,,\r\n'
)

COMMENTS = "Date,Link,Message\r\n2026-05-02 09:00 UTC,https://example.invalid/comment,Useful point.\r\n"
REACTIONS = "Date,Type,Link\r\n2026-05-03 09:00 UTC,LIKE,https://example.invalid/reaction\r\n"
POSITIONS = "Company Name,Title,Description,Location,Started On,Finished On\r\nAcme Systems,Founder,,Test City,Jan 2024,\r\n"
EDUCATION = "School Name,Start Date,End Date,Notes,Degree Name,Activities\r\nTest University,2010,2014,,BSc,\r\n"
SKILLS = "Name\r\nOperations\r\nStrategy\r\n"


def export_files(include_all_activity: bool = True) -> dict[str, str]:
    files = {
        "Profile.csv": PROFILE,
        "Connections.csv": CONNECTIONS,
        "Positions.csv": POSITIONS,
        "Education.csv": EDUCATION,
        "Skills.csv": SKILLS,
        "messages_123456.csv": MESSAGES,
    }
    if include_all_activity:
        files.update(
            {
                "Invitations.csv": INVITATIONS,
                "Shares_123456.csv": SHARES,
                "Comments_123456.csv": COMMENTS,
                "Reactions_123456.csv": REACTIONS,
            }
        )
    return files


def write_export(folder: Path, files: dict[str, str] | None = None) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in (files or export_files()).items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="")


def strict_validate(node, schema, path="$", root_schema=None):
    root_schema = root_schema or schema
    if "$ref" in schema:
        target = root_schema
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return strict_validate(node, target, path, root_schema)
    if "anyOf" in schema:
        if any(not strict_validate(node, option, path, root_schema) for option in schema["anyOf"]):
            return []
        return [f"{path}: did not match any allowed schema"]
    errors = []
    expected = schema.get("type")
    if expected is not None:
        allowed = expected if isinstance(expected, list) else [expected]

        def matches(kind):
            return {
                "object": isinstance(node, dict),
                "array": isinstance(node, list),
                "string": isinstance(node, str),
                "integer": isinstance(node, int) and not isinstance(node, bool),
                "number": isinstance(node, (int, float)) and not isinstance(node, bool),
                "boolean": isinstance(node, bool),
                "null": node is None,
            }.get(kind, True)

        if not any(matches(kind) for kind in allowed):
            return [f"{path}: expected {expected}"]
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: value {node!r} is outside the enum")
    if isinstance(node, dict):
        for key in schema.get("required", []):
            if key not in node:
                errors.append(f"{path}: missing {key}")
        properties = schema.get("properties", {})
        for key, value in node.items():
            if key in properties:
                errors.extend(strict_validate(value, properties[key], f"{path}.{key}", root_schema))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: undocumented field {key}")
            elif isinstance(schema.get("additionalProperties"), dict):
                errors.extend(
                    strict_validate(
                        value,
                        schema["additionalProperties"],
                        f"{path}.{key}",
                        root_schema,
                    )
                )
    if isinstance(node, list) and "items" in schema:
        for index, value in enumerate(node):
            errors.extend(strict_validate(value, schema["items"], f"{path}[{index}]", root_schema))
    return errors


class MessagePrivacyTests(unittest.TestCase):
    def test_audit_message_reader_projects_metadata_only(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "messages.csv"
            path.write_text(MESSAGES, encoding="utf-8", newline="")
            result = audit_mod.read_message_csv(path)
        self.assertNotIn(SENTINEL, repr(result))
        self.assertEqual(
            set(result["rows"][0]),
            {"CONVERSATION ID", "FROM", "TO", "DATE", "FOLDER"},
        )

    def test_scan_message_reader_projects_metadata_only(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            (folder / "messages_123456.csv").write_text(MESSAGES, encoding="utf-8", newline="")
            src = scan_mod.ExportSource(str(folder))
            rows = scan_mod.read_message_rows(src)
        self.assertNotIn(SENTINEL, repr(rows))
        self.assertEqual(set(rows[0]), {"CONVERSATION ID", "FROM", "TO", "DATE", "FOLDER"})

    def test_outbound_only_is_never_relationship_warmth(self):
        rows = [
            {
                "CONVERSATION ID": "c1",
                "FROM": "Synthetic Person",
                "TO": "Bailey Outbound",
                "DATE": f"2026-06-0{day} 09:00 UTC",
                "FOLDER": "SENT",
            }
            for day in range(3, 7)
        ]
        messages = audit_mod.process_messages(
            rows,
            "Synthetic Person",
            as_of=datetime.date.fromisoformat(AS_OF),
        )
        counterparty = messages["counterparties"][0]
        self.assertEqual(counterparty["warmth"], "outbound_only")
        self.assertNotIn(counterparty["warmth"], {"hot", "warm", "dormant"})


class CsvAndExportTests(unittest.TestCase):
    def test_header_signatures_handle_realistic_variants(self):
        variants = [
            CONNECTIONS,
            "Notes:\r\nFirst Name,Last Name,Company,Position,Connected On\r\nA,One,Co,Founder,1 Jan 2026\r\n",
            "Notes:,Short note\r\nFirst Name,Last Name,Company,Position,Connected On\r\nA,One,Co,Founder,1 Jan 2026\r\n",
            (
                'Notes:,"one,\r\nmultiline note"\r\n'
                "First Name,Last Name,Company,Position,Connected On\r\n"
                'A,One,"Co ""Quoted""",Founder,1 Jan 2026\r\n'
            ),
        ]
        with tempfile.TemporaryDirectory() as td:
            for index, content in enumerate(variants):
                path = Path(td) / f"connections-{index}.csv"
                path.write_text(content, encoding="utf-8", newline="")
                parsed = audit_mod.read_csv(
                    path,
                    required_headers={"First Name", "Last Name", "Connected On"},
                )
                self.assertEqual(parsed["headers"][0], "First Name")
                self.assertEqual(len(parsed["rows"]), 1 if index else 3)

    def test_minute_only_utc_timestamp_parses(self):
        parsed = audit_mod.parse_date("2026-03-01 09:00 UTC")
        self.assertEqual(parsed.isoformat(), "2026-03-01T09:00:00+00:00")

    def test_complete_named_folder_with_one_activity_file_is_partial(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td) / "Complete_LinkedInDataExport_2026-06-07"
            files = export_files(include_all_activity=False)
            write_export(folder, files)
            audit = audit_mod.extract(folder, as_of=datetime.date.fromisoformat(AS_OF))
        self.assertEqual(audit["_meta"]["export_type"], "partial")

    def test_member_id_candidates_are_sorted_and_warned(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            files = export_files()
            files["messages_999999.csv"] = MESSAGES.replace("Bailey Outbound", "Zed Alternate")
            write_export(folder, files)
            audit = audit_mod.extract(folder, as_of=datetime.date.fromisoformat(AS_OF))
        self.assertTrue(any("multiple CSV candidates" in w for w in audit["_meta"]["warnings"]))
        names = {c["name"] for c in audit["messages"]["counterparties"]}
        self.assertNotIn("Zed Alternate", names)


class DeterminismAndContractTests(unittest.TestCase):
    def run_cli(self, script: Path, export: Path, out: Path, extra=None):
        cmd = [sys.executable, str(script), str(export), str(out), "--as-of", AS_OF]
        if extra:
            cmd.extend(extra)
        return subprocess.run(cmd, capture_output=True, text=True, check=False)

    def test_fixed_date_runs_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            export = root / "export"
            write_export(export)
            for script, filename in [
                (AUDIT_DIR / "power_audit.py", "audit.json"),
                (SCAN_DIR / "scan.py", "network-scan.json"),
            ]:
                out_a = root / f"{script.stem}-a"
                out_b = root / f"{script.stem}-b"
                first = self.run_cli(script, export, out_a)
                second = self.run_cli(script, export, out_b)
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual((out_a / filename).read_bytes(), (out_b / filename).read_bytes())

    def test_audit_schema_covers_exact_emitted_contract_with_optional_gap(self):
        with tempfile.TemporaryDirectory() as td:
            export = Path(td) / "export"
            write_export(export)
            audit = audit_mod.extract(export, as_of=datetime.date.fromisoformat(AS_OF))
            audit_mod.classify(audit)
            audit["network"]["gap"] = audit_mod.network_gap(
                audit, ["founder_owner_entrepreneur"]
            )
        schema = json.loads((AUDIT_DIR / "audit.schema.json").read_text(encoding="utf-8"))
        errors = strict_validate(audit, schema)
        self.assertEqual(errors, [], "\n".join(errors))
        self.assertNotIn("_raw", audit)

        broken = dict(audit)
        broken["undocumented_stable_field"] = True
        self.assertTrue(strict_validate(broken, schema))

    def test_brand_direction_contract_is_fixed_and_consumed(self):
        schema = json.loads(
            (REPO / "skills/linkedin-brand-direction/brand-direction.schema.json").read_text(
                encoding="utf-8"
            )
        )
        required = {
            "goal",
            "topic_lane",
            "positioning_angle",
            "format_mix",
            "cadence",
            "first_three_posts",
            "evidence",
        }
        self.assertEqual(set(schema["required"]), required)
        post_skill = (REPO / "skills/linkedin-post/SKILL.md").read_text(encoding="utf-8")
        for field in sorted(required):
            self.assertRegex(post_skill, rf"`{re.escape(field)}`")
        self.assertIn("linkedin-pack-state.json", post_skill)


class PrivacyAndRunnerTests(unittest.TestCase):
    def test_demo_scrubs_other_company_mentions_and_brand_label(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "demo.html"
            lead = {
                "first": "Synthetic",
                "last": "Person",
                "name": "Synthetic Person",
                "position": "Founder and partner to Secret Holdings",
                "company": "Current Company",
                "url": "https://example.invalid/profile",
                "email": "",
                "tier": "top",
                "scope": "unknown",
                "warm_class": "light",
            }
            scan_mod.render_html_v3(
                path,
                [lead],
                {"total": 1},
                "Private Brand",
                anonymise=True,
                as_of=datetime.date.fromisoformat(AS_OF),
                known_companies=["Current Company", "Secret Holdings"],
            )
            html = path.read_text(encoding="utf-8")
        self.assertNotIn("Secret Holdings", html)
        self.assertNotIn("Current Company", html)
        self.assertNotIn("Private Brand", html)

    def test_stdout_and_demo_source_do_not_expose_person_name_or_url_keys(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            export = root / "export"
            write_export(export)
            for script in (AUDIT_DIR / "power_audit.py", SCAN_DIR / "scan.py"):
                out = root / script.stem
                result = subprocess.run(
                    [sys.executable, str(script), str(export), str(out), "--as-of", AS_OF],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("Synthetic Person", result.stdout)

            html = (root / "scan" / "network-scan.html").read_text(encoding="utf-8")
            data = re.search(
                r'<script id="data" type="application/json">(.*?)</script>',
                html,
                re.S,
            ).group(1)
            records = json.loads(data)
            self.assertNotIn(SENTINEL, html)
            self.assertTrue(records)
            for record in records:
                self.assertNotIn("name", record)
                self.assertNotIn("url", record)

    def test_one_input_runner_writes_action_ready_bundle_and_state_pointer(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "double-wrapped.zip"
            inner = root / "inner.zip"
            export_dir = root / "payload" / "Complete_LinkedInDataExport_2026-06-07"
            write_export(export_dir)
            with zipfile.ZipFile(inner, "w") as zf:
                for path in export_dir.rglob("*"):
                    if path.is_file():
                        zf.write(path, Path("wrapper") / export_dir.name / path.name)
            with zipfile.ZipFile(source, "w") as zf:
                zf.write(inner, "download/archive.zip")

            output_root = root / "outputs"
            state_file = root / "state" / "linkedin-pack-state.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    str(source),
                    "--outcome",
                    "leads",
                    "--as-of",
                    AS_OF,
                    "--output-root",
                    str(output_root),
                    "--state-file",
                    str(state_file),
                    "--no-open",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = output_root / AS_OF
            required = {
                "lead-worklist.md",
                "revival-worklist.md",
                "network-building-worklist.md",
                "brand-direction.json",
                "first-three-posts.md",
                "network-scan.html",
                "network-scan-full.html",
                "network-scan.json",
                "audit.json",
                "draft-icp.json",
            }
            self.assertTrue(required.issubset({p.name for p in output.iterdir()}))
            self.assertIn("Draft opener", (output / "lead-worklist.md").read_text(encoding="utf-8"))
            self.assertIn("Complete draft", (output / "first-three-posts.md").read_text(encoding="utf-8"))
            state = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertEqual(Path(state["latest_output"]), output)
            self.assertEqual(Path(state["brand_direction"]), output / "brand-direction.json")


if __name__ == "__main__":
    unittest.main()
