# context/entities/ - people, ventures and topics worth remembering properly

The home for someone or something you keep coming back to that is not a client and not a lead. A mentor, a partner, an advisor, a venture you are watching, a topic that keeps returning. Full convention in `rules/entity-folders.md`.

## Check here first

Most people already have a home, and a second home means two versions of the truth:

| The person or thing is | It lives in |
|---|---|
| Someone you are selling to | `context/leads.md` - stage lives there, never here |
| A paying or past client | `context/clients.md` plus `clients/<slug>/` |
| Someone in your circle | `network/inner-circle.md` |
| A business you own or run | `companies/<slug>/` |
| None of the above, and worth tracking | here |

## The shape

One file to start, `<slug>.md`:

```yaml
---
entity: <slug>
type: person | venture | topic | org
status: active | dormant | archived
reviewed: YYYY-MM-DD
---
```

Most stay a single file. When one outgrows it, `python scripts/entity_check.py` proposes a folder and you approve:

```
<slug>/
  profile.md    the current read only
  log.md        dated evidence, append-only
  sources/      their documents, never edited after filing
```

## The rules that do not relax

- **No pipeline stage.** That belongs to your leads and clients files.
- **Never invent.** A thin entity stays thin. A blank line is honest; a plausible-sounding fill is the dangerous kind of wrong, because it reads exactly like something you were told.
- **Unconfirmed stays unconfirmed** until you confirm it, folder or no folder.
- **The log is append-only.** A correction is a new dated block pointing back, never an edit to the old one.

Run `python scripts/entity_check.py` for promotions due, reviews overdue, and shape drift. It never writes.
