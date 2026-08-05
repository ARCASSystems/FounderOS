# Working preferences

How you want this OS to work with you. Not what you know, not what you decided about your business - how you want to be worked with.

This file is read **before** output, the same way `core/voice-profile.yml` is read before any writing. That is the whole difference between this and a memory. A memory is something a model might recall after you complain. This is a file that gates the answer before you see it, and you can open it, argue with it, and delete a line you no longer mean.

**It ships empty on purpose.** It fills as you work, one correction at a time. A file full of guesses about how you like to be worked with is worse than an empty one, because you would spend your first week deleting somebody else's assumptions.

---

## Active

Read before producing output. Every row here has your yes behind it.

| Preference | Applies to | Since | Evidence |
|---|---|---|---|

---

## Proposed

Candidates waiting on your yes. **Nothing here is read as a gate.** The session brief counts these rows, the morning loop asks about them, and one word from you moves a row up to Active or deletes it.

| Preference | Applies to | Since | Evidence |
|---|---|---|---|

---

## What belongs in here

Six things worth a row, drawn from what people actually correct:

- **Decide for me, or give me options.** With the line: which calls do you always want to make yourself?
- **Show me, or just do it.** How much working out you want to see before the answer.
- **What you never want asked twice.** The question that has a permanent answer.
- **The shape of a normal answer.** Length, and whether it opens with the answer or the reasoning.
- **What "done" means to you.** The proof you want attached before anything is called finished.
- **Standing vetoes.** Something the OS proposed once and got told off for.

What does NOT belong here: facts about your business (those go to `context/`), how you write (that is `core/voice-profile.yml`), and decisions with a date and a trigger (those are `context/decisions.md`). This file is only about the working relationship.

---

## The rules

- **No line without a source.** Every row carries the date and the thing you actually said. A preference with no evidence is somebody's guess about you, and guesses are what this file exists to replace.
- **Nothing lands Active without your yes.** Sessions may propose. Only you promote. A behaviour layer written behind your back is the one thing you would not forgive, and it would be trivially easy to build that by accident.
- **Applies to is narrow by default.** "Answers about the pipeline" beats "everything", because a preference stated once in one context and then applied everywhere is how an OS becomes annoying. Widen a row later if it turns out to hold everywhere.
- **A row that stops being true gets deleted, not argued with.** This is your file. Six months of stale preferences is worse than none.
- **The same correction should never be needed twice.** That is the test. If you find yourself saying "I told you, just pick one" a second time, the loop is broken - either the row was never written or nothing is reading it. Say so; that is a bug in the OS, not in you.

## How rows get here

Three doors, all of them ending in your yes:

1. **You say it.** "From now on", "I prefer", "never ask me again" - the capture hook spots the shape and proposes a row.
2. **You correct the OS.** "Too long", "you asked me that already", "just pick one". A correction of the OS's manner is the most honest source there is, because you were not trying to configure anything.
3. **`/dream` finds it in a rant.** Preference is one of the five things a rant gets classified as. It proposes a row here rather than filing the observation somewhere nothing reads.
