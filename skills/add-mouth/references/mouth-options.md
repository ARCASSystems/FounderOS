# Mouth options - what each adds, what it costs, where your text goes

`setup.py` wires the OS-native mouth by default. It needs nothing extra. The rest are opt-in.
The one thing that matters most when you pick: **does your text leave your machine, and does
it cost anything.** That is stated for each option below.

## OS-native (default, free, fully local)

Your operating system already has a voice. The default uses it:

- **Windows:** System.Speech (SAPI), driven through PowerShell. Built in.
- **macOS:** the `say` command. Built in. Pick a voice with `--voice <name>` (see `say -v ?`).
- **Linux:** `spd-say` (speech-dispatcher) to speak, or `espeak-ng` / `espeak` to speak and to
  render a file. If none is present: `sudo apt install espeak-ng` (or your distro's package).

Free, no key, and your text never leaves the machine. Rendering to a file produces a `.wav`
(an `.aiff` on macOS). This is the accessibility-floor mouth and it is the default for a reason.

## Piper (opt-in, free, fully local, better voice)

[Piper](https://github.com/rhasspy/piper) is a free neural voice that runs offline. It sounds
markedly better than the OS-native voice and still never sends your text anywhere.

1. Install Piper so `piper` is on your PATH (see the Piper releases page for your platform).
2. Download a voice model (a `.onnx` file) from the Piper voices list.
3. Put the model path in `voice/mouth-config.json` as `"voice": "/path/to/voice.onnx"`.
4. Re-run: `python skills/add-mouth/setup.py --engine piper`.

Cost: free. Locality: fully local. Trade: a one-time download and a little setup for a better
voice that still respects privacy.

## ElevenLabs (opt-in, paid, NOT local)

[ElevenLabs](https://elevenlabs.io) gives broadcast-quality voices. Use it for something you
publish, not for everyday read-backs. It is a deliberate spend.

1. Store your key in the gitignored `.env`: say "connect elevenlabs" or run
   `python scripts/connect.py set-secret ELEVENLABS_API_KEY` (pasted on stdin, never as an
   argument). The key never lands in a tracked file.
2. Optionally set a voice id in `voice/mouth-config.json` as `"voice": "<elevenlabs-voice-id>"`.
3. Re-run: `python skills/add-mouth/setup.py --engine elevenlabs`.

Cost: paid, per the ElevenLabs plan you choose. Locality: NOT local - your text is sent to
ElevenLabs to synthesize. `say.py` prints that it used the ElevenLabs mouth every time, so the
trade is never hidden. The OS-native and Piper voices stay free and local for everything else.

## Browser (the voice loop, not a separate mouth)

The `add-voice` skill's page already speaks through the browser's built-in voice, inside the
talk-and-listen loop. If what you want is a conversation rather than a one-way read-back, that
is `add-voice`, not this skill. `add-mouth` is for speaking an answer or rendering a file from
any skill, without holding a conversation.

## How a skill speaks its output

Any skill's text output can be piped to the mouth:

```
python voice/say.py "a line you want read aloud"
echo "longer text from another command" | python voice/say.py
python voice/say.py --out today.wav "render today's brief to a file"
```

The mouth speaks what it is given. It does not generate content, and it does not send the
audio anywhere - sending or posting is an action, and actions live behind the `add-hands`
confirm gate, not here.
