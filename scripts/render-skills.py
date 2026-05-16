#!/usr/bin/env python3
"""Render skills.html from skills/<name>/SKILL.md frontmatter.

Stdlib only. Deterministic: same inputs produce the same output.

Each SKILL.md begins with YAML frontmatter delimited by --- lines, e.g.

  ---
  name: voice-interview
  description: >
    Set up the writing-voice profile. ...
  ---

Reads name + description from every skills/<name>/SKILL.md, trims the
description to one summary sentence, and emits skills.html with a
matching look and feel to founder-os-playbook.html.
"""

import html as html_mod
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MANIFEST = ROOT / "playbook.manifest.json"
OUTPUT = ROOT / "skills.html"


def parse_frontmatter(text: str) -> dict:
    """Tiny YAML frontmatter parser. Handles scalar values and `>` folded blocks."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    body = parts[1]
    out: dict = {}
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2).rstrip()
        if value in (">", "|", ">-", "|-"):
            collected: list[str] = []
            j = i + 1
            while j < len(lines) and (lines[j].startswith("  ") or not lines[j].strip()):
                collected.append(lines[j][2:] if lines[j].startswith("  ") else "")
                j += 1
            joined = " ".join(s.strip() for s in collected if s.strip())
            out[key] = joined
            i = j
        else:
            out[key] = value.strip().strip('"').strip("'")
            i += 1
    return out


def first_sentence(text: str) -> str:
    """First sentence of a description, capped at ~220 chars for the summary line."""
    text = text.strip()
    m = re.match(r"^(.+?[.!?])(\s|$)", text)
    summary = m.group(1) if m else text
    if len(summary) > 220:
        summary = summary[:217].rstrip() + "..."
    return summary


def github_url_for(skill_slug: str, github_repo: str) -> str:
    return f"{github_repo}/blob/main/skills/{skill_slug}/SKILL.md"


def collect_skills() -> list[dict]:
    skills: list[dict] = []
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        slug = path.parent.name
        if slug.startswith("_") or slug.startswith("."):
            continue
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        name = fm.get("name") or slug
        desc = fm.get("description") or ""
        skills.append({
            "slug": slug,
            "name": name,
            "summary": first_sentence(desc),
            "description": desc,
        })
    return skills


def render_card(skill: dict, github_repo: str) -> str:
    summary = html_mod.escape(skill["summary"]) if skill["summary"] else \
        "<em>No description yet.</em>"
    name = html_mod.escape(skill["name"])
    url = github_url_for(skill["slug"], github_repo)
    return (
        f'  <article class="sk-card" id="sk-{html_mod.escape(skill["slug"])}">\n'
        f'    <h3 class="sk-name"><a href="{url}" target="_blank"><code>{name}</code></a></h3>\n'
        f'    <p class="sk-summary">{summary}</p>\n'
        f'    <p class="sk-meta"><a href="{url}" target="_blank">Read SKILL.md &rarr;</a></p>\n'
        f'  </article>'
    )


def render_toc(skills: list[dict]) -> str:
    items: list[str] = []
    for sk in skills:
        slug = html_mod.escape(sk["slug"])
        name = html_mod.escape(sk["name"])
        items.append(f'  <li><a href="#sk-{slug}"><code>{name}</code></a></li>')
    return "\n".join(items)


HTML_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Founder OS Skills - ARCAS Systems</title>
<style>
:root{
  --navy:#041E37;--purple:#8234EA;--magenta:#F70872;--mint:#35D39A;
  --gray-light:#F8F8FA;--gray-mid:#E8E8EE;--gray-text:#6B7280;
  --body-text:#1A2840;--content-max:760px;--radius:8px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;font-size:16px}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  background:#fff;color:var(--body-text);line-height:1.65;
}
a{color:var(--purple);text-decoration:none}
a:hover{text-decoration:underline}
code{background:var(--gray-light);padding:2px 6px;border-radius:4px;font-size:.92em;color:var(--purple);font-family:ui-monospace,monospace}

.hero{background:var(--navy);color:#fff;padding:64px max(40px,calc(50% - 460px));}
.hero-tag{display:inline-block;background:rgba(130,52,234,.3);color:var(--mint);font-size:11px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;padding:4px 12px;border-radius:20px;margin-bottom:18px}
.hero h1{font-size:2.2rem;font-weight:700;line-height:1.2;letter-spacing:-.02em;margin-bottom:14px}
.hero p{color:rgba(255,255,255,.78);max-width:640px;font-size:1.05rem;margin-bottom:10px}
.hero a.back{color:var(--mint);font-size:13px;margin-top:14px;display:inline-block}

.body{padding:48px max(40px,calc(50% - 460px));}
h2{font-size:1.3rem;font-weight:700;color:var(--purple);margin:36px 0 16px;letter-spacing:-.01em}
h2:first-child{margin-top:0}

.toc{column-count:3;column-gap:24px;margin:8px 0 32px;list-style:none;font-size:13px;line-height:1.9}
.toc li{break-inside:avoid}
.toc code{font-size:12px;padding:1px 5px}

.callout{background:var(--gray-light);border-left:4px solid var(--purple);border-radius:0 var(--radius) var(--radius) 0;padding:18px 22px;margin:24px 0;font-size:14px;color:var(--body-text);max-width:var(--content-max)}
.callout strong{color:var(--purple)}

.sk-grid{display:grid;grid-template-columns:1fr;gap:14px;margin-top:18px;max-width:var(--content-max)}
.sk-card{border:1px solid var(--gray-mid);border-radius:var(--radius);padding:18px 22px;border-left:4px solid var(--purple);background:#fff}
.sk-name{font-size:1rem;font-weight:700;margin-bottom:6px;color:var(--body-text)}
.sk-name a{color:var(--body-text)}
.sk-name a:hover{color:var(--purple)}
.sk-name code{background:none;color:var(--body-text);padding:0;font-size:1rem}
.sk-summary{font-size:14px;color:var(--body-text);line-height:1.6;margin-bottom:8px}
.sk-meta{font-size:12px;color:var(--gray-text);margin:0}
.sk-meta a{color:var(--purple)}

.closing{background:var(--gray-light);padding:36px max(40px,calc(50% - 460px));border-top:1px solid var(--gray-mid);text-align:right}
.closing p{font-size:14px;font-weight:700;color:var(--navy);margin:0}
.closing p.last{color:var(--magenta);margin-top:4px}

@media(max-width:780px){
  .hero{padding:48px 22px}
  .body{padding:36px 22px}
  .closing{padding:32px 22px}
  .toc{column-count:2}
  .hero h1{font-size:1.7rem}
}
@media(max-width:520px){
  .toc{column-count:1}
}
</style>
</head>
<body>

<header class="hero">
  <div class="hero-tag">Founder OS</div>
  <h1>All __SKILL_COUNT__ skills</h1>
  <p>The playbook covers what the OS does and where to start. This page lists every skill the OS ships with - what it does and where to read its source. Browse the list, or jump to any skill from the index.</p>
  <p><a class="back" href="founder-os-playbook.html">&larr; back to the playbook</a></p>
</header>

<main class="body">

  <h2>What you are looking at</h2>
  <p style="max-width:var(--content-max);font-size:15px">Each entry below is a skill that ships with the public Founder OS repo. Click any skill to read its <code>SKILL.md</code> on GitHub - that file holds the exact instructions the AI follows when the skill fires. You can tune any skill by editing its file directly.</p>
  <div class="callout"><strong>How to enhance a skill:</strong> most skills read from one or more files in <code>core/</code>, <code>context/</code>, or <code>brain/</code>. The way to make a skill produce sharper output is to make the files it reads sharper. Voice-coupled skills (email-drafter, linkedin-post, proposal-writer) get sharper when you re-run the voice interview after a real writing sample. Brand-coupled skills (proposal-writer, your-deliverable-template) get sharper after the brand interview. Brain-coupled skills (meeting-prep, brain-pass, strategic-analysis) get sharper as the brain layer fills with real entries.</p></div>

  <h2>Index</h2>
  <ol class="toc">
__TOC__
  </ol>

  <h2>The skills</h2>
  <div class="sk-grid">
__CARDS__
  </div>

</main>

<footer class="closing">
  <p>People don't fail processes.</p>
  <p class="last">Processes fail people.</p>
</footer>

</body>
</html>
"""


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    github_repo = manifest.get("github_url", "https://github.com/ARCASSystems/FounderOS")
    skills = collect_skills()
    if not skills:
        print("ERROR: no SKILL.md files found under skills/*", file=sys.stderr)
        return 1

    toc = render_toc(skills)
    cards = "\n".join(render_card(sk, github_repo) for sk in skills)
    out = (
        HTML_SHELL
        .replace("__SKILL_COUNT__", str(len(skills)))
        .replace("__TOC__", toc)
        .replace("__CARDS__", cards)
    )
    OUTPUT.write_text(out, encoding="utf-8")
    print(f"OK: rendered {len(skills)} skills, wrote skills.html ({len(out)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
