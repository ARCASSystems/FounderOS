#!/usr/bin/env python3
"""register_census.py - makes rules/writing-style.md countable.

The problem it exists for: the writing rules were ninety-three lines of prose
and nothing enforced them. The commit guard blocks em dashes, and after that
every judgment about whether a draft sounds like a person was handed to a model
and asked for an opinion. An opinion is not a measurement, so the same tells
came back every week and nobody could tell whether writing was improving. This
counts them instead. Eighteen classes, each one traceable to a line of
rules/writing-style.md, which is also where the banned-word list is read from
so the page and this script cannot drift apart.

What it cannot do: judge whether the writing is true, kind, or worth sending.
It counts tells. The reading pass is still the reading pass.

Invariants: read-only, standard library only, no network, no API key, no model
call, ASCII-safe output. Works on the free floor because it is arithmetic.
Exit 0 (pass or warn), 2 (gate FAIL), 1 (unreadable input).

Usage:
  python scripts/register_census.py <file>                    # human table
  python scripts/register_census.py <file> --lines            # every hit
  python scripts/register_census.py <file> --json             # machine
  python scripts/register_census.py <file> --gate deliverable # exit 2 on FAIL
  python scripts/register_census.py --text "..." --gate content
Formats: .md .markdown .txt .html .htm .docx. Anything else returns SKIP.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import math
import re
import sys
import zipfile
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STYLE_PAGE = REPO_ROOT / "rules" / "writing-style.md"
EXCEPTIONS = REPO_ROOT / "rules" / "banned-words-exceptions.txt"
VOICE_PROFILE = REPO_ROOT / "core" / "voice-profile.yml"


# ----------------------------------------------------------- the page --

def load_banned_words(style_page: Path | None = None) -> list[str]:
    """The banned list, read from the page that publishes it.

    Keeping one copy is the whole point: a second list in this file would be
    right on the day it was written and wrong by the next edit.
    """
    page = style_page or STYLE_PAGE
    if not page.is_file():
        return []
    words: list[str] = []
    in_section = False
    for line in page.read_text(encoding="utf-8", errors="replace").splitlines():
        st = line.strip()
        if st.startswith("## "):
            in_section = "banned word" in st.lower()
            continue
        if not in_section:
            continue
        # Any list shape a person actually writes: "- x", "* x", "+ x", "1. x".
        m = re.match(r"^(?:[-*+]|\d+[.)])\s+(.*)$", st)
        if not m:
            continue
        term = re.sub(r"\s*\([^)]*\)\s*", "", m.group(1)).strip()  # "leverage (as a verb)"
        # Trailing punctuation has to go or the word is unmatchable: a list
        # written "- synergy." became the pattern \bsynergy\.\b, which matches
        # nothing, so the term looked enforced and silently was not.
        term = term.strip("`*_\"' ").rstrip(".,;:!?").strip()
        if term and "{{" not in term and len(term) < 40:
            words.append(term.lower())
    return words


class StylePageEmpty(RuntimeError):
    """The page yielded no banned words. Silence here is the dangerous answer."""


def load_voice_banned(root: Path | None = None) -> list[str]:
    """The founder's own banned words, if they have done the voice interview."""
    path = (root or REPO_ROOT) / "core" / "voice-profile.yml"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^\s*banned_words:\s*$", text, re.MULTILINE)
    if not m:
        return []
    out: list[str] = []
    for line in text[m.end():].splitlines()[1:]:
        if not line.startswith((" ", "\t")):
            break
        st = line.strip()
        if not st.startswith("- "):
            break
        w = st[2:].strip().strip("\"'")
        if w and not w.startswith("[") and "{{" not in w:
            out.append(w.lower())
    return out


def load_exceptions(path: Path | None = None) -> list[tuple[str, str]]:
    """Settled judgments: (term, glob). A gate that re-raises a decision you
    already made trains you to stop reading it."""
    p = path or EXCEPTIONS
    if not p.is_file():
        return []
    out: list[tuple[str, str]] = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        st = line.strip()
        if not st or st.startswith("#") or "|" not in st:
            continue
        parts = [x.strip() for x in st.split("|")]
        if len(parts) < 2 or not parts[0]:
            continue
        scope = parts[1]
        glob = scope
        m = re.search(r"\(([^)]*[*/][^)]*)\)\s*$", scope)
        if m:
            glob = m.group(1).strip()
        out.append((parts[0].lower(), glob))
    return out


# ------------------------------------------------------------------ text --

@dataclass
class Para:
    text: str    # cleaned prose
    raw: str     # source text, markers kept, for lead-in detection
    line: int    # source line, or paragraph index for html and docx
    kind: str    # heading | prose | bullet | table


_MD_BULLET = re.compile(r"^(?:[-*+]|\d+[.)])\s+(.*)$")
_MD_HEADING = re.compile(r"^#{1,6}\s+(.*)$")
_INLINE_CLEAN = [
    (re.compile(r"!\[([^\]]*)\]\([^)]*\)"), r"\1"),
    (re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]"), r"\1"),
    (re.compile(r"\[([^\]]+)\]\([^)]*\)"), r"\1"),
    (re.compile(r"<[^>]+>"), ""),
    (re.compile(r"`([^`]*)`"), r"\1"),
    (re.compile(r"\*\*|__"), ""),
    (re.compile(r"(?<!\w)[*_](?=\S)|(?<=\S)[*_](?!\w)"), ""),
]


def _clean_inline(s: str) -> str:
    for pat, rep in _INLINE_CLEAN:
        s = pat.sub(rep, s)
    return unescape(re.sub(r"\s+", " ", s)).strip()


def paras_from_markdown(text: str) -> list[Para]:
    lines = text.splitlines()
    out: list[Para] = []
    i = 0
    if lines and lines[0].strip() == "---":          # front matter is metadata
        for j in range(1, min(len(lines), 200)):
            if lines[j].strip() == "---":
                i = j + 1
                break
    buf: list[str] = []
    start = 0
    kind = "prose"
    in_code = in_comment = False

    def flush() -> None:
        nonlocal buf
        if buf:
            raw = " ".join(x.strip() for x in buf)
            out.append(Para(_clean_inline(raw), raw, start, kind))
        buf = []

    for idx in range(i, len(lines)):
        st = lines[idx].strip()
        if in_comment:
            if "-->" in st:
                in_comment = False
            continue
        if st.startswith("<!--"):
            flush()
            if "-->" not in st:
                in_comment = True
            continue
        if st.startswith("```") or st.startswith("~~~"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        if not st:
            flush()
            continue
        if st.startswith("|"):
            flush()
            cells = [c.strip() for c in st.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c or "--") for c in cells):
                out.append(Para(_clean_inline(" ".join(cells)), st, idx + 1, "table"))
            continue
        m = _MD_HEADING.match(st)
        if m:
            flush()
            out.append(Para(_clean_inline(m.group(1)), st, idx + 1, "heading"))
            continue
        if re.fullmatch(r"(?:-{3,}|\*{3,}|_{3,})", st):
            flush()
            continue
        m = _MD_BULLET.match(st)
        if m:
            flush()
            buf, start, kind = [m.group(1)], idx + 1, "bullet"
            continue
        if st.startswith(">"):
            st = st.lstrip("> ").strip()
        if not buf:
            start, kind = idx + 1, "prose"
        buf.append(st)
    flush()
    return out


class _HTMLBlocks(HTMLParser):
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "section",
             "article", "blockquote", "figcaption", "dd", "dt", "summary", "header", "footer"}
    SKIP = {"script", "style", "svg", "code", "pre", "head", "title", "noscript"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paras: list[Para] = []
        self._buf: list[str] = []
        self._raw: list[str] = []
        self._kind = "prose"
        self._skip = 0
        self._n = 0

    def _flush(self) -> None:
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        raw = re.sub(r"\s+", " ", "".join(self._raw)).strip()
        if text:
            self._n += 1
            self.paras.append(Para(text, raw, self._n, self._kind))
        self._buf, self._raw = [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
            return
        if self._skip:
            return
        if tag in self.BLOCK:
            self._flush()
            self._kind = ("heading" if tag[0] == "h" and tag[1:].isdigit()
                          else "bullet" if tag == "li"
                          else "table" if tag in ("td", "th") else "prose")
        elif tag in ("strong", "b"):
            self._raw.append("**")
        elif tag == "br":
            self._buf.append(" ")
            self._raw.append(" ")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag in self.BLOCK:
            self._flush()
            self._kind = "prose"
        elif tag in ("strong", "b"):
            self._raw.append("**")

    def handle_data(self, data):
        if self._skip:
            return
        self._buf.append(data)
        self._raw.append(data)


def paras_from_html(text: str) -> list[Para]:
    p = _HTMLBlocks()
    p.feed(text)
    p._flush()
    return [Para(_clean_inline(x.text), x.raw, x.line, x.kind) for x in p.paras]


def paras_from_docx(path: Path) -> list[Para]:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    out: list[Para] = []
    for n, pm in enumerate(re.finditer(r"<w:p[ >].*?</w:p>", xml, re.DOTALL), start=1):
        px = pm.group(0)
        parts: list[str] = []
        raw_parts: list[str] = []
        for r in re.findall(r"<w:r[ >].*?</w:r>", px, re.DOTALL):
            t = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", r, re.DOTALL))
            if not t:
                continue
            parts.append(t)
            bold = re.search(r"<w:b\s*/>|<w:b\s+w:val=\"(?:1|true)\"", r)
            raw_parts.append(f"**{t}**" if bold else t)
        text = unescape("".join(parts)).strip()
        if not text:
            continue
        kind = "prose"
        if re.search(r'<w:pStyle w:val="(?:Heading|Title)', px):
            kind = "heading"
        elif "<w:numPr>" in px:
            kind = "bullet"
        out.append(Para(re.sub(r"\s+", " ", text), unescape("".join(raw_parts)), n, kind))
    return out


def load_paras(path: Path) -> list[Para] | None:
    ext = path.suffix.lower()
    if ext in (".md", ".markdown", ".txt"):
        return paras_from_markdown(path.read_text(encoding="utf-8", errors="replace"))
    if ext in (".html", ".htm"):
        return paras_from_html(path.read_text(encoding="utf-8", errors="replace"))
    if ext == ".docx":
        return paras_from_docx(path)
    return None


# ------------------------------------------------------------- patterns --

def _rx(*pats: str) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in pats]


# group -> class -> patterns. Every class names a line of rules/writing-style.md,
# and tests/test_register_census.py fails when one does not.
PATTERNS: dict[str, dict[str, list[re.Pattern]]] = {
    "clarity": {
        "cross_ref": _rx(
            r"\bpage\s+\d+\b",
            r"\b(?:see|as)\s+(?:noted|mentioned|discussed|described|set out|shown|explained)\s+(?:above|earlier|below|later)\b",
            r"\bsee (?:above|below)\b",
            r"\bthe rest of (?:this|the) (?:document|paper|page|section|plan)\b",
            r"\b(?:in|from|on) (?:section|chapter|page) \d",
            r"\bas (?:above|below)\b",
            r"\bthe (?:section|page) (?:above|below)\b",
        ),
        "hedge_of_fact": _rx(
            r"\barguably\b", r"\bto some extent\b", r"\bin many ways\b", r"\bmore or less\b",
            r"\bit could be (?:said|argued)\b", r"\bone could argue\b",
            r"\bit is fair to say\b", r"\bit seems (?:that|likely|fair)\b",
            r"\bappears to be the case\b", r"\balmost (?:nobody|no one|everyone)\b",
        ),
    },
    "register": {
        "honesty_signal": _rx(
            r"\bworth (?:stating|saying|noting|naming|being clear|spelling out)\b",
            r"\bthe honest (?:position|answer|view|truth|note|version|read)\b",
            r"\b(?:an?|one) honest (?:note|answer|position|caveat|word)\b",
            r"\bto be (?:honest|clear|frank|direct|blunt)\b",
            r"\bhonestly\b", r"\bfrankly\b", r"\bcandidly\b",
            r"\bin plain (?:terms|words|language|english)\b",
            r"\bthe truth is\b", r"\blet me be (?:clear|honest|direct|blunt)\b",
            r"\bit'?s worth (?:saying|noting|stating)\b", r"\bfor what it'?s worth\b",
        ),
        "finger_pointing": _rx(
            r"\b(?:has|have|had) never been (?:used|asked|tried|opened|touched|contacted|invited|considered)\b",
            r"\b(?:nobody|no one) has (?:spoken|asked|used|tried|looked|checked|contacted|noticed)\b",
            r"\b(?:the )?least used\b", r"\bunused asset\b", r"\bunderused\b",
            r"\bnot a complaint\b", r"\b(?:has|have) been ignored\b",
            r"\bsits? unused\b", r"\bnobody (?:knew|noticed|checked|owns)\b",
        ),
        "negative_parallelism": _rx(
            r"\bit'?s not (?:about )?[^.!?\n]{1,40}?,? it'?s\b",
            r"\bnot (?:just|only|merely|simply) [^.!?\n]{1,40}?,? but\b",
            r",\s*not (?:the|a|an|just|because|to)\b",
            r"\bnot (?:a|an) [^.!?\n]{1,30}?\bbut (?:a|an)\b",
        ),
    },
    "structure": {
        "meta_commentary": _rx(
            r"\bin this (?:document|paper|memo|section|note|report|proposal|deck),? (?:we|I|you)\b",
            r"\bthis (?:document|paper|memo|report|proposal|section|deck) (?:covers|sets out|describes|explains|outlines|will|presents|summari[sz]es)\b",
            r"\blet'?s (?:walk|break|dive|unpack|take a look|get into)\b",
            r"\bin conclusion\b", r"\bto summari[sz]e\b", r"\bin summary\b", r"\bto sum up\b",
            r"\bas (?:we|you) (?:have|can) see[n]?\b", r"\blet us now\b",
            r"\bthe (?:following|below) (?:sections?|pages?) (?:will|set out|cover|show)\b",
            r"\bwe will (?:now|then) (?:turn|look|move)\b",
            r"\bhere'?s the (?:truth|thing)\b",
            r"\bthe purpose of this (?:document|note|paper)\b",
        ),
        "define_by_exclusion": _rx(
            r"\b(?:this|it|that|here) is not (?:a|an|about) \b",
            r"\bnot a (?:framework|pitch|sales|checklist|template|silver bullet|magic|manifesto)\b",
        ) + [re.compile(r"\bis NOT\b")],  # case-sensitive: the shouted negation is the tell
        "triplet": _rx(r"\b\w+(?: \w+)?, \w+(?: \w+)?,? and \w+(?: \w+)?[.!?]"),
    },
    "vocab": {
        "idiom": _rx(
            r"\bmove the needle\b", r"\blow[- ]hanging fruit\b", r"\bboil the ocean\b",
            r"\bat the end of the day\b", r"\bthink outside the box\b",
            r"\bcircle back\b", r"\btouch base\b", r"\bdeep dive\b",
            r"\bmoving forward\b", r"\bon the same page\b", r"\braise the bar\b",
            r"\bhit the ground running\b", r"\bbandwidth\b", r"\bdouble down\b",
        ),
        "no_contraction": _rx(
            r"\bdo not\b", r"\bdoes not\b", r"\bdid not\b", r"\bis not\b", r"\bare not\b",
            r"\bwas not\b", r"\bwere not\b", r"\bwill not\b", r"\bwould not\b",
            r"\bcannot\b", r"\bcan not\b", r"\bit is\b", r"\bthat is\b", r"\byou are\b",
            r"\bwe are\b", r"\bthey are\b", r"\bhave not\b", r"\bhas not\b",
        ),
        "dash": _rx("[" + chr(0x2014) + chr(0x2013) + "]"),
    },
}

# Classes with no regex: the report explains them in these words.
COMPUTED = {
    "aphorism_closer": ("register", "paragraph ends on a short quotable line after a long one"),
    "paragraph_overload": ("clarity", "four or more sentences and over 75 words"),
    "label_colon": ("structure", "bold or Label: lead-in opening a paragraph"),
    "heading_one_liner": ("structure", "heading with a single sentence under it"),
    "banned_word": ("vocab", "a term from the banned list in rules/writing-style.md"),
    "semicolon": ("vocab", "semicolon in prose"),
    "hyphen_density": ("vocab", "spaced hyphens past about ten per thousand words"),
}

# One line per class, in the words of rules/writing-style.md. The scorecard
# prints these, and tests/test_register_census.py fails when a class has no
# entry here or no rule on the page - which is how the two stay in step.
CLASS_RULE = {
    "banned_word": "a term from the banned list in rules/writing-style.md",
    "dash": "no em dashes, no en dashes",
    "hyphen_density": "the spaced hyphen stays under about ten per thousand words",
    "semicolon": "no semicolons, break into two sentences",
    "triplet": "no rule-of-three constructions",
    "meta_commentary": "no meta-commentary, just cover it",
    "idiom": "avoid idioms, non-native readers",
    "no_contraction": "contractions in writing that talks",
    "paragraph_overload": "one idea per paragraph",
    "cross_ref": "no cross-references inside a document",
    "hedge_of_fact": "do not hedge a fact you know",
    "honesty_signal": "do not signal your own honesty",
    "finger_pointing": "do not point a finger at what nobody did",
    "negative_parallelism": "no negation-contrast",
    "aphorism_closer": "aphorism budget, one per document",
    "label_colon": "no label-colon openers",
    "define_by_exclusion": "do not define a thing by what it is not",
    "heading_one_liner": "a heading over one sentence is a label the sentence did not need",
}

# Below this, a document is scored as if it were this long. See the scoring
# block in census_paras for why this number is 200 and not 1000.
DENSITY_FLOOR_WORDS = 200
# And below THIS, the score itself is too small a sample to fail a gate on.
# Zero-tolerance classes still fail, because one "to be honest" in a two-line
# note is still one too many for something a client reads.
MIN_WORDS_TO_SCORE_A_GATE = 80

GROUP_WEIGHT = {"clarity": 4, "register": 4, "structure": 2, "vocab": 1}
GROUP_CAP = {"clarity": 30, "register": 30, "structure": 20, "vocab": 15}

# A profile is a channel, not a quality bar. A client deliverable and a note to
# yourself fail for different things, and pretending otherwise is how a gate
# gets routed around.
ZERO_TOLERANCE = {
    "deliverable": {"honesty_signal", "cross_ref", "meta_commentary"},
    "content": {"meta_commentary"},
    "internal": set(),
}
BUDGET = {"aphorism_closer": 1, "finger_pointing": 1, "hyphen_density": 10,
          "label_colon_density": 1 / 3}
# Counted everywhere so --lines still shows them, scored only where the rule
# applies. "Contractions always" is a rule for writing that talks: a post, an
# email, a caption. Holding a contract or a doctrine page to it produces noise,
# which is measurable - the repo's own pages run 6 to 22 per thousand words.
PROFILE_ONLY = {"no_contraction": {"content"}}
GATE_FAIL_SCORE = {"deliverable": 80, "content": 70, "internal": 60}
GATE_WARN_SCORE = {"deliverable": 90, "content": 85, "internal": 75}
HALF_WEIGHT = {"dash", "semicolon", "banned_word", "triplet", "no_contraction",
               "idiom", "hyphen_density"}


# ------------------------------------------------------------- measure --

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[\"'(\[A-Z0-9])")
_WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
# A short closing line that gives an instruction is a person telling you what to
# do, not an epigram. Closers opening with these are not counted.
_IMPERATIVE = re.compile(
    r"^(?:Do|Don't|Never|Always|Use|Run|Read|Keep|Cut|Say|Ask|Name|Check|Delete|Start|Stop|"
    r"Skip|Cite|Only|No|Then|Just|Avoid|Treat|Put|Write|Add|Remove|Leave|Make|Get|Send|Tell|"
    r"Let|Note|See|Mark|Set|Pick|Choose|Confirm|Verify|Test|Log|Record|State|Show|Give|Hold|"
    r"Open|Close|Look|Find|Count|Build|Ship|Flag|Prefer|Expect|Try|Call|Draft|Save|Reply|"
    r"Answer|Include|Match|Move|Return|Report|Sort|Stay|Take|Wait|Watch)\b")


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]


def _syllables(word: str) -> int:
    w = word.lower().strip("'-")
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and n > 1:
        n -= 1
    return max(1, n)


@dataclass
class Hit:
    cls: str
    group: str
    line: int
    snippet: str


@dataclass
class Census:
    words: int = 0
    sentences: int = 0
    paragraphs: int = 0
    fk_grade: float = 0.0
    avg_sentence: float = 0.0
    burstiness: float = 0.0
    longest_sentence: int = 0
    bold_leadin_density: float = 0.0
    hits: list[Hit] = field(default_factory=list)
    penalties: dict[str, float] = field(default_factory=dict)
    score: int = 100

    def count(self, cls: str) -> int:
        return sum(1 for h in self.hits if h.cls == cls)

    def by_class(self) -> dict[str, list[Hit]]:
        out: dict[str, list[Hit]] = {}
        for h in self.hits:
            out.setdefault(h.cls, []).append(h)
        return out


def _snip(text: str, m: re.Match, width: int = 70) -> str:
    a = max(0, m.start() - 25)
    b = min(len(text), m.end() + 35)
    s = text[a:b].strip()
    return ("..." if a > 0 else "") + s[:width] + ("..." if b < len(text) else "")


def _group_of(cls: str) -> str:
    for g, classes in PATTERNS.items():
        if cls in classes:
            return g
    return COMPUTED.get(cls, ("vocab", ""))[0]


def census_paras(paras: list[Para], banned: list[str] | None = None,
                 exclude: set[str] | None = None, profile: str = "deliverable") -> Census:
    """Measure a paragraph list.

    `exclude` drops whole classes before scoring. The scorecard uses it so a
    writing skill is not marked down for quoting the words it bans. `profile`
    names the channel, because a post and a contract fail for different things.
    """
    c = Census()
    prose = [p for p in paras if p.kind in ("prose", "bullet")]
    c.paragraphs = len(prose)
    banned = banned if banned is not None else banned_words_or_warn()
    banned_rx = [(w, re.compile(r"\b" + re.escape(w) + r"\b", re.IGNORECASE))
                 for w in dict.fromkeys(banned) if w]

    all_sents: list[list[str]] = []
    for p in prose:
        for s in sentences(p.text):
            all_sents.append(_WORD.findall(s))
    c.sentences = len(all_sents)
    c.words = sum(len(s) for s in all_sents)
    if c.sentences and c.words:
        syl = sum(_syllables(w) for s in all_sents for w in s)
        avg = c.words / c.sentences
        c.fk_grade = round(0.39 * avg + 11.8 * (syl / c.words) - 15.59, 1)
        lengths = [len(s) for s in all_sents]
        c.longest_sentence = max(lengths)
        if len(lengths) > 1:
            var = sum((n - avg) ** 2 for n in lengths) / len(lengths)
            c.burstiness = round(math.sqrt(var) / avg, 2) if avg else 0.0
        c.avg_sentence = round(avg, 1)

    for p in paras:
        if p.kind == "table":
            continue
        for group, classes in PATTERNS.items():
            for cls, pats in classes.items():
                taken: list[tuple[int, int]] = []   # overlapping patterns count once
                for pat in pats:
                    for m in pat.finditer(p.text):
                        if any(m.start() < b and m.end() > a for a, b in taken):
                            continue
                        taken.append((m.start(), m.end()))
                        c.hits.append(Hit(cls, group, p.line, _snip(p.text, m)))
        for _w, rx in banned_rx:
            for m in rx.finditer(p.text):
                c.hits.append(Hit("banned_word", "vocab", p.line, _snip(p.text, m)))
        if p.kind in ("prose", "bullet"):
            for m in re.finditer(r";", p.text):
                c.hits.append(Hit("semicolon", "vocab", p.line, _snip(p.text, m)))

    # computed classes
    lead = 0
    for p in prose:
        raw = p.raw.strip()
        # Bold lead-ins count on paragraphs and bullets. The plain "Label: text"
        # form counts only on prose, so a record field in a list ("- Status: open")
        # reads as metadata rather than as a slide title.
        if (re.match(r"^\*\*[^*]{2,60}[.:]\*\*\s*\S", raw)
                or re.match(r"^\*\*[^*]{2,60}\*\*[.:]\s*\S", raw)
                or (p.kind == "prose" and re.match(r"^[A-Z][A-Za-z' -]{1,30}:\s+[A-Za-z\"']", raw))):
            lead += 1
            c.hits.append(Hit("label_colon", "structure", p.line, raw[:70]))
        sents = sentences(p.text)
        wc = len(_WORD.findall(p.text))
        if len(sents) >= 4 and wc > 75:
            c.hits.append(Hit("paragraph_overload", "clarity", p.line,
                              f"{len(sents)} sentences, {wc} words: {p.text[:50]}..."))
        if len(sents) >= 2:
            last, prev = sents[-1], sents[-2]
            lw, pw = _WORD.findall(last), _WORD.findall(prev)
            if (3 <= len(lw) <= 9 and len(pw) >= 12 and not re.search(r"\d", last)
                    and last.endswith(".")
                    and not re.match(r"^(?:I|We|You|Please|Thank)\b", last)
                    and not _IMPERATIVE.match(last)):
                c.hits.append(Hit("aphorism_closer", "register", p.line, last))
    c.bold_leadin_density = round(lead / c.paragraphs, 2) if c.paragraphs else 0.0

    # A heading over one sentence, with nothing else under it, is a label the
    # sentence did not need.
    for i, p in enumerate(paras):
        if p.kind != "heading":
            continue
        nxt = paras[i + 1] if i + 1 < len(paras) else None
        after = paras[i + 2] if i + 2 < len(paras) else None
        if (nxt and nxt.kind == "prose" and len(sentences(nxt.text)) <= 1
                and (after is None or after.kind == "heading")):
            c.hits.append(Hit("heading_one_liner", "structure", p.line, p.text[:60]))

    # The spaced hyphen is what replaces the banned em dash, so it is scored as
    # a density rather than a hard count. Ten per thousand words is roughly one
    # per paragraph, which is where it stops reading as punctuation and starts
    # reading as a tic.
    for p in paras:
        for m in re.finditer(r"\s-\s", p.text):
            c.hits.append(Hit("hyphen_density", "vocab", p.line, _snip(p.text, m)))

    if exclude:
        c.hits = [h for h in c.hits if h.cls not in exclude]

    # Scored on density, not on total count. Absolute counts punish a long
    # document for being long: the first draft gave this repo's own doctrine
    # pages a D, which would have taught founders to ignore the whole thing.
    #
    # The floor was 1000 words at first, which quietly reintroduced the same
    # bug under it: identical writing at identical density scored 98 at fifteen
    # words and 76 at a hundred and fifty, because everything below the floor
    # was still being scored on absolute counts, and most real deliverables
    # live below it. Two hundred is low enough that a normal document is scored
    # on its actual density and high enough that one tell in a two-line note is
    # not extrapolated into a catastrophe.
    scale = 1000.0 / max(c.words, DENSITY_FLOOR_WORDS)
    counts = {cls: len(hs) for cls, hs in c.by_class().items()}
    group_pen: dict[str, float] = {g: 0.0 for g in GROUP_WEIGHT}
    for cls, raw_n in counts.items():
        if cls in PROFILE_ONLY and profile not in PROFILE_ONLY[cls]:
            continue
        n: float = raw_n
        group = _group_of(cls)
        if cls == "label_colon":
            n = max(0, raw_n - int(c.paragraphs * BUDGET["label_colon_density"]))
        n = n * scale
        if cls in BUDGET and cls != "label_colon":
            n = max(0.0, n - BUDGET[cls])
        if cls in HALF_WEIGHT:
            n = n * 0.5
        group_pen[group] += GROUP_WEIGHT[group] * n
    for g, pen in group_pen.items():
        c.penalties[g] = round(min(GROUP_CAP[g], pen), 1)
    c.score = max(0, int(round(100 - sum(c.penalties.values()))))
    return c


def census_text(text: str, fmt: str = "md", profile: str = "deliverable") -> Census:
    paras = paras_from_html(text) if fmt == "html" else paras_from_markdown(text)
    return census_paras(paras, profile=profile)


def banned_words_or_warn(warn=None) -> list[str]:
    """The banned list, and a loud complaint when there is not one.

    `rules/` is a file the founder is invited to edit, so the page can go
    missing, get emptied, or have its heading restructured. Any of those made
    the census quietly enforce zero banned words and report a clean score,
    which is worse than not running: it tells you the writing passed a check
    that did not happen.
    """
    page = load_banned_words()
    if not page:
        msg = (f"register-census: no banned words found in {STYLE_PAGE}. "
               "The page is missing, empty, or its '## Banned Words and Phrases' "
               "heading has been renamed. Every other class still ran; the "
               "banned-word class did NOT.")
        (warn or (lambda m: print(m, file=sys.stderr)))(msg)
    return page + load_voice_banned()


def census_file(path: Path, profile: str = "deliverable") -> Census | None:
    paras = load_paras(path)
    if paras is None:
        return None
    exempt = {term for term, glob in load_exceptions() if _matches(path, glob)}
    banned = [w for w in banned_words_or_warn() if w not in exempt]
    return census_paras(paras, banned=banned, profile=profile)


def _matches(path: Path, glob: str) -> bool:
    try:
        rel = path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel = path.as_posix()
    return fnmatch.fnmatch(rel, glob) or fnmatch.fnmatch(path.name, glob)


def top_classes(c: Census, profile: str = "deliverable", n: int = 3) -> list[tuple[str, int]]:
    """The classes worth fixing first, heaviest group by count.

    Classes that are not scored on this profile are left out: naming a class the
    gate is not applying is how a report teaches people to distrust it.
    """
    items = [(cls, hs) for cls, hs in c.by_class().items()
             if not (cls in PROFILE_ONLY and profile not in PROFILE_ONLY[cls])]
    items.sort(key=lambda kv: -GROUP_WEIGHT[kv[1][0].group] * len(kv[1]))
    return [(cls, len(hs)) for cls, hs in items[:n]]


def grade(score: int) -> str:
    return "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 65 else "D"


# ---------------------------------------------------------------- gate --

def gate(c: Census, profile: str) -> tuple[str, list[str]]:
    """Return (status, reasons) with status in pass | warn | fail."""
    profile = profile if profile in ZERO_TOLERANCE else "deliverable"
    reasons: list[str] = []
    counts = {cls: len(hs) for cls, hs in c.by_class().items()}
    for cls in sorted(ZERO_TOLERANCE[profile]):
        if counts.get(cls):
            reasons.append(f"{cls} {counts[cls]} (zero tolerance)")
    if profile == "deliverable":
        for cls in ("aphorism_closer", "finger_pointing"):
            if counts.get(cls, 0) > BUDGET[cls]:
                reasons.append(f"{cls} {counts[cls]} (budget {BUDGET[cls]})")
        if counts.get("dash"):
            reasons.append(f"dash {counts['dash']} (em and en dashes never ship)")
    scoreable = c.words >= MIN_WORDS_TO_SCORE_A_GATE
    if scoreable and c.score < GATE_FAIL_SCORE[profile]:
        reasons.append(f"score {c.score} below {GATE_FAIL_SCORE[profile]}")
    if reasons:
        return "fail", reasons
    warns: list[str] = []
    if not scoreable:
        warns.append(f"{c.words} words is too short to score a gate on - the "
                     "zero-tolerance classes were still checked")
    elif c.score < GATE_WARN_SCORE[profile]:
        warns.append(f"score {c.score} below {GATE_WARN_SCORE[profile]}")
    if c.burstiness and c.burstiness < 0.35 and c.sentences >= 8:
        warns.append(f"burstiness {c.burstiness} - sentence lengths read like a metronome")
    if c.fk_grade > 9 and profile != "internal":
        warns.append(f"reading grade {c.fk_grade} - target is under 8 for readers "
                     "whose first language is not English")
    return ("warn", warns) if warns else ("pass", [])


# -------------------------------------------------------------- render --

def to_dict(c: Census, gate_result: tuple[str, list[str]] | None = None,
            label: str = "") -> dict:
    classes = {}
    for cls, hs in sorted(c.by_class().items(), key=lambda kv: -len(kv[1])):
        classes[cls] = {"group": hs[0].group, "hits": len(hs),
                        "lines": [h.line for h in hs],
                        "snippets": [h.snippet for h in hs]}
    d = {
        "label": label, "score": c.score, "grade": grade(c.score),
        "words": c.words, "sentences": c.sentences, "paragraphs": c.paragraphs,
        "fk_grade": c.fk_grade, "avg_sentence": c.avg_sentence,
        "burstiness": c.burstiness, "longest_sentence": c.longest_sentence,
        "bold_leadin_density": c.bold_leadin_density,
        "penalties": c.penalties, "classes": classes,
    }
    if gate_result:
        d["gate"] = {"status": gate_result[0], "reasons": gate_result[1]}
    return d


def render(c: Census, label: str, gate_result: tuple[str, list[str]] | None,
           profile: str, show_lines: bool) -> str:
    out = [f"register-census: {label}  score {c.score} ({grade(c.score)})  "
           f"words {c.words}  grade {c.fk_grade}  avg sentence {c.avg_sentence}  "
           f"burstiness {c.burstiness}"]
    by = c.by_class()
    if not by:
        out.append("  no tells found")
    for cls, hs in sorted(by.items(),
                          key=lambda kv: (-GROUP_WEIGHT[kv[1][0].group], -len(kv[1]))):
        lines = ", ".join(f"L{h.line}" for h in hs[:8]) + (" ..." if len(hs) > 8 else "")
        out.append(f"  {hs[0].group:<10} {cls:<22} {len(hs):>3}   {lines}")
        if show_lines:
            for h in hs[:12]:
                out.append(f"      L{h.line}: {h.snippet}")
    top = top_classes(c, profile or "deliverable")
    if top:
        out.append("  fix first: " + ", ".join(f"{cls} ({n})" for cls, n in top))
    if gate_result:
        status, reasons = gate_result
        out.append(f"gate {profile}: {status.upper()}"
                   + (" - " + "; ".join(reasons) if reasons else ""))
    return "\n".join(out)


def _force_utf8() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _force_utf8()
    ap = argparse.ArgumentParser(
        description="Count the writing tells rules/writing-style.md names.")
    ap.add_argument("path", nargs="?", help="file to measure (.md .txt .html .docx)")
    ap.add_argument("--text", default=None, help="measure this text instead of a file")
    ap.add_argument("--format", default="md", choices=["md", "html"])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lines", action="store_true", help="print every hit with its snippet")
    ap.add_argument("--gate", default=None, choices=["deliverable", "content", "internal"],
                    help="apply a gate profile and exit 2 on FAIL")
    args = ap.parse_args(argv)

    label = args.path or "<text>"
    profile = args.gate or "deliverable"
    if args.text is not None:
        c = census_text(args.text, args.format, profile)
    elif args.path:
        p = Path(args.path)
        if not p.exists():
            print(f"register-census: no file at {p}", file=sys.stderr)
            return 1
        c = census_file(p, profile)
        if c is None:
            print(f"register-census: {p.name} SKIP - no text extractor for "
                  f"{p.suffix or 'this format'}")
            return 0
    else:
        c = census_text(sys.stdin.read(), args.format, profile)
        label = "<stdin>"

    g = gate(c, args.gate) if args.gate else None
    if args.json:
        print(json.dumps(to_dict(c, g, label), ensure_ascii=True))
    else:
        print(render(c, label, g, args.gate or "", args.lines))
    return 2 if (g and g[0] == "fail") else 0


if __name__ == "__main__":
    sys.exit(main())
