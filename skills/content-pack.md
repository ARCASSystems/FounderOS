# Content Pack

A logical pack, not a folder. Claude Code discovers skills as top-level directories under `skills/`, so the pack is held together by convention and by the links in this manifest rather than by nesting. The members do not share a name prefix; this manifest reads them as one connected unit.

This is the marketing function for a founder who is also their own content team. It covers the path from one idea to a week of presence across channels, all in the founder's own voice.

## The front door

[content-start](content-start/SKILL.md) is the entry. Say "turn this idea into content" or "help me with content". It checks whether the OS holds your voice, gives one honest disclaimer, and routes you to the outcome you want. You bring the idea; it makes sure the output sounds like you and aims it at the right channel.

## What the pack is

You bring one idea: a lesson, a story, an opinion, a customer message. The pack turns it into the format you actually need: a single post, the same idea across every channel, a sequenced campaign, or a reply to something incoming. Everything runs locally and free. The OS drafts in your voice; it never publishes, never schedules, and never invents engagement numbers. Publishing stays your hand on the button.

## The outcomes and the skills behind them

| Outcome | Skill | Status |
| --- | --- | --- |
| Front door (idea to format) | [content-start](content-start/SKILL.md) | Ready |
| A single post in your voice | [linkedin-post](linkedin-post/SKILL.md) | Ready |
| One idea across every channel | [content-repurposer](content-repurposer/SKILL.md) | Ready |
| A sequenced, funnel-gated campaign | [campaign-from-theme](campaign-from-theme/SKILL.md) | Ready |
| A reply to an incoming review or message | [review-responder](review-responder/SKILL.md) | Ready |
| Capture your personal writing voice | [voice-interview](voice-interview/SKILL.md) | Ready |
| Capture a brand's voice | [brand-voice-interview](brand-voice-interview/SKILL.md) | Ready |

## The shared reference

The pack's shared reference is your voice. [your-voice](your-voice/SKILL.md) holds the tone rules and anti-AI baseline that every writing member applies internally, reading `core/voice-profile.yml` (personal) or `brands/<slug>/voice.yml` (a brand). The skills cite it; they do not restate the rules inline and drift. This is why the content reads consistently across channels instead of each post sounding different.

## Honest about the limits

The OS drafts from your ideas in your voice. It does not auto-publish, schedule, run analytics on what performed, or report engagement it cannot see. Without a voice profile the drafts read clean but generic, and the pack says so rather than shipping a fabricated voice. Its strength is turning one idea into channel-ready drafts that sound like you; the publishing, the timing, and the reading of results stay with you.

## Dependencies between members

- Every writing member reads a voice profile; `voice-interview` (personal) or `brand-voice-interview` (per brand) sets it. The front door sets it up first if it is missing rather than shipping the wrong voice.
- `campaign-from-theme` gates on five funnel questions (speaker, objective, audience, channels, success metric) before it drafts; it will not produce until they are answered, by design.
- `review-responder` asks whose voice to use (operator or brand) before drafting a reply.
