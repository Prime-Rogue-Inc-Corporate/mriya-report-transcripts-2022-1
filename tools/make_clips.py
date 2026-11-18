#!/usr/bin/env python3
"""Cut confirmation clips for every flagged passage that still needs a human ear.

The publisher confirms by listening, not by reading ASR text. This reads flags.csv,
cuts a padded clip around each flag whose state is not VERIFIED, drops it in clips/,
and writes clips/CONFIRM.md as a checklist.

  python3 tools/make_clips.py --audio-root /path/to/audio --pad 15
  python3 tools/make_clips.py --audio-root ~/MriyaDrive/audio --only T-ID,T-FUND

Needs ffmpeg on PATH. Clips are re-encoded to 64 kbps mono mp3 so they are small enough
to send; the clip is for confirmation, never the artifact of record. The artifact of
record is the full hashed source file.
"""
import argparse, csv, os, re, subprocess, sys

def to_s(t):
    t = t.strip()
    if not t: return None
    if re.fullmatch(r"\d+(\.\d+)?", t): return float(t)
    p = [float(x) for x in t.split(":")]
    while len(p) < 3: p.insert(0, 0.0)
    return p[0]*3600 + p[1]*60 + p[2]

def hms(s):
    s = int(s); return f"{s//3600:02d}-{s%3600//60:02d}-{s%60:02d}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flags", default="flags.csv")
    ap.add_argument("--manifest", default="MANIFEST.csv")
    ap.add_argument("--audio-root", required=True, help="folder holding the source audio")
    ap.add_argument("--out", default="clips")
    ap.add_argument("--pad", type=float, default=15.0, help="seconds of lead-in and lead-out")
    ap.add_argument("--only", help="comma-separated flag classes to cut")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    only = set(a.only.split(",")) if a.only else None
    titles = {}
    if os.path.exists(a.manifest):
        with open(a.manifest, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                titles[r["media_id"]] = r.get("title", "")

    os.makedirs(a.out, exist_ok=True)
    todo, missing = [], []
    with open(a.flags, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("state") or "").upper() == "VERIFIED":
                continue
            if only and r.get("class") not in only:
                continue
            start, end = to_s(r.get("start", "")), to_s(r.get("end", ""))
            if start is None:
                missing.append((r.get("flag_id"), "no start timestamp")); continue
            if end is None or end <= start:
                end = start + 60.0
            src = None
            for ext in (".mp3", ".m4a", ".opus", ".wav", ".mp4", ".webm"):
                p = os.path.join(a.audio_root, r["media_id"] + ext)
                if os.path.exists(p): src = p; break
            if not src:
                missing.append((r.get("flag_id"), f"no audio for {r['media_id']} under {a.audio_root}")); continue
            ss = max(0.0, start - a.pad)
            out = os.path.join(a.out, f"{r['flag_id']}_{r['media_id']}_{hms(start)}.mp3")
            todo.append((r, src, ss, (end - start) + 2*a.pad, out))

    for r, src, ss, dur, out in todo:
        cmd = ["ffmpeg","-nostdin","-loglevel","error","-y","-ss",f"{ss:.3f}","-t",f"{dur:.3f}",
               "-i",src,"-vn","-ac","1","-b:a","64k",out]
        print(("DRY  " if a.dry_run else "cut  ") + out)
        if not a.dry_run:
            subprocess.run(cmd, check=True)

    with open(os.path.join(a.out, "CONFIRM.md"), "w", encoding="utf-8") as f:
        f.write("# Confirmation queue\n\n")
        f.write("Each clip below is a flagged passage awaiting a human ear. Listening is the only\n")
        f.write("thing that moves a passage from `[ASR]` to `[VERIFIED]`. Nothing here may be quoted,\n")
        f.write("published or sent to a third party until it is confirmed.\n\n")
        f.write("Clips carry `--pad` seconds of lead-in and lead-out so the passage has context.\n")
        f.write("The clip is for confirmation only; the artifact of record is the full hashed source.\n\n")
        f.write("Log the outcome in `verification.csv`, then set the flag's `state`.\n\n")
        f.write("| # | flag | class | speaker (claimed) | basis | at | clip | words as transcribed | confirmed? |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for i, (r, src, ss, dur, out) in enumerate(todo, 1):
            q = (r.get("quote_verbatim") or "").replace("|", "\\|")[:200]
            f.write(f"| {i} | `{r['flag_id']}` | {r.get('class','')} | {r.get('speaker','') or '—'} "
                    f"| {r.get('speaker_basis','') or '—'} | {r.get('start','')} "
                    f"| `{os.path.basename(out)}` | {q} | ☐ yes ☐ no ☐ unclear |\n")
        if missing:
            f.write("\n## Could not cut\n\n")
            for fid, why in missing:
                f.write(f"- `{fid}` — {why}\n")
        f.write(f"\n---\n\n{len(todo)} clip(s) queued, {len(missing)} not cut.\n")
    print(f"\n{len(todo)} cut, {len(missing)} skipped. Checklist: {a.out}/CONFIRM.md", file=sys.stderr)

if __name__ == "__main__":
    main()
