#!/usr/bin/env python3
"""UserPromptSubmit capture hook for Founder OS.

Reads the user's submitted prompt from stdin (Claude Code passes a JSON
envelope with a `prompt` field). Classifies the prompt shape against five
patterns: rant, named-entity mention, status update, preference utterance,
and correction of the OS's own manner. For each detected shape, emits a
`[capture-suggestion]` system note on stdout - Claude Code prepends this to
the model's context so the model sees the suggestion before composing its
reply.

The correction shape (v1.49) is the one that compounds. "Too long", "you
asked me that already", "just pick one" are not complaints, they are the
user telling you how they want to be worked with - at the only moment they
ever say it, which is when they are annoyed and not trying to configure
anything. Routed like a name correction: applied now, then offered as a row
in core/working-preferences.md, which is read before output rather than
recalled after a complaint. The test is that the same correction never has
to be given twice.

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

Independently of the four capture shapes, the script also emits a one-line
`[bias-check]` nudge when the prompt asks for a decision or opinion, pointing
at the output bias self-check in rules/biases.md before the model answers.

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

# Named-entity mention: three-signal AND-gate (v1.23.1).
#
# Signal A: meeting verb with mandatory preposition. The preposition (with /
# to / from) is required - bare verbs like "called", "met", "emailed" fire
# too widely without an anchor.
#
# Signal B: capitalized-name-immediately-after. Within 0-30 characters of
# the Signal A match end, NAMED_ENTITY must match a non-stop-listed token.
# Tight coupling (30 chars vs prior 80) reduces compound-noun and far-field
# false positives.
#
# Signal C: first-person agent. The same sentence must contain a first-person
# token from FIRST_PERSON_TOKEN. Eliminates sentence-initial bare-verb false
# positives like "Spoke to Legal" which cannot have a first-person anchor.
#
# Trigger condition: all three signals present in the same sentence
# (split on [.!?\n]+). Any absent signal → return False.
#
# Regex shape: cap letter + 2+ letters, with a lookahead that requires at
# least one lowercase letter somewhere in the token. The lookahead lets
# CamelCase brands ("GitHub", "OpenAI", "YouTube") capture as a single
# token while structurally excluding all-caps acronyms ("API", "USA", "UAE",
# "JSON") - those are almost never person names.
NAMED_ENTITY = re.compile(r"\b([A-Z](?=[a-zA-Z]*[a-z])[a-zA-Z]{2,})\b")

MEETING_VERBS = re.compile(
    r"\b("
    r"had a (?:call|chat|meeting|coffee|drink|conversation) with|"
    r"met with|"
    r"spoke (?:to|with)|"
    r"spoken (?:to|with)|"
    r"caught up with|"
    r"jumped on a call with|"
    r"got a reply from|"
    r"heard back from|"
    r"replied to|"
    r"introduced to|"
    r"connected with"
    r")\b",
    re.IGNORECASE,
)

# First-person tokens for Signal C.
FIRST_PERSON_TOKEN = re.compile(r"\b(I|I've|I'd|I'm|we|We|me|my|My)\b")

# Words to ignore when looking for a person's name. Common title-case nouns
# that frequently appear near meeting verbs in developer-founder speech but
# are not people. Keep tight - over-stopping kills real captures.
#
# v1.23.1: removed 7 categories that Signal A's mandatory-preposition
# requirement already rejects structurally (Days, Months, Temporal pronouns,
# Sentence-initial verbs, Determiners/quantifiers, Connectives,
# Religious/cultural occasions). Added 3 brand entries and 12 institutional
# head nouns for compound-name detection via the next-word peek in Signal B.
NAMED_ENTITY_STOPLIST = frozenset({
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
    "Cloudflare",
    # Founder-stack brands
    "Notion", "Linear", "Asana", "Trello", "Airtable", "Coda", "Obsidian",
    "Github", "Gitlab", "Bitbucket", "Figma", "Canva", "Gamma", "Vercel",
    "Supabase", "Firebase", "Stripe", "Hubspot", "Salesforce", "Calendly",
    "Loom", "Granola", "Apollo", "Hunter", "Instantly", "Outreach",
    "Wordpress", "Paypal",
    # Office suite
    "Outlook", "Gmail", "Excel", "Word", "Powerpoint", "Docs", "Sheets",
    "Drive", "Onedrive", "Dropbox", "Workspace",
    # Kinship terms - capitalized when used as names ("called Mom")
    "Mom", "Dad", "Mum", "Mother", "Father", "Brother", "Sister",
    "Wife", "Husband", "Son", "Daughter", "Uncle", "Aunt", "Cousin",
    "Grandma", "Grandpa", "Grandmother", "Grandfather",
    # Internal departments / functions - common business prose
    "Marketing", "Sales", "Engineering", "Finance", "Operations",
    "Legal", "Product", "Design", "Support", "Customer",
    # Corporate suffixes that match the regex
    "Inc",
    # Institutional head nouns - second-token compound detection
    # (e.g. "Dubai Chamber": "Chamber" is stop-listed so the next-word peek
    # rejects "Dubai" as a person-name candidate)
    "Chamber", "Office", "Authority", "Council", "Bank", "University",
    "Hospital", "Group", "Holdings", "Ltd", "Llc", "Co",
})

# Pre-lowercased view of the stop-list for case-insensitive comparison.
NAMED_ENTITY_STOPLIST_LOWER = frozenset(w.lower() for w in NAMED_ENTITY_STOPLIST)

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

# Correction of the OS's own manner (v1.49). Distinct from a preference: a
# preference is stated deliberately ("from now on"), a correction is fired off
# mid-work when the last output was wrong in shape rather than in fact. It is
# the most honest source of a working preference there is, because the user was
# not trying to configure anything.
#
# Split in two on purpose, because the phrases differ in how much they can mean
# something else. CORRECTION_STRONG names the assistant ("you keep", "I already
# told you") or is an explicit instruction about form. CORRECTION_SHORT covers
# phrases that ARE corrections when fired off as a short reply and are ordinary
# prose inside a long message ("the meeting was too long"). BOTH count only
# under the length gate below, and both are rejected inside quotations and
# after reported-speech lead-ins - see is_correction.
# Conservative on purpose: a false positive here trains the user to ignore the
# suggestion, which costs more than a missed capture.
CORRECTION_STRONG = re.compile(
    r"(?:"
    r"you (?:already )?asked me (?:that|this)|"
    r"I (?:already )?told you|"
    r"we (?:already )?(?:went over|covered) (?:this|that)|"
    r"you keep [a-z]+ing|"
    r"asked you not to|"
    r"get to the point|"
    r"skip the (?:preamble|summary|intro|recap|caveats)|"
    r"don'?t give me (?:a menu|options|a list)|"
    r"stop (?:repeating|explaining|narrating|hedging)|"
    r"you are (?:repeating|over-?explaining)|"
    r"you're (?:repeating|over-?explaining)"
    r")",
    re.IGNORECASE,
)

CORRECTION_SHORT = re.compile(
    r"(?:"
    r"too (?:long|much|wordy|verbose|detailed)|"
    r"shorter|"
    r"just (?:pick|choose|decide|answer)|"
    r"not what I asked|"
    r"less detail|"
    r"fewer (?:words|options)"
    r")",
    re.IGNORECASE,
)

# A reply this short that says "too long" is about the last output. The same
# words inside a paragraph are usually about something else entirely. Since the
# review of 2026-08-07 this gate covers EVERY correction shape, strong ones
# included: a 400-character brief that happens to contain "I already told you"
# is narrative, not a correction fired at the OS.
CORRECTION_MAX_CHARS = 200

# Two more guards against capturing speech ABOUT a correction as a correction
# OF the OS. A match inside double or curly quotes is someone being quoted
# ('The client wrote, "you already asked me that"'), and a match right after a
# reported-speech lead-in is a story about a human ("I told Alex to get to the
# point"). Single straight quotes are deliberately not treated as spans -
# contractions ("don't") would make them fire on ordinary prose.
_QUOTE_PAIRS = (('"', '"'), ("“", "”"))
_REPORTED_LEADIN = re.compile(
    r"(?:\b(?:wrote|writes|said|says|saying|replied|responded|commented|messaged"
    r"|emailed)\b[\s:,]*[\"“']?\s*$)"
    r"|(?:\b(?:told|asked|reminded|begged)\s+(?!you\b)\w+\s+(?:to\s+|that\s+)?$)",
    re.IGNORECASE,
)


def _in_quotes(text: str, start: int, end: int) -> bool:
    for opener, closer in _QUOTE_PAIRS:
        pos = 0
        while True:
            a = text.find(opener, pos)
            if a == -1:
                break
            b = text.find(closer, a + 1)
            if b == -1:
                break
            if a < start and end <= b + 1:
                return True
            pos = b + 1
    return False

# Question marker. If the prompt ends with `?` (or contains a `?` followed by
# only whitespace), it's a question - never a rant, even if long.
TRAILING_QUESTION = re.compile(r"\?\s*$")

# Private-tag filter. Stripped before any write, per rules/operating-rules.md.
PRIVATE_BLOCK = re.compile(r"<private>.*?</private>", re.IGNORECASE | re.DOTALL)


# ---------------------------------------------------------------------------
# Decision / opinion nudge. Independent of the capture classifier above: when
# the prompt asks for a decision, recommendation, or opinion, emit a one-line
# reminder to run the output bias self-check (rules/biases.md) before the model
# answers. An opinion is not a tool call, so no PreToolUse hook can intercept
# it; this raises the reminder at the moment a decision-prompt arrives. Known
# limit: it pattern-matches phrasing, not intent, so it WILL miss some
# decision-asks. Tight on purpose - firing on every prompt is the "slow and
# preachy" failure the self-check itself warns against.
# ---------------------------------------------------------------------------

DECISION_PATTERNS = [
    r"\bshould (i|we|it|they|you)\b",
    r"\bwhat should\b",
    r"\bwhich (one|option|way|approach|is better|do you|would)\b",
    r"\bis it worth\b",
    r"\bworth (it|doing|building|the)\b",
    r"\b(what|whats|what's) your (take|opinion|read|call|view)\b",
    r"\bdo you think\b",
    r"\bwhat would you do\b",
    r"\brecommend(ation)?\b",
    r"\bbetter to\b",
    r"\bare you sure\b",
    r"\b(help me )?(decide|choose)\b",
    r"\bchoose between\b",
    r"\bpros and cons\b",
    r"\btrade ?-?offs?\b",
    r"\bgo or no.?go\b",
    r"\bversus\b",
    r"\bvs\.?\b",
]
DECISION_RX = re.compile("|".join(DECISION_PATTERNS), re.IGNORECASE)

BIAS_NUDGE = (
    "[bias-check] Decision/opinion ask - before you answer, run rules/biases.md: "
    "counter-case, confidence level, what evidence is absent, and the do-nothing "
    "option. Flag if you are agreeing mainly because it is the user's existing plan."
)


# ---------------------------------------------------------------------------
# Detection.
# ---------------------------------------------------------------------------

def has_named_entity_near_meeting_verb(prompt: str) -> bool:
    """Return True iff the prompt contains a sentence with all three signals:

    A) A meeting verb with a mandatory preposition (with / to / from).
    B) A non-stop-listed capitalized name within 30 chars of the verb end.
       Additional next-word peek: if the word immediately following the
       candidate is an institutional head noun (Chamber, Bank, Group, etc.)
       the candidate is treated as part of a compound institutional name and
       rejected.
    C) A first-person token (I / I've / I'd / I'm / we / me / my) in the
       same sentence.

    Sentences are split on [.!?\\n]+. All three signals must be present in
    the same sentence; any absent signal causes the sentence to be skipped.
    """
    for sentence in re.split(r"[.!?\n]+", prompt):
        sentence = sentence.strip()
        if not sentence:
            continue

        # Signal A: meeting verb with mandatory preposition.
        verb_matches = list(MEETING_VERBS.finditer(sentence))
        if not verb_matches:
            continue

        # Signal C: first-person token in the same sentence.
        if not FIRST_PERSON_TOKEN.search(sentence):
            continue

        # Signal B: capitalized name within 30 chars of any verb match end.
        for verb_match in verb_matches:
            verb_end = verb_match.end()
            window = sentence[verb_end : verb_end + 30]

            for name_match in NAMED_ENTITY.finditer(window):
                candidate = name_match.group(1)

                # Stop-list filter (case-insensitive).
                if candidate.lower() in NAMED_ENTITY_STOPLIST_LOWER:
                    continue

                abs_start = verb_end + name_match.start()

                # Sentence-start rejection: skip if immediately preceded by
                # sentence-ending punctuation (safety guard for edge cases).
                if abs_start > 0 and sentence[abs_start - 1] in ".!?\n":
                    continue

                # Institutional compound detection: peek at the next word.
                # If it is in the stop-list (Chamber, Bank, Group, etc.) this
                # candidate is the first token of a compound entity name, not
                # a person. Reject.
                rest = window[name_match.end():]
                next_word_m = re.match(r"[ \t]+([A-Za-z]+)", rest)
                if (
                    next_word_m
                    and next_word_m.group(1).lower() in NAMED_ENTITY_STOPLIST_LOWER
                ):
                    continue

                return True
    return False


def is_correction(prompt: str) -> bool:
    """Return True if the user is correcting HOW the OS works rather than what
    it knows. Conservative on purpose, three gates: the whole message must be
    short enough to be a reply to the last output, the matched phrase must not
    sit inside a quotation, and it must not follow a reported-speech lead-in.
    A missed capture costs one more correction; a false capture teaches the
    user to distrust every suggestion."""
    if not prompt:
        return False
    s = prompt.strip()
    if len(s) > CORRECTION_MAX_CHARS:
        return False
    m = CORRECTION_STRONG.search(s) or CORRECTION_SHORT.search(s)
    if not m:
        return False
    if _in_quotes(s, m.start(), m.end()):
        return False
    lead = s[max(0, m.start() - 60):m.start()]
    if _REPORTED_LEADIN.search(lead):
        return False
    return True


def detect_shape(prompt: str) -> str | None:
    """Return one of: correction, rant, named-entity, status-update,
    preference, or None.

    Priority order matters - a prompt that matches multiple shapes is
    classified by the strongest signal. A correction is the most specific
    (it is about this reply, right now), then preferences, then status
    updates, then named-entity, then rant (the catch-all for long
    unstructured input).
    """
    if not prompt or not prompt.strip():
        return None

    if is_correction(prompt):
        return "correction"

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


def is_decision_prompt(prompt: str) -> bool:
    """Return True if the prompt is asking for a decision, recommendation, or
    opinion. Drives the output bias self-check nudge. Independent of
    detect_shape - a plain decision question matches no capture shape but still
    warrants the nudge."""
    return bool(prompt and DECISION_RX.search(prompt))


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

    now = datetime.now(timezone.utc).astimezone()
    today = now.strftime("%Y-%m-%d")
    timestamp = now.isoformat(timespec="seconds")
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

def render_note(shape: str, capture_path: Path | None, repo: Path | None = None) -> str:
    """Return the system-note text for the detected shape.

    `repo` is used to compute a repo-relative display path for the rant
    capture. Without it, the note would leak the operator's absolute local
    filesystem path into model context on every rant.
    """
    if shape == "rant":
        if capture_path:
            if repo is not None:
                try:
                    rel = capture_path.relative_to(repo).as_posix()
                except ValueError:
                    rel = capture_path.name
            else:
                rel = capture_path.name
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
            "'always X' / 'stop doing Y'). Before continuing the response, propose saving it. "
            "Format: 'Want me to save that as a working preference? I read it before every answer. "
            "Yes/no/skip.' Wait for confirmation, then append ONE row to the Active table in "
            "core/working-preferences.md: the preference in their words, where it applies, today's "
            "date, and their exact sentence as the evidence. No row without evidence. Do not write "
            "without the yes, and do not widen the scope beyond what they said."
        )

    if shape == "correction":
        return (
            "[capture-suggestion: correction]\n"
            "The user corrected HOW you work, not what you know ('too long' / 'you asked me that "
            "already' / 'just pick one'). Two things, in this order. FIRST: apply the correction in "
            "THIS reply, immediately - a correction that gets filed instead of obeyed is worse than "
            "one that gets ignored. SECOND, in one line at the end: 'Want that saved so I stop doing "
            "it? Yes/no/skip.' On yes, append ONE row to the Active table in "
            "core/working-preferences.md with their words as the evidence and today's date; if the "
            "file does not exist, copy it from templates/working-preferences.md first. Do not write "
            "without the yes. Do not apologise at length, do not explain why it happened, and never "
            "argue with the correction."
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

    capture_path: Path | None = None
    if shape == "rant":
        capture_path = eager_capture_rant(repo, prompt)

    if shape is not None:
        note = render_note(shape, capture_path, repo)
        if note:
            print(note)

    # Independent of the capture classifier: nudge the output bias self-check
    # when the prompt is asking for a decision or opinion (rules/biases.md).
    if is_decision_prompt(prompt):
        print(BIAS_NUDGE)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # Last-resort silent exit. A hook crash must not break the session.
        raise SystemExit(0)
