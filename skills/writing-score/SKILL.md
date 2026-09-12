---
name: writing-score
description: >
  Score your recent writing against rules/writing-style.md and show whether it is improving.
  Say "score my writing", "is my writing getting better", "writing scorecard", "check my
  register" (or run /founder-os:writing-score). Counts the tells, names the three to fix
  first, and reports the change since the last run. Read-only on your files.
why: "The writing rules were a page with nothing behind them - every judgment about whether a draft sounded like a person was an opinion, so the same tells came back every week and nobody could tell whether the writing was improving."
enhance: "Run it on one file first (python scripts/register_census.py <path> --lines) before running the whole scorecard - seeing the actual sentences flagged is what makes the class names mean anything."
allowed-tools: ["Read", "Glob", "Bash"]
mcp_requirements: []
---

# Writing score

Runs on: local-exec - the measurement is a Python script over your files. On a cloud or read-only surface, report that the scan did not run rather than estimating a score by reading.

Counts what `rules/writing-style.md` says and shows the trend. It never rewrites anything.

## What it measures

Eighteen classes, each one a rule on that page. The banned-word list is read off the page itself, so there is one list and it is the one you can read. No model call, no key, no network: this works on any plan.

The score starts at 100 and comes down by density per thousand words, so a long document is not marked down for being long. Three profiles, because a client deliverable and a note to yourself fail for different things:

| Profile | For | Fails below |
|---|---|---|
| `deliverable` | anything a client or reader receives | 80 |
| `content` | posts, captions, emails | 70 |
| `internal` | your own notes, brain files, plans | 60 |

## Procedure

1. **Check the script is there.** If `scripts/register_census.py` is missing, say so and stop:
   `The register census is not installed. Restarting Claude Code fixes this most of the time. If it happens again, say "update Founder OS".`

2. **Run the scorecard.**

   ```bash
   python scripts/writing_scorecard.py
   ```

   Default is the last 30 days of your own files. Engine folders (`skills/`, `scripts/`, `rules/`, `docs/`, `templates/`) are skipped: they are the product, not your writing. `--all` includes them, `--days N` widens the window, `--path <folder>` narrows it.

3. **Read the result back in plain words.** Lead with the mean score and the change since the last run. Then the three classes with the most hits, each with the rule it breaks and one real sentence from their own files. A class name on its own teaches nothing.

4. **Name one thing to do.** Not a list. The highest-count class, the file with the most instances, and the fix in one sentence.

5. **If a file failed its gate**, say which and why. A high score with a failed gate is normal and is not a contradiction: three classes are zero-tolerance on a deliverable because they never belong in something a client reads.

## One file at a time

The scorecard answers "is this improving". For one document before it goes out:

```bash
python scripts/register_census.py drafts/proposal.md --lines
python scripts/register_census.py drafts/proposal.md --gate deliverable
```

`--lines` prints every hit with the sentence around it, which is the form worth reading. The gate exits 2 on a fail, so it can sit in front of a send.

## When a hit is wrong

Some will be. A banned word can be the right word, and a settled judgment should not be raised again every week, because a gate that re-raises decisions you already made is a gate you learn to skip. Record it once in `rules/banned-words-exceptions.txt` with the date and the reason, scoped to the kind of file it applies to. The census reads that file and stops flagging it there.

If a whole class is wrong for how you write, that is a conversation about the rule, not about the file. The rule lives on one page and the script reads it. Change the page.

## What this cannot do

It counts tells. It cannot tell you whether what you wrote is true, whether it is kind, or whether it should be sent at all. `scripts/claims_check.py` covers the first. The reading pass covers the rest, and this exists to give that pass its attention back rather than to replace it.

## Output

One screen. The mean and the delta, the three classes to fix, the lowest-scoring files, one action. Written to `state/writing-scorecard.md`, with one line appended to `state/writing-scores.jsonl` so the next run has something to compare against.

No em dashes or en dashes in the report. Hyphens only.
