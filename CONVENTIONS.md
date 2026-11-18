# Conventions

## Media IDs

`MR-<YYYY>-<NNNN>` — year of publication, then a zero-padded serial in feed order.
`MR-2022-0001`. The ID never changes once assigned, even if the item is later withdrawn.

Third-party shows carrying a principal use the same scheme with a `TP` infix: `MR-TP-2022-0001`.

On acquisition and hashing, each item is also registered in the investigation's
`sources/register.csv` and takes an evidence ID there. **Media ID and evidence ID are both carried in
`MANIFEST.csv`.** The media ID is this lane's handle; the evidence ID is the file's.

## Uncertainty markers — the repo's own, use these

`[inaudible]` · `[unclear]` · `[speaker uncertain]` — each means exactly what it says.
**Never resolve one by guessing.** A plausible-looking transcript is more dangerous than an
obviously rough one.

## Transcript states

| State | Meaning | May be quoted |
|---|---|---|
| `[ASR]` | Machine output, unreviewed | **No. Never** |
| `[VERIFIED]` | A human listened at the timestamp and confirmed the words | Yes, short and exact |
| `[DISPUTED]` | Audio ambiguous; alternatives recorded | No, and it cannot carry a finding |

A `[VERIFIED]` passage against hashed audio is `D1` for *this person said these words*. It is never
`D1` for the truth of what was said.

## Speaker basis codes

| Code | Basis |
|---|---|
| `SELF` | The speaker names themself in the audio. Also generates a `T-ID` flag |
| `INTRO` | The host or another speaker names them on air |
| `VOICEPRINT` | Match against a held reference sample. The sample's own provenance is recorded beside it |
| `PUBLISHER` | The publisher's firsthand recognition, dated. Not a machine match |
| `UNNAMED` | Default, and it stays the default |

**Non-principals are not named.** A guest or caller on a volunteer broadcast is `SPEAKER_nn` plus a
role label — unless they are a public figure, spoke in an official capacity, or are a principal.

## Annotation

Passage-level annotation, classification and ranking are **investigation work product and are not
published here.** This repository carries the transcripts, their provenance and their corrections.
What anyone makes of a given passage is analysis, licensed separately and kept separately.

## Transcript file format

Every transcript carries the full per-item header. These fields are mandatory — attribution is
structural to the fair-dealing basis, not a courtesy, and a transcript stripped of it loses that
basis (`COPYRIGHT.md`).

```
---
media_id: MR-2022-0001
title: <as published>
source_channel: <channel name and ID>
source_video_id: <platform ID>
source_url: <URL as at capture>
published: 2022-00-00
duration: 00:00:00
source: <S-T id>
media_sha256: <hex of the file as acquired, BEFORE any processing>
captured_at: <UTC date and time>
capture_method: <tool>
transcribed_at: <date>
transcribed_with: <tool and version>
live_at_source: yes | no | removed
last_checked: <date>
state: ASR | VERIFIED | DISPUTED
verified_by:
verified_date:
---

[00:00:00] SPEAKER_01 (UNNAMED) [ASR]
Text.

[00:01:12] Named Speaker (INTRO, 2026-11-18) [VERIFIED]
Text.
```

One speaker turn per block. Timestamps at turn starts. Never edit the text of a block without
changing its state back to `[ASR]`.

## Redaction

Any residential address, phone number, email or other personal identifier spoken on air is replaced
in the open text with `[REDACTED — personal identifier]`, timestamp retained. This applies with more
force here than anywhere else in the investigation: live radio is where people say their address out
loud.


## Third-party shows — a separate rights posture

Items published by **someone other than Mriya Report** are not covered by the preservation
argument in `COPYRIGHT.md`, which rests on this publisher's own material being withdrawn from
public view. For a third party's show: **metadata and short verified quotation only.** No full
verbatim transcript enters this repository without a specific decision recorded in
`corrections.md`.

## Removals

Where an item is no longer live at source, it is logged in `removals.csv`: prior location, date
last seen, and the archival record establishing it existed. **The removal is a documented event in
its own right**, and documenting it is as time-critical as the capture, because the evidence that
something existed also decays.

This repository is a preservation effort under time pressure. **Capture precedes transcription.** A
recording that disappears cannot be transcribed later; a recording in hand can be transcribed any
time. Nothing in the acquisition queue waits on a transcription decision.

## Corrections

Corrections are made **against the recording** and **logged in `corrections.md`**, never silently
applied. A transcript repository whose history can be quietly rewritten is worth nothing to anyone
relying on it.
