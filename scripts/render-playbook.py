#!/usr/bin/env python3
"""Render founder-os-playbook.html from playbook.manifest.json + playbook.template.html.

Stdlib only. Deterministic: running twice produces byte-identical output.

Volatile values (counts, costs, version) live in the manifest. Stable prose,
structure, SVGs, and CSS live in the template. The renderer substitutes
{{token}} scalars and {{*_html}} block tokens.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "playbook.manifest.json"
TEMPLATE = ROOT / "playbook.template.html"
OUTPUT = ROOT / "founder-os-playbook.html"


def render_stats_strip(items):
    tone_class = {"default": "", "magenta": " mag", "dim": " dim"}
    out = []
    for s in items:
        cls = tone_class.get(s.get("tone", "default"), "")
        out.append(
            '  <div class="stat-item">\n'
            f'    <span class="stat-num{cls}">{s["num"]}</span>\n'
            f'    <span class="stat-label">{s["label"]}</span>\n'
            '  </div>'
        )
    return "\n".join(out)


def render_seven_days(days):
    out = []
    for i, d in enumerate(days):
        out.append(
            f'    <div class="day" onclick="toggleDay({i})">\n'
            f'      <div class="day-num">{d["day"]}</div>\n'
            f'      <div class="day-content">\n'
            f'        <div class="day-title">{d["title"]}</div>\n'
            f'        <div class="day-time">{d["time_min"]} minutes</div>\n'
            f'        <div class="day-detail">{d["detail"]}</div>\n'
            f'      </div>\n'
            f'    </div>'
        )
    return "\n".join(out)


def render_tune_first(rows):
    if not rows:
        return ""
    cards = []
    for r in rows:
        chain = " &rarr; ".join(
            f'<code class="tf-code">{s}</code>' for s in r["tune_first"]
        )
        cards.append(
            '  <div class="tf-card">\n'
            f'    <div class="tf-focus">{r["focus"]}</div>\n'
            f'    <div class="tf-chain">{chain}</div>\n'
            f'    <div class="tf-why">{r["why_different"]}</div>\n'
            '  </div>'
        )
    return "\n".join(cards)


def render_cloud_claude(cfg):
    if not cfg:
        return ""
    return cfg.get("html", "")


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    template = TEMPLATE.read_text(encoding="utf-8")

    replacements = {
        "{{version}}": str(manifest.get("version", "")),
        "{{skill_count}}": str(manifest["skill_count"]),
        "{{command_count}}": str(manifest["command_count"]),
        "{{operating_files}}": str(manifest["operating_files"]),
        "{{setup_minutes}}": str(manifest["setup_minutes"]),
        "{{subscription_cost_band}}": manifest["subscription_cost_band"],
        "{{free_tier_warning}}": manifest["free_tier_warning"],
        "{{github_url}}": manifest["github_url"],
        "{{stats_strip_html}}": render_stats_strip(manifest["stats_strip"]),
        "{{seven_days_html}}": render_seven_days(manifest["seven_days"]),
        "{{tune_first_html}}": render_tune_first(manifest.get("tune_skills_first_table")),
        "{{cloud_claude_html}}": render_cloud_claude(manifest.get("cloud_claude")),
    }

    out = template
    scalar_hits = 0
    loop_hits = 0
    for token, value in replacements.items():
        n = out.count(token)
        if n == 0:
            continue
        out = out.replace(token, value)
        if token.endswith("_html}}"):
            loop_hits += n
        else:
            scalar_hits += n

    leftover = [t for t in replacements if t in out]
    if leftover:
        print(f"ERROR: tokens remain unrendered: {leftover}", file=sys.stderr)
        sys.exit(1)

    OUTPUT.write_text(out, encoding="utf-8")
    print(
        f"OK: rendered {scalar_hits} scalar tokens, {loop_hits} block tokens, "
        f"wrote founder-os-playbook.html ({len(out)} chars)"
    )


if __name__ == "__main__":
    main()
