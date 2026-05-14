#!/usr/bin/env python3
"""UserPromptSubmit capture hook for Founder OS.

Reads the user's submitted prompt from stdin (Claude Code passes a JSON
envelope with a `prompt` field). Classifies the prompt shape against four
patterns: rant, named-entity mention, status update, preference utterance.
For each detected shape, emits a `[capture-suggestion]` system note on
stdout - Claude Code prepends this to the model's context so the model
sees the suggestion before composing its reply.

For rants specifically, the script also performs an EAGER capture: it
writes the rant text immediately to `brain/rants/<YYYY-MM-DD>.md` so the
text is safe on disk even if the user walks away before answering the
routing question. This is the v1.23 fix that closes the "rant captured
then forgotten" silent loss.

For all other shapes the script is SUGGEST-ONLY. It never writes outside
of `brain/rants/` (so it cannot accidentally corrupt clients.md, log.md,
or MEMORY.md if a false positive fires). The actual writes still go
through Claude + the user's confirmation, per the bootloader routing
table.

Free-tier accessible. No LLM call. Stdlib only.

Hook contract:
    stdin:  {"prompt": "<user message>", ...other fields}
    stdout: optional capture-suggestion block, consumed by Claude
    stderr: optional warning, ignored by Claude Code on exit 0
    exit:   0 always (never block the prompt)

If anything fails (no Founder OS install, bad JSON, no rants dir), the
script exits 0 silently so it cannot break the session.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Detection patterns. Conservative on purpose - false-positives are worse
# than missed captures because they train the user to ignore the suggestion.
# ---------------------------------------------------------------------------

# Rant shape: long unstructured dump with no clear ask. We use char count as
# a cheap proxy for token count. 800 chars ~= 200 tokens. Plus: must NOT end
# in a question mark (a question is a query, not a rant). Plus: at least one
# first-person pronoun (rants are about the speaker).
RANT_MIN_CHARS = 800
FIRST_PERSON = re.compile(r"\b(I|I'm|I've|I'll|me|my|mine)\b")
EMOTIONAL_VERBS = re.compile(
    r"\b(frustrated|annoyed|tired|exhausted|sick of|fed up|"
    r"can'?t stand|hate|love|done with|over it|burnt out|stuck|"
    r"overwhelm|confused|lost|drowning|swamped)\b",
    re.IGNORECASE,
)

# Named-entity mention with a meeting verb. Requires:
# - Capitalized word that is NOT a common title-case noun (months, days,
#   tech brands, etc - see NAMED_ENTITY_STOPLIST below)
# - A meeting/contact verb within PROXIMITY_CHARS of the candidate name
# Two-token discipline: the bare regex match \b([A-Z][a-z]{2,})\b fires on
# every title-case word in the language. Without the stop-list + proximity
# requirement, prompts like "I just called Python from my bash script" or
# "I had a call with Notion's API team" would trigger a suggestion - the
# kind of false positive that trains the user to ignore the hook.
NAMED_ENTITY = re.compile(r"\b([A-Z][a-z]{2,})\b")
MEETING_VERBS = re.compile(
    r"\b(met with|met|called|spoke (to|with)|spoken (to|with)|"
    r"emailed|messaged|texted|DM'?d|whatsapped|"
    r"had a call with|got a reply from|heard back from|"
    r"replied to|jumped on a call with|caught up with|"
    r"introduced to|connected with)\b",
    re.IGNORECASE,
)

# Words to ignore when looking for a person's name. Common title-case nouns
# that frequently appear near meeting verbs in developer-founder speech but
# are not people. Keep tight - over-stopping kills real captures.
NAMED_ENTITY_STOPLIST = frozenset({
    # Days
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    # Months
    "January", "February", "March", "April", "June",
    "July", "August", "September", "October", "November", "December",
    # Temporal pronouns / sentence starters
    "Today", "Tomorrow", "Yesterday", "Tonight", "Morning", "Afternoon",
    "Evening", "Last", "Next", "This", "That",
    # Tech / languages / runtimes
    "Python", "Ruby", "Java", "Javascript", "Typescript", "Bash", "Powershell",
    "Node", "React", "Vue", "Angular", "Django", "Rails", "Express",
    # AI / model brands
    "Claude", "Anthropic", "Openai", "Chatgpt", "Gpt", "Gemini", "Llama",
    "Mistral", "Cohere", "Copilot",
    # Major platforms
    "Google", "Apple", "Microsoft", "Amazon", "Meta", "Facebook", "Twitter",
    "Linkedin", "Youtube", "Tiktok", "Instagram", "Whatsapp", "Telegram",
    "Discord", "Slack", "Zoom", "Teams", "Reddit", "Medium", "Substack",
    # Founder-stack brands
    "Notion", "Linear", "Asana", "Trello", "Airtable", "Coda", "Obsidian",
    "Github", "Gitlab", "Bitbucket", "Figma", "Canva", "Gamma", "Vercel",
    "Supabase", "Firebase", "Stripe", "Hubspot", "Salesforce", "Calendly",
    "Loom", "Granola", "Apollo", "Hunter", "Instantly", "Outreach",
    # Office suite
    "Outlook", "Gmail", "Excel", "Word", "Powerpoint", "Docs", "Sheets",
    "Drive", "Onedrive", "Dropbox",
    # Common verbs that capitalize at sentence start
    "Just", "Finally", "Maybe", "Probably", "Actually", "Honestly", "Basically",
    # Common determiners and quantifiers that show up sentence-initial
    "Some", "Many", "Few", "Several", "Various", "Most", "All", "Both",
    "Either", "Neither", "Each", "Every", "Other", "Another", "Such",
    # Common connectives that show up sentence-initial
    "Also", "Then", "Now", "Here", "There", "Still", "However", "Although",
    "Because", "Since", "While", "When", "Where", "Why", "What", "Who",
    "Whose", "Which", "How", "Therefore", "Otherwise", "Meanwhile",
})

# A capitalized candidate counts as a "real name" if it appears within this
# many characters of a meeting-verb match. Tighter = fewer false positives;
# looser = catches names mentioned earlier or later in the sentence.
NAMED_ENTITY_PROXIMITY_CHARS = 80

# Status update: first-person + completion verb.
STATUS_UPDATE = re.compile(
    r"\b(I|I've|I just|I finally|just|finally)\s+"
    r"(finished|sent|shipped|launched|closed|signed|delivered|completed|"
    r"wrote|published|drafted|deployed|merged|wrapped up|done with)\b",
    re.IGNORECASE,
)

# Preference utterance. The classic durable-preference phrases. Conservative -
# we look for the explicit framings, not anything that COULD be a preference.
PREFERENCE = re.compile(
    r"\b("
    r"from now on|"
    r"going forward|"
    r"I prefer|"
    r"I'd prefer|"
    r"never ask me|"
    r"don'?t ever ask|"
    r"don'?t ask me about|"
    r"always (do|use|write|format|treat|prefix|suffix|capitalize|lowercase)|"
    r"never (do|use|write|format|treat|prefix|suffix)|"
    r"stop (doing|asking|using|saying)|"
    r"can you stop|"
    r"I want you to (always|never)"
    r")\b",
    re.IGNORECASE,
)

# Question marker. If the prompt ends with `?` (or contains a `?` followed by
# only whitespace), it's a question - never a rant, even if long.
TRAILING_QUESTION = re.compile(r"\?\s*$")

# Private-tag filter. Stripped before any write, per rules/operating-rules.md.
PRIVATE_BLOCK = re.compile(r"<private>.*?</private>", re.IGNORECASE | re.DOTALL)


# ---------------------------------------------------------------------------
# Detection.
# ---------------------------------------------------------------------------

def has_named_entity_near_meeting_verb(prompt: str) -> bool:
    """Return True iff the prompt contains at least one capitalized word that
    looks like a person's name, within NAMED_ENTITY_PROXIMITY_CHARS of a
    meeting/contact verb.

    Filters out common title-case nouns via NAMED_ENTITY_STOPLIST (months,
    days, tech brands, sentence-start verbs). This is the two-token
    discipline: a real name has a verb near it; a common title-case noun
    might be anywhere in the prompt and is not necessarily a captureable
    contact event.
    """
    verb_matches = list(MEETING_VERBS.finditer(prompt))
    if not verb_matches:
        return False

    for name_match in NAMED_ENTITY.finditer(prompt):
        candidate = name_match.group(1)
        if candidate in NAMED_ENTITY_STOPLIST:
            continue
        name_pos = name_match.start()
        for verb_match in verb_matches:
            verb_pos = verb_match.start()
            if abs(name_pos - verb_pos) <= NAMED_ENTITY_PROXIMITY_CHARS:
                return True
    return False


def detect_shape(prompt: str) -> str | None:
    """Return one of: rant, named-entity, status-update, preference, or None.

    Priority order matters - a prompt that matches multiple shapes is
    classified by the strongest signal. Preferences are most specific,
    then status updates, then named-entity, then rant (the catch-all for
    long unstructured input).
    """
    if not prompt or not prompt.strip():
        return None

    if PREFERENCE.search(prompt):
        return "preference"

    if STATUS_UPDATE.search(prompt):
        return "status-update"

    if has_named_entity_near_meeting_verb(prompt):
        return "named-entity"

    # Rant heuristic. Long, first-person, not a question. Emotional verbs
    # tighten the signal but are not required - some rants are just long
    # context dumps.
    if (
        len(prompt) >= RANT_MIN_CHARS
        and FIRST_PERSON.search(prompt)
        and not TRAILING_QUESTION.search(prompt)
    ):
        return "rant"

    return None


# ---------------------------------------------------------------------------
# Eager rant capture. The only write path in this script.
# ---------------------------------------------------------------------------

def eager_capture_rant(repo: Path, prompt: str) -> Path | None:
    """Write the rant to brain/rants/<date>.md immediately. Returns the path
    written, or None if anything went wrong (silently)."""
    rants_dir = repo / "brain" / "rants"
    try:
        rants_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None

    # Private-tag filter. Strip <private>...</private> blocks. If the entire
    # input was wrapped, do not write at all.
    cleaned = PRIVATE_BLOCK.sub("", prompt).strip()
    if not cleaned:
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    target = rants_dir / f"{today}.md"

    entry = (
        "---\n"
        f"captured: {timestamp}\n"
        "processed: false\n"
        "mode: unknown\n"
        "source: user-prompt-capture-hook\n"
        "---\n\n"
        f"{cleaned}\n\n"
        "---\n\n"
    )

    try:
        if target.exists():
            # Prepend to existing file, after the header.
            existing = target.read_text(encoding="utf-8")
            header_end = existing.find("\n\n")
            if existing.startswith("# Rants - ") and header_end != -1:
                header = existing[: header_end + 2]
                body = existing[header_end + 2 :]
                target.write_text(header + entry + body, encoding="utf-8")
            else:
                # No header found; prepend a fresh header + entry.
                target.write_text(
                    f"# Rants - {today}\n\n" + entry + existing,
                    encoding="utf-8",
                )
        else:
            target.write_text(
                f"# Rants - {today}\n\n" + entry,
                encoding="utf-8",
            )
    except OSError:
        return None

    return target


# ---------------------------------------------------------------------------
# Note rendering. The strings here are what Claude sees as added context.
# ---------------------------------------------------------------------------

def render_note(shape: str, capture_path: Path | None) -> str:
    """Return the system-note text for the detected shape."""
    if shape == "rant":
        if capture_path:
            rel = capture_path.as_posix()
            return (
                "[capture-suggestion: rant-eager-captured]\n"
                f"The user's prompt looks like a rant. It has been eagerly written to {rel} "
                "so it is safe on disk. Acknowledge in one short line that it was captured, "
                "then offer routing: 'Want to act on it now? Say decision, draft, plan, "
                "or log - or ignore and /dream will pick it up later.' Do not summarise the "
                "rant content. Do not interview the user."
            )
        return (
            "[capture-suggestion: rant]\n"
            "The user's prompt looks like a rant. Propose running /rant to capture it. "
            "Confirm with the user before writing."
        )

    if shape == "named-entity":
        return (
            "[capture-suggestion: named-entity]\n"
            "The user mentioned a named person AND a contact/meeting verb. Before continuing "
            "the response, propose capturing this to context/clients.md (or context/leads.md if "
            "the user has split the pipeline). Format: 'Want me to add <name> to your clients/leads? "
            "Yes/no/skip.' Wait for confirmation, then invoke /capture-meeting <name> or write a "
            "single row directly. Do not write without the user's yes."
        )

    if shape == "status-update":
        return (
            "[capture-suggestion: status-update]\n"
            "The user reported a completed action ('I finished/sent/shipped/closed/etc'). Before "
            "continuing the response, propose logging this to brain/log.md. Format: 'Want me to log "
            "that to brain/log.md? Yes/no/skip.' Wait for confirmation, then invoke brain-log skill. "
            "Do not write without the user's yes."
        )

    if shape == "preference":
        return (
            "[capture-suggestion: preference]\n"
            "The user expressed a durable preference ('from now on' / 'I prefer' / 'never ask me' / "
            "'always X' / 'stop doing Y'). Before continuing the response, propose adding it as a "
            "behavioral guard. Format: 'Want me to save that as a preference? It'll persist across "
            "every session. Yes/no/skip.' Wait for confirmation, then add a one-line guard entry "
            "to ~/.claude/projects/<slug>/memory/MEMORY.md under Behavioral Guards. If the auto-memory "
            "path is unclear, ask the user to confirm the path once. Do not write without the yes."
        )

    return ""


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def find_repo_root() -> Path | None:
    """Resolve the Founder OS repo root from CLAUDE_PROJECT_DIR."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if not project_dir:
        return None
    root = Path(project_dir)
    if not root.is_dir():
        return None
    # Sanity-check: this should look like a Founder OS install (or be in the
    # process of becoming one).
    if not (root / "CLAUDE.md").exists() and not (root / "core" / "identity.md").exists():
        return None
    return root


def read_prompt_from_stdin() -> str | None:
    """Claude Code passes the hook a JSON envelope on stdin. We extract
    the `prompt` field. If anything is malformed, return None."""
    try:
        raw = sys.stdin.read()
    except OSError:
        return None
    if not raw:
        return None
    # The envelope is JSON. Older versions may pass plain text - tolerate both.
    raw = raw.strip()
    if raw.startswith("{"):
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(envelope, dict):
            return None
        prompt = envelope.get("prompt")
        if isinstance(prompt, str):
            return prompt
        return None
    # Fallback: treat raw stdin as the prompt itself.
    return raw


def main() -> int:
    repo = find_repo_root()
    if repo is None:
        return 0

    prompt = read_prompt_from_stdin()
    if not prompt:
        return 0

    # Bypass for prompts that already begin with a slash command - the user
    # is invoking a specific skill, so suggestion would be noise.
    if prompt.lstrip().startswith("/"):
        return 0

    shape = detect_shape(prompt)
    if shape is None:
        return 0

    capture_path: Path | None = None
    if shape == "rant":
        capture_path = eager_capture_rant(repo, prompt)

    note = render_note(shape, capture_path)
    if note:
        print(note)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # Last-resort silent exit. A hook crash must not break the session.
        raise SystemExit(0)
