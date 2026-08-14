# The security baseline - what leaves your machine, and the guards already at the door

One page. Read it once when you install, and again any time you are about to say yes to something new - a connector, a voice tier, a plugin pack, an MCP server. Everything on this page describes what is already built and running in this repo, and it was checked line by line against the code in an outside review. Nothing here is a promise about a future version.

## The short version

Your files live on your disk as plain markdown. In its default text mode the OS starts no listener and stores no service key, phones home to nobody, and keeps no telemetry. ARCAS receives nothing. Optional tiers change that locally and say so before you commit: Tier 0 voice serves its page on 127.0.0.1:8765, Tier 1 realtime listens on 127.0.0.1:8756 and 8757, and Tier 1 and Tier 2 store their service keys in the gitignored `.env`. What leaves the machine leaves through the named surfaces below - the model itself (the one constant of using a hosted model) plus surfaces you switched on with an explicit yes.

## What leaves the machine, surface by surface

| Surface | What leaves | When | On by default? |
|---|---|---|---|
| A Claude Code session | The files the session reads, and what you type | Every session - this is how a hosted model works | Yes - the one constant. Files you never bring into a session are never sent. Anthropic's plan terms govern it; ARCAS receives nothing. |
| A cloud session (claude.ai/code) | Same as above, but the session runs in a remote sandbox on a branch | Only when you start one from the app | No - local is the default |
| Voice, Tier 0 (browser) | Your speech audio goes to the browser's built-in speech service; a local page is served on 127.0.0.1:8765 | While you talk | No - voice is opt-in. The 0-local tier (faster-whisper) keeps speech on the machine entirely. |
| Voice, Tier 1 (realtime) | Audio streams to Google, and every sentence the voice speaks was sent to Google first - including answers read out of your files. The file stays home; the sentence does not. Local bridge on 127.0.0.1:8756 and 8757; key in `.env`. | While the realtime front is open | No - opt-in, and the trade is stated before you commit |
| Voice, Tier 2 (premium mouth) | The text being spoken goes to ElevenLabs; key in `.env` | When the paid mouth is on | No - opt-in, paid |
| The scrape helper | A robots.txt HEAD (and GET if needed), then the page GET - retried up to three times. With `--render`, the page's own subresources load too. | Only when you ask for a page | No - fires on your ask, never on its own |
| Web fetch and search inside skills | The URL you asked to ingest (WebFetch), or a search query when a skill refreshes a live source (legal-compliance names when) | Only on your ask, and the skill says what it is fetching | No - nothing browses on its own |
| GitHub operations (`github-ops`) | Issue, PR, branch, release, and workflow data to and from GitHub through the `gh` CLI you authenticated | When you ask for a GitHub action | No - needs your own `gh auth login` first |
| Connectors (Telegram bot) | The messages you send through it | When a send happens | No - each connector is set up on its own explicit yes |
| git push | Everything the repo tracks, to the remote you push to | Only when you say push | No - nothing pushes anywhere unless you ask |

Those are the shipped surfaces as of this version. A capability you add later - a connector, an MCP server, a plugin pack - brings its own surface with it, which is exactly what the five questions at the bottom of this page are for. A seat inside the OS has no send surface of its own: its generated agent file keys the no-external-calls rule to the row's own `never` field, so nothing leaves by a seat's hand unless its charter names a connector explicitly.

## Connectors and MCP servers - who can see what

A connector or MCP server is someone else's code with a key to some of your accounts. Plain rules:

- **What it can see is decided by the server, not by you.** A calendar MCP sees your calendar. An email MCP sees your mail. Read the access screen at connect time as if it were a door key, because it is.
- **Three trust classes, in falling order.** Shipped in this repo (markdown and stdlib Python you can read before it runs). Official vendor connectors (their code, their terms - the OS only guides setup and stores nothing for the account-level ones). Community third-party servers (out of this repo's security scope entirely - report issues to their authors, and think twice before connecting one to real accounts).
- **Nothing is installed silently, as a rule the assistant follows.** Any capability from outside the OS is proposed with its exact source and its own passport, one yes each - that rule is written into the `hire` skill. Be clear about what kind of protection this is: it is an instruction the assistant follows, not a mechanical gate that could stop a rogue install. The mechanical gates are the ones in the guard chain below, which is why they exist.

## Where secrets live

- **Secrets go into gitignored files only, enforced by code.** `python scripts/connect.py set-secret` refuses any target that is not on its allowlist - `.env` for service keys, `.mcp.local.json` for MCP-local secrets, both gitignored - so a token cannot land in a tracked file through that path. It never echoes a secret value back to the screen. On a machine with no version history the proof is the shipped ignore list read directly, matched line for line, because there is no git to ask.
- **The target must be one file, with one name.** Three shapes are refused outright: anything carrying folder parts, anything off the allowlist, and - since v1.54.1 - a file that is a second name for another file on disk. That last one is the awkward case: a hard link is not a path pointing elsewhere, it is the same file object under two names, so it resolves inside your OS folder and satisfies every containment check ever written while the write also lands in whatever else carries that name. An outside review found it; it is now refused before anything is written.
- **The always-on secret scanner** rejects commits whose staged lines carry token-shaped strings (API keys, bot tokens, PEM private-key headers, high-entropy assignments). It runs even when every other check is unconfigured, and it never prints the matched value - including when the same line carries a second violation.
- **No model key on disk by default.** Your Claude subscription sign-in replaces stored key files. The only keys that ever exist are ones you added for optional tiers, and they live in `.env`.

## The guard chain already running - a rejection layer, not a proof

Honest framing first: local hooks run when they are installed and Python works, `--no-verify` skips them, and CI re-checks only after a push has already reached the remote. So this chain rejects mistakes loudly and early; it is not proof that a mistake can never land. That is the strongest true claim, and it is still worth having:

1. **The privacy guardian** (`scripts/check-private-names.py`) runs at commit time and again in CI: the secret scanner (always on), private names from your own gitignored patterns file (never shipped, never leaves), em/en dash and AI-attribution checks, and a line-ending gate.
2. **The remote-safety flip** refuses any commit while your identity file is tracked AND a git remote can still push to the public FounderOS repository - that repository specifically, not everything by the same owner. The fix it prints keeps updates flowing in and blocks anything going out. "Own my history" wires this for you.
3. **The charter audit** (`python scripts/employee_verdict.py charters`) treats a seat's charter as its permission grant: a blanket tool grant is flagged, and `hire` runs the audit as an explicit step of every hire, findings shown, not swallowed.
4. **The file-ownership rules in the agent generator** (`scripts/agents_sync.py`): seat ids are validated so they cannot become paths outside `.claude/agents/`, and a generated file you edited is detected by digest and never overwritten or deleted.
5. **The gitignored-only secret writer** (`scripts/connect.py set-secret`) - the mechanical half of the secrets rule above.
6. **The three doors, in default mode.** 2026's defining agent-security incident needed an exposed listening server, a stored key file, and a third-party skill registry. Default text mode has none of the three; the optional voice tiers open local listeners on 127.0.0.1 and store their own keys in `.env`, as the table above says per tier. The full record with sources and the honest limits: `docs/why-local-first.md`.

## The five questions to ask before any yes

The `hire` skill prints these as a passport on every proposal. Ask them yourself of anything that wants in from outside, no matter who built it:

1. What may it touch?
2. What does it never do?
3. What does it cost to run?
4. What leaves my machine, named by name?
5. How do I turn it off or fire it?

A yes without those five answers is not consent, it is hope.

## What this page is not

- Not a vulnerability policy. Found a security bug in this repo? That is `SECURITY.md` - how to reach us and what happens next.
- Not a claim that using a hosted model is risk-free. The honest version: your files stay on your disk, what you bring into a session goes to Anthropic under your plan terms, and each optional surface above has its own named recipient. The limits are written down in `docs/why-local-first.md`, not rounded up to a slogan.
