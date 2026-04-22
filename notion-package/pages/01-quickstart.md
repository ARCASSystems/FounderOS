# Quickstart

Five minutes if you already have Notion and a paid Claude plan. Ten if you need to set one of them up.

You'll need:

1. A Notion account (free plan works)
2. A Claude Pro or Max subscription (the Claude Project feature is on Pro and Max)
3. A voice-to-text tool you like (Wispr Flow is what this was built around, but any will do)

No developer tools. No API keys. No terminal.

---

## Step 1. Duplicate the Notion template

Open the public Founder OS template page. Click **Duplicate** in the top right. Pick your own workspace as the destination.

You'll now have a copy inside your Notion. Nobody else can see it. Your data, your workspace.

The duplicate brings six databases with it: Profiles, Decisions, Priorities, Clients, Brain Log, Flags. Plus a landing page with everything wired together.

---

## Step 2. Create a Claude Project

In the Claude web app (claude.ai), go to **Projects** in the left sidebar. Click **New Project**. Name it "Founder OS."

Projects are where Claude holds persistent context for one specific job. Think of this Project as your operating system's brain.

---

## Step 3. Paste the system prompt

Inside your new Project, find the **Custom instructions** or **Project instructions** field.

Open the file `system-prompts/paperclip-project-prompt.md` from this package. Copy the whole thing. Paste it into your Project instructions. Save.

This is what tells Claude how to route your voice notes into the right Notion database.

---

## Step 4. Connect Notion

Claude needs permission to read and write your Notion pages. You've got two options.

**Option A. Claude Project with Notion connector.** Inside your Project, look for the Notion integration. Sign in to Notion when prompted. Grant access to the workspace where you duplicated the template. Done.

**Option B. Claude app with Notion MCP.** If you run the Claude desktop app, open settings, add the Notion MCP, sign in. Same result.

Both paths work. Option A is smoother if you're new to MCP. Option B is for founders already running Claude as their daily driver app.

---

## Step 5. Tell Claude who you are

In the Project, send this first message:

> I just installed Founder OS. Walk me through setting up my identity file. Keep it short. Ask me one question at a time.

Claude will ask you five or six questions. Who you are. What you run. How many people. What's on your plate this week. It writes your identity page in Notion as you answer.

That's setup done. You're live.

---

## Step 6. Route your first voice note

Open Wispr Flow (or whatever voice tool you use). Talk for two or three minutes. A call you just finished. A decision you're wrestling with. Whatever happened in your day that matters.

Paste the transcript into Claude.

Say:

> Route this.

Claude reads it, pulls out the signals (decisions, commitments, people, pipeline moves), and proposes what should go where. You'll see a table of proposed writes. Reply **yes** or **no** per row. Or just say **all yes** and move on.

Claude writes the approved rows into your Notion. Check the databases. The entries are there.

That's the loop. You speak. Claude routes. You approve. Your operating system updates.

---

## If something breaks

- **Notion doesn't connect.** Check that you signed into the right workspace. The one where you duplicated the template.
- **Claude doesn't see your databases.** In the Project, confirm the Notion integration shows the workspace name. If not, disconnect and reconnect.
- **Claude writes to the wrong place.** Tell it. "That decision should have gone to Priorities, not Decisions." It'll update the routing map.
- **You're on the free Claude plan.** Projects require Pro or Max. The Claude app with Notion MCP works on free but routing quality drops fast. Upgrade if you're using this daily.

---

## What to read next

- `02-your-first-route.md`. Worked example with a real transcript.
- `03-the-two-drivers.md`. Why Claude plus Wispr Flow changes how founders work.
- `05-what-youll-not-find.md`. Honest limits. What this doesn't do yet.

If you want the power-user terminal version (local markdown, git history, hooks, custom skills), the waitlist is at github.com/ARCASSystems/FounderOS.
