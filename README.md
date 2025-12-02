# Korg microSAMPLER Bank Format — A Field Guide for the Perplexed

## What This Is

A short, sharp guide to the weird little world inside `.msmpl_bank` files. This exists so future developers don't repeat our mistakes, cry into hex editors, or assume the audio is "just PCM" because some guy said so.

## The High‑Level Truth

Korg's microSAMPLER stores **raw, uncompressed 16‑bit PCM audio**, but it wraps it in a file format that:

- *looks* like PCM at first glance
- *acts* like encrypted alien residue when misread
- hides the real samples behind headers, metadata, and byte-swapping trickery

The result? Many folks convince themselves the audio is compressed, encoded, scrambled, or possessed by ghosts.

It isn't. It's just **organized in a way that Korg never really told anyone about**.

## The Three Tags

Every `.msmpl_bank` file is a jungle of repeating blocks. Three species roam this habitat:

- `` — Bank header.
- `` — Sample data block. This is the one you want.
- `` — Sequence block. Not covered here, but lurking.

If you're hunting for audio: **follow the SmpDs**.

## The Gotcha That Bit Everyone (Including Us)

The audio *is* raw PCM… but:

### 🧨 It's **big‑endian** PCM inside the file.

### 🎧 WAV files expect **little‑endian**.

If you don't swap the byte pairs before writing the WAV, the result is:

- shrieking static
- digital banshee noises
- the sound of your soul leaving your body

Swap bytes → music. Don't swap → apocalypse.

## Sample Block Anatomy (SmpD)

Each sample block looks like this:

```
00: "6150SmpD"
08: something length-related
16: unknown but length-related fields
32: 8-byte sample name
40+: assorted flags and parameters
96: PCM data length (3 bytes, little-endian)
99: start of PCM data
```

Things Korg actually documented: nothing.

Things reverse-engineering taught us:

- Byte 102 (`fmt`) contains both the **sample rate code** and **mono/stereo bit**.
- The PCM length at offset 96 is accurate.
- Multiple SmpD blocks appear in a bank, but only some contain real audio (length > 0).
- Korg pads blocks to alignment boundaries because reasons.

## Sample Rate Encoding

`fmt` byte's lower 4 bits:

```
0x00 → 48 kHz (mono)
0x04 → 24 kHz (mono)
0x08 → 12 kHz (mono)
0x0C →  6 kHz (mono)

LSB = 1 → stereo
```

If you want to understand why they did it this way, you're asking questions the universe cannot answer.

## Why Everyone Gets Tricked

### 1. The file *starts* with a bunch of SmpD blocks that **contain no audio**.

They're metadata only — length = 0.

### 2. The real audio blocks live farther down.

They're evenly spaced, aligned, and easy to mistake for unrelated structures.

### 3. Byte order isn't documented.

When 16‑bit audio looks like random static, most devs assume "wrong sample rate" or "wrong offset." Nope. It's just endian hell.

### 4. Korg's editor hides all this.

The official editor/librarian app exports WAVs but never reveals how the sausage is made.

## How To Actually Extract Audio

1. Scan for `6150SmpD`.
2. For each hit:
   - Read name at bytes 32–40
   - Read length at bytes 96–99
   - Read `fmt` byte at 102
   - Read PCM bytes starting at 96 + length
3. Swap every pair of bytes.
4. Write to WAV using the decoded sample rate.

That's it. No voodoo. No compressors. No secret sauce.

## Why This README Exists

Because assumptions grow like mold:

- "The samples are ADPCM!" (nope)
- "The samples are compressed!" (nope)
- "The whole file is one long PCM chunk!" (nope)
- "The grid blocks hold the audio!" (only metadata)
- "The Microsampler is magic!" (yes, but not for this reason)

This README is here to help new developers:

- trust data, not rumors
- read bytes, not forum posts
- bring snacks when opening hex editors

## Final Advice

When you hear static:

- **swap the bytes** before questioning your sanity.

When nothing makes sense:

- assume Korg aligned something oddly.

When all fails:

- walk away, drink water, come back.

Happy hacking.

