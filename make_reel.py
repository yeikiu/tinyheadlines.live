"""Refresh the B site's reel with the most varied recent scenes (JQ 28-nov: «no quiero solo phys.org en la web en los
ejemplos», «necesitas variedad de los que estas creando ahora»). Run by run/publish_web.py before each B publish.

Picks 6 scenes from data/scenes (news of the last 72 h first, then older), greedily maximising different outlets
and topics, never two in a row from the same outlet; writes assets/s-<id>.webp (640x480) and rewrites the reel's
<li> lines (12: 6 + their aria-hidden copies) and the two screens of the signage section. Prints what it chose.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHELF = ROOT / "data" / "scenes"
FFMPEG = ROOT / "runtime" / "ffmpeg" / "ffmpeg.exe"
N = 6


def ts(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def scenes() -> list[dict]:
    out = []
    for d in SHELF.iterdir():
        st, poster = d / "story.json", d / "poster.jpg"
        if d.is_dir() and st.exists() and poster.exists() and (d / "scene.mp4").exists():
            try:
                s = json.loads(st.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            s["_poster"] = poster
            out.append(s)
    now = datetime.now(timezone.utc)
    out.sort(key=lambda s: (now - ts(s.get("published")) > timedelta(hours=72), -ts(s.get("published")).timestamp()))
    return out


def pick(all_s: list[dict]) -> list[dict]:
    chosen: list[dict] = []
    while len(chosen) < N and len(chosen) < len(all_s):
        outlets = [c.get("medio") for c in chosen]
        topics = [c.get("tema") for c in chosen]
        best = min((s for s in all_s if s not in chosen),
                   key=lambda s: (outlets.count(s.get("medio")), topics.count(s.get("tema"))))
        chosen.append(best)
    # order: never the same outlet twice in a row when avoidable
    ordered: list[dict] = []
    rest = list(chosen)
    while rest:
        nxt = next((s for s in rest if not ordered or s.get("medio") != ordered[-1].get("medio")), rest[0])
        ordered.append(nxt)
        rest.remove(nxt)
    return ordered


def esc(t: str) -> str:
    return (t or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> int:
    chosen = pick(scenes())
    if len(chosen) < 3:
        print("too few scenes, reel unchanged")
        return 0
    for s in chosen:
        dest = HERE / "assets" / f"s-{s['id']}.webp"
        if not dest.exists():
            subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y", "-i", str(s["_poster"]), "-vf",
                            "scale=-2:480,crop=640:480,eq=gamma=1.15", "-quality", "80", str(dest)], check=True)
    page = HERE / "index.html"
    raw = page.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    idx = [i for i, l in enumerate(lines) if "<li" in l and 'src="assets/s-' in l]
    if not idx or idx[-1] - idx[0] != len(idx) - 1:
        print("reel block not found, unchanged")
        return 1
    li = [f'      <li><img src="assets/s-{s["id"]}.webp" width="640" height="480" loading="lazy" '
          f'alt="Realistic 3D scene: {esc(s.get("corto") or s.get("titular"))}"><small>{esc(s.get("medio"))}</small></li>'
          for s in chosen]
    li += [f'      <li aria-hidden="true"><img src="assets/s-{s["id"]}.webp" width="640" height="480" loading="lazy" '
           f'alt=""><small>{esc(s.get("medio"))}</small></li>' for s in chosen]
    lines[idx[0]:idx[-1] + 1] = li
    out = nl.join(lines)
    out = re.sub(r'(<div class="tv"><img src="assets/)s-[^"]+(\.webp")', rf'\1s-{chosen[0]["id"]}\2', out)
    out = re.sub(r'(<div class="totem"><img src="assets/)s-[^"]+(\.webp")', rf'\1s-{chosen[1]["id"]}\2', out)
    page.write_bytes(out.encode("utf-8"))
    used = {f"s-{s['id']}.webp" for s in chosen}
    for f in (HERE / "assets").glob("s-*.webp"):
        if f.name not in used:
            f.unlink()
    print("reel:", ", ".join(f"{s['id']} ({s.get('medio')})" for s in chosen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
