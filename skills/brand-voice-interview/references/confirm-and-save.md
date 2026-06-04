# Phase 4 - Confirm and save

Load this when you reach Phase 4.

Show this block (filled with captured values from BOTH positioning and voice):

> Part 3 of 3 - Confirm and save.
>
> Here is what I captured for `<display_name>`. Confirm or correct any line.
>
> **Positioning**
> - Slug: <slug>
> - Offer: <one-line>
> - Price band: <range>
> - Delivery: <model>
> - Primary segment: <one-line>
> - Promise: <one-line>
> - Proof points: <count> captured
> - Refuses to promise: <count> captured
> - Direct competitors: <count> captured
> - Off-limits channels: <list>
> - Archetype: <value or inferred-from-samples>
>
> **Voice**
> - Speaker: <value>
> - Register: <value>
> - Rhythm: <value>
> - Opening: <value>
> - Closing: <value>
> - Sign-off: <value or "no sign-off">
> - Person: <value>
> - Contractions: <value>
> - Preferred words: <list>
> - Banned words: <list>
> - Idiosyncrasies: <list>
> - Buyer first sentence: <value>
> - Buyer phrases: <list>
> - Anti-example pairs: <count>
> - Samples: <count>
>
> Looks right? (yes / change X)

If yes, write both files. If they want to change something, edit and re-confirm.

## File output

Write `brands/<slug>/voice.yml` using the structure from `templates/brand-voice.yml.template`. Replace every `[BRACKETED]` placeholder with the captured value or `[NOT SET]` if skipped.

Write `brands/<slug>/positioning.yml` using the structure from `templates/brand-positioning.yml.template`.

If `archetype` was inferred from samples (user skipped), pick the closest match from the samples and write it with a `# inferred` comment on the line.

Do not invent values. Empty lists are `[]`. Skipped string fields are `"[NOT SET]"`.
