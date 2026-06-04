# Description tuning

Read this when you offer to tune a skill's description for better triggering accuracy.

The description field is the primary mechanism that determines whether the model invokes a skill. After creating or improving a skill, offer to tune the description for better triggering accuracy.

## Step 1: generate trigger eval queries

Create about 20 eval queries - a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

The queries must be realistic - the kind of thing a real user would type. Concrete and specific, with detail: file paths, personal context about the user's job or situation, column names and values, company names, URLs, a little backstory. Some in lowercase, some with abbreviations or typos or casual speech. Mix lengths. Focus on edge cases over clear-cut ones.

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. revenue is in column C and costs are in column D i think"`

For the **should-trigger** queries (8 to 10), aim for coverage. Different phrasings of the same intent, some formal, some casual. Include cases where the user does not name the skill or file type but clearly needs it. Throw in uncommon use cases and cases where this skill competes with another but should win.

For the **should-not-trigger** queries (8 to 10), the most valuable are the near-misses - queries that share keywords or concepts with the skill but actually need something different. Adjacent domains, ambiguous phrasing where a naive keyword match would trigger but should not. Do not make negatives obviously irrelevant. "Write a fibonacci function" as a negative for a PDF skill is too easy and tests nothing.

## Step 2: review with the user

Present the eval set to the user. They can edit queries, toggle should-trigger, and add or remove entries. This step matters - bad eval queries lead to bad descriptions.

## Step 3: run the tuning loop

Evaluate the current description by running each query a few times to get a reliable trigger rate, then propose an improved description based on what failed. Re-evaluate. Iterate a handful of times. Split the eval set so you select the winning description by held-out test score rather than train score, to avoid overfitting.

### How skill triggering works

Skills appear in the model's available-skills list with their name and description, and the model decides whether to consult a skill based on that description. The model only consults skills for tasks it cannot easily handle on its own. Simple one-step queries like "read this PDF" may not trigger a skill even with a perfect description, because the model handles them directly. Complex, multi-step, or specialized queries reliably trigger skills when the description matches. Make your eval queries substantive enough that the model would actually benefit from the skill.

## Step 4: apply the result

Take the winning description and update the skill's SKILL.md frontmatter. Show the user before and after, and report the scores.

## Step 5: description length check (mandatory)

Run the HARD CHECK from the top of the SKILL.md (at or under 900 PASS, 901 to 1024 WARN, over 1024 STOP). Tuning loops sometimes produce long descriptions that score well on triggering but exceed the install ceiling.
