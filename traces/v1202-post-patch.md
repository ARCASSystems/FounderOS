# FounderOS v1.20.2 post-patch trace

- Trace date: 2026-05-10
- Fresh install root: C:\arcas_dev\test-installs\founderos-v1202-trace-post
- Product state traced: post-patch v1.20.2 working tree
- Persona: Sara Karim, founder of Northline Studio, a 5-person Dubai design studio selling brand, web, and campaign work to UAE SMEs. Eight years in, no marketing hire.

## New and changed intake answers

### Setup 0.2.5 Positioning

Question: Who do you sell to in one sentence? You can say skip.

Sara: UAE small business owners with no in-house marketing hire.

Question: What do you sell in one sentence? You can say skip.

Sara: Brand, web, and campaign design projects that make the business easier to trust.

Question: What visible pain does your buyer feel before they come to you? You can say skip.

Sara: They look smaller than they are, and the current website or deck makes the offer feel unclear.

### Voice buyer-language questions

Question: When your buyer describes their problem to you, what is the first sentence out of their mouth?

Sara: We look smaller than we are.

Question: What is a phrase your buyer says that makes you nod every time? One to three phrases is enough.

Sara: People do not get what we do. The site does not match the business anymore. We need someone who can make it clear without making it loud.

### Brand visual proof question

Question: Do you have any existing visual proof I should look at later - a deck, website, logo folder, proposal, or style guide? If yes, where is it? If no, say no.

Sara: Old client deck in Google Drive, the current website, and a text logo folder. Use them as references, not as final brand rules.

## Key artifacts

### core\identity.md

~~~text
# core/identity.md

> Who the founder is and how they work. This file is the source of truth for all role behavior.
> Update it when something meaningfully changes about how they operate.

---

## Basics

**Name:** Sara Karim
**Role:** Founder / Creative director
**Location:** Dubai, UAE
**Team size:** 5 people
**Time zone:** Asia/Dubai

---

## Background

Sara runs Northline Studio, a Dubai design studio for UAE small businesses that need brand, web, and campaign design without hiring an internal marketing team. She is 8 years into the business and still leads sales, creative direction, and client delivery.

---

## Positioning

**Sells to:** UAE small business owners with no in-house marketing hire.
**Sells:** Brand, web, and campaign design projects that make the business easier to trust.
**Buyer pain:** They look smaller than they are, and the current website or deck makes the offer feel unclear.

---

## How They Work

**Work style:** sequential work in deep blocks
**Deep work timing:** morning
**Approach:** practical and visual, fast once the client problem is clear
**Energy model:** strongest before client calls begin
**Input method:** voice-to-text for thinking, keyboard for final drafts

---

## Decision Style

**Decision style:** dialogue

Sara decides best by talking the choice through, then writing the actual next step. She stalls when too many half-decisions stay open at once.

**Bias toward:** clear client work over abstract brand theory
**When stuck:** talks it out and looks for the smallest visible proof

---

## Communication Preferences

- **Prefers:** direct and short
- **Prompts:** conversational voice notes
- **Response length:** short by default, longer when strategy is unclear

---

~~~

### core\voice-profile.yml

~~~text
voice:
  rhythm: "mixed"
  opening_style: "confession"
  closing_style: "weight"
  signoff_phrase: ""
  person_default: "mixed"
  contractions: "always"
  hedging: "occasional"
  reading_level: 8
  preferred_words:
    - "proof"
    - "useful"
    - "quiet"
    - "trust"
  banned_words:
    - "premium"
    - "disrupt"
    - "world-class"
  idiosyncrasies:
    - "starts with a small admission before the point"
    - "uses short fragments after a longer thought"
    - "uses parentheses for quiet asides"
  buyer_language:
    first_sentence: "We look smaller than we are."
    phrases:
      - "People do not get what we do."
      - "The site does not match the business anymore."
      - "We need someone who can make it clear without making it loud."
  samples:
    - title: "Post-call note"
      context: "work email"
      text: |
        I have been thinking about yesterday's call. The website is not the first problem. The first problem is that the offer feels like three businesses trying to share one front door. If we fix that, the pages get easier.
    - title: "Studio note"
      context: "LinkedIn draft"
      text: |
        I used to think good design meant making the client look bigger. I was wrong. Most of the time, the braver work is making the business easier to trust.
    - title: "Client boundary"
      context: "email"
      text: |
        I can take this on, but only if we keep one decision-maker in the room. Too many opinions will make the work safer, not better.
~~~

### core\brand-profile.yml

~~~text
identity:
  display_name: "Northline Studio"
  tagline: "Brand and web design for UAE small businesses"
  support_contact: "hello@northline.example"

colors:
  primary:
    hex: "#17324D"
    usage: "section headers + emphasis"
  secondary:
    hex: "#CFAE70"
    usage: "accents + CTAs"
  dark:
    hex: "#111827"
    usage: "body text + dark backgrounds"
  light:
    hex: "#F7F4EF"
    usage: "light backgrounds + dividers"
  accent:
    hex: "#2F9C95"
    usage: "highlights only - use sparingly"

fonts:
  primary:
    family: "Inter"
    source: "google_fonts"
  secondary:
    family: "Cormorant Garamond"
    source: "google_fonts"
  weights:
    section_header: { font: "primary", weight: "Bold", size_pt: 15 }
    subsection: { font: "primary", weight: "Medium", size_pt: 11 }
    body: { font: "primary", weight: "Light", size_pt: 9 }
    emphasis: { font: "primary", weight: "Regular", size_pt: 10 }
    footer: { font: "primary", weight: "Light", size_pt: 8 }
    cover_title: { font: "primary", weight: "Bold", size_pt: 26 }
    cover_subtitle: { font: "primary", weight: "Medium", size_pt: 15 }

logo:
  logomark:
    path: "text-only"
    description: "temporary wordmark until logo files are added"
  full:
    path: "[NOT SET]"
    description: "not set"
  white:
    path: "[NOT SET]"
    description: "not set"

footer:
  text: "Northline Studio | hello@northline.example"

assets_dir: "core/brand-assets/"

existing_assets:
  has_assets: "partial"
  references:
    - type: "deck"
      location: "Google Drive / Northline old client deck"
      notes: "Use only as visual proof. The structure is old."
~~~

## LinkedIn post diff

~~~diff
diff --git "a/C:\\arcas_dev\\test-installs\\founderos-v1202-trace-post\\pre-linkedin.txt" "b/C:\\arcas_dev\\test-installs\\founderos-v1202-trace-post\\post-linkedin.txt"
index 137e076..f19a844 100644
--- "a/C:\\arcas_dev\\test-installs\\founderos-v1202-trace-post\\pre-linkedin.txt"
+++ "b/C:\\arcas_dev\\test-installs\\founderos-v1202-trace-post\\post-linkedin.txt"
@@ -1,23 +1,31 @@
-I stopped chasing big-logo clients when I realized I was using their brand to borrow confidence.
+I stopped chasing big-logo clients after a smaller founder said something I could not ignore.

-It looked smart from the outside.
-Inside the studio, it made the work worse.
+"We look smaller than we are."

-The bigger the name, the more people had to approve the smallest thing.
-The first call felt exciting.
-The second call turned into a committee.
-The third call became "can you send a deck and we'll circle back?"
+That sentence changed how I qualify design work.

-Meanwhile, the smaller UAE business with an owner in the room would decide fast, trust the work, and actually ship.
+A big-logo client can sound like proof.
+But sometimes the project is mostly approval layers, soft timelines, and a committee trying to agree on taste.

-That changed how I qualify clients at Northline.
+The smaller business with the owner in the room is different.
+They are not asking for decoration.
+They are saying:

-I now listen for three things:
--> Is the decision-maker in the first conversation?
--> Do they know what problem they want solved?
--> Will they let design do its job, or are they buying decoration?
+-> People do not get what we do.
+-> The site does not match the business anymore.
+-> We need someone who can make it clear without making it loud.

-A famous logo can still be a good client.
-But it is no longer the prize.
+That is a real design problem.
+It has a buyer.
+It has pain.
+It has a decision attached to it.

-The prize is a client with urgency, trust, and a real decision to make.
+So I stopped using famous logos as the prize.
+
+Now I listen for the owner who can name the problem in plain words.
+The one who feels the gap every time they send the website link.
+The one who wants the business to be easier to trust.
+
+That is where the useful work is.
+
+Quiet, specific, and much harder to fake.
~~~

## Post-patch LinkedIn post output

~~~text
I stopped chasing big-logo clients after a smaller founder said something I could not ignore.

"We look smaller than we are."

That sentence changed how I qualify design work.

A big-logo client can sound like proof.
But sometimes the project is mostly approval layers, soft timelines, and a committee trying to agree on taste.

The smaller business with the owner in the room is different.
They are not asking for decoration.
They are saying:

-> People do not get what we do.
-> The site does not match the business anymore.
-> We need someone who can make it clear without making it loud.

That is a real design problem.
It has a buyer.
It has pain.
It has a decision attached to it.

So I stopped using famous logos as the prize.

Now I listen for the owner who can name the problem in plain words.
The one who feels the gap every time they send the website link.
The one who wants the business to be easier to trust.

That is where the useful work is.

Quiet, specific, and much harder to fake.
~~~

## /rant final outcome

Input: I am tired of leads going cold after the first call.

~~~text
Question: Does this need a decision, a draft, a plan, or just to be captured?

Sara: Draft. I need a follow-up that makes them choose a path.

Route: email-drafter

Draft:
Subject: Quick check on whether this is real

Hi [Name],

I have been thinking about our first call.

The problem sounded clear to me: the business has outgrown the way it shows up, and the current site is making people work too hard to understand what you do.

Before I shape a proposal, I want to check the decision.

Is this a project you want to move on this month, something to revisit later, or a no for now?

Any of those answers is fine. I would rather know than keep you in a polite follow-up loop.

Sara
~~~

## Result

- Identity now has `## Positioning`.
- Voice profile now has `buyer_language`.
- Brand profile now has `existing_assets`.
- LinkedIn output uses buyer wording from the intake instead of generic client qualification language.
- `/rant` routes to `email-drafter` and returns a useful follow-up draft instead of a capture receipt.
