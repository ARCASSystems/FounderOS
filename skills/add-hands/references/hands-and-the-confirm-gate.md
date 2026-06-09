# Hands and the confirm gate - what the OS can do, and what it asks first

`setup.py` wires the safe hands and the gate. Read this so you know exactly what the OS can
do for you, what it stops to ask about, and what it cannot do yet.

## The three classes

Every action belongs to one class, and the class decides what happens. The class is recorded
in `voice/hands-config.json` so you can see and change it.

### Auto - runs freely (safe, reversible, local)

These cannot lose work or reach outside your machine, so the OS does them without asking:

- **open** - open a file, a folder, an app, or a link with your operating system's opener.
  `python voice/hands.py open .` opens the OS folder; `open https://example.com` opens a link.
- **note** - append a dated line to `brain/log.md`. You can delete the line to undo it.
  `python voice/hands.py note "called the supplier, waiting on a quote"`.

Asking for a yes on these would only get in your way, so it does not.

### Confirm - stops for an explicit yes (irreversible)

These can change something you cannot simply undo, so the OS shows you the action and waits:

- **run** - run a local command. It is **OFF by default**. Turn it on by setting
  `handlers.run.enabled` to `true` in `voice/hands-config.json`. Even then:
  - `python voice/hands.py run "git status"` prints the exact command and refuses.
  - `python voice/hands.py run "git status" --yes` runs it. The `--yes` is your confirmation.

  The OS never supplies the `--yes` for you. That is the gate: an irreversible action needs an
  explicit, informed yes, and the command is shown before you give it.

### Not built - refused honestly

These are named so you are never misled about what the OS can do:

- **send** a message, **post** to a channel, push to a remote, delete or overwrite a file.
- **computer control** - driving your screen, mouse, or keyboard.

They are not built. The dispatcher refuses them with a plain message rather than half-doing or
pretending. When they are added, they enter the **Confirm** class, behind this same gate, and
never run on their own. Sending and posting will also need a tool connected through `connect`,
so a credential never lands in a tracked file.

## Why a gate and not a feature switch

Hands are where an assistant stops being safe by default. A long list of actions that all run
on their own is how an OS sends the wrong message or overwrites the wrong file. The gate is the
people-first answer: the OS is useful for everything reversible, and it stops and asks for
everything that is not. It is the same approval-gates discipline the OS already applies to its
own writes, now applied to actions in the world.

## Turning on the command runner (a deliberate choice)

The command runner is the one confirm-class action shipped today. Enabling it is a decision you
make, not a default and not something a skill flips on:

1. Open `voice/hands-config.json`.
2. Set `handlers.run.enabled` to `true`.
3. From then on, `run` works but stops for `--yes` every time, showing the command first.

If you never enable it, the OS can still open things and save notes - the safe hands - and that
is the whole default.
