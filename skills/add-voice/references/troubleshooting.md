# Voice troubleshooting

The three failures this layer is built to survive, and what to do about each.

## "The site can't be reached" / ERR_CONNECTION_REFUSED

The server is a plain local Python process. If you closed the terminal, rebooted, or it
crashed, it is simply not running - there is nothing to serve. This is not a bug.

Fix: start it again.

```
python voice/server.py
```

If you want it to survive a reboot, set up a scheduled task or a login item that runs that
command. That is an opt-in convenience, not wired by default (the OS does not install
always-on processes for you without asking).

## Answers get worse or error out after a long session

The most common cause is context bloat - loading too much into the model each turn. This
layer defends against it on purpose: the brain context is kept lean (a short preamble plus a
small slice of `core/identity.md`, never the whole repo). If answers still degrade over a
very long run, stop and restart the server to clear any process state:

```
# Ctrl+C in the server terminal, then
python voice/server.py
```

If you keep hitting errors, check `voice/runtime-log.jsonl` - every turn logs its route,
latency, and whether it was ok. A run of `"ok": false` lines points at the failing route.

## It hears me and saves, but never answers out loud

The conversational answer needs a reasoning CLI on your machine's PATH. Check it:

```
# open http://127.0.0.1:8765/health in the browser - "brain_available": false means
# the configured command is not on PATH.
```

Fixes:

- Confirm the CLI named in `voice/config.json` `brain_cmd` is installed and on PATH.
- If you run the OS through a different agent, set `brain_cmd` to that agent's headless form
  (see tiers.md) and confirm it answers a prompt from the terminal.
- Ears (speech in) and "Save last to brain" do not need the model and keep working
  regardless, so you are never fully stuck.

## My browser has no Talk button / it is greyed out

Firefox and Safari have no built-in speech recognition. The page falls back to a text box so
the loop still works (type your turn, hear the answer). For spoken input use Chrome or Edge,
or add the faster-whisper upgrade (tiers.md) which captures audio in any browser.

## Is my audio leaving my machine?

In Chrome and Edge, the built-in speech recognition sends your audio to the browser vendor to
transcribe it. No key, no cost, but not local. The banner on the page says so. For fully
local speech, add the faster-whisper upgrade. Your brain - your files and the answers - is on
your disk in every tier.
