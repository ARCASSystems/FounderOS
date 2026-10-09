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
    "[bias-check] Decision/opinion ask - if a skill fits the ask (founder-next-move "
    "for what to do next, unit-economics for pricing and numbers), run it first: this "
    "check adds to its answer, it does not replace it. Then apply rules/biases.md: "
    "counter-case, confidence level, what evidence is absent, and the do-nothing "
    "option. Flag if you are agreeing mainly because it is the user's existing plan."
)

# The progress card's way back (founder-fit fixes, 8 and 9 Oct 2026). A
# scripted-founder run showed that "I ran the test, what now?" did not trigger
# founder-next-move, so the model never read the open card and pushed a paid
# pre-order the card had ruled out. This nudge does not depend on the skill
# firing: when a card holds a test with no decision yet and the prompt reports a
# result, it names the card and its venture. The pattern wants a result, not the
# word "test", so "run the unit test" or "I ran out of flour" stay quiet.
RESULT_TALK_RX = re.compile(
    r"\b(?:ran|did|done|finished|tried|completed)\b[^.?!\n]{0,40}?"
    r"(?<!unit )(?<!unit-)\b(?:tests?|experiments?|interviews?|conversations?|calls?|surveys?|chats?)\b"
    r"|\b(?:talked|spoke|asked|met|messaged|called|interviewed|texted|surveyed|visited|showed)\b"
    r"|\btested\b"
    r"|\b(?:test|experiment)\s+(?:result|results|is done|went|worked|failed)\b"
    r"|\b(?:my|the|here are (?:my|the))\s+results?\b|\bresults?\s+(?:are|is)\s+(?:in|back)\b"
    r"|\b(?:heard back|signed up|replied|responded|booked)\b"
    r"|\b(?:what now|now what|what next|what'?s next|do next|next move|next step)\b"
    r"|\b\d+\s+(?:of|out of)\s+\d+\b",
    re.IGNORECASE,
)

# --- progress card parser (identical in scripts/brain-snapshot.py and
# scripts/user-prompt-capture.py; tests/test_founder_fit_fixes.py pins the two
# copies together) ---
CARD_MAX_CHARS = 64 * 1024
CARD_FIELD_RX = re.compile(r"^([A-Za-z][A-Za-z0-9 ,()/-]{0,40}?)\s*:\s*(.*)$")
# A decision is keep, change or stop, or a word that means one of them, in any
# tense, at the start of the line. An extension ("extend a week", "keep
# testing", "continue the test") is not a decision: the test is still running.
# Anything else - "(to be filled after the test)", "TBD", "none yet", the
# template's own "keep / change / stop" - leaves the test open, so the card
# keeps coming back.
CARD_DECIDED = re.compile(
    r"^(?:(?:i|we)(?:'ll| will| have|'ve)?\s+|let'?s\s+|decision\s*[:-]?\s*)?"
    r"(?:keep|kept|keeping|change[ds]?|changing|stop(?:s|ped|ping)?|park(?:s|ed|ing)?|paus(?:e|es|ed|ing)"
    r"|continue[ds]?|pivot(?:s|ed|ing)?|kill(?:s|ed|ing)?|drop(?:s|ped|ping)?|greenlight|iterate)\b")
CARD_STILL_RUNNING = re.compile(
    r"^(?:(?:i|we)(?:'ll| will)?\s+)?(?:extend\w*|(?:keep|keeping|continue|continuing)\s+"
    r"(?:testing|the test|this test|it running|waiting|trying|asking|running|collecting)"
    r"|(?:one more|another) (?:week|day|month)|more time\b|waiting\b)")
CARD_EMPTY = {"none", "tbd", "n/a", "na", "pending", "none open", "(none open)", "not yet", "nothing"}
CARD_KEY_ALIAS = {"target": "target, set before the test"}


def parse_progress_card(text: str) -> dict | None:
    """Read the one card at the top of context/progress-card.md.

    Bounded and forgiving on purpose. Founders edit the card by hand, so labels
    may change case, sit indented, carry a bullet, a number, a checkbox, bold or
    a note in brackets, and the decision may say "pending". Only the first
    record counts: reading stops at `## Closed tests`, at a second
    `# Progress card` heading, or at a second Test or Decision line, so a blank
    template can never pair with an old record further down. Frontmatter at the
    top is skipped. Returns None when the card has no filled-in test.
    """
    fields: dict[str, str] = {}
    lines = text[:CARD_MAX_CHARS].lstrip("﻿").splitlines()
    if lines and lines[0].strip() == "---":
        for end in range(1, min(len(lines), 60)):
            if lines[end].strip() == "---":
                lines = lines[end + 1:]
                break
    for line in lines:
        clean = line.strip()
        if clean.startswith("|"):
            cells = [c.strip().replace("**", "") for c in clean.strip("|").split("|")]
            if len(cells) < 2 or not cells[0] or set(cells[0]) <= set("-: "):
                continue
            clean = f"{cells[0]}: {cells[1]}"
        clean = clean.lstrip("-*+> \t").replace("**", "").replace("__", "").strip()
        clean = re.sub(r"^(?:\d+[.)]\s+|\[[ xX]?\]\s*)", "", clean)
        clean = re.sub(r"^_+|_+(?=\s*:)|(?<=:)_+", "", clean).strip()
        low = clean.lower()
        if low.startswith("#"):
            if low.lstrip("#").strip().startswith("closed tests"):
                break
            if "test" in fields and low.lstrip("#").strip().startswith("progress card"):
                break
            continue
        match = CARD_FIELD_RX.match(clean)
        if not match:
            continue
        key = re.sub(r"\s*\([^)]*\)\s*$", "", match.group(1).strip().lower())
        key = CARD_KEY_ALIAS.get(key, key)
        if key in fields:
            if key in ("test", "decision"):
                break
            continue
        fields[key] = match.group(2).strip()
    test = fields.get("test", "")
    if not test or test.startswith("<") or test.lower() in CARD_EMPTY or not re.search(r"[A-Za-z]", test):
        return None
    decision = fields.get("decision", "").strip()
    low = decision.lower().replace("’", "'").strip(" \t*_\"'`")
    template = low.startswith("<") or {"keep", "change", "stop"} <= set(re.findall(r"[a-z]+", low))
    decided = bool(CARD_DECIDED.match(low)) and not CARD_STILL_RUNNING.match(low) and not template

    def value(key: str) -> str:
        val = fields.get(key, "")
        if val.startswith("<") or re.fullmatch(r"[Yy]{4}-[Mm]{2}-[Dd]{2}", val):
            return ""
        return val[:120]

    return {
        "test": test[:200],
        "decision_open": not decided,
        "decision": value("decision") if decided else "",
        "alias": value("venture alias"),
        "target": value("target, set before the test"),
        "deadline": value("deadline"),
        "status": value("status"),
        "result": value("result"),
    }


def read_progress_card(repo: Path) -> dict | None:
    """Parse context/progress-card.md, quietly None when it is missing or unreadable."""
    try:
        with open(repo / "context" / "progress-card.md", encoding="utf-8", errors="replace") as fh:
            return parse_progress_card(fh.read(CARD_MAX_CHARS))
    except OSError:
        return None
# --- end progress card parser ---


# A next-move ask routes to the skill (9 Oct 2026). In a round-4 run, "What's my
# next move?" from a founder never fired founder-next-move: the model answered
# from general knowledge, offered no card, named a regulator from memory, and
# later saved a paid-booking test while the permit was unknown. The skill holds
# those rules, so the ask is routed to it, whether or not a card exists yet.
NEXT_MOVE_RX = re.compile(
    r"\b(?:what (?:should|do|can) i (?:do|focus on|work on) (?:next|now|this week)"
    r"|what'?s my next (?:move|step)|my next move|where do i (?:start|push)"
    r"|i have an idea|is (?:this|it) a good idea|help me validate|what now|now what)\b",
    re.IGNORECASE,
)
NEXT_MOVE_NUDGE = (
    "[next-move] This asks what to do next. Run the founder-next-move skill before you "
    "answer: it proposes one move from the founder's files, offers to save a test as the "
    "progress card on a clear yes, and holds any money test until the founder may take money for it."
)


def card_nudge(card: dict) -> str:
    venture = card["alias"] or "the venture on the card"
    due = f", due {card['deadline']}" if card["deadline"] else ""
    return (
        f"[progress-card] An open test for {venture}{due} is on context/progress-card.md. "
        "If the founder is talking about that venture, run the founder-next-move skill "
        "before you answer: it reads the card, compares any result with the target "
        "written before the test without moving it, asks the founder for the decision "
        "and waits, and keeps the closed test when the next one is saved. If they mean "
        "a different venture, ask before applying this card. No money test, and no "
        "order at a price, until they know they may take money for it."
    )


# Round D (9 Oct 2026): in all three disconfirmed runs the founder said "Change.
# I'll try a different kind of customer." and the model held the write back to
# ask who the new customer was, or asked whether to record it. The next session
# read the old test as untested and sent the founder to re-run it. The skill
# text alone had held in round C and failed here, so a reply that opens with a
# decision word gets a reminder in that turn.
#
# Gated, because the review before Codex round 3 showed the bare words fire on
# everyday chat ("continue", "Change it to bullet points") while a card stays
# open for days. The reminder fires only when the model's last message asked
# for the decision. With no readable transcript it falls back to the card
# itself: a result or a status beyond untested means a decision is due.
DECISION_REPLY_RX = re.compile(
    r"^\W*(?:(?:ok(?:ay)?|yes|yeah|yep|alright|right|sure|so|well|decision|my decision is|my call is"
    r"|i think|i guess|i'?ll|i will|i want to|i'd like to|i'd|we|we'?ll|we will|we should|let'?s|let us)\W+){0,4}"
    r"(?:keep|kept|keeping|change[ds]?|changing|stop(?:s|ped|ping)?|pivot(?:s|ed|ing)?|kill(?:s|ed|ing)?"
    r"|drop(?:s|ped|ping)?|paus(?:e|es|ed|ing)|park(?:s|ed|ing)?|extend(?:s|ed|ing)?|continue[ds]?|continuing)\b",
    re.IGNORECASE,
)
DECISION_REPLY_MAX = 600
DECISION_ASKED_RX = re.compile(
    r"\bkeep\b[^?\n]{0,120}\b(?:change|pivot)\b[^?\n]{0,120}\b(?:stop|kill|re-?test)\b"
    r"|\bkill\b[^?\n]{0,60}\bpivot\b"
    r"|\byour (?:decision|call)\b|\bdecision\b[^\n]{0,60}\?",
    re.IGNORECASE,
)
TRANSCRIPT_TAIL_BYTES = 256 * 1024


def last_assistant_text(transcript_path: str | None) -> str | None:
    """The text of the model's last message, read from the session transcript.

    None when there is no transcript or it cannot be read, so the caller can
    tell "no transcript" apart from "the last message said nothing".
    """
    if not transcript_path:
        return None
    try:
        with open(transcript_path, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - TRANSCRIPT_TAIL_BYTES))
            tail = fh.read().decode("utf-8", "replace")
    except (OSError, ValueError):
        return None
    for line in reversed(tail.splitlines()):
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(event, dict) or event.get("type") != "assistant":
            continue
        content = (event.get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
            if texts:
                return "\n".join(texts)
    return ""


def decision_is_due(card: dict, transcript_path: str | None) -> bool:
    asked = last_assistant_text(transcript_path)
    if asked is not None:
        return bool(DECISION_ASKED_RX.search(asked))
    return bool(card["result"]) or card["status"].lower() in ("attempted", "supported", "disconfirmed")


def native_copy_note(repo: Path) -> str:
    """A warning when Claude Code's own copy of the skill is older than its source.

    An install updated from 1.55.2 runs the old update command, so the native
    copy in .claude/skills can keep the old text, with no card and the old money
    advice, while these nudges send the founder to it.
    """
    try:
        source = (repo / "skills" / "founder-next-move" / "SKILL.md").read_bytes()
        native = (repo / ".claude" / "skills" / "founder-next-move" / "SKILL.md").read_bytes()
    except OSError:
        return ""
    if source == native:
        return ""
    return (" The copy in .claude/skills/founder-next-move is older than skills/founder-next-move/SKILL.md: "
            "follow skills/founder-next-move/SKILL.md, and tell the founder once that "
            "`python scripts/skills_sync.py --apply` refreshes it.")


def decision_nudge(card: dict) -> str:
    venture = card["alias"] or "the venture on the card"
    return (
        f"[progress-card] If this answers your question about the decision on the open test for {venture} "
        "(keep, change or stop), their answer is their yes to record it. If the founder-next-move skill "
        "has not run in this conversation, run it now: it holds the card's rules. If they are closing the "
        "test, write it to context/progress-card.md in this reply, before any question, as the first line "
        "under ## Closed tests (newest first), in exactly this shape: "
        "- YYYY-MM-DD | Test: ... | Target: ... | Result: ... | Status: ... | Decision: <keep, "
        "change or stop>, \"<their words>\". Then take its Test result due line out of Must Do. "
        "Do not wait to hear the next customer or test. Change no target and no other card line, "
        "and write the next test only after its own yes. If they are extending the same test, "
        "write the partial result, set Status to attempted, keep the target and leave Decision empty."
    )


def has_open_card(repo: Path) -> bool:
    """True when context/progress-card.md holds a filled test with no decision yet."""
    card = read_progress_card(repo)
    return bool(card and card["decision_open"])


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
    cleaned = PRIVATE_BLOCK.sub("", prompt)
    # An unclosed <private> hides everything after it, matching the card rule.
    cleaned = re.sub(r"<private>.*\Z", "", cleaned, flags=re.IGNORECASE | re.DOTALL).strip()
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


def read_envelope_from_stdin() -> tuple[str | None, str | None]:
    """Claude Code passes the hook a JSON envelope on stdin. Return its
    `prompt` and `transcript_path` fields. If anything is malformed, the
    prompt is None."""
    try:
        raw = sys.stdin.read()
    except OSError:
        return None, None
    if not raw:
        return None, None
    # The envelope is JSON. Older versions may pass plain text - tolerate both.
    raw = raw.strip()
    if raw.startswith("{"):
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError:
            return None, None
        if not isinstance(envelope, dict):
            return None, None
        prompt = envelope.get("prompt")
        transcript = envelope.get("transcript_path")
        transcript = transcript if isinstance(transcript, str) else None
        if isinstance(prompt, str):
            return prompt, transcript
        return None, None
    # Fallback: treat raw stdin as the prompt itself.
    return raw, None


def read_prompt_from_stdin() -> str | None:
    """The prompt alone, for callers that do not need the transcript path."""
    return read_envelope_from_stdin()[0]


def main() -> int:
    repo = find_repo_root()
    if repo is None:
        return 0

    prompt, transcript_path = read_envelope_from_stdin()
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

    card_named = False
    reply = prompt.replace("\u2019", "'")
    if len(reply) <= DECISION_REPLY_MAX and DECISION_REPLY_RX.search(reply):
        card = read_progress_card(repo)
        if card and card["decision_open"] and decision_is_due(card, transcript_path):
            print(decision_nudge(card) + native_copy_note(repo))
            card_named = True
    if not card_named and RESULT_TALK_RX.search(prompt):
        card = read_progress_card(repo)
        if card and card["decision_open"]:
            print(card_nudge(card) + native_copy_note(repo))
            card_named = True
    if not card_named and NEXT_MOVE_RX.search(prompt):
        print(NEXT_MOVE_NUDGE + native_copy_note(repo))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # Last-resort silent exit. A hook crash must not break the session.
        raise SystemExit(0)
