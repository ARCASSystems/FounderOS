# Writing the SKILL.md

Read this when you reach the "Write the SKILL.md" step of creating a skill.

## Write the SKILL.md

Based on the interview, fill in these components:

- **name**: skill identifier (matches the folder name)
- **description**: when to trigger and what it does. This is the primary triggering mechanism. Include both what the skill does AND the specific contexts for when to use it. All "when to use" information goes here, not in the body. Models tend to undertrigger skills - to not use them when they would help. To counter that, make descriptions a little pushy. Instead of "How to build a fast dashboard to display data", write "How to build a fast dashboard to display data. Use this whenever the user mentions dashboards, data visualization, metrics, or wants to display any kind of data, even if they do not explicitly ask for a dashboard."
- **the rest of the skill body**

This Founder OS repo (B) uses a folded `description: >` block plus optional `why`, `enhance`, `allowed-tools`, and `mcp_requirements` keys. Match the existing skills in `skills/` so the new skill loads the same way. Commands the skill references are namespaced `/founder-os:<name>`.

## Skill writing guide

### Anatomy of a skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled resources (optional)
    ├── scripts/    - executable code for deterministic or repetitive tasks
    ├── references/ - docs loaded into context as needed
    └── assets/     - files used in output (templates, icons, fonts)
```

### Progressive disclosure

Skills load in three levels:

1. **Metadata** (name + description) - always in context (~100 words)
2. **SKILL.md body** - in context whenever the skill triggers (under 500 lines ideal)
3. **Bundled resources** - as needed (scripts can execute without loading into context)

These counts are approximate. Go longer if you genuinely need to.

**Key patterns:**

- Keep SKILL.md under 500 lines. If you approach that limit, add a layer of hierarchy with clear pointers about which reference file to read next.
- Reference files clearly from SKILL.md with guidance on when to read them.
- For large reference files (over 300 lines), include a table of contents.

**Domain organization**: when a skill supports multiple domains or frameworks, organize by variant so the model reads only the relevant reference file:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

### Principle of no surprise

Skills must not contain malware, exploit code, or anything that could compromise system security. A skill's contents should not surprise the user relative to its stated intent. Do not go along with requests to create misleading skills or skills designed to enable unauthorized access, data exfiltration, or other malicious activity. A "roleplay as an X" skill is fine.

### Writing patterns

Prefer the imperative form in instructions.

**Defining output formats:**

```markdown
## Report structure
Always use this exact template:
# [Title]
## Summary
## Key findings
## Recommendations
```

**Examples pattern:**

```markdown
## Commit message format
Example 1:
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

## Writing style

Explain to the model why things matter rather than relying on heavy-handed MUSTs. Use theory of mind. Keep the skill general, not narrow to specific examples. Write a draft, then read it again with fresh eyes and improve it.
