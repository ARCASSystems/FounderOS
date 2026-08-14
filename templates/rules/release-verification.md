# Release verification - why a green suite was not enough

This file governs how Founder OS itself ships. It lives in the repo rather than in the maintainer's head because the discipline was paid for in public: across v1.53.0 to v1.54.2, two outside reviews surfaced sixteen findings against releases that shipped with a full passing suite, six green CI gates, and hand-run verification tables. Fifteen reproduced; the one that arrived without a reproduction did not survive checking, which is itself the filter this page mandates. The changelog carries both accounts. The causes were structural, so the counter-measures are structural, and they apply to any contribution that ships from here.

## The structural problem no effort fixes

Whoever builds a change writes its tests from the same mental model as the code. The proven specimen from this repo's own history: a test in the maintainer's suite pushed to a bare repo in the same temp folder and asserted the OS report "a second copy exists away from this computer." The test encoded the bug as the expected result. It passed every run and could never have failed, because the author of the code and the author of the test were the same person holding the same wrong idea.

That is not sloppiness, it is a limit of self-verification. The counter-measure is not more tests by the same hands - it is a second context with none of the builder's assumptions, told to break the claims rather than confirm the features.

## The four gates

**1. Refute before push.** Before a release commits, a context that did not build it - another model, a fresh session, a reviewer - gets the diff and the release's user-facing claims, instructed to refute them. Every finding needs a reproduction or an explicit unverified flag; this repo's review history shows the filter working in both directions: of sixteen findings across the two reviews, the fifteen that carried reproductions all held, and the one without was the one that fell. A defect found before the push is a build note. The same defect found after is a patch release with an apology in the changelog.

**2. A user-facing claim is a specification.** Every sentence a founder can read as a promise - "backed up", "your install is complete", "nothing leaves the machine" - is a claim with failure modes, not copy. "Backed up" turned out to have four; none had a test, because it had been treated as wording. Each release enumerates its claims in the update pack, and each carries either a test that tried to make it false or an honest unverified label. A claim with neither does not ship wearing confidence.

**3. A finding names an instance; the fix names the class.** One review said "setup.md tells founders to reinstall." That file was fixed - and fifteen other files, seventeen messages, kept saying it for two more releases, because nobody grepped. An outside finding closes only when the pattern has been searched repo-wide and the release notes say so. The grep costs thirty seconds; skipping it cost three releases.

**4. The coverage floor is mechanical.** Any script that writes secrets, sends anything, deletes files, or reports safety status carries a test file, enforced by a check in the maintainer's suite (which runs upstream of every release and is not shipped in this repo - the README's standing note) - a check, not a judgment call, because judgment is exactly what left the credential-writing helper untested for three releases ("it is small"). The floor's debt list can shrink and cannot grow.

## What convergence looks like

Not zero findings - a review that finds nothing is usually shallow, not proof of perfection. The measures that matter, and the record so far:

- No install-breaking defect reaches a founder. The refute pass exists to catch these before the push.
- No defect class is found twice. A repeat class is a process failure, whatever the code says.
- Severity falls release over release. v1.53's findings were "the advertised install path does not work." v1.54.1's were serious - three routes to a false "backed up" line and a secret escaping through a hard link - but every one required an unusual configuration, where v1.53's hit every founder on the path the README advertises. That narrowing, install-breaking to corner-case, is the system working. It has to keep earning that sentence every release.
- Every real finding becomes a permanent test. The suite grew 847 to 883 across one review cycle, and that growth is the point: the suite is the accumulated memory of every mistake ever caught, which is why the same mistake cannot come back quietly.

## For a founder reading this

Nothing here asks anything of you. It is the standard the updates you receive are held to, written down where you can check it - the same way `rules/security-baseline.md` writes down what leaves your machine. If you ever find the OS telling you something that is not true, that is a defect of the highest class this file exists to prevent, and solutions@arcassystems.com wants to know about it.
