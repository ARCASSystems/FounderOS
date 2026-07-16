# Setup - Phases 3 to 5: Companies, First Project, Remaining Projects

Load this when the Founder OS root is built. It creates company folders, builds the first project as the reference project, skeletons the rest, writes `stack.json`, and verifies context isolation. Return to the router (`SKILL.md`) for the phase order.

---

## PHASE 3: COMPANY FOLDERS

For each business from Phase 0:

### 3.1 Create Company Folder
Ask where they keep their project folders. A founder with no project-folder habit (paper notebook, everything in email) gets the default: create the company folder inside the OS root. Name the trade-off out loud in one line - projects inside the OS root share the root CLAUDE.md context in every session; they can be moved out later without losing anything.

### 3.2 Company CLAUDE.md
Read `templates/company-claude-md.md` for structure. Personalize with:
- Business name and description
- Key people from 0.2
- Active projects (will be filled in Phase 4)
- Business-specific rules or constraints

Under 60 lines. Show draft. Get approval. Write it.

### 3.2.5 Company business-context file (recommended)

Copy `templates/business-context.template.md` to `companies/<slug>-business.md` (where `<slug>` is the company folder name from 3.1). This is your business, not a prospect - the operator template captures ICP, pricing, offer structure for the company you run. Prospect records (companies you sell to or watch) are created on-demand via the `prospect-init` flow and land at `companies/prospects/<slug>.md`; the wizard does not pre-create those.

Replace `{{COMPANY_NAME}}` on the **Company name** line with the company name captured in Phase 0.1. Leave every `[FILL]` marker intact - the `business-context-loader` skill walks them on first run with the founder. The universal placeholder pass (Phase 2.2) will not see this file because it runs Phase 2 only; if any other `{{...}}` placeholder lands here later, replace it with `[NOT SET]`.

This file is the input that `business-context-loader`, `proposal-writer`, `client-update`, and `strategic-analysis` read for ICP, pricing tier, positioning, and offer structure. Without it those skills produce generic output. The wizard surfaces it once; the founder fills it the first time they need a company-specific deliverable.

If the founder skips it, log a backlog item: `- [ ] Fill companies/<slug>-business.md before next proposal or strategic analysis`. Also log: `- [ ] Use prospect-init when you start tracking your first prospect company (creates companies/prospects/<slug>.md)`.

### 3.3 Company .mcp.json
Based on tool stack from 0.5, create a `.mcp.json` with only the MCPs this business needs.

There is no stack-token-to-MCP-server mapping shipped, and most MCPs need their own auth setup the wizard must not start - so the faithful default is an empty config: `{"mcpServers": {}}`. Write that, tell the founder plainly ("your tools are noted; connecting them is a later, optional step - say 'connect gmail' when you want it"), and log a backlog item naming the tools captured in 0.5. Never invent server entries.

Show proposed config. Get approval. Write it.

---

## PHASE 4: FIRST PROJECT

Take the top priority from 0.4. Build it properly as the reference project.

### 4.1 Create Project Folder
Inside the correct company folder. Choose the right template based on project type:

- **Email/Campaigns**: templates/, active/, data/, archive/
- **Website**: src/, content/, assets/, reference/
- **Lead Pipeline**: prospects/, outreach/, templates/
- **Data/Dashboards**: exports/, reports/, queries/
- **General**: docs/

### 4.2 Project CLAUDE.md
Read `templates/project-claude-md.md` for structure. Under 40 lines. Include:
- What this project does
- Current task
- Tools used
- Project-specific rules

### 4.3 Project .mcp.json
Subset of company MCPs relevant to this project.

### 4.4 Live Test
Ask: "Do you have a real task in this project we can try right now - even a small one? A draft, a note, a decision to log?"

If they have something, execute it. Confirm only project context loaded, MCPs work, output quality is good.

If they don't have a task yet (no active clients, pre-revenue, just starting), skip the live test. Tell them: "You can run `/founder-os:status` anytime to check readiness, and test a real task once one comes up."

---

## PHASE 5: REMAINING PROJECTS + CROSS-REFERENCES

### 5.0 Write Tool Stack to stack.json

Take the tool-stack answers captured in Phase 0.5 (knowledge base, email, calendar, automation, CRM, file storage, meeting notes, voice input, server, prospecting DB, video tool, booking, primary channel) plus the business model confirmed in Phase 0.2.7, and write them to `stack.json` at the Founder OS root.

Steps:
1. Read the existing `stack.json`. Preserve the `_description`, `_wizard_version`, `_allowed_values`, and `_notes` fields.
2. Set `_generated` to today's date in `YYYY-MM-DD` format.
3. For each field the user answered in 0.5, set the value to the exact lowercase token from `_allowed_values` (e.g. `notion`, `gmail`, `google_calendar`, `n8n`). If the user named a tool not in `_allowed_values`, ask them to pick the closest match or set the value to `null` and log the actual tool name in the backlog.
4. Set `business_model` to the token confirmed in Phase 0.2.7 (`service` / `ecommerce` / `saas_software` / `marketplace` / `content_creator` / `regulated_deep_tech` / `other`). Write `null` ONLY when 0.2.7 was skipped or left unresolved. The token was captured for exactly this write - leaving it `null` when a confirmed answer exists means `unit-economics` starts every number conversation in the wrong frame.
5. For fields the user did not answer, leave the value as `null`.
6. Validate the file is parseable JSON before writing. If parse fails, stop and surface the error.
7. Confirm to the user: "Wrote your tool stack to `stack.json`. Skills that adapt to your tools now read from here."

### 5.1 Skeleton Projects
For each remaining workstream from 0.3 that wasn't built in Phase 4:
- Create the folder with a stub CLAUDE.md and .mcp.json
- Don't spend time on full setup - just the skeleton

### 5.2 Update Company Files
Go back to each company CLAUDE.md and update the "Active Projects" section.

### 5.3 Verify Isolation
Open two different project folders (ideally different businesses). Confirm:
- No context from Business A appears in Business B
- MCPs are scoped correctly
- Global identity is accessible when needed but not pre-loaded

On an in-place install (projects inside the OS root - the ZIP default), the third point holds only partially: Claude Code's CLAUDE.md cascade loads the root bootloader in every nested project. That is a known trade-off of the in-place layout, not a broken install - check the first two points, note the third as expected-partial, and do not chase it.
