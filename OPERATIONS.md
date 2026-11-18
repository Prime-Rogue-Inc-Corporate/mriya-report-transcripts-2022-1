# Operations — mriya-report-transcripts-2022-1

Operator's copy. Read `README.md`, `LICENSE` and `COPYRIGHT.md` first — they govern.
**Owner / publisher:** Kevin J.S. Duska Jr., Prime Rogue Inc.
**Lane state:** `claude/transcripts-thread-state.md` in the project — authoritative for scope and
standards. This README is the operator's copy.

---

## Publisher's rulings, 2026-11-18

| | |
|---|---|
| **Scope** | **Everything publicly shared gets transcribed.** If it was broadcast to the public, it is in scope |
| **Audio** | **Google Drive.** Audio is pushed to Drive, never committed to git. Bound to the corpus by SHA-256 in `MANIFEST.csv` and `SHA256SUMS` |
| **Confirmation** | Anything needing a human ear is **cut to a clip** in `clips/` for the publisher to confirm. `tools/make_clips.py`, checklist at `clips/CONFIRM.md` |

One safeguard held pending a word either way: **`[ASR]` machine text is not pushed to this repo.**
Only `[VERIFIED]` transcripts land here. ASR fabricates on proper names, and an unverified
transcript that puts words in a named serving officer's mouth is published the moment it is pushed,
not drafted. Say the word and it changes.

## What is in here

| Path | Holds |
|---|---|
| `MANIFEST.csv` | One row per media item. The index of the corpus |
| `index/YT-INDEX-2022.csv` | The YouTube channel's 2022 videos — the raw 24/7 restreams |
| `transcripts/<media_id>.md` | Human-readable, speaker-attributed, timestamped transcript |
| `transcripts/<media_id>.json` | Machine transcript, word-level timestamps, diarization labels |
| `verification.csv` | Who listened to which passage, when. The audit trail behind `[VERIFIED]` |
| `clips/` | Padded confirmation clips + `CONFIRM.md` checklist |
| `SHA256SUMS` | Checksums of every acquired source file |
| `tools/` | `harvest_feed.py` (index the feed), `make_clips.py` (cut confirmation clips) |

## The corpus, as measured 2026-11-18

Two separate bodies of audio, and the difference between them decides the whole method.

| | Items | Runtime | What it is |
|---|---|---|---|
| **Podcast feed** (`anchor.fm/s/ace6a3f0/podcast/rss`) | ~416 total, **69 in 2022** | ~620 h total, **109 h in 2022** | The **curated** extract: titled, dated, guest named in the title |
| **YouTube channel** (`@mriya_report`, 566 videos) | **159 in 2022 (12 Aug – 18 Nov)** | **1,264 h** | The **raw 24/7 restream**. Mostly untitled beyond a date; typical item runs 8–12 h |

**The feed is the index; YouTube is the haystack.** Three of 159 YouTube items in 2022 carry a
real title. Transcribing the restreams whole is thousands of hours and four figures of ASR spend.
They get searched by date window, when a date is known to matter — not swept.

**Known gap: the channel's oldest videos are not yet indexed.** The listing in hand starts at
12 August 2022; the channel holds 566 videos and has been broadcasting since the day before the
full-scale invasion. The unindexed block is roughly **February to 11 August 2022**.

## Repo rotation

New repo at a calendar-year boundary of **publication date**, or when `git count-objects -vH`
size-pack passes **800 MB**, whichever comes first. `mriya-report-transcripts-<YYYY>-<n>`; volume
`n` increments only on the size trigger. With audio in Drive, the text alone will not reach the
size trigger, so in practice rotation is annual.

| | |
|---|---|
| Predecessor | — (first volume) |
| Successor | — |

**Keep these pointers current.** A corpus split across repos with no index is a corpus you lost.

## Indexes before media

The index is the thing that cannot be reconstructed. If a feed or channel goes down mid-capture, an
index in hand says exactly what the missing remainder was; without one you do not know what you
lost. Media capture takes hours. Enumeration takes minutes. **Both indexes before any media.**

Capture the channel's and the show's own text too — About pages, descriptions, pinned posts. Small,
and it goes when the channel goes.

## The two rules that matter most

1. **No passage leaves this repository in any form unless it is `[VERIFIED]`.** Machine output is
   never quoted. The README accuracy notice is the floor; this is the control.
2. **No speaker is named without a recorded basis.** `SELF` / `INTRO` / `VOICEPRINT` / `PUBLISHER`
   / `UNNAMED` — see `CONVENTIONS.md`.
