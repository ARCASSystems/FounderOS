# Seat to workflow map

The bridge between the two ways you will talk about your own OS. You think in roles ("the pipeline side of things has gone quiet"). The machine runs workflows (a specific chain of steps over specific files). This table is the one place those two vocabularies meet.

**Ships empty on purpose.** Fill in a row when a workflow actually exists and runs. A map full of workflows you intend to build is a wish list, and it will quietly stop matching reality within a month.

## How to fill it in

One row per workflow that genuinely recurs. Two columns for the stages, and that split is the whole point of the table:

- **Deterministic stages** are the ones with exactly one right answer: counting, filing, rendering, moving something from one state to another. These belong in code and should never be handed to a model. They cost nothing to run, they run the same way every time, and their failures are loud.
- **Judgment stages** are the ones needing a call: what to say, whether this is worth doing, who someone actually is, whether the output is any good. These need the model, and each one needs a named check on its output before anything acts on it.

Writing a workflow down in two columns tells you something useful before you build any of it. A workflow that is entirely judgment is expensive and will vary between runs. A workflow that is entirely deterministic does not need a model at all. Most real ones are a deterministic spine with one or two judgment stages, and knowing which is which is what keeps them cheap and honest.

| Role | Workflow | Runs when | Deterministic stages (code) | Judgment stages (model, each with a check) | Writes to |
|---|---|---|---|---|---|
| | | | | | |

## Reading the table later

- **A row with no "runs when"** is not a workflow, it is an idea. Move it out.
- **A judgment stage with no check** is the row to fix first. It means something acts on an unverified call.
- **Two rows writing to the same file** is worth a second look. One file, one writer, or they will overwrite each other and you will not see it happen.
- **A role with no rows** is honest. It means you cover that function by hand, which is a fine answer and better than a workflow that exists only on this page.

## Cross-reference

- `roles/index.md` - what each role is for and when it takes over
- `rules/digital-employees.md` - when a recurring workflow earns a named job, a measure, and a review
- `rules/context-discipline.md` - why the deterministic column belongs in code
