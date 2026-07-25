# Update packs

One file per release, per group of changes. A pack is what an update looks like from your side: what changed, whether it matters to you, and what to do about it.

## Why packs exist

Pulling new files is easy. Pulling new files into an OS you have spent months personalizing is where it goes wrong. Your `CLAUDE.md` has your edits in it. Your rules have your corrections. A plain overwrite takes those away and you find out weeks later, when something you fixed is broken again.

So an update is not a download. It is a conversation your own assistant has with you, using these packs as the script. Each pack names what changed, filters itself against what you have actually adopted, and proposes each edit as a diff you accept or decline. Nothing lands silently.

## How to use them

Say "update Founder OS" (or run `/founder-os:update`). That pulls the new files and then walks the packs newer than your version, skipping anything for a module you do not run. You never need to open this folder.

Read one directly if you want to know what a release did before you take it.

## The five sections, and why each is required

Every pack carries all five. A pack missing one does not ship.

1. **What changed.** Plain description. No version numbers doing the talking.
2. **Why it matters to you.** The honest answer, including "it might not". A pack that cannot say who this is for and who can skip it has not been thought through.
3. **Files.** Added, changed, and which module each belongs to, so the skip logic is visible rather than magic.
4. **Integration protocol.** Step by step, written to survive being pasted into any assistant by someone who is not a developer.
5. **No Claude Code? The by-hand path.** The single file to copy, or the single edit to make, to get most of the value with no tooling at all. **A pack that cannot state this does not ship.** If a change cannot be described as a by-hand step, it is too complicated to be an update and belongs in a release you choose to install fresh.

## The three-way merge, in plain terms

When a release changes a file you may have edited, three versions exist: the old shipped one, the new shipped one, and yours. The update compares all three, works out what the release actually changed, and proposes that change on top of your version, leaving your edits where they are.

You see a diff and say yes or no, per file. Never a batch yes. If the merge cannot be done cleanly, you get told that plainly and nothing is written. A refused update is a working install. A silently merged one might not be.

## Naming

`updates/<version>-<slug>.md`, for example `1.43.0-doctrine.md`. Several packs per release is normal and preferred: it lets you take the part you want and leave the rest.
