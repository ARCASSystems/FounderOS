# FounderOS - Avatar and Dream Outcomes

Who we are building this for, and what we want them to be able to do.

## Avatar

**Name:** The solo founder (or near-solo founder).

**Stage:** They run one to three businesses, often as the only full-time operator. They may have a small team or contractors but every meaningful decision routes through them. They are post-idea, post-MVP, in the messy middle where revenue exists but the operating layer is held together by their own attention.

**Pain right now:**
- Every Monday they wake up unsure what the priority is. Last week's commitments have aged. New asks have piled up. The pipeline is somewhere in their head and partly in three different tools.
- They are doing all the roles - sales, operations, marketing, finance, product - and the OS in their head has become the bottleneck. When they take a day off, things fall through.
- They have tried Notion templates, Asana setups, founder dashboards. Each one solved a slice and added a new tool to maintain. None of them remembered context across sessions.
- They are "AI-curious" but skeptical. They have seen too many demos that work in a controlled prompt and break in real workflow.

**What they pay for today:** Their AI subscription (typically Claude Pro $20 or Claude Max $200), maybe Notion ($10), maybe a CRM. They are budget-aware. Every new tool needs to earn its place.

**What they want:** A system that holds context for them. Knows their priorities, their open commitments, who is waiting on what. Surfaces stalls before they compound. Routes the right work to the right role. Operates in their voice. And does not require them to migrate everything they already have into a new tool.

## Three dream outcomes

### 1. "Monday morning, the brief tells me what is stalling and forces a decision."

The founder opens Claude Code on Monday. The session-start brief surfaces flags that have been open for 2+ weeks, decisions that are blocking new work, and clients that have aged without contact. Each item gets a kill / keep / escalate prompt. The founder makes the calls in 15 minutes. The week has direction before the inbox is touched.

### 2. "Every meeting captures into client context. Friday I see all commitments I made this week."

A meeting happens (call, coffee, video). The founder runs the capture skill, drops the transcript or a brain dump, and the OS routes the right pieces to the right places: client context updated, commitments logged, decisions parked, follow-up emails drafted but not sent. By Friday, the weekly retro shows every commitment made and every one not yet honored. Nothing dies in their head.

### 3. "Outbound runs without me writing each message. I review and approve a batch of 10 in 5 minutes."

Cold outreach drafts are generated based on the founder's actual voice (extracted from past posts, past emails, past conversations). They land in a queue. The founder reviews 10 at a time, approves or edits, and sends. The system tracks who responded, who did not, who needs a follow-up, who should be dropped. The founder is the approver, not the writer.

## What we are explicitly solving for

- **Context loss between sessions.** The OS reads the same files at boot every time. Nothing decays just because a session ended.
- **Stall detection.** Flags age. The OS escalates them weekly. The founder does not have to remember to remember.
- **Multi-business reality.** Most "founder tools" assume one company. FounderOS handles a founder who runs three.
- **Voice consistency.** Posts, emails, drafts, replies - all checked against the founder's actual voice, not a generic AI tone.
- **The compulsive free-value trap.** Pre-meeting and pre-send gates so the founder cannot accidentally give away $5K of consulting in a "quick coffee."

## What we are NOT trying to be

- A CRM. The OS coordinates context; a CRM manages pipeline at scale. FounderOS works for the messy-middle stage where the pipeline is small enough to live in markdown.
- A team management tool. FounderOS is for one operator. AgentOS handles team scenarios.
- An autopilot. The founder approves every customer-facing action. The OS speeds the work; it does not replace the judgment.

## How this connects to the other repos

- **PersonalOS** is upstream of this. Career and skill context that the founder built before starting their company stays in PersonalOS and FounderOS reads from it.
- **AgentOS** is what this is built on. FounderOS is a curated migration from AgentOS, packaged for the solo-founder use case. If the founder grows past one operator, they graduate to a custom AgentOS deployment.
- **Future Enterprise OS** is where this leads if the founder hires a team. FounderOS becomes Layer 1 (the founder's personal OS) and a Company OS gets layered on top.
