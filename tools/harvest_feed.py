#!/usr/bin/env python3
"""Stage 1 of the transcripts lane: harvest a podcast feed into MANIFEST.csv rows,
then keyword-sweep titles and descriptions to rank what is worth transcribing.

Stage 1 is free. Stage 2 (transcription) costs money, so it only ever runs on the
shortlist this produces.

Usage
-----
  # from the network
  python3 tools/harvest_feed.py --url https://anchor.fm/s/ace6a3f0/podcast/rss \
      --year 2022 --out MANIFEST.csv --save-feed evidence/feed-2026-11-18.xml

  # from a feed already on disk (preferred: the XML is itself an artifact, so keep it)
  python3 tools/harvest_feed.py --file evidence/feed-2026-11-18.xml --year 2022

  # rank what to transcribe
  python3 tools/harvest_feed.py --file evidence/feed-2026-11-18.xml --sweep

Notes
-----
* --year filters by publication year and sets the media-ID prefix. Omit it for the whole feed.
* Always --save-feed. The raw XML is the acquisition artifact; hash it and register it.
* Stdlib only, deliberately. No install step, nothing to audit.
"""

import argparse
import csv
import hashlib
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# The sweep's term set is investigation work product and is NOT carried in this repository.
# Supply it with --keywords FILE, a JSON object of {"label": ["term", ...]}; --always FILE takes
# a JSON list of terms that promote an item regardless of score. Without them, the script indexes
# the feed and does not rank.
KEYWORDS = {}
ALWAYS = []

NS = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "content": "http://purl.org/rss/1.0/modules/content/",
}

MANIFEST_FIELDS = [
    "media_id", "evidence_id", "title", "show", "platform", "source_id", "url", "guid",
    "published", "duration", "speakers_claimed", "acquisition_status", "audio_sha256",
    "capture_date", "capture_method", "transcript_state", "flags_count", "notes",
]


def text_of(el):
    if el is None:
        return ""
    return html.unescape("".join(el.itertext())).strip()


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def fetch(url, save_to=None):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "prime-rogue-transcripts/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    if save_to:
        os.makedirs(os.path.dirname(save_to) or ".", exist_ok=True)
        with open(save_to, "wb") as f:
            f.write(raw)
        print(f"feed saved: {save_to}  sha256={hashlib.sha256(raw).hexdigest()}", file=sys.stderr)
    return raw


def parse(raw):
    root = ET.fromstring(raw)
    channel = root.find("channel")
    show = text_of(channel.find("title")) if channel is not None else ""
    items = []
    for it in (channel.findall("item") if channel is not None else []):
        desc = text_of(it.find("description")) or text_of(it.find("content:encoded", NS))
        enc = it.find("enclosure")
        pub_raw = text_of(it.find("pubDate"))
        try:
            pub = parsedate_to_datetime(pub_raw).astimezone(timezone.utc).date().isoformat()
        except Exception:
            pub = pub_raw
        items.append({
            "show": show,
            "title": text_of(it.find("title")),
            "desc": strip_tags(desc),
            "guid": text_of(it.find("guid")),
            "published": pub,
            "duration": text_of(it.find("itunes:duration", NS)),
            "url": (enc.get("url") if enc is not None else ""),
            "length": (enc.get("length") if enc is not None else ""),
        })
    return show, items


def handles(s):
    return sorted(set(re.findall(r"@[A-Za-z0-9_]{2,15}", s)))


def score(item):
    blob = (item["title"] + " " + item["desc"]).lower()
    hits = {}
    for cls, terms in KEYWORDS.items():
        found = [t for t in terms if t in blob]
        if found:
            hits[cls] = found
    always = [t for t in ALWAYS if t in blob]
    # Weight the classes that bear on open findings.
    weights = {"T-ID": 10, "T-LEGAL": 5, "T-FUND": 4, "T-ORG": 3, "T-CRIT": 4, "PERSON": 3}
    total = sum(weights.get(c, 1) * len(v) for c, v in hits.items())
    if always:
        total += 6
    return total, hits, always


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url")
    src.add_argument("--file")
    ap.add_argument("--save-feed")
    ap.add_argument("--year", type=int, help="filter by publication year; sets the media-ID prefix")
    ap.add_argument("--prefix", default="MR")
    ap.add_argument("--out", default="MANIFEST.csv")
    ap.add_argument("--source-id", default="S-T01")
    ap.add_argument("--platform", default="anchor/rss")
    ap.add_argument("--sweep", action="store_true", help="rank instead of writing the manifest")
    ap.add_argument("--keywords", help="JSON file of {label: [terms]}; not carried in this repo")
    ap.add_argument("--always", help="JSON file of terms that promote regardless of score")
    a = ap.parse_args()

    global KEYWORDS, ALWAYS
    if a.keywords:
        import json; KEYWORDS = json.load(open(a.keywords, encoding="utf-8"))
    if a.always:
        import json; ALWAYS = json.load(open(a.always, encoding="utf-8"))
    if a.sweep and not KEYWORDS:
        sys.exit("--sweep needs --keywords; the term set is not carried in this repository")

    raw = fetch(a.url, a.save_feed) if a.url else open(a.file, "rb").read()
    show, items = parse(raw)
    print(f"show: {show}\nitems in feed: {len(items)}", file=sys.stderr)

    if a.year:
        items = [i for i in items if str(i["published"]).startswith(str(a.year))]
        print(f"items in {a.year}: {len(items)}", file=sys.stderr)

    items.sort(key=lambda i: str(i["published"]))

    if a.sweep:
        ranked = []
        for i in items:
            total, hits, always = score(i)
            ranked.append((total, i, hits, always))
        ranked.sort(key=lambda r: -r[0])
        print(f"\n{'score':>5}  {'date':10}  {'dur':>8}  title / why")
        print("-" * 100)
        for total, i, hits, always in ranked:
            if total == 0:
                continue
            why = "; ".join(f"{c}:{','.join(v[:4])}" for c, v in hits.items())
            if always:
                why = f"ALWAYS:{','.join(always)}; " + why
            print(f"{total:>5}  {i['published']:10}  {i['duration']:>8}  {i['title'][:70]}")
            print(f"{'':>5}  {'':10}  {'':>8}  -> {why[:150]}")
            hs = handles(i["title"] + " " + i["desc"])
            if hs:
                print(f"{'':>5}  {'':10}  {'':>8}  -> handles: {' '.join(hs[:12])}")
        zero = sum(1 for r in ranked if r[0] == 0)
        print(f"\n{len(ranked) - zero} scored, {zero} scored zero.")
        print("A zero score is NOT evidence an episode is empty: a principal hosting under a")
        print("show name will not appear in the metadata. The sweep ranks; it does not filter.")
        return

    year = a.year or "ALL"
    rows, n = [], 0
    for i in items:
        n += 1
        rows.append({
            "media_id": f"{a.prefix}-{year}-{n:04d}",
            "evidence_id": "",
            "title": i["title"],
            "show": i["show"],
            "platform": a.platform,
            "source_id": a.source_id,
            "url": i["url"],
            "guid": i["guid"],
            "published": i["published"],
            "duration": i["duration"],
            "speakers_claimed": " ".join(handles(i["title"] + " " + i["desc"])),
            "acquisition_status": "listed",
            "audio_sha256": "",
            "capture_date": "",
            "capture_method": "",
            "transcript_state": "",
            "flags_count": "0",
            "notes": i["desc"][:300],
        })

    exists = os.path.exists(a.out) and os.path.getsize(a.out) > 0
    with open(a.out, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        if not exists:
            w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {a.out} at {datetime.now(timezone.utc).isoformat()}", file=sys.stderr)


if __name__ == "__main__":
    main()
